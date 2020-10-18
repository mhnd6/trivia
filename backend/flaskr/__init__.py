import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

  #   '''
  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  # '''
    @app.route('/')
    def get_plants():

        return 'hello world'

    #  '''
    #  @TODO: Use the after_request decorator to set Access-Control-Allow
    #  '''

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type , Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH< DELETE, OPTIONS')
        return response

    #   '''
    # @TODO:
    # Create an endpoint to handle GET requests
    # for all available categories.
    # '''

    @app.route('/categories', methods=['GET'])
    def get_categoris():
        categoris = Category.query.all()
        formatted_categoris = [category.format() for category in categoris]
        try:
            categories = {}
            for cat in categoris:
                categories[cat.id] = cat.type

            return jsonify({
                'success': True,
                'categories': categories
            })
        except:
            abort(404)

      #   '''
      # @TODO:
      # Create an endpoint to handle GET requests for questions,
      # including pagination (every 10 questions).
      # This endpoint should return a list of questions,
      # number of total questions, current category, categories.

      # TEST: At this point, when you start the application
      # you should see questions and categories generated,
      # ten questions per page and pagination at the bottom of the screen for three pages.
      # Clicking on the page numbers should update the questions.
      # '''

    @app.route('/questions', methods=['GET'])
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categoris = Category.query.all()
        formatted_categoris = [category.format() for category in categoris]

        categories = {}
        for cat in categoris:
            categories[cat.id] = cat.type

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': categories
        })

      #   '''
      # @TODO:
      # Create an endpoint to DELETE question using a question ID.

      # TEST: When you click the trash icon next to a question, the question will be removed.
      # This removal will persist in the database and when you refresh the page.
      # '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })

        except:
            abort(422)

    #   '''
    # @TODO:
    # Create an endpoint to POST a new question,
    # which will require the question and answer text,
    # category, and difficulty score.

    # TEST: When you submit a question on the "Add" tab,
    # the form will clear and the question will appear at the end of the last page
    # of the questions list in the "List" tab.
    # '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        search = body.get('searchTerm', None)

        try:
            if search:
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike('%{}%'.format(search)))
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection.all())
                })
            else:
                newQuestion = Question(
                    question=question,
                    answer=answer,
                    category=category,
                    difficulty=difficulty
                )

                newQuestion.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': newQuestion.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })

        except:
            abort(422)

    #   '''
    # @TODO:
    # Create a POST endpoint to get questions based on a search term.
    # It should return any questions for whom the search term
    # is a substring of the question.

    # TEST: Search by any phrase. The questions list will update to include
    # only question that include that string within their question.
    # Try using the word "title" to start.
    # '''

    #   '''
    # @TODO:
    # Create a GET endpoint to get questions based on category.

    # TEST: In the "List" tab / main screen, clicking on one of the
    # categories in the left column will cause only questions of that
    # category to be shown.
    # '''
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):

        selection = Question.query.filter(
            Question.category == category_id).order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all())
        })

    #   '''
    # @TODO:
    # Create a POST endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.

    # TEST: In the "Play" tab, after a user selects "All" or a category,
    # one question at a time is displayed, the user is allowed to answer
    # and shown whether they were correct or not.
    # '''

    @app.route('/quizzes', methods=['POST'])
    def get_quiz():
        body = request.get_json()
        try:
            previous_questions = body.get('previous_questions', None)
            quiz_category = body.get('quiz_category', None)
            categoryID = quiz_category['id']

            # based on the category id it will filter the query
            if categoryID == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter(
                    Question.category == categoryID).all()

            # if the length of previous questions array == number of questions then force end
            if len(previous_questions) == len(questions):
                return jsonify({
                    'end': True
                })
            # get a random question
            question = random.choice(questions)

            # the next block of code will check if the question inside the previous questions array
            check = False
            while not check:
                if question.id in previous_questions:
                    question = random.choice(questions)
                else:
                    check = True

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except:
            abort(400)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'not found'
        }), 404

    @app.errorhandler(422)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    return app
