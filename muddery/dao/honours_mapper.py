"""
This model translates default strings into localized strings.
"""

from __future__ import print_function

from evennia.utils import logger
from database.models import honours
from django.db import transaction
from django.apps import apps
from django.conf import settings


class HonoursMapper(object):
    """
    This model stores all character's honours.
    """
    def __init__(self):
        self.objects = apps.get_model(settings.ADDITIONAL_DATA_APP, "honours").objects
        self.honours = {}
        self.rankings = []

    def reload(self):
        """
        Reload all data.
        """
        self.honours = {}
        self.rankings = []

        for record in self.objects.all():
            self.honours[record.character] = {"honour": record.honour,
                                              "place": 0,
                                              "ranking": 0}
        self.make_rankings()

    def make_rankings(self):
        """
        Calculate all character's rankings.
        """
        rankings = sorted(self.honours.items(), lambda x, y: cmp(x[1]["honour"], y[1]["honour"]), reverse=True)
        # only ranking normal players
        self.rankings = [item[0] for item in rankings if item[1]["honour"] >= 0]
        
        if not self.rankings:
            return
        
        last = self.rankings[0]
        for i, key in enumerate(self.rankings):
            self.honours[key]["place"] = i
            self.honours[key]["ranking"] = i + 1
            if self.honours[key]["honour"] == self.honours[last]["honour"]:
                self.honours[key]["ranking"] = self.honours[last]["ranking"]
            last = key
            
    def has_info(self, character):
        """
        If a character has honour information.
        
        Args:
            character: (Object) Character object.
            
        Return:
            boolean: has or not.
        """
        return self.honours.has_key(character.id)

    def get_info(self, character):
        """
        Get a character's honour information.
        
        Args:
            character: (Object) Character object.
            
        Return:
            dict: Character's honour information.
        """
        try:
            return self.honours[character.id]
        except Exception, e:
            print("Can not get character's honour: %s" % e)
            
    def get_honour(self, character, default=None):
        """
        Get a character's honour.
        
        Args:
            character: (Object) Character object.
            
        Return:
            number: Character's honour.
        """
        return self.get_honour_by_id(character.id, default)

    def get_honour_by_id(self, character_id, default=None):
        """
        Get a character's honour.
        
        Args:
            character_id: (string) A character's id.
            
        Return:
            number: Character's honour.
        """
        try:
            return self.honours[character_id]["honour"]
        except Exception, e:
            if default is not None:
                return default
            else:
                print("Can not get character's honour: %s" % e)
            
    def get_ranking(self, character):
        """
        Get a character's ranking.
        
        Args:
            character: (Object) Character object.
            
        Return:
            number: Character's ranking.
        """
        try:
            return self.honours[character.id]["ranking"]
        except Exception, e:
            print("Can not get character's ranking: %s" % e)
            
    def get_top_rankings(self, number):
        """
        Get top ranking characters.
        """
        if number <= 0:
            return
        return [id for id in self.rankings[:number]]
        
    def get_nearest_rankings(self, character, number):
        """
        Get nearest ranking characters.
        """
        character_id = character.id
        if character_id in self.honours:
            place = self.honours[character_id]["place"]
            begin = place - number / 2
            if begin < 0:
                begin = 0
            end = begin + number + 1
            if end > len(self.rankings):
                end = len(self.rankings)
                begin = end - number - 1
                if begin < 0:
                    begin = 0
            return [id for id in self.rankings[begin:end]]
        else:
            return [id for id in self.rankings[-number:]]

    def set_honour(self, character, honour):
        """
        Set a character's honour.
        
        Args:
            character: character object
            honour: character's honour
        """
        try:
            character_id = character.id
            record = self.objects.filter(character=character_id)
            if record:
                record.update(honour = honour)
                self.honours[character_id]["honour"] = honour
            else:
                record = honours()
                record.character = character_id
                record.honour = honour
                record.save()
                self.honours[character_id] = {"honour": honour,
                                              "place": 0,
                                              "ranking": 0}
            self.make_rankings()
        except Exception, e:
            print("Can not set character's honour: %s" % e)

    def set_honours(self, new_honours):
        """
        Set a set of characters' honours.
        
        Args:
            new_honours: (dict) {character's id: character's honour}
        """
        success = False
        with transaction.atomic():
            for key, value in new_honours.iteritems():
                self.objects.filter(character=key).update(honour=value)
            success = True
        
        if success:
            for key, value in new_honours.iteritems():
                self.honours[key]["honour"] = value
            self.make_rankings()
        else:
            print("Can not set character's honours")
            
    def remove_honour(self, character):
        """
        Remove a character's honour.
        """
        try:
            self.objects.get(character=character.id).delete()
            del self.honours[character.id]
            self.make_rankings()
        except Exception, e:
            print("Can not remove character's honour: %s" % e)
            
    def get_characters(self, character, number):
        """
        Get opponents whose ranking is in the given number.
        """
        character_id = character.id
        if character_id in self.honours:
            place = self.honours[character_id]["place"]
            begin = place - number / 2
            if begin < 0:
                begin = 0
            end = begin + number + 1
            if end > len(self.rankings):
                end = len(self.rankings)
                begin = end - number - 1
                if begin < 0:
                    begin = 0
            return [id for id in self.rankings[begin:end] if id != character_id]
        else:
            return [id for id in self.rankings[-number:]]
        

# main honour handler
HONOURS_MAPPER = HonoursMapper()
