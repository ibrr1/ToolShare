# Create your tests here.
from django.contrib.auth.models import AnonymousUser, User
import unittest
from django.test import TestCase, RequestFactory
from tool_share_app.models import User, Address, States, Shed, Tool, ToolCategory, CurrentlyBorrowedTools,ToolBorrowingRequest
import datetime
from tool_share_app import models
from django.core.urlresolvers import reverse
from tool_share_app.views import login, session, shed_registration
from django.test import Client
from tool_share_app.views import user_profile, session
from django.middleware.csrf import get_token


class TestRegistration(TestCase):
    # fixtures = ['tool_share_app_views_testdata.json']

    def test_registration_views_valid(self):
        # valid url
        response = self.client.get("/registration/")
        self.assertTemplateUsed(response, 'registration.html')
        self.assertEqual(response.status_code, 200)
        state = States.objects.filter(state_name="New York")
        # valid input
        response = self.client.post("/registration/",
                                    data={'first_name': 'adam',
                                          'last_name': 'adam',
                                          'email': 'adam@hotmail.com',
                                          'password': '123456',
                                          'password_verification': '123456',
                                          'street_address': '220',
                                          'zip_code': '77777',
                                          'state': 28,
                                          'city': 'rochester'})
        self.assertEqual(response.status_code, 200)

    def test_registration_views_invalid(self):
        # wrong url
        response = self.client.post("/registra/")
        self.assertNotEqual(response.status_code, 200)
        # invalid email
        response = self.client.post("/registration/",
                                     data={'first_name': 'lion',
                                          'last_name': 'lion',
                                          'email': 'ibrr@hotmail',
                                          'password': '123456',
                                          'password_verification': '123456',
                                          'street_address': 's a 1',
                                          'zip_code': '11111',
                                          'state': 2,
                                          'city': 'rochester'}, follow=True)
                                      # 'admin':'False', 'address':'address'})
        self.assertEqual(response.status_code, 200) # stays in the same url, but post fails
        # invalid: passwords not equal
        response = self.client.post("/registration/",
                                    data={'first_name': 'lion',
                                          'last_name': 'lion',
                                          'email': 'ibrr@hotmail.com',
                                          'password': '123456',
                                          'password_verification': '1234',
                                          'street_address': 's a 1',
                                          'zip_code': '11111',
                                          'state': 2,
                                          'city': 'lion'})
        self.assertNotEqual(response.status_code, 302) # not equal to 302 aka post fails


class TestLogin(TestCase):

    def setUp(self):
        address = Address.objects.create(zip_code="11111", state = States.objects.create(state_name="New York"), city="lion", street_address="s a 1")
        self.user = User.objects.create(email="ibrr1@hotmail.com", first_name="lion", last_name="lion", password="123456",
                                      admin=False, address=address)
        self.factory = RequestFactory()

    def test_login_view_valid(self):
        client = Client()
        response = client.post('/', {'email': 'ibrr1@hotmail.com', 'password': '123456'})
        self.assertEqual(response.status_code, 302)

    def test_login_view_invalid(self):
        client = Client()
        # wrong password
        response = client.post('/', {'email': 'ibrr1@hotmail.com', 'password': '1234'})
        self.assertNotEqual(response.status_code, 302)
        # wrong email
        response = client.post('/', {'email': 'ibrr1@hotmai', 'password': '1234'})
        self.assertNotEqual(response.status_code, 302)


class TestUserProfile(TestCase):

    def setUp(self):
        # creating user to be able to enter the user profile
        self.address = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"), city="lion", street_address="s a 1")
        self.user = User.objects.create(email="adam@hotmail.com", first_name="lion", last_name="lion", password="123456",
                                      admin=False, address=self.address)
        # opening session manually
        session = self.client.session
        session['user_email'] = "adam@hotmail.com"
        session['is_open'] = True
        session.save()

    def test_user_profile_no_shed(self):
        # opening user profile while no shed is registered, redirects to shed creation
        response = self.client.get('/user_profile/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/shed_creation/')
        self.assertTemplateUsed(response, 'new_shed_registration.html')

    def test_user_profile(self):
        # opening user profile
        Shed.objects.create(name='adam shed', address=self.address)
        response = self.client.get('/user_profile/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile.html')


class TestShedRegistration(TestCase):
    def setUp(self):
        # creating user to be able to enter the user profile
        self.address = Address.objects.create(zip_code="11121", state=States.objects.create(state_name="New York"), city="lion", street_address="s a 1")
        self.user = User.objects.create(email="adam@hotmail.com", first_name="lion", last_name="lion", password="123456",
                                      admin=False, address=self.address)
        self.factory = RequestFactory()
        # opening session manually
        session = self.client.session
        session['user_email'] = "adam@hotmail.com"
        session['is_open'] = True
        session.save()

    def test_shed_registration_get(self):
        response = self.client.get('/shed_creation/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'new_shed_registration.html')

    def test_shed_registration_post(self):
        # successful shed registration
        response = self.client.post('/shed_creation/', {'shed_name':'adam', 'street_address':'123 www'},follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response,'/user_profile/') # successfully data is posted and system redirects to next page


class TestManageTools(TestCase):

    def setUp(self):
        # creating user to be able to enter the user profile
        self.address = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"), city="lion", street_address="s a 1")
        self.user = User.objects.create(email="adam@hotmail.com", first_name="adam", last_name="adam", password="123456",
                                      admin=False, address=self.address)
        Shed.objects.create(name='adam shed', address=self.address)
        # opening session manually
        session = self.client.session
        session['user_email'] = "adam@hotmail.com"
        session['is_open'] = True
        session['shed_created'] = True
        session.save()

    def test_manage_tools(self):
        # Tests the basic manage tools link
        response = self.client.get('/user_profile/manage_tools/all_tools/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_tools.html')

    def test_manage_tools_listing(self):
        # Tests manage tools when a listing type is selected
        response = self.client.get('/user_profile/manage_tools/all_tools/', {'tool_listing_type':'tools_shed'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_tools.html')

    def test_manage_tools_addition(self):
        # Tests manage tools adding a new tool
        response = self.client.get('/user_profile/manage_tools/all_tools/', {'name':'tool','condition':'Good','category':'Screwdrivers','location':self.address,'description':'jkjkjk'})
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, 'manage_tools.html')


class TestChangePassword(TestCase):
    def setUp(self):
        # creating user to be able to enter the user profile
        self.address = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"), city="lion", street_address="s a 1")
        self.user = User.objects.create(email="adam@hotmail.com", first_name="lion", last_name="lion", password="123456",
                                      admin=False, address=self.address)
        Shed.objects.create(name='adam shed', address=self.address)
        # opening session manually
        session = self.client.session
        session['user_email'] = "adam@hotmail.com"
        session['is_open'] = True
        session['shed_created'] = True
        session.save()

    def test_change_password_get(self):
        response = self.client.get('/change_password/', {'current_password': '123456', 'new_password': '1234567', 'new_password_verification':'1234567'},follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_password.html')

    def test_change_password_post_valid(self):
        # changing password successfully and being redirected to user profile
        response = self.client.post('/change_password/', {'current_password': '123456', 'new_password': '1234567', 'new_password_verification':'1234567'},follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/user_profile/')

    def test_change_password_post_invalid(self):
        # new password and verifying new password are not the same
        response = self.client.post('/change_password/', {'current_password': '123456', 'new_password': '1234567', 'new_password_verification':'12347'},follow=True)
        self.assertEqual(response.status_code, 200)


class TestUpdateUserInfo(TestCase):

    def setUp(self):
        # creating user to be able to enter the user profile
        self.address = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"), city="lion", street_address="s a 1")
        self.user = User.objects.create(email="adam@hotmail.com", first_name="lion", last_name="lion", password="123456",
                                      admin=False, address=self.address)
        Shed.objects.create(name='adam shed', address=self.address)
        # opening session manually
        session = self.client.session
        session['user_email'] = "adam@hotmail.com"
        session['is_open'] = True
        session['shed_created'] = True
        session.save()

    def test_update_user_info(self):
        response = self.client.post("/user_profile/update_account/",
                                    {'first_name': 'adam',
                                    'last_name': 'adam',
                                    'street_address': '123 bnb ',
                                    'zip_code': '15986',
                                    'city': 'roch',
                                    'state': 28})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'manage_account.html')


class TestLogout(TestCase):

    def test_logout(self):
        response = self.client.post('/user_profile/logout/',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response,'/')# succussfully redirects to login page


class TestTools(TestCase):

    def setUp(self):
        # creating user to be able to enter the user profile
        self.address = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"), city="lion", street_address="432 s a 1")
        self.user = User.objects.create(email="adam@hotmail.com", first_name="lion", last_name="lion", password="123456",
                                      admin=False, address=self.address)
        Shed.objects.create(name='adam shed', address=self.address)
        # opening session manually
        session = self.client.session
        session['user_email'] = "adam@hotmail.com"
        session['is_open'] = True
        session['shed_created'] = True
        session.save()
        self.category = ToolCategory.objects.create(category='Hardware')
        self.tool = Tool.objects.create(name='tool', condition='Good',category=self.category,location=self.address,description='jkjkjk',owner=self.user,status='Available',activate='Activate')

    def test_update_tool_info_get(self):
        response = self.client.get('/user_profile/manage_tools/dfsd/update_tool/'+str(self.tool.id)+'/', {'tool_id':self.tool})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'update_tool.html')

    def test_update_tool_info_get(self):
        response = self.client.get('/user_profile/manage_tools/all_tools/delete/'+str(self.tool.id)+'/',follow=True)
        self.assertEqual(response.status_code, 200) # delete successful, redirecting
        self.assertRedirects(response,'/user_profile/manage_tools/all_tools/') # redirects to all tools page
        # self.assertTemplateUsed(response, 'update_tool.html')
    # def test_update_tool_info_post(self):
    #     print('/user_profile/manage_tools/dfsd/update_tool/'+str(self.tool.id))
    #     response = self.client.post('/user_profile/manage_tools/dfsd/update_tool/'+str(self.tool.id)+'/',{'name':'tool','condition':'Good','description':'jkjkjk','category':self.category,'location':'Home','status':'Available','activate':'Activate'})
    #     self.assertEqual(response.status_code, 200)
    #     # self.assertTemplateUsed(response, '_tool.html')
    #     self.assertRedirects(response,'/user_profile/manage_tools/all_tools/')


class TestNotification(TestCase):

    def setUp(self):
        # creating user to be able to enter the user profile
        self.address = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"),
                                              city="lion", street_address="432 s a 1")
        self.user = User.objects.create(email="adam@hotmail.com", first_name="lion", last_name="lion", password="123456",
                                        admin=False, address=self.address)
        Shed.objects.create(name='adam shed', address=self.address)
        # opening session manually
        session = self.client.session
        session['user_email'] = "adam@hotmail.com"
        session['is_open'] = True
        session['shed_created'] = True
        session.save()
        self.category = ToolCategory.objects.create(category='Hardware')
        self.tool=Tool.objects.create(name='tool', condition='Good',category=self.category,location=self.address,description='jkjkjk',owner=self.user,status='Available',activate='Activate')

    def test_notification(self):
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications.html')

    def test_notification_delete(self):
        response = self.client.get('/notifications/', {'notification_id':''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notifications.html')


class TestSelectAdmin(TestCase):
    def setUp(self):
        # creating user to be able to enter the user profile
        self.address1 = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"),
                                              city="lion", street_address="432 s a 1")
        self.address2 = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"),
                                              city="lion", street_address="432 ssds ")
        self.user1 = User.objects.create(email="adam@hotmail.com", first_name="adam", last_name="adam", password="123456",
                                         admin=True, address=self.address1)
        self.user2 = User.objects.create(email="ann@hotmail.com", first_name="ann", last_name="ann", password="123456",
                                         admin=False, address=self.address2)
        Shed.objects.create(name='adam shed', address=self.address1)
        # opening session manually
        session = self.client.session
        session['user_email'] = "adam@hotmail.com"
        session['is_open'] = True
        session['shed_created'] = True
        session.save()

    def test_select_admin(self):
        response = self.client.get('/user_profile/select_admin/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'select_admin.html')


class Test_Tool_Sharing(TestCase):
    def setUp(self):
        # creating user to be able to enter the user profile
        self.address1 = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"),
                                              city="lion", street_address="432 s a 1")
        self.address2 = Address.objects.create(zip_code="11111", state=States.objects.create(state_name="New York"),
                                              city="lion", street_address="432 ssds ")
        self.user1 = User.objects.create(email="adam@hotmail.com", first_name="adam", last_name="adam", password="123456",
                                         admin=True, address=self.address1)
        self.user2 = User.objects.create(email="ann@hotmail.com", first_name="ann", last_name="ann", password="123456",
                                         admin=False, address=self.address2)
        Shed.objects.create(name='adam shed', address=self.address1)
        # opening session manually
        session = self.client.session
        session['user_email'] = "adam@hotmail.com"
        session['is_open'] = True
        session['shed_created'] = True
        session.save()
        self.category = ToolCategory.objects.create(category='Hardware')
        self.tool=Tool.objects.create(name='tool', condition='Good',category=self.category,location=self.address1,description='jkjkjk',owner=self.user1,status='Available',activate='Activate')
        self.borrowed_tool = CurrentlyBorrowedTools.objects.create(possesor=self.user1,tool=self.tool,start_time=datetime.datetime.now(),return_time=datetime.date.today())
        self.request = ToolBorrowingRequest.objects.create(requester=self.user2,date_request=datetime.datetime.now(),date_return=datetime.date.today(),tool_requested=self.tool)

    def test_incoming_tool_requests(self):
        response = self.client.get('/incoming_tool_requests/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'incoming_tool_requests.html')


    def test_requested_tools(self):
        response = self.client.get('/user_profile/requested_tools/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requested_tools.html')

    def test_my_borrowed_tools(self):
        response = self.client.get('/user_profile/my_borrowed_tools/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_borrowed_tools.html')

    def test_tools_in_possession(self):
        response = self.client.get('/tools_in_possession/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tools_in_possession.html')

    def test_tool_returned(self):
        response = self.client.get('/tool_returned/'+str(self.tool.id)+'/',follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_borrowed_tools.html')
