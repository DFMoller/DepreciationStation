from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from os import path # os -> operating system
from flask_admin.contrib.sqla import ModelView
from flask_admin import Admin
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
import json, datetime, sys
from datetime import datetime, date

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
    from .models import History, Search, Today

    create_database(app)

    admin = Admin(app)
    admin.add_view(ModelView(Search, db.session))
    admin.add_view(ModelView(History, db.session))
    admin.add_view(ModelView(Today, db.session))
# 
    startRestfulAPI(app, History, Today, Search)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Database Created!')
    else:
        print('Database Found!')


def startRestfulAPI(app, History, Today, Search):

    api = Api(app)

    reading_post_args = reqparse.RequestParser()
    reading_post_args.add_argument("data", type=str, help="Reading data is required", required=True)
    # # reading_post_args.add_argument("value", type=float, help="value is required", required=True)
    # # reading_post_args.add_argument("mileage", type=float, help="mileage is required", required=True)
    # # reading_post_args.add_argument("title", type=str, help="title is required", required=True)
    # # reading_post_args.add_argument("date", type=str, help="date is required", required=True)

    search_post_args = reqparse.RequestParser()
    search_post_args.add_argument("year", type=int, help="year is required", required=True)
    search_post_args.add_argument("color", type=str, help="color is required", required=True)

    # # This serializes responses
    # reading_fields = {
    #     "car_id": fields.Integer,
    #     "value": fields.Float,
    #     "mileage": fields.Float,
    #     "date": fields.String
    # }

    search_fields = {
        "id": fields.Integer,
        "year": fields.Integer,
        "color": fields.String
    }

    class postReadings(Resource):

        # @marshal_with(reading_fields)
        def post(self):

            args = reading_post_args.parse_args()

            data_received = json.loads(args['data'].decode('utf-8'))

            # data = request.form['data']
            # print("Data: " + str(type(data_received)))

            feedback = {
                "Function": "POST READINGS DATA",
                "current_id": data_received[0]["search_id"],
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
                    if (Today.query.filter_by(date=reading['date'], rel_link=reading['rel_link']).first()):
                        # Already exists
                        feedback['items_already_existing'] += 1
                    else:
                        # Create new entry
                        reading_instance = Today(search_id=reading['search_id'], title=reading['title'], value=reading['value'], mileage=reading['mileage'], date=reading['date'], rel_link=reading['rel_link'])
                        db.session.add(reading_instance)
                        feedback['new_added'] += 1

            if feedback['items_with_empty_parameters'] == 0 and feedback['new_added'] > 0:
                db.session.commit()
                feedback['committed'] = True
                deleteOldEntries()

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

            result = Search.query.filter_by(color=args['color'].lower(), year=args['year']).first()

            if result:
                feedback["Status"] = "Search Already Exists"
                logFeedback(feedback)
                abort(409, message=f'Search for: [id = {result.id}, color = {args["color"].capitalize()}, year = {str(args["year"])}] already exists')

            new_search = Search(year=args['year'], color=args['color'].lower())
            db.session.add(new_search)
            db.session.commit()

            added_search = Search.query.filter_by(year=args['year'], color=args['color'].lower()).first()
            
            feedback["Status"] = f'New Search Added to Database: [id = {added_search.id}, color = {args["color"].capitalize()}, year = {str(args["year"])}]'
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

    class deleteOldEntries(Resource):

        def delete(self):

            entries_today = Today.query.all()

            new_entries_exist = False
            today = date.today().strftime('%d/%m/%Y')
            for entry in entries_today:
                if entry.date == today:
                    new_entries_exist = True
                    break

            if new_entries_exist:
                num_deleted = 0
                today = date.today()
                for entry in entries_today:
                    date_obj = datetime.strptime(entry.date, '%d/%m/%Y').date()
                    if date_obj < today:
                        # print(date_obj.strftime("%d/%m/%Y") + " < " + today.strftime("%d/%m/%Y"))
                        db.session.delete(entry)
                        num_deleted += 1

                if num_deleted > 0:
                    db.session.commit()

                return {
                    "Function": "Delete old entries",
                    "Status": "New entries exist",
                    "Entries deleted": num_deleted
                }

            else:
                return {
                    "Status": "No New Entries Exist, Commit new data before deleting the old"
                }


    api.add_resource(postReadings, "/addReadings")
    api.add_resource(postSearch, "/addSearch")
    api.add_resource(getSearches, "/getSearches")
    api.add_resource(deleteOldEntries, "/deleteOldEntries")

    # addToday_args = reqparse.RequestParser()
    # addToday_args.add_argument("data", type=str, help="Today data is required", required=True)

    # class addToday(Resource):

    #     def post(self):

    #         args = addToday_args.parse_args()
    #         data_received = json.loads(args['data'])
    #         entries_added = 0

    #         for entry in data_received:

    #             result = Today.query.filter_by(date=entry['date'], rel_link=entry['rel_link']).first()
    #             if not result:
    #                 instance_today = Today(search_id=entry["search_id"], title=entry["title"], value=entry["value"], mileage=entry["mileage"], date=entry["date"], rel_link=entry["rel_link"])

    #                 db.session.add(instance_today)
    #                 db.session.commit()
    #                 entries_added += 1

    #         return {"entries added": entries_added}

    # api.add_resource(addToday, "/addToday")

    addHistory_args = reqparse.RequestParser()
    addHistory_args.add_argument("data", type=str, help="Today's data is required", required=True)

    class addHistory(Resource):

        def post(self):

            args = addHistory_args.parse_args()
            data_received = json.loads(args['data'])
            entries_added = 0
            duplicate_entries = 0

            for id_key in data_received:
                result = History.query.filter_by(search_id=id_key, date=data_received[id_key]['date']).first()
                if not result:
                    instance_history = History(search_id=id_key, median_value=data_received[id_key]["median_value"], date=data_received[id_key]["date"])
                    db.session.add(instance_history)
                    entries_added += 1
                else:
                    duplicate_entries += 1

            if entries_added > 0:
                db.session.commit()

            return {
                "Function": "Add History",
                "Entries added": entries_added,
                "Duplicate entries": duplicate_entries
            }

    api.add_resource(addHistory, "/addHistory")



def logFeedback(feedback):

    feedback_string = f'''

******************
DateTime: {datetime.now()}
******************
'''

    for key in feedback:
        feedback_string += key + ": " + str(feedback[key]) + "\n"

    feedback_string += "******************"

    with open("DepreciationStation/website/api_log/api_log.txt", "a") as file:
        file.write(feedback_string)
        file.close()


