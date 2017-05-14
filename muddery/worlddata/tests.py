from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.contrib import auth

class TestEditor(TestCase):

    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_editor(self):
        user_model = auth.get_user_model()
        user = user_model.objects.create_user(username='test',password='test',email='')
        user.is_staff = True
        user.save()

        login = self.client.login(username="test", password="test")
        self.assertTrue(login)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/')
        self.failUnlessEqual(response.status_code, 200)
        
        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/defines.html')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/worlddata/editor/defines/game_settings/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/defines/class_categories/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/defines/typeclasses/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/defines/equipment_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/defines/equipment_positions/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/defines/character_careers/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/defines/quest_objective_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/defines/quest_dependency_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/defines/event_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/defines/event_trigger_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/worldmap.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/worldmap/world_rooms/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/worldmap/world_exits/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/worldmap/exit_locks/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/worldmap/world_objects/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/worldmap/world_npcs/form.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/characters.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/characters/character_careers/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/characters/character_models/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/characters/world_npcs/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/characters/common_characters/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/characters/skills/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/characters/default_skills/form.html')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/worlddata/editor/characters/npc_dialogues/form.html')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/worlddata/editor/characters/character_loot_list/form.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/objects.html')
        self.failUnlessEqual(response.status_code, 200)

        response = self.client.get('/worlddata/editor/objects/world_objects/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/objects/common_objects/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/objects/object_creators/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/objects/creator_loot_list/form.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/equipments.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/equipments/equipment_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/equipments/equipment_positions/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/equipments/equipments/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/equipments/career_equipments/form.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/quests.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/quests/quests/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/quests/quest_reward_list/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/quests/quest_objective_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/quests/quest_objectives/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/quests/quest_dependency_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/quests/quest_dependencies/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/quests/dialogue_quest_dependencies/form.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/events.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/events/event_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/events/event_trigger_types/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/events/event_data/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/events/event_attacks/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/events/event_dialogues/form.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/dialogues.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/dialogues/dialogues/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/dialogues/dialogue_quest_dependencies/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/dialogues/dialogue_relations/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/dialogues/dialogue_sentences/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/dialogues/npc_dialogues/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/dialogues/event_dialogues/form.html')
        self.failUnlessEqual(response.status_code, 200)
        
        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/localization.html')
        self.failUnlessEqual(response.status_code, 200)
        
        response = self.client.get('/worlddata/editor/localization/localized_strings/form.html')
        self.failUnlessEqual(response.status_code, 200)
