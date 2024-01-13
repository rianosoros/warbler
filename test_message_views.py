"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os, unittest
from unittest import TestCase
from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")



class MessageTests(unittest.TestCase):

    def setUp(self):
        # Set up a test database
        self.app = create_app('test_config.py')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # Clean up the test database
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_logged_in_see_follower_following_pages(self):
        user1 = User(username='user1', email='user1@example.com', password='password1')
        user2 = User(username='user2', email='user2@example.com', password='password2')
        db.session.add_all([user1, user2])
        db.session.commit()

        with self.app.test_client() as client:
            client.post('/login', data=dict(username='user1', password='password1'), follow_redirects=True)
            response = client.get(f'/users/{user2.id}/followers')
            self.assertEqual(response.status_code, 200)

    def test_logged_out_disallowed_follower_following_pages(self):
        user = User(username='testuser', email='test@example.com', password='testpassword')
        db.session.add(user)
        db.session.commit()

        with self.app.test_client() as client:
            response = client.get(f'/users/{user.id}/followers')
            self.assertEqual(response.status_code, 403)

    def test_logged_in_add_message(self):
        user = User(username='testuser', email='test@example.com', password='testpassword')
        db.session.add(user)
        db.session.commit()

        with self.app.test_client() as client:
            client.post('/login', data=dict(username='testuser', password='testpassword'), follow_redirects=True)
            response = client.post('/messages/new', data=dict(text='Test message'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_logged_in_delete_message(self):
        user = User(username='testuser', email='test@example.com', password='testpassword')
        message = Message(text='Test message', user=user)
        db.session.add_all([user, message])
        db.session.commit()

        with self.app.test_client() as client:
            client.post('/login', data=dict(username='testuser', password='testpassword'), follow_redirects=True)
            response = client.post(f'/messages/{message.id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_logged_out_prohibited_add_message(self):
        with self.app.test_client() as client:
            response = client.post('/messages/new', data=dict(text='Test message'), follow_redirects=True)
            self.assertEqual(response.status_code, 403)

    def test_logged_out_prohibited_delete_message(self):
        user = User(username='testuser', email='test@example.com', password='testpassword')
        message = Message(text='Test message', user=user)
        db.session.add_all([user, message])
        db.session.commit()

        with self.app.test_client() as client:
            response = client.post(f'/messages/{message.id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 403)

    def test_logged_in_prohibited_add_message_as_another_user(self):
        user1 = User(username='user1', email='user1@example.com', password='password1')
        user2 = User(username='user2', email='user2@example.com', password='password2')
        db.session.add_all([user1, user2])
        db.session.commit()

        with self.app.test_client() as client:
            client.post('/login', data=dict(username='user1', password='password1'), follow_redirects=True)
            response = client.post(f'/users/{user2.id}/messages/new', data=dict(text='Test message'), follow_redirects=True)
            self.assertEqual(response.status_code, 403)

    def test_logged_in_prohibited_delete_message_as_another_user(self):
        user1 = User(username='user1', email='user1@example.com', password='password1')
        user2 = User(username='user2', email='user2@example.com', password='password2')
        message = Message(text='Test message', user=user2)
        db.session.add_all([user1, user2, message])
        db.session.commit()

        with self.app.test_client() as client:
            client.post('/login', data=dict(username='user1', password='password1'), follow_redirects=True)
            response = client.post(f'/messages/{message.id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()
