
"""
This file checks user's edit actions and put changes into db.
"""

import os
import cStringIO
from PIL import Image, ImageFont, ImageDraw
from django import http
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.db.models.fields.related import ManyToOneRel
from django.conf import settings
from evennia.utils import logger
from muddery.utils.exception import MudderyError
from muddery.worlddata.editor.form_view import FormView
from worlddata import models

class DialogueInfo(object):
    """
    Dialogue block's information.
    """
    def __init__(self):
        self.dlg_key = None
        self.root_key = None
        self.root_distance = None
        self.parents = set()
        self.children = set()
        self.pos_x = None
        self.pos_y = None


class DialogueChainImage(object):
    """
    This object deal with dialogue relation's edit forms and views.
    """
    def __init__(self, form_name, request):
        """
        Set form name and request.

        Args:
            form_name: model form's name
            request: http request

        Returns:
            None
        """
        self.form_name = form_name
        self.request = request

        # get request data
        if self.request.POST:
            self.request_data = self.request.POST
        else:
            self.request_data = self.request.GET

        self.search_range = 3
        self.valid = None
        self.record = None
        self.error = None
        self.data = None

        self.dlg_map = [[] for _ in xrange(-self.search_range, self.search_range + 1)]
        self.dialogues = {}

    def is_valid(self):
        """
        Validate the request.

        Returns:
            boolean: is valid
        """
        if self.valid is None:
            # If the request has not been parsed, parse it.
            self.valid = self.parse_request()

        return self.valid

    def parse_request(self):
        """
        Parse request data.

        Returns:
            boolean: Parse success.
        """
        # record's id
        self.record = self.request_data.get("_record", None)

        return True

    def search_dlg(self, dlg_key, distance):

        if dlg_key in self.dialogues:
            return

        info = DialogueInfo()
        info.dlg_key = dlg_key
        info.distance = distance
        self.dialogues[dlg_key] = info

        # Find next dialogues
        children = models.dialogue_relations.objects.filter(dialogue=dlg_key)
        for child in children:
            info.children.add(child.next_dlg)
            if distance < self.search_range:
                self.search_dlg(child.next_dlg, distance + 1)

        # Find previous dialogues.
        parents = models.dialogue_relations.objects.filter(next_dlg=dlg_key)
        for parent in parents:
            info.parents.add(parent.dialogue)
            if distance < self.search_range:
                self.search_dlg(parent.dialogue, distance + 1)

    def is_root(self, dlg_key):
        """
        Check if this dialogue is a root.

        Args:
            dlg_key: dialogue's key.

        Returns:
            boolean
        """
        try:
            models.npc_dialogues.objects.get(dialogue=dlg_key)
            # This dialogue is a root.
            return True
        except Exception, e:
            pass

        try:
            models.dialogue_relations.objects.get(next_dlg=dlg_key)
            return True
        except Exception, e:
            pass

        return False

    def search_root(self, dialogues, distance, checked):
        """
        Recursion search dialogue's root.

        Args:
            dialogues: A list of dialogue's keys.

        Returns:
            (root dialogue's key, distance)
        """
        if not dialogues:
            return

        for dialogue in dialogues:
            if self.is_root(dialogue):
                return dialogue, distance

        total_parents = []
        for dialgue in dialogues:
            # Check this dialogue's parents.
            records = models.dialogue_relations.objects.filter(next_dlg=dialgue)
            parents = [record.dialogue for record in records if record.dialogue not in checked]

            total_parents.extend(parents)
            checked.update(parents)

        result = self.search_root(total_parents, distance + 1, checked)
        if not result:
            return dialogues[0], distance

        return result

    def find_root(self, dlg_key):
        """
        Find a dialogue's root.

        Args:
            dlg_key:

        Returns:
            (root dialogue's key, distance)
        """
        records = models.dialogue_relations.objects.filter(next_dlg=dlg_key)
        if not records:
            return dlg_key, 0

        parents = [record.dialogue for record in records]
        checked = set(parents)
        return self.search_root(parents, 1, checked)

    def query_data(self):
        """
        Get db instance for the image.

        Returns:
            None
        """
        if not self.valid:
            raise MudderyError("Invalid form: %s." % self.form_name)

        if not self.record:
            return

        self.data = None
        try:
            # Query record's data.
            relation = models.dialogue_relations.objects.get(pk=self.record)
        except Exception, e:
            return

        self.search_dlg(relation.dialogue, 0)

        # get distance to the root
        roots_distance = {}
        for dlg_info in self.dialogues.values():
            root_key, root_distance = self.find_root(dlg_info.dlg_key)
            if root_key not in roots_distance:
                roots_distance[root_key] = root_distance
            else:
                if root_distance < roots_distance[root_key]:
                    roots_distance[root_key] = root_distance
            dlg_info.root_key = root_key
            dlg_info.root_distance = root_distance

        # build a map according to roots
        max_y = 0
        for dlg_info in self.dialogues.values():
            root_pos = roots_distance[dlg_info.root_key]
            dlg_info.pos_y = dlg_info.root_distance - root_pos
            if dlg_info.pos_y > max_y:
                max_y = dlg_info.pos_y

        # group dialogues by root
        root_trees = {}
        for dlg_info in self.dialogues.values():
            if dlg_info.root_key not in root_trees:
                root_trees[dlg_info.root_key] = [[] for _ in xrange(max_y + 1)]
            root_trees[dlg_info.root_key][dlg_info.pos_y].append(dlg_info.dlg_key)

        # calculate x pos
        pos_x = 0
        for root_tree in root_trees.values():
            for dlg_key in root_tree:
                pass

        # sort every line by parent number
        for line in self.dlg_map:
            line.sort(key=lambda x:len(self.dialogues[x].parents))

        # store positions
        for line in xrange(len(self.dlg_map)):
            for block in xrange(len(self.dlg_map[line])):
                dlg = self.dlg_map[line][block]
                self.dialogues[dlg].position = (block, line,)

    def render(self):
        """
        Render a new image.

        Returns:
            HttpResponse
        """
        if not self.valid:
            raise MudderyError("Invalid form: %s." % self.form_name)

        # Query data.
        if not self.data:
            self.query_data()
        print(self.dlg_map)

        # get validate levels
        begin_level = self.search_range
        end_level = self.search_range
        max_length = 0
        for i in xrange(0, len(self.dlg_map)):
            length = len(self.dlg_map[i])
            if length > 0:
                if i < begin_level:
                    begin_level = i
                if i > end_level:
                    end_level = i
                if length > max_length:
                    max_length = length

        # set sizes
        border = 20
        block_width = 80
        block_height = 20
        space_width = 20
        space_height = 20
        margin = 5
        total_width = (block_width + space_width) * max_length + border * 2
        total_height = (block_height + space_height) * (end_level - begin_level + 1) + border * 2

        image = Image.new("RGB", (total_width, total_height), (127, 255, 255))
        font_file = os.path.join(settings.GAME_DIR, "static", "worldeditor", "font", "Arial Unicode.ttf")
        font = ImageFont.truetype(font_file, 13)

        # draw image
        draw = ImageDraw.Draw(image)
        for line in xrange(begin_level, end_level + 1):
            for block in xrange(0, len(self.dlg_map[line])):
                dlg_key = self.dlg_map[line][block]

                # set position
                x = block * (block_width + space_width) + border
                y = (line - begin_level) * (block_height + space_height) + border

                # get name
                name = None
                try:
                    dialogue = models.dialogues.objects.get(key=dlg_key)
                    name = dialogue.name[:8]
                except Exception, e:
                    pass

                # draw block
                draw.rectangle([x, y, x + block_width, y + block_height], outline=(63, 63, 63))

                # draw text
                if name:
                    width = draw.textsize(name, font=font)[0]
                    max = block_width - margin * 2
                    if width > max:
                        length = int(float(max) / width / 2 * len(name))
                        while length < len(name) and draw.textsize(name[:length], font=font)[0] < max:
                            length += 1
                        name = name[:length - 1]

                    draw.text((x + margin, y), name, fill=(63, 63, 63), font=font)

                # draw lines to its children
                line_begin_x = x + block_width / 2
                line_begin_y = y + block_height
                print "begin: %s %s" % (block, line)
                for child in self.dialogues[dlg_key].children:
                    end_block, end_line = self.dialogues[child].position
                    print "end: %s %s" % (end_block, end_line)
                    line_end_x = end_block * (block_width + space_width) + border + block_width / 2
                    line_end_y = (end_line - begin_level) * (block_height + space_height) + border
                    draw.line([line_begin_x, line_begin_y, line_end_x, line_end_y], fill=(63, 63, 63))

        del draw

        buf = cStringIO.StringIO() # a memory buffer used to store the generated image
        image.save(buf, "png")

        return HttpResponse(buf.getvalue(), "image/png")
