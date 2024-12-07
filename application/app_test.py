import unittest
from unittest.mock import patch, MagicMock
from app import app

class TestApp(unittest.TestCase):
    @patch('app.db_conn')
    def test_home_route(self, mock_db_conn):
        # Mock the database cursor and its behavior
        mock_cursor = MagicMock()
        mock_db_conn.cursor.return_value = mock_cursor

        # Perform the test
        tester = app.test_client(self)
        response = tester.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello From CLO835", response.data)

    @patch('app.db_conn')
    def test_addemp_route(self, mock_db_conn):
        # Mock the database cursor and its behavior
        mock_cursor = MagicMock()
        mock_db_conn.cursor.return_value = mock_cursor

        # Mock the query execution
        mock_cursor.execute.return_value = None

        # Simulate form data
        form_data = {
            'emp_id': '123',
            'first_name': 'John',
            'last_name': 'Doe',
            'primary_skill': 'Python',
            'location': 'Remote'
        }

        # Perform the test
        tester = app.test_client(self)
        response = tester.post('/addemp', data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"John Doe", response.data)

if __name__ == '__main__':
    unittest.main()
