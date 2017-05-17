import sys
from muddery.utils.localiztion_handler import localize_form_field
from muddery.worlddata import forms_base


class GameSettingsForm(forms_base.GameSettingsForm):
    pass


class ClassCategoriesForm(forms_base.ClassCategoriesForm):
    pass


class TypeclassesForm(forms_base.TypeclassesForm):
    pass


class EquipmentTypesForm(forms_base.EquipmentTypesForm):
    pass


class EquipmentPositionsForm(forms_base.EquipmentPositionsForm):
    pass


class CharacterCareersForm(forms_base.CharacterCareersForm):
    pass


class QuestObjectiveTypesForm(forms_base.QuestObjectiveTypesForm):
    pass


class EventTypesForm(forms_base.EventTypesForm):
    pass


class EventTriggerTypes(forms_base.EventTriggerTypes):
    pass


class QuestDependencyTypesForm(forms_base.QuestDependencyTypesForm):
    pass


class WorldAreasForm(forms_base.WorldAreasForm):
    pass


class WorldRoomsForm(forms_base.WorldRoomsForm):
    def __init__(self, *args, **kwargs):
        super(WorldRoomsForm, self).__init__(*args, **kwargs)
        localize_form_field(self, "peaceful")


class WorldExitsForm(forms_base.WorldExitsForm):
    pass


class ExitLocksForm(forms_base.ExitLocksForm):
    pass


class TwoWayExitsForm(forms_base.TwoWayExitsForm):
    pass


class WorldObjectsForm(forms_base.WorldObjectsForm):
    pass


class WorldNPCsForm(forms_base.WorldNPCsForm):
    pass


class ObjectCreatorsForm(forms_base.ObjectCreatorsForm):
    pass


class CreatorLootListForm(forms_base.CreatorLootListForm):
    pass


class CharacterLootListForm(forms_base.CharacterLootListForm):
    pass


class QuestRewardListForm(forms_base.QuestRewardListForm):
    pass


class CommonObjectsForm(forms_base.CommonObjectsForm):
    pass


class FoodsForm(forms_base.FoodsForm):
    pass


class SkillBooksForm(forms_base.SkillBooksForm):
    pass


class CharacterModelsForm(forms_base.CharacterModelsForm):
    pass


class CommonCharacterForm(forms_base.CommonCharacterForm):
    pass


class DefaultObjectsForm(forms_base.DefaultObjectsForm):
    pass


class SkillsForm(forms_base.SkillsForm):
    pass


class DefaultSkillsForm(forms_base.DefaultSkillsForm):
    pass


class NPCDialoguesForm(forms_base.NPCDialoguesForm):
    pass


class QuestsForm(forms_base.QuestsForm):
    pass


class QuestObjectivesForm(forms_base.QuestObjectivesForm):
    pass


class QuestDependenciesForm(forms_base.QuestDependenciesForm):
    pass


class DialogueQuestDependenciesForm(forms_base.DialogueQuestDependenciesForm):
    pass


class EquipmentsForm(forms_base.EquipmentsForm):
    pass


class CareerEquipmentsForm(forms_base.CareerEquipmentsForm):
    pass


class EventDataForm(forms_base.EventDataForm):
    pass


class EventAttacksForm(forms_base.EventAttacksForm):
    pass


class EventDialoguesForm(forms_base.EventDialoguesForm):
    pass


class DialoguesForm(forms_base.DialoguesForm):
    pass


class DialogueRelationsForm(forms_base.DialogueRelationsForm):
    pass


class DialogueSentencesForm(forms_base.DialogueSentencesForm):
    pass


class LocalizedStringsForm(forms_base.LocalizedStringsForm):
    pass


class ImageResourcesForm(forms_base.ImageResourcesForm):
    pass


class IconResourcesForm(forms_base.IconResourcesForm):
    pass


class Manager:
    relations = {}

    @classmethod
    def get_form(cls, model_name):
        """
        Get form class by model's name.

        Args:
            model_name: model's name

        Returns:
        """
        return cls.relations[model_name]

    @classmethod
    def init_data(cls):
        module = sys.modules[cls.__module__]
        for name in dir(module):
            try:
                form_class = getattr(module, name)
                model_name = form_class.Meta.model.__name__
                cls.relations[model_name] = form_class
            except Exception, e:
                pass


Manager.init_data()
