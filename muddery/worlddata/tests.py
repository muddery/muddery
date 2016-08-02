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
        
        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/worldmap.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/characters.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/objects.html')
        self.failUnlessEqual(response.status_code, 200)
        
        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/equipments.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/quests.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/events.html')
        self.failUnlessEqual(response.status_code, 200)

        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/dialogues.html')
        self.failUnlessEqual(response.status_code, 200)
        
        # Check that the respose is 200 OK.
        response = self.client.get('/worlddata/editor/localization.html')
        self.failUnlessEqual(response.status_code, 200)
