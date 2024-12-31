from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db
from werkzeug.exceptions import HTTPException

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})
    with app.app_context():
        db.create_all()

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization')
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        try:
            categories = Category.query.all()
            if not categories:
                abort(404)
            
            formattedCategories = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'categories': formattedCategories
            })
        except Exception:
            abort(500)

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            if page < 1:
                abort(400)

            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            questions = Question.query.all()
            formattedQuestions = [question.format() for question in questions]
            
            if start >= len(formattedQuestions):
                abort(404)

            categories = Category.query.all()
            formattedCategories = {category.id: category.type for category in categories}

            return jsonify({
                'success': True,
                'questions': formattedQuestions[start:end],
                'total_questions': len(formattedQuestions),
                'categories': formattedCategories
            })
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(500)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(404)

            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except Exception as e:
            db.session.rollback()
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(500)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()
            if not body:
                abort(400)

            question = body.get('question')
            answer = body.get('answer')
            category = body.get('category')
            difficulty = body.get('difficulty')

            if not all([question, answer, category is not None, difficulty is not None]):
                abort(422)
            
            if not Category.query.get(category):
                abort(404)
            
            try:
                difficulty = int(difficulty)
                if difficulty < 1 or difficulty > 5:
                    abort(400)
            except (TypeError, ValueError):
                abort(400)

            new_question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty
            )
            new_question.insert()

            return jsonify({
                'success': True,
                'created': new_question.id
            })

        except Exception as e:
            db.session.rollback()
            if isinstance(e, HTTPException):
                abort(e.code)
            print(f"Error in create_question: {str(e)}")
            abort(500)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            if not body:
                abort(400)

            search_term = body.get('searchTerm')
            if not search_term:
                abort(422)

            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')).all()
            formattedQuestions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': formattedQuestions,
                'total_questions': len(formattedQuestions)
            })
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(500)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:categoryId>/questions')
    def get_questions_by_category(categoryId):
        try:
            category = Category.query.get(categoryId)
            if category is None:
                abort(404)

            questions = Question.query.filter(Question.category == categoryId).all()
            if not questions:
                abort(404)

            formattedQuestions = [question.format() for question in questions]

            return jsonify({
                'success': True,
                'questions': formattedQuestions,
                'total_questions': len(formattedQuestions),
                'current_category': categoryId
            })
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(500)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            if not body:
                abort(400)

            previous_questions = body.get('previous_questions')
            quiz_category = body.get('quiz_category')

            try:
                category_id = int(quiz_category['id'])
            except (TypeError, ValueError):
                abort(422)

            if category_id != 0:
                category = Category.query.get(category_id)
                if not category:
                    abort(404)
                questions = Question.query.filter(
                    Question.category == category_id).all()
            else:
                questions = Question.query.all()

            available_questions = [q.format() for q in questions 
                                if q.id not in previous_questions]

            if not available_questions:
                return jsonify({
                    'success': True,
                    'question': None
                })

            question = random.choice(available_questions)

            return jsonify({
                'success': True,
                'question': question
            })

        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            print(f"Error in play_quiz: {str(e)}")
            abort(500)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500

    return app
