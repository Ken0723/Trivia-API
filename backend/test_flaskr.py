import os
import unittest

from dotenv import load_dotenv
from flaskr import create_app
from models import db, Question, Category
import json


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        load_dotenv()
        """Define test variables and initialize app."""
        self.database_path = 'postgresql://{}:{}@{}:{}/{}'.format(
            os.getenv('DB_USER'),
            os.getenv('DB_PASSWORD'),
            os.getenv('DB_HOST'),
            os.getenv('DB_PORT'),
            os.getenv('DB_TEST_NAME')
        )

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    # Test get categories lsit

    def test_get_categories(self):
        response = self.client.get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']) > 0)

    # Test get questions with pagination
    def test_get_questions(self):
        response = self.client.get('/questions?page=1')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']) <= 10)

    # Test get question by category and 404 error with id 1000
    def test_get_questions_by_category(self):
        response = self.client.get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue('questions' in data)
        self.assertTrue('total_questions' in data)
        self.assertTrue('current_category' in data)

    def test_404_get_questions_by_category(self):
        response = self.client.get('/categories/1000/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)

    # Test create question and 400 error with missing data
    def test_create_question(self):
        new_question = {
            'question': 'Test Question',
            'answer': 'Test Answer',
            'difficulty': 1,
            'category': 1
        }
        response = self.client.post('/questions', json=new_question)
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_400_create_question(self):
        response = self.client.post('/questions', json={})
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)


    # Test searching for questions
    def test_search_questions(self):
        response = self.client.post(
            '/questions/search',
            json={
                'searchTerm': 'test'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue('questions' in data)
        self.assertTrue('total_questions' in data)

    # Test Play a quiz/422 error(no quiz data sent)
    def test_play_quiz(self):
        quiz_data = {
            'previous_questions': [],
            'quiz_category': {'id': 1, 'type': 'Science'}
        }
        response = self.client.post('/quizzes', json=quiz_data)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue('question' in data)

    def test_422_play_quiz(self):
        response = self.client.post('/quizzes', json={})
        data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)

    # Test 404 error not found with page 1000
    def test_404_error_not_found(self):
        response = self.client.get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    # Test delete a question/404 with id 1000
    def test_delete_question(self):
        question = Question(
            question='Test Question',
            answer='Test Answer',
            category=1,
            difficulty=1
        )
        with self.app.app_context():
            question.insert()
            question_id = question.id

        response = self.client.delete(f'/questions/{question_id}')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)

    def test_404_delete_question(self):
        response = self.client.delete('/questions/1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
