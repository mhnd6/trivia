import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# helper paginating function to return 10 questions per page


def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

# helper function to return all available categories


def get_categories():
    categoris = Category.query.all()
    formatted_categoris = [category.format() for category in categoris]

    categories = {}
    for cat in categoris:
        categories[cat.id] = cat.type

    return categories


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    #   after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type , Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH< DELETE, OPTIONS')
        return response

    # GET requests for all available categories.
    @app.route('/categories', methods=['GET'])
    def get_categoris():

        try:
            categories = get_categories()

            return jsonify({
                'success': True,
                'categories': categories
            })
        except Exception:
            abort(404)

    # GET requests for questions,
    @app.route('/questions', methods=['GET'])
    def retrieve_questions():

        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        categories = get_categories()

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': categories
        })

    # DELETE question using a question ID.
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

        except Exception:
            abort(422)

    # POST endpoint to get questions based on a search term.
    @app.route('/questions', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search = body.get('searchTerm', None)

        try:
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search)))
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(selection.all())
            })
        except Exception:
            abort(422)

    # Create an endpoint to POST a new question,
    @app.route('/questions/add', methods=['POST'])
    def create_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        try:
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

        except Exception:
            abort(422)

    # get questions based on category.
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

    # endpoint to get questions to play the quiz.
    # This endpoint should take category and previous question parameters
    # and return a random questions within the given category,
    # if provided, and that is not one of the previous questions.
    @app.route('/quizzes', methods=['POST'])
    def get_play_quiz():
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

            # Force End the quiz when all qustions showed up
            if len(previous_questions) == len(questions):
                return jsonify({
                    'end': True
                })

            # get a random question
            question = random.choice(questions)

            # Check if the question has been chosen
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
        except Exception:
            abort(400)

    # handling errors
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
