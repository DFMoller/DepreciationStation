from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Search, Reading
from .plotting import plot_snapshot, plot_timeline, remove_outliers
from datetime import datetime

views = Blueprint('views', __name__) # don't have to call it the file name

@views.route('/', methods=["GET", "POST"])
def home():

    readings = Reading.query.all()
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
        if cat.id not in filtered_ids:
            filtered_ids[cat.id] = cat.color
            snapshot_data[cat.color] = []
            timeline_data[cat.color] = []
    
    # all_categories = Search.query.all()
    # all_ids = {}
    # for cat in all_categories:
    #     if cat.id not in all_ids:
    #         all_ids[cat.id] = cat.color
    #         timeline_data[cat.color] = []

    latest_date = max(datetime.strptime(i.date, '%d/%m/%Y') for i in readings if i.search_id in filtered_ids)

    for i in readings:
        if i.search_id in filtered_ids:
            if i.date == latest_date.strftime("%d/%m/%Y"):
                snapshot_instance = (i.mileage, i.value)
                snapshot_data[filtered_ids[i.search_id]].append(snapshot_instance)
            timeline_instance = (i.mileage, i.value, i.date)
            timeline_data[filtered_ids[i.search_id]].append(timeline_instance)

    snapshot_graph = plot_snapshot(remove_outliers(snapshot_data), year_selection)
    timeline_graph = plot_timeline(timeline_data, year_selection)

    return render_template('home.html', snapshot_graph=snapshot_graph, timeline_graph=timeline_graph, years=years, year_selection=year_selection)


@views.route('/data')
def data():
    print("Database Tables: " + str(db.engine.table_names()))
    # print(Search.query.all())
    readings = Reading.query.all()
    searches = Search.query.all()
    return render_template('data.html', readings=readings, searches=searches)
