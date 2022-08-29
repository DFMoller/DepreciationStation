from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Search, History, Today
from .plotting import ChartingEngine, plot_scatter_snapshot, plot_timeline, plot_density_snapshot
from datetime import datetime, date

views = Blueprint('views', __name__) # don't have to call it the file name

@views.route('/', methods=["GET", "POST"])
def home():
    # Determine which year to display
    years = []
    all_searches = Search.query.all()
    for x in all_searches:
        if x.year not in years:
            years.append(x.year)
    years = sorted(years)
    if request.method == "GET":
        year_selection = years[-1]
    elif request.method == "POST":
        year_selection = request.form.get("year-selection")
    snapshot_readings = Today.query.all()
    history_readings = History.query.all()
    ce = ChartingEngine(snapshot_readings, history_readings, all_searches, year_selection)
    xlabels = ce.get_timeline_xlables()
    datasets = ce.get_timeline_datasets()
    return render_template('home.html', years=years, year_selection=year_selection, datasets=datasets, xlabels=xlabels)

# @views.route('/delete_data')
# def delete():

#     all_history = History.query.all()
#     # all_today = Today.query.all()

#     # today = date.today().strftime('%d/%m/%Y')
#     cutoff = datetime.strptime("29/07/2021", '%d/%m/%Y')

#     history_deleted = 0
#     # discard = []
#     for x in all_history:
#         if datetime.strptime(x.date, '%d/%m/%Y') < cutoff:
#             db.session.delete(x)
#             # if x.date not in discard:
#             #     discard.append(x.date)
#             history_deleted += 1

#     # ret_str = ""
#     # for x in discard:
#     #     ret_str += x + ", "

#     # return ret_str

#     # today_deleted = 0
#     # for x in all_today:
#     #     if x.date == today:
#     #         db.session.delete(x)
#     #         today_deleted += 1

#     if history_deleted > 0:
#         db.session.commit()

#     return {
#         "History Deleted": history_deleted
#         # "Today Deleted": today_deleted
#     }


# @views.route('/data')
# def data():
#     print("Database Tables: " + str(db.engine.table_names()))
#     # print(Search.query.all())
#     readings = Reading.query.all()
#     searches = Search.query.all()
#     return render_template('data.html', readings=readings, searches=searches)

# @views.route('/export_today')
# def export_today:
#     print("Exporting Today's Entries")
#     entries_today = Reading.query.filter_by(date="21/07/2021")
#     for entry in entries_today:
#         instance_today = Today

