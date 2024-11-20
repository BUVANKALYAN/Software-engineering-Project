import unittest
import json
from app import app, init_db
import sqlite3

class EventManagementTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config['TESTING'] = True
        app.config['MAIL_SUPPRESS_SEND'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_event_management.db'  # Use file-based database
        cls.client = app.test_client()
        init_db()

    def setUp(self):
        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users")
        cursor.execute("DELETE FROM events")
        cursor.execute("DELETE FROM participation")
        conn.commit()  # Commit changes to avoid locking
        conn.close()


    def test_user_registration_success(self):
        response = self.client.post('/register', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful! You can now log in.', response.data)

    def test_login_success(self):
        self.client.post('/register', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        
        response = self.client.post('/home', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.assertIn(b'Login successful!', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post('/home', data={
            'username': 'wronguser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Username not found. Please register.', response.data)

    def test_event_creation(self):
        self.client.post('/register', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.client.post('/home', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)

        response = self.client.post('/add_event', json={
            'event_name': 'Tech Conference',
            'date': '2024-12-01',
            'occupancy': 100
        })
        self.assertIn(b'Event created successfully!', response.data)

def test_process_event_registration(self):
    # Add necessary setup steps for this test
    event = {
        "name": "Sample Event",
        "location": "Sample City",
        "date": "2024-12-01",
        "occupancy": 100
    }

    # Manually insert event and user data if needed for this test
    self.client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    self.client.post('/home', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)

    response = self.client.post('/process_event_registration', json={
        'email': 'test@example.com',
        'event_name': 'Sample Event'
    })
    data = json.loads(response.data)
    print("Process Event Registration Response:", data)  # Debug output
    self.assertTrue(data.get('success', False))


    def test_chatbot_response(self):
        response = self.client.post('/chatbot_response', json={'message': 'organize an event'})
        data = json.loads(response.data)
        self.assertIn("Please provide the event details and your budget.", data['response'])

    def test_process_event_registration(self):
        # Register a user and log them in
        self.client.post('/register', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        self.client.post('/home', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)

        # Insert an event that the user will register for
        conn = sqlite3.connect('event_management.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (name, location, date, occupancy, creator_id) VALUES (?, ?, ?, ?, ?)", 
                       ('Sample Event', 'Sample City', '2024-12-01', 100, 1))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Attempt to register for the event
        response = self.client.post('/process_event_registration', json={
            'event_name': 'Sample Event'
        })
        data = json.loads(response.data)

        # Verify that the registration was successful
        self.assertTrue(data.get('success', False))
        self.assertIn('ticket_number', data)

class CustomTestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passed_tests = []
        self.failed_tests = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed_tests.append(test)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.failed_tests.append((test, self._exc_info_to_string(err, test)))

    def addError(self, test, err):
        super().addError(test, err)
        self.failed_tests.append((test, self._exc_info_to_string(err, test)))

    def stopTestRun(self):
        super().stopTestRun()
        print("\nSummary of Test Results:")
        print(f"Total Passed: {len(self.passed_tests)}")
        print("Passed Tests:")
        for test in self.passed_tests:
            print(f" - {test}")

        if self.failed_tests:
            print(f"\nTotal Failed: {len(self.failed_tests)}")
            print("Failed Tests:")
            for test, err in self.failed_tests:
                print(f" - {test}")
                print(f"   Error: {err}")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(EventManagementTestCase)
    runner = unittest.TextTestRunner(resultclass=CustomTestResult)
    runner.run(suite)
