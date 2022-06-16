import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def questions_paginate(request, selection):
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

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories', methods=['GET'])
    def get_all_categories():
        selection = Category.query.order_by(Category.id).all()
        get_current_categories = questions_paginate(request, selection)

        if len(get_current_categories) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'categories': {cat.id: cat.type for cat in selection}
        })

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
    def get_all_questions():
        try:
            # show all questions
            selection = Question.query.order_by(Question.id).all()
            # show the total num of questions
            totalQuestions = len(selection)
            # show current questions in a page
            get_current_questions = questions_paginate(request, selection)

            # if the page number is not found
            if (len(get_current_questions) == 0):
                abort(404)

            # get all categories
            categories = Category.query.all()
            categoriesDict = {}
            for category in categories:
                categoriesDict[category.id] = category.type

            return jsonify({
                'success': True,
                'questions': get_current_questions,
                'total_questions': totalQuestions,
                'categories': categoriesDict
            })
        except Exception as e:
            print(e)
            abort(400)

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question_by_id(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            get_current_questions = questions_paginate(request, selection)
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': get_current_questions,
                'total_questions': len(selection)
            })

        except Exception:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=['POST'])
    def post_question():
        # get the body from requist
        body = request.get_json()

        # show new data, none if not enterd
        newQuestion = body.get('question', None)
        newAnswer = body.get('answer', None)
        newCategory = body.get('category', None)
        newDifficulty = body.get('difficulty', None)

        try:
            # add 
            question = Question(question=newQuestion, answer=newAnswer,
                                category=newCategory, difficulty=newDifficulty)
            question.insert()

            # send back the current questions, to update frontend of the app
            selection = Question.query.order_by(Question.id).all()
            get_current_questions = questions_paginate(request, selection)

            return jsonify({
                'success': True,
                'created': question.id,
                'questions': get_current_questions,
                'total_questions': len(selection)
            })

        except Exception as e:
            print(e)
            abort(422)
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/search", methods=['POST'])
    def search_input():
        body = request.get_json()
        search = body.get('searchTerm')
        questions = Question.query.filter(
            Question.question.ilike('%'+search+'%')).all()

        if questions:
            get_current_questions = questions_paginate(request, questions)
            return jsonify({
                'success': True,
                'questions': get_current_questions,
                'total_questions': len(questions)
            })
        else:
            abort(404)


    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:cat_id>/questions', methods=['GET'])
    def get_questions_by_category(cat_id):
        #cat_id = cat_id + 1
        category = Category.query.get(cat_id)
        #category = Category.query.filter(
        #    Category.id == cat_id).first()

        if cat_id is None:
            abort(404)

        selection = Question.query.order_by(Question.id).filter(
            Question.category == cat_id).all()
        get_current_questions = questions_paginate(request, selection)

        #if len(get_current_questions) == 0:
        #    abort(404)

        return jsonify({
            'success': True,
            'questions': get_current_questions,
            'total_questions': len(selection),
            'categories': category.type,
            'current_category': category.id
        })

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
    def post_quiz():
        # show the qestion category an the previous_question
        body = request.get_json()
        quiz_category = body.get('quiz_category')
        previous_question = body.get('previous_question')

        try:
            if (quiz_category['id'] == 0):
                questionsQuery = Question.query.all()
            else:
                questionsQuery = Question.query.filter_by(
                    category=quiz_category['id']).all()

            randomIndex = random.randint(0, len(questionsQuery)-1)
            nextQuestion = questionsQuery[randomIndex]

            stillQuestions = True
            while nextQuestion.id not in previous_question:
                nextQuestion = questionsQuery[randomIndex]
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": nextQuestion.answer,
                        "category": nextQuestion.category,
                        "difficulty": nextQuestion.difficulty,
                        "id": nextQuestion.id,
                        "question": nextQuestion.question
                    },
                    'previousQuestion': previous_question
                })

        except Exception as e:
            print(e)
            abort(404)


    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def Page_not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404
    
    @app.errorhandler(500)
    def server_side_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    @app.errorhandler(422)
    def request_unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not Processable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400



    return app

