import pygal
from pygal.style import Style
from scipy.stats import linregress, zscore, stats
from pandas import DataFrame
import numpy as np
from datetime import datetime

def plot_snapshot(graph_data, year):

    custom_style = Style(
        font_family='googlefont:Poppins',
        foreground='#04588C',
        foreground_strong='#EE6945',
        foreground_subtle='#A9BFD0',
        background='transparent',
        plot_background='transparent'
    )

    
    # xy_chart = pygal.XY(style=custom_style, legend_at_bottom=True, legend_at_bottom_columns=len(years))
    xy_chart = pygal.XY(style=custom_style, legend_at_bottom=True, stroke=False)
    xy_chart.title = f'Vehicles from {year} listed on Autotrader Today'
    xy_chart.x_title = "Mileage (km)"
    xy_chart.y_title = "Value (Rand)"

    for color in graph_data:
        xy_chart.add(color, graph_data[color])
    
    return xy_chart.render_data_uri()

def plot_timeline(graph_data, year):

    custom_style = Style(
        font_family='googlefont:Poppins',
        foreground='#04588C',
        foreground_strong='#EE6945',
        foreground_subtle='#A9BFD0',
        background='transparent',
        plot_background='transparent'
    )

    all_dates = []
    final_data = {}
    max_val = 0;
    for color in graph_data:
        df = DataFrame(graph_data[color], columns=["mileage", "value", "date"])
        unique_dates = df["date"].unique()
        line = []
        for date in unique_dates:
            filtered_df = df[df["date"] == date]
            sorted_df = filtered_df.sort_values("value")
            median_value = sorted_df["value"].median()
            if median_value > max_val:
                max_val = median_value
            instance = (datetime.strptime(date, '%d/%m/%Y'), int(median_value))
            line.append(instance)
            date_obj = datetime.strptime(date, '%d/%m/%Y')
            if date_obj not in all_dates:
                all_dates.append(date_obj)
        final_data[color] = line

    # max_val = 0
    # for color in graph_data:
    #     for tup in graph_data[color]:
    #         if tup[1] > max_val:
    #             max_val = tup[1]
    # print(str(max_val))

    dateline = pygal.DateLine(style=custom_style, legend_at_bottom=True, x_value_formatter=lambda dt: dt.strftime('%d/%m/%Y'), range=(0, max_val + 100000), min_scale=max_val*0.0001)
    # xy_chart.x_value_formatter = lambda dt: str(dt)
    dateline.title = f'Vehicles from {year} || Historical Data'
    dateline.x_title = "Time"
    dateline.y_title = "Value (Rand)"

    for col in final_data:
        dateline.add(col, final_data[col])

    all_dates = sorted(all_dates)
    x_labels = []
    for date in all_dates:
        x_labels.append(date) # This is a datetime object
        print(date)
    
    dateline.x_labels = x_labels
    
    # dateline.x_value_formatter = lambda dt: '%s' % dt

    return dateline.render_data_uri()

def remove_outliers(data):
    filtered_data = {}
    for color in data:
        df = DataFrame(data[color], columns=["mileage", "value"])
        z_scores = stats.zscore(df)
        abs_z_scores = np.abs(z_scores)
        filtered_entries = (abs_z_scores < 2.5).all(axis=1)
        new_df = df[filtered_entries]
        tuples = [tuple(x) for x in new_df.to_numpy()]
        filtered_data[color] = tuples
    return filtered_data

def regression(colors_dict):
    lines_data = []
    for year in colors_dict:
        if len(colors_dict[year]) > 10:
            mileages = [x[0] for x in colors_dict[year]]
            values = [x[1] for x in colors_dict[year]]
            min_mil = mileages[0]
            max_mil = mileages[0]
            for mil in mileages:
                if mil < min_mil:
                    min_mil = mil
                if mil > max_mil:
                    max_mil = mil
            res = linregress(mileages, values)
            data = {
                "year": year,
                "slope": res.slope,
                "intercept": res.intercept,
                "min_x": min_mil,
                "max_x": max_mil
            }
            lines_data.append(data)
    return lines_data