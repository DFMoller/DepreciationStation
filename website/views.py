from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Search, History, Today
from .plotting import plot_scatter_snapshot, plot_timeline, plot_density_snapshot
from datetime import datetime, date

views = Blueprint('views', __name__) # don't have to call it the file name

@views.route('/', methods=["GET", "POST"])
def home():

    history_readings = History.query.all()
    today_readings = Today.query.all()
    years = []
    for x in Search.query.all():
        if x.year not in years:
            years.append(x.year)
    years = sorted(years)
    snapshot_data = {}
    timeline_data = {}

    if request.method == "GET":
        year_selection = years[0]
    elif request.method == "POST":
        year_selection = request.form.get("year-selection")

    filtered_categories = Search.query.filter_by(year=year_selection)
    filtered_ids = {}
    for cat in filtered_categories:
        # if cat.id not in filtered_ids:
        filtered_ids[cat.id] = cat.color
        snapshot_data[cat.color] = []
        timeline_data[cat.color] = []

    # all_categories = Search.query.all()
    # all_ids = {}
    # for cat in all_categories:
    #     if cat.id not in all_ids:
    #         all_ids[cat.id] = cat.color
    #         timeline_data[cat.color] = []

    # latest_date = max(datetime.strptime(i.date, '%d/%m/%Y') for i in readings if i.search_id in filtered_ids)

    num_readings = 0
    for i in today_readings:
        if i.search_id in filtered_ids and num_readings < 6000:
            snapshot_instance = (i.mileage, i.value)
            snapshot_data[filtered_ids[i.search_id]].append(snapshot_instance)
            num_readings += 1

    # print("Num Readings: " + str(num_readings))

    for i in history_readings:
        if i.search_id in filtered_ids:
            timeline_instance = (i.date, i.median_value)
            timeline_data[filtered_ids[i.search_id]].append(timeline_instance)

    # for i in readings:
    #     if i.search_id in filtered_ids:
    #         if i.date == latest_date.strftime("%d/%m/%Y"):
    #             snapshot_instance = (i.mileage, i.value)
    #             snapshot_data[filtered_ids[i.search_id]].append(snapshot_instance)
    #         timeline_instance = (i.mileage, i.value, i.date)
    #         timeline_data[filtered_ids[i.search_id]].append(timeline_instance)

    scatter_snapshot_graph = plot_scatter_snapshot(snapshot_data, year_selection)
    density_snapshot_graph = plot_density_snapshot(snapshot_data, year_selection)
    timeline_graph = plot_timeline(timeline_data, year_selection)

    return render_template('home.html', density_snapshot_graph=density_snapshot_graph, scatter_snapshot_graph=scatter_snapshot_graph, timeline_graph=timeline_graph, years=years, year_selection=year_selection)

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

