import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_all_categories(self):
        """Test for get_all_categories
        Tests for the status code, if success is true,
        if categories is returned and the length of
        the returned categories
        """

        # make request and process response
        response = self.client().get('/categories')
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def __create_test_question(self):
        """This creates a test question in the database.
        This test data is created to prevent having to drop
        the database during the running of the test suite.
        """
        # insert test qestion into Question constructor
        question = Question(
            question='This is a test question that should deleted',
            answer='This is a test question that should deleted',
            difficulty=1,
            category='1')

        # create a new test question in the database
        question.insert()

        # return id of the test question
        return question.id

    def test_get_paginated_questions(self):
        """Test for get all paginated questions
        This tests the return values for a successful
        return of paginated questions
        the assertion that ensures the paginated questions
        is always 10, is determined by a constant that could
        change.
        """
        # make request and process response
        response = self.client().get('/questions')
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_get_paginated_questions_invalid_page(self):
        """Test for out of bound page
        This test ensures a page that is out of bound
        returns a 404 error
        """

        # make request and process response
        response = self.client().get('/questions?page=10000000')
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question(self):
        """Test for deleting a question.
        __create_test_question function is used to prevent having
        to drop the database during the running of the test suite.
        """

        # create test question and get id
        test_question_id = self.__create_test_question()

        # delete test question and process response
        response = self.client().delete(
            '/questions/{}'.format(test_question_id))
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question successfully deleted")

    def test_delete_question_duplicate_id(self):
        """unsuccessful deletion of question
        This tests the error message returned when
        you try to delete the same question twice.
        """

        # create test question and get id
        test_question_id = test_question_id = self.__create_test_question()

        # delete test question
        self.client().delete('/questions/{}'.format(test_question_id))
        
        # delete test question again
        response = self.client().delete(
            '/questions/{}'.format(test_question_id))
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_delete_question_id_doesnot_exist(self):
        """Tests deletion of question id that doesn't exist
        This tests the error message returned a valid id that
        doesn't exist is used.
        """
        # this tests an id that doesn't exist
        response = self.client().delete('/questions/1211256')
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_delete_question_invalid_id(self):
        """Tests deletion of question with invalid id"""
        # make request and process response
        response = self.client().delete('/questions/sadsa2112kjsds6')
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_create_question(self):
        """Test for creating question."""

        # create test data
        test_data = {
            'question': 'This is a test question',
            'answer': 'this is a test answer',
            'difficulty': 1,
            'category': 1,
        }

        # make request and process response
        response = self.client().post('/questions', json=test_data)
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question successfully created!')

    def test_create_question_empty_data(self):
        """Test for ensuring data with empty fields are not processed."""

        # create test data
        test_data = {
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1,
        }

        # make request and process response
        response = self.client().post('/questions', json=test_data)
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_search_questions(self):
        """Test for searching for a question."""

        # create test data
        test_data = {
            'searchTerm': 'largest lake in Africa',
        }

        # make request and process response
        response = self.client().post('/questions/search', json=test_data)
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_search_term_empty_data(self):
        """Test for empty search term."""

        # create test data
        test_data = {
            'searchTerm': '',
        }

        # make request and process response
        response = self.client().post('/questions/search', json=test_data)
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_search_term_not_found(self):
        """Test for search term not found."""

        # create test data
        test_data = {
            'searchTerm': 'dfjdtrertwfresyg346474yg',
        }

        # make request and process response
        response = self.client().post('/questions/search', json=test_data)
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_get_questions_by_category(self):
        """Test for getting questions by category."""

        # make a request for the Sports category with id of 6
        response = self.client().get('/categories/6/questions')
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Sports')

    def test_get_category_invalid_id(self):
        """Test for invalid category id"""

        # make a request with invalid category id 1987
        response = self.client().get('/categories/1987/questions')
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_quiz_questions(self):
        """Tests playing quiz questions"""

        # request data
        request_data = {
            'previous_questions': [5, 9],
            'quiz_category': {
                'type': 'History',
                'id': 4
            }
        }

        # make request and process response
        response = self.client().post('/quizzes', json=request_data)
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'], 5)
        self.assertNotEqual(data['question']['id'], 9)
        self.assertEqual(data['question']['category'], 4)

    def test_no_data_to_play_quiz(self):
        """Test for the case where no data is sent"""

        # make request and process response
        response = self.client().post('/quizzes', json={})
        data = response.get_json()

        # make assertions on the response data
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request error')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()