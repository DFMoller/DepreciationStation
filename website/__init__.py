from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from os import path # os -> operating system
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
import json, datetime

db = SQLAlchemy()
DB_NAME = "colors_database.db"

def create_app():

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'abcdefg' # secures cookies and session data
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Register blueprints
    from .views import views

    app.register_blueprint(views, url_prefix='/') # prefix would go before any routes in blueprints

    # Make sure this model file runs befor we initialize our Database
    from .models import Reading, Search

    create_database(app)

    admin = Admin(app)
    admin.add_view(ModelView(Search, db.session))
    admin.add_view(ModelView(Reading, db.session))

    startRestfulAPI(app, Reading, Search)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Database Created!')
    else:
        print('Database Found!')


def startRestfulAPI(app, Reading, Search):

    api = Api(app)

    reading_post_args = reqparse.RequestParser()
    reading_post_args.add_argument("data", type=str, help="Reading data is required", required=True)
    # reading_post_args.add_argument("value", type=float, help="value is required", required=True)
    # reading_post_args.add_argument("mileage", type=float, help="mileage is required", required=True)
    # reading_post_args.add_argument("title", type=str, help="title is required", required=True)
    # reading_post_args.add_argument("date", type=str, help="date is required", required=True)

    search_post_args = reqparse.RequestParser()
    search_post_args.add_argument("year", type=int, help="year is required", required=True)
    search_post_args.add_argument("color", type=str, help="color is required", required=True)

    # This serializes responses
    reading_fields = {
        "car_id": fields.Integer,
        "value": fields.Float,
        "mileage": fields.Float,
        "date": fields.String
    }

    search_fields = {
        "id": fields.Integer,
        "year": fields.Integer,
        "color": fields.String
    }
    
    class postReadings(Resource):

        # @marshal_with(reading_fields)
        def post(self):

            args = reading_post_args.parse_args()

            data_received = json.loads(args['data'])

            # data = request.form['data']
            # print("Data: " + str(type(data_received)))

            feedback = {
                "Function": "POST READINGS DATA",
                "items_with_empty_parameters": 0,
                "items_already_existing": 0,
                "new_added": 0,
                "committed": False
            }

            for reading in data_received:

                parameters = ("search_id", "value", "mileage", "title", "date", "rel_link")

                if not all(key in reading for key in parameters):
                    feedback['items_with_empty_parameters'] += 1
                else:

                    if (Reading.query.filter_by(date=reading['date'], rel_link=reading['rel_link']).first()):
                        # Already exists
                        feedback['items_already_existing'] += 1
                    else:
                        # Create new entry
                        reading_instance = Reading(search_id=reading['search_id'], title=reading['title'], value=reading['value'], mileage=reading['mileage'], date=reading['date'], rel_link=reading['rel_link'])
                        db.session.add(reading_instance)
                        feedback['new_added'] += 1
            
            if feedback['items_with_empty_parameters'] == 0 and feedback['new_added'] > 0:
                db.session.commit()
                feedback['committed'] = True

            logFeedback(feedback)

            return feedback
    
    class postSearch(Resource):
        
        @marshal_with(search_fields)
        def post(self):
            
            args = search_post_args.parse_args()

            feedback = {
                "Function": "ADD SEARCH",
                "Search_Name": args["color"].capitalize() + " Cars from " + str(args["year"]),
                "Status": ""
            }

            result = Search.query.filter_by(color=args['color'], year=args['year']).first()

            if result:
                feedback["Status"] = "Search Already Exists"
                logFeedback(feedback)
                abort(409, message="Search for " + args['color'].capitalize() + " Cars of " + str(args['year']) + " already exists")

            new_search = Search(year=args['year'], color=args['color'].lower())
            db.session.add(new_search)
            db.session.commit()

            feedback["Status"] = "New Search Added to Database"
            logFeedback(feedback)

            return new_search, 201

    class getSearches(Resource):

        # @marshal_with(get_cars)
        def get(self):

            feedback = {
                "Function": "GET LIST OF SEARCHES"
            }

            searches = Search.query.all()
            serializable_searches = []
            for search in searches:
                instance = {}
                instance["id"] = search.id
                instance["year"] = search.year
                instance["color"] = search.color
                serializable_searches.append(instance)

            logFeedback(feedback)

            return serializable_searches

    
    api.add_resource(postReadings, "/addReadings")
    api.add_resource(postSearch, "/addSearch")
    api.add_resource(getSearches, "/getSearches")




def logFeedback(feedback):

    feedback_string = f'''

******************
DateTime: {datetime.datetime.now()}
******************
'''

    for key in feedback:
        feedback_string += key + ": " + str(feedback[key]) + "\n"

    feedback_string += "******************"

    with open("api_log.txt", "a") as file:
        file.write(feedback_string)
        file.close()
    

