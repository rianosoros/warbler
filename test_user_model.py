"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os , unittest
from unittest import TestCase
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

class UserTests(unittest.TestCase):

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

    def test_repr_method(self):
        user = User(username='testuser', email='test@example.com', password='testpassword')
        self.assertEqual(repr(user), f"<User #None: testuser, test@example.com>")

    def test_is_following(self):
        user1 = User(username='user1', email='user1@example.com', password='password1')
        user2 = User(username='user2', email='user2@example.com', password='password2')
        user1.following.append(user2)
        self.assertTrue(user1.is_following(user2))
        self.assertFalse(user2.is_following(user1))

    def test_is_not_following(self):
        user1 = User(username='user1', email='user1@example.com', password='password1')
        user2 = User(username='user2', email='user2@example.com', password='password2')
        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user2.is_following(user1))

    def test_is_followed_by(self):
        user1 = User(username='user1', email='user1@example.com', password='password1')
        user2 = User(username='user2', email='user2@example.com', password='password2')
        user1.followers.append(user2)
        self.assertTrue(user1.is_followed_by(user2))
        self.assertFalse(user2.is_followed_by(user1))

    def test_is_not_followed_by(self):
        user1 = User(username='user1', email='user1@example.com', password='password1')
        user2 = User(username='user2', email='user2@example.com', password='password2')
        self.assertFalse(user1.is_followed_by(user2))
        self.assertFalse(user2.is_followed_by(user1))

    def test_user_create_success(self):
        user = User.signup(username='testuser', email='test@example.com', password='testpassword', image_url='/static/images/test-pic.png')
        db.session.commit()
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')

    def test_user_create_failure(self):
        # Test for failure when creating a user with duplicate username
        user1 = User.signup(username='testuser', email='test1@example.com', password='testpassword', image_url='/static/images/test-pic.png')
        db.session.commit()
        user2 = User.signup(username='testuser', email='test2@example.com', password='testpassword', image_url='/static/images/test-pic.png')
        db.session.commit()
        self.assertIsNone(user2.id)

    def test_user_authenticate_success(self):
        user = User.signup(username='testuser', email='test@example.com', password='testpassword', image_url='/static/images/test-pic.png')
        db.session.commit()
        authenticated_user = User.authenticate(username='testuser', password='testpassword')
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.id, user.id)

    def test_user_authenticate_invalid_username(self):
        user = User.signup(username='testuser', email='test@example.com', password='testpassword', image_url='/static/images/test-pic.png')
        db.session.commit()
        authenticated_user = User.authenticate(username='invaliduser', password='testpassword')
        self.assertFalse(authenticated_user)

    def test_user_authenticate_invalid_password(self):
        user = User.signup(username='testuser', email='test@example.com', password='testpassword', image_url='/static/images/test-pic.png')
        db.session.commit()
        authenticated_user = User.authenticate(username='testuser', password='invalidpassword')
        self.assertFalse(authenticated_user)

if __name__ == '__main__':
    unittest.main()