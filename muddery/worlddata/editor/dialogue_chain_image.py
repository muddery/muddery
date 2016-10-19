
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

        self.dialogues = {}
        self.max_x = 0
        self.max_y = 0

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

        # Count the NPCs who use this dialogue.
        npc_num = models.npc_dialogues.objects.filter(dialogue=dlg_key).count()
        if npc_num > 0:
            return True

        # Find its parents number.
        parent_num = models.dialogue_relations.objects.filter(next_dlg=dlg_key).count()
        if parent_num == 0:
            return True

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

        # group dialogues by root
        root_trees = {}
        for dlg_info in self.dialogues.values():
            if dlg_info.root_key not in root_trees:
                root_trees[dlg_info.root_key] = []
            root_trees[dlg_info.root_key].append(dlg_info.dlg_key)

        # calculate y pos
        for root_tree in root_trees:
            pass

        # build a map according to roots
        self.max_y = 0
        for dlg_info in self.dialogues.values():
            root_pos = roots_distance[dlg_info.root_key]
            dlg_info.pos_y = dlg_info.root_distance - root_pos
            if dlg_info.pos_y > self.max_y:
                self.max_y = dlg_info.pos_y

        # calculate x pos
        self.max_x = -1
        for root_tree in root_trees.values():
            from_x = self.max_x + 1
            for pos_y in xrange(len(root_tree)):
                pos_x = from_x
                for i in xrange(len(root_tree[pos_y])):
                    self.dialogues[root_tree[pos_y][i]].pos_x = i + pos_x
                    self.dialogues[root_tree[pos_y][i]].pos_y = pos_y
                    if i + pos_x > self.max_x:
                        self.max_x = i + pos_x

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

        # set sizes
        border = 20
        block_width = 80
        block_height = 20
        space_width = 20
        space_height = 20
        margin = 5
        total_width = (block_width + space_width) * (self.max_x + 1) + border * 2
        total_height = (block_height + space_height) * (self.max_y + 1) + border * 2

        image = Image.new("RGB", (total_width, total_height), (127, 255, 255))
        font_file = os.path.join(settings.GAME_DIR, "static", "worldeditor", "font", "Arial Unicode.ttf")
        font = ImageFont.truetype(font_file, 13)

        # draw image
        draw = ImageDraw.Draw(image)
        for dlg in self.dialogues.values():
            # set position
            x = dlg.pos_x * (block_width + space_width) + border
            y = dlg.pos_y * (block_height + space_height) + border

            # get name
            name = None
            try:
                dialogue = models.dialogues.objects.get(key=dlg.dlg_key)
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

            for child in self.dialogues[dlg.dlg_key].children:
                line_end_x = self.dialogues[child].pos_x * (block_width + space_width) + border + block_width / 2
                line_end_y = self.dialogues[child].pos_y * (block_height + space_height) + border
                draw.line([line_begin_x, line_begin_y, line_end_x, line_end_y], fill=(63, 63, 63))

        del draw

        buf = cStringIO.StringIO() # a memory buffer used to store the generated image
        image.save(buf, "png")

        return HttpResponse(buf.getvalue(), "image/png")
