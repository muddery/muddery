"""
This model translates default strings into localized strings.
"""

import importlib
from muddery.server.conf import settings
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy import select, update, delete
from muddery.server.utils.utils import class_from_path
from muddery.server.database.db_manager import DBManager
from muddery.server.utils.singleton import Singleton


class HonoursMapper(Singleton):
    """
    This model stores all character's honours.
    """
    def __init__(self):
        self.model_name = "honours"
        module = importlib.import_module(settings.GAME_DATA_MODEL_FILE)
        self.model = getattr(module, self.model_name)
        self.session = DBManager.inst().get_session(settings.GAME_DATA_APP)
        self.honours = {}
        self.rankings = []

    async def reload(self):
        """
        Reload all data.
        """
        self.honours = {}
        self.rankings = []

        stmt = select(self.model)
        result = self.session.execute(stmt)
        for record in result.scalars():
            self.honours[record.character] = {
                "honour": record.honour,
                "place": 0,
                "ranking": 0
            }
        self.make_rankings()

    def make_rankings(self):
        """
        Calculate all character's rankings.
        """
        rankings = sorted(self.honours.items(), key=lambda x: x[1]["honour"], reverse=True)
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
        return character.id in self.honours

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
        except Exception as e:
            print("Can not get character's honour: %s" % e)

    def get_honour(self, char_db_id, default=None):
        """
        Get a character's honour.
        
        Args:
            char_id: (string) A character's id.
            
        Return:
            number: Character's honour.
        """
        try:
            return self.honours[char_db_id]["honour"]
        except Exception as e:
            if default is not None:
                return default
            else:
                print("Can not get character's honour: %s" % e)
            
    def get_ranking(self, char_db_id):
        """
        Get a character's ranking.
        
        Args:
            char_db_id: (int) Character's db id.
            
        Return:
            number: Character's ranking.
        """
        try:
            return self.honours[char_db_id]["ranking"]
        except Exception as e:
            print("Can not get character's ranking: %s" % e)
            
    def get_top_rankings(self, number):
        """
        Get top ranking characters.
        """
        if number <= 0:
            return
        return [char_id for char_id in self.rankings[:number]]
        
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

    async def create_honour(self, char_id, honour):
        """
        Add a new character's honour.

        Args:
            char_id: character's id
            honour: character's honour
        """
        try:
            record = self.model(
                character=char_id,
                honour=honour
            )
            self.session.add(record)

            self.honours[char_id] = {
                "honour": honour,
                "place": 0,
                "ranking": 0
            }
            self.make_rankings()
        except Exception as e:
            print("Can not create character's honour: %s" % e)

    async def set_honour(self, char_id, honour):
        """
        Set a character's honour.
        
        Args:
            char_id: character's id
            honour: character's honour
        """
        stmt = update(self.model).where(character=char_id).values(honour=honour)
        result = self.session.execute(stmt)
        if result.rowcount > 0:
            try:
                self.honours[char_id]["honour"] = honour
            except Exception as e:
                print("Can not set character's honour: %s" % e)
        else:
            # Add a new honour record.
            await self.create_honour(char_id, honour)

        self.make_rankings()

    async def set_honours(self, new_honours):
        """
        Set a set of characters' honours.
        
        Args:
            new_honours: (dict) {character's id: character's honour}
        """
        for key in new_honours:
            if key not in self.honours:
                await self.create_honour(key, 0)

        success = False
        with self.session.begin():
            for key, value in new_honours.items():
                stmt = update(self.model).where(character=key).values(honour=value)
                result = self.session.execute(stmt)
            success = True
        
        if success:
            for key, value in new_honours.items():
                self.honours[key]["honour"] = value
            self.make_rankings()
        else:
            print("Can not set character's honours")
            
    async def remove_character(self, char_db_id):
        """
        Remove a character's honour.
        """
        try:
            stmt = delete(self.model).where(character=char_db_id)
            self.session.execute(stmt)
            del self.honours[char_db_id]
            self.make_rankings()
        except Exception as e:
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
