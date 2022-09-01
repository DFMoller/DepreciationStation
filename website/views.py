from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Search, History, Today
from .plotting import ChartingEngine, plot_scatter_snapshot, plot_timeline, plot_density_snapshot
from datetime import datetime, date
import time, json

views = Blueprint('views', __name__) # don't have to call it the file name

@views.route('/', methods=["GET", "POST"])
def home():
    start_time = time.time()
    time_dict = {
        'dt': str(datetime.now()),
        'Total View Time': 0,
        'Search Query Time': 0,
        'Today Query Time': 0,
        'History Query Time': 0,
        'Charting Engine Time': 0,
        'Get xLabels Time': 0,
        'Get Timeline Datasets Time': 0
    }
    # Determine which year to display
    years = []
    before_search_query_time = time.time()
    all_searches = Search.query.all()
    time_dict['Search Query Time'] = time.time() - before_search_query_time
    for x in all_searches:
        if x.year not in years:
            years.append(x.year)
    years = sorted(years)
    if request.method == "GET":
        year_selection = years[-1]
    elif request.method == "POST":
        year_selection = request.form.get("year-selection")
    before_today_query_time = time.time()
    # snapshot_readings = Today.query.all()
    time_dict['Today Query Time'] = time.time() - before_today_query_time
    before_history_query_time = time.time()
    history_readings = History.query.all()
    time_dict['History Query Time'] = time.time() - before_history_query_time
    before_ce_time = time.time()
    ce = ChartingEngine(history_readings, all_searches, year_selection)
    time_dict['Charting Engine Time'] = time.time() - before_ce_time
    before_xlabels_time = time.time()
    xlabels = ce.get_timeline_xlables()
    time_dict['Get xLabels Time'] = time.time() - before_xlabels_time
    before_datasets_time = time.time()
    median_datasets = ce.get_timeline_datasets_median()
    relative_datasets = ce.get_timeline_datasets_relative()
    time_dict['Get Timeline Datasets Time'] = time.time() - before_datasets_time
    time_dict['Total View Time'] = time.time() - start_time
    return render_template('home.html', years=years, year_selection=year_selection, median_datasets=median_datasets, relative_datasets=relative_datasets, xlabels=xlabels, time_dict=time_dict)

# @views.route('/delete_data')
# def delete():

#     all_history = History.query.all()
#     # all_today = Today.query.all() 

#     # today = date.today().strftime('%d/%m/%Y')
#     cutoff = datetime.strptime("12/04/2022", '%d/%m/%Y')

#     history_deleted = 0
#     discard = []
#     for x in all_history:
#         if datetime.strptime(x.date, '%d/%m/%Y') < cutoff:
#             db.session.delete(x)
#             history_deleted += 1
#             discard.append(str(x))

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

#     return json.dumps(discard)


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

