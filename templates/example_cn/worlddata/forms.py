# -*- coding: utf-8 -*-

import sys
from django.contrib.admin.forms import forms
from django.conf import settings
from django.apps import apps
from worlddata import models
from worlddata import forms_base


class GameSettingsForm(forms_base.GameSettingsForm):
    def __init__(self, *args, **kwargs):
        super(GameSettingsForm, self).__init__(*args, **kwargs)

        self.fields['connection_screen'].label = u"欢迎文字"
        self.fields['connection_screen'].help_text = u"欢迎文字会在用户连接到游戏的时候显示。"

        self.fields['solo_mode'].label = u"单人模式"
        self.fields['solo_mode'].help_text = u"在单人模式下，一个玩家不会看到其他的玩家。"

        self.fields['global_cd'].label = u"公共CD"
        self.fields['global_cd'].help_text = u"施放技能的公共CD。"

        self.fields['auto_cast_skill_cd'].label = u"自动施放技能CD"
        self.fields['auto_cast_skill_cd'].help_text = u"系统自动施放技能的时间间隔，必须大于公共CD。"

        self.fields['player_reborn_cd'].label = u"玩家重生CD"
        self.fields['player_reborn_cd'].help_text = u"玩家死后重生的时间间隔，如果小于等于0，则玩家会立即重生。"

        self.fields['npc_reborn_cd'].label = u"NPC重生CD"
        self.fields['npc_reborn_cd'].help_text = u"NPC死后重生的时间间隔，如果小于等于0，则NPC不会重生。"

        self.fields['can_give_up_quests'].label = u"允许放弃任务"
        self.fields['can_give_up_quests'].help_text = u"如果允许放弃任务，则玩家可以主动放弃任务。"

        self.fields['auto_resume_dialogues'].label = u"自动继续对话"
        self.fields['auto_resume_dialogues'].help_text = u"如果允许自动继续对话，玩家在登入系统时会自动继续上次未完成的对话。"

        self.fields['default_home_key'].label = u"默认位置"
        self.fields['default_home_key'].help_text = u"所有物体的默认位置，如果物体的所在的房间被移除，则物体会自动移动到默认位置。如果为空，则设为数据表中的第一个房间。"

        self.fields['start_location_key'].label = u"初始位置"
        self.fields['start_location_key'].help_text = u"玩家初次进入系统时的位置。如果为空，则设为数据表中的第一个房间。"

        self.fields['default_player_home_key'].label = u"玩家默认位置"
        self.fields['default_player_home_key'].help_text = u"玩家的默认位置，如果玩家死亡，则会自动移动到玩家默认位置。如果为空，则设为数据表中的第一个房间。"

        self.fields['default_player_model_key'].label = u"默认玩家模型"
        self.fields['default_player_model_key'].help_text = u"默认选用的玩家模型。"


class ClientSettingsForm(forms_base.ClientSettingsForm):
    def __init__(self, *args, **kwargs):
        super(ClientSettingsForm, self).__init__(*args, **kwargs)

        self.fields['map_room_size'].label = u"地图房间尺寸"
        self.fields['map_scale'].label = u"地图比例"
        self.fields['show_command_box'].label = u"是否可以输入命令"
        self.fields['can_close_dialogue'].label = u"是否可以关闭对话"


class ClassCategoriesForm(forms_base.ClassCategoriesForm):
    def __init__(self, *args, **kwargs):
        super(ClassCategoriesForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['desc'].label = u"描述"


class TypeclassesForm(forms_base.TypeclassesForm):
    def __init__(self, *args, **kwargs):
        super(TypeclassesForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['path'].label = u"路径"
        self.fields['category'].label = u"类别"
        self.fields['desc'].label = u"描述"
        self.fields['can_loot'].label = u"是否可以拾取"


class EquipmentTypesForm(forms_base.EquipmentTypesForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentTypesForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['desc'].label = u"描述"


class EquipmentPositionsForm(forms_base.EquipmentPositionsForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentPositionsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['desc'].label = u"描述"


class CharacterCareersForm(forms_base.CharacterCareersForm):
    def __init__(self, *args, **kwargs):
        super(CharacterCareersForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['desc'].label = u"描述"


class QuestObjectiveTypesForm(forms_base.QuestObjectiveTypesForm):
    def __init__(self, *args, **kwargs):
        super(QuestObjectiveTypesForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['desc'].label = u"描述"


class EventTypesForm(forms_base.EventTypesForm):
    def __init__(self, *args, **kwargs):
        super(EventTypesForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['desc'].label = u"描述"


class EventTriggerTypes(forms_base.EventTriggerTypes):
    def __init__(self, *args, **kwargs):
        super(EventTriggerTypes, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['desc'].label = u"描述"


class QuestDependencyTypesForm(forms_base.QuestDependencyTypesForm):
    def __init__(self, *args, **kwargs):
        super(QuestDependencyTypesForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['desc'].label = u"描述"


class WorldRoomsForm(forms_base.WorldRoomsForm):
    def __init__(self, *args, **kwargs):
        super(WorldRoomsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['typeclass'].label = u"类型"
        self.fields['desc'].label = u"描述"
        self.fields['position'].label = u"位置"


class WorldExitsForm(forms_base.WorldExitsForm):
    def __init__(self, *args, **kwargs):
        super(WorldExitsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['typeclass'].label = u"类型"
        self.fields['desc'].label = u"描述"
        self.fields['verb'].label = u"动作"
        self.fields['location'].label = u"位置"
        self.fields['destination'].label = u"目的地"
        self.fields['condition'].label = u"条件"


class ExitLocksForm(forms_base.ExitLocksForm):
    def __init__(self, *args, **kwargs):
        super(ExitLocksForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['unlock_condition'].label = u"解锁条件"
        self.fields['unlock_verb'].label = u"解锁动作"
        self.fields['locked_desc'].label = u"锁定描述"
        self.fields['auto_unlock'].label = u"允许自动解锁"


class WorldObjectsForm(forms_base.WorldObjectsForm):
    def __init__(self, *args, **kwargs):
        super(WorldObjectsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['typeclass'].label = u"类型"
        self.fields['desc'].label = u"描述"
        self.fields['location'].label = u"位置"
        self.fields['condition'].label = u"条件"


class WorldNPCsForm(forms_base.WorldNPCsForm):
    def __init__(self, *args, **kwargs):
        super(WorldNPCsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['typeclass'].label = u"类型"
        self.fields['desc'].label = u"描述"
        self.fields['location'].label = u"位置"
        self.fields['model'].label = u"模版"
        self.fields['level'].label = u"等级"
        self.fields['condition'].label = u"条件"


class ObjectCreatorsForm(forms_base.ObjectCreatorsForm):
    def __init__(self, *args, **kwargs):
        super(ObjectCreatorsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['loot_verb'].label = u"拾取动作"
        self.fields['loot_condition'].label = u"拾取条件"


class CreatorLootListForm(forms_base.CreatorLootListForm):
    def __init__(self, *args, **kwargs):
        super(CreatorLootListForm, self).__init__(*args, **kwargs)

        self.fields['provider'].label = u"提供者"
        self.fields['object'].label = u"掉落物品"
        self.fields['number'].label = u"掉落数量"
        self.fields['odds'].label = u"掉落概率"
        self.fields['quest'].label = u"任务条件"
        self.fields['condition'].label = u"掉落条件"


class CharacterLootListForm(forms_base.CharacterLootListForm):
    def __init__(self, *args, **kwargs):
        super(CharacterLootListForm, self).__init__(*args, **kwargs)

        self.fields['provider'].label = u"提供者"
        self.fields['object'].label = u"掉落物品"
        self.fields['number'].label = u"掉落数量"
        self.fields['odds'].label = u"掉落概率"
        self.fields['quest'].label = u"任务条件"
        self.fields['condition'].label = u"掉落条件"


class QuestRewardListForm(forms_base.QuestRewardListForm):
    def __init__(self, *args, **kwargs):
        super(QuestRewardListForm, self).__init__(*args, **kwargs)

        self.fields['provider'].label = u"提供者"
        self.fields['object'].label = u"掉落物品"
        self.fields['number'].label = u"掉落数量"
        self.fields['odds'].label = u"掉落概率"
        self.fields['quest'].label = u"任务条件"
        self.fields['condition'].label = u"掉落条件"


class CommonObjectsForm(forms_base.CommonObjectsForm):
    def __init__(self, *args, **kwargs):
        super(CommonObjectsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['typeclass'].label = u"类型"
        self.fields['desc'].label = u"描述"
        self.fields['max_stack'].label = u"最大堆叠"
        self.fields['unique'].label = u"是否唯一"


class CharacterModelsForm(forms_base.CharacterModelsForm):
    def __init__(self, *args, **kwargs):
        super(CharacterModelsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['level'].label = u"等级"
        self.fields['max_exp'].label = u"最大经验值"
        self.fields['max_hp'].label = u"最大生命"
        self.fields['max_mp'].label = u"最大魔法"
        self.fields['attack'].label = u"攻击力"
        self.fields['defence'].label = u"防御力"
        self.fields['give_exp'].label = u"提供经验"


class CommonCharacterForm(forms_base.CommonCharacterForm):
    def __init__(self, *args, **kwargs):
        super(CommonCharacterForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['typeclass'].label = u"类型"
        self.fields['desc'].label = u"描述"
        self.fields['model'].label = u"模版"
        self.fields['level'].label = u"等级"


class SkillsForm(forms_base.SkillsForm):
    def __init__(self, *args, **kwargs):
        super(SkillsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['typeclass'].label = u"类型"
        self.fields['desc'].label = u"描述"
        self.fields['cd'].label = u"技能CD"
        self.fields['passive'].label = u"被动技能"
        self.fields['condition'].label = u"施放条件"
        self.fields['function'].label = u"技能函数"
        self.fields['effect'].label = u"技能效果"


class DefaultSkillsForm(forms_base.DefaultSkillsForm):
    def __init__(self, *args, **kwargs):
        super(DefaultSkillsForm, self).__init__(*args, **kwargs)

        self.fields['character'].label = u"角色模版"
        self.fields['skill'].label = u"技能标识"


class QuestsForm(forms_base.QuestsForm):
    def __init__(self, *args, **kwargs):
        super(QuestsForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['typeclass'].label = u"类型"
        self.fields['desc'].label = u"描述"
        self.fields['condition'].label = u"接任务的条件"
        self.fields['action'].label = u"完成任务后的动作"


class NPCDialoguesForm(forms_base.NPCDialoguesForm):
    def __init__(self, *args, **kwargs):
        super(NPCDialoguesForm, self).__init__(*args, **kwargs)

        self.fields['npc'].label = u"NPC"
        self.fields['dialogue'].label = u"对话"
        self.fields['default'].label = u"是否为默认"


class EquipmentsForm(forms_base.EquipmentsForm):
    def __init__(self, *args, **kwargs):
        super(EquipmentsForm, self).__init__(*args, **kwargs)

        self.fields['position'].label = u"位置"
        self.fields['type'].label = u"类型"
        self.fields['attack'].label = u"攻击值"
        self.fields['defence'].label = u"防御值"


class CareerEquipmentsForm(forms_base.CareerEquipmentsForm):
    def __init__(self, *args, **kwargs):
        super(CareerEquipmentsForm, self).__init__(*args, **kwargs)

        self.fields['career'].label = u"职业"
        self.fields['equipment'].label = u"装备"


class QuestObjectivesForm(forms_base.QuestObjectivesForm):
    def __init__(self, *args, **kwargs):
        super(QuestObjectivesForm, self).__init__(*args, **kwargs)

        self.fields['quest'].label = u"任务"
        self.fields['ordinal'].label = u"序号"
        self.fields['type'].label = u"类型"
        self.fields['object'].label = u"对象"
        self.fields['number'].label = u"数量"
        self.fields['desc'].label = u"描述"


class QuestDependenciesForm(forms_base.QuestDependenciesForm):
    def __init__(self, *args, **kwargs):
        super(QuestDependenciesForm, self).__init__(*args, **kwargs)

        self.fields['quest'].label = u"任务"
        self.fields['dependency'].label = u"依赖任务"
        self.fields['type'].label = u"依赖类型"


class DialogueQuestDependenciesForm(forms_base.DialogueQuestDependenciesForm):
    def __init__(self, *args, **kwargs):
        super(DialogueQuestDependenciesForm, self).__init__(*args, **kwargs)

        self.fields['dialogue'].label = u"对话"
        self.fields['dependency'].label = u"依赖任务"
        self.fields['type'].label = u"依赖类型"


class EventDataForm(forms_base.EventDataForm):
    def __init__(self, *args, **kwargs):
        super(EventDataForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['type'].label = u"类型"
        self.fields['trigger_type'].label = u"触发类型"
        self.fields['trigger_obj'].label = u"触发对象"
        self.fields['condition'].label = u"条件"


class EventAttacksForm(forms_base.EventAttacksForm):
    def __init__(self, *args, **kwargs):
        super(EventAttacksForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"事件"
        self.fields['mob'].label = u"攻击者"
        self.fields['level'].label = u"等级"
        self.fields['odds'].label = u"概率"
        self.fields['desc'].label = u"描述"


class EventDialoguesForm(forms_base.EventDialoguesForm):
    def __init__(self, *args, **kwargs):
        super(EventDialoguesForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"事件"
        self.fields['dialogue'].label = u"对话"
        self.fields['npc'].label = u"NPC"


class DialoguesForm(forms_base.DialoguesForm):
    def __init__(self, *args, **kwargs):
        super(DialoguesForm, self).__init__(*args, **kwargs)

        self.fields['key'].label = u"标识"
        self.fields['name'].label = u"名称"
        self.fields['condition'].label = u"条件"


class DialogueRelationsForm(forms_base.DialogueRelationsForm):
    def __init__(self, *args, **kwargs):
        super(DialogueRelationsForm, self).__init__(*args, **kwargs)

        self.fields['dialogue'].label = u"对话"
        self.fields['next'].label = u"后续"


class DialogueSentencesForm(forms_base.DialogueSentencesForm):
    def __init__(self, *args, **kwargs):
        super(DialogueSentencesForm, self).__init__(*args, **kwargs)

        self.fields['dialogue'].label = u"对话"
        self.fields['ordinal'].label = u"序号"
        self.fields['speaker'].label = u"说话者"
        self.fields['content'].label = u"内容"
        self.fields['action'].label = u"动作"
        self.fields['provide_quest'].label = u"提供任务"
        self.fields['complete_quest'].label = u"完成任务"


class LocalizedStringsForm(forms_base.LocalizedStringsForm):
    def __init__(self, *args, **kwargs):
        super(LocalizedStringsForm, self).__init__(*args, **kwargs)

        self.fields['origin'].label = u"原文"
        self.fields['local'].label = u"本地化"


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
