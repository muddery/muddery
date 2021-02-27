
"""
Store object's element key data in memory.
"""

from django.apps import apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist


class PlayerCharacter(object):
    """
    The storage of player character data.
    """
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = apps.get_model(settings.GAME_DATA_APP, model_name)
        self.records = {}
        self.nicknames = {}

        # load data
        for record in self.model.objects.all():
            self.records[record.object_id] = {
                "nickname": record.nickname,
            }
            self.nicknames[record.nickname] = record.object_id

    def add(self, object_id, nickname):
        """
        Store an object's key.
        :param object_id:
        :param nickname:
        :return:
        """
        if object_id in self.records:
            if self.records["nickname"] == nickname:
                return

        try:
            record = self.model()
            record.object_id = object_id
            record.nickname = nickname
            record.save()

            self.records[object_id] = {
                "nickname": record.nickname,
            }
            self.nicknames[nickname] = object_id
        except Exception as e:
            print("Can not add %s's nickname: %s" % (object_id, nickname))

    def remove(self, object_id):
        """
        Remove an object.
        :param object_id:
        :return:
        """
        if not object_id in self.records:
            return

        try:
            self.model.objects.get(object_id=object_id).delete()
            nickname = self.records[object_id]["nickname"]
            del self.records[object_id]
            del self.nicknames[nickname]
        except ObjectDoesNotExist:
            pass
        except Exception as e:
            print("Can not remove object's element key: %s %s" % (object_id, e))

    def get_nickname(self, object_id):
        """
        Get a player character's nickname.
        :param object_id:
        :return:
        """
        try:
            return self.records[object_id]["nickname"]
        except KeyError:
            return None

    def get_object_id(self, nickname):
        """
        Get an player character's id by its nickname.
        :param key:
        :return:
        """
        try:
            return self.nicknames[nickname]
        except KeyError:
            return None


PLAYER_CHARACTER = PlayerCharacter("player_character")
