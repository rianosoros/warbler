import unittest
from models import db, Message, User

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

    def test_repr_method(self):
        user = User(username='testuser', email='test@example.com', password='testpassword')
        message = Message(text='Test message', user=user)
        db.session.add_all([user, message])
        db.session.commit()
        self.assertEqual(repr(message), f"<Message #{message.id}: {message.text}, {message.user_id}>")

    def test_logged_in_view_follower_following_pages(self):
        user1 = User(username='user1', email='user1@example.com', password='password1')
        user2 = User(username='user2', email='user2@example.com', password='password2')
        db.session.add_all([user1, user2])
        db.session.commit()

        with self.app.test_client() as client:
            client.post('/login', data=dict(username='user1', password='password1'), follow_redirects=True)
            response = client.get(f'/users/{user2.id}/followers')
            self.assertEqual(response.status_code, 200)

    def test_system_prevent_editing_messages_when_not_logged_in(self):
        user = User(username='testuser', email='test@example.com', password='testpassword')
        message = Message(text='Test message', user=user)
        db.session.add_all([user, message])
        db.session.commit()

        with self.app.test_client() as client:
            response = client.post(f'/messages/{message.id}/edit', follow_redirects=True)
            self.assertEqual(response.status_code, 403)

    def test_system_prevent_deleting_messages_when_not_logged_in(self):
        user = User(username='testuser', email='test@example.com', password='testpassword')
        message = Message(text='Test message', user=user)
        db.session.add_all([user, message])
        db.session.commit()

        with self.app.test_client() as client:
            response = client.post(f'/messages/{message.id}/delete', follow_redirects=True)
            self.assertEqual(response.status_code, 403)

    def test_user_can_edit_own_messages_successfully(self):
        user = User(username='testuser', email='test@example.com', password='testpassword')
        message = Message(text='Test message', user=user)
        db.session.add_all([user, message])
        db.session.commit()

        with self.app.test_client() as client:
            client.post('/login', data=dict(username='testuser', password='testpassword'), follow_redirects=True)
            response = client.post(f'/messages/{message.id}/edit', data=dict(text='Edited message'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            edited_message = Message.query.filter_by(id=message.id).first()
            self.assertEqual(edited_message.text, 'Edited message')

    def test_user_cannot_edit_another_users_messages(self):
        user1 = User(username='user1', email='user1@example.com', password='password1')
        user2 = User(username='user2', email='user2@example.com', password='password2')
        message = Message(text='Test message', user=user2)
        db.session.add_all([user1, user2, message])
        db.session.commit()

        with self.app.test_client() as client:
            client.post('/login', data=dict(username='user1', password='password1'), follow_redirects=True)
            response = client.post(f'/messages/{message.id}/edit', data=dict(text='Attempted edit'), follow_redirects=True)
            self.assertEqual(response.status_code, 403)
            unchanged_message = Message.query.filter_by(id=message.id).first()
            self.assertEqual(unchanged_message.text, 'Test message')

if __name__ == '__main__':
    unittest.main()
