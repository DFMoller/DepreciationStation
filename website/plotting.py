import pygal
from pygal.style import Style
from scipy.stats import linregress, zscore, stats
from pandas import DataFrame
import numpy as np
from datetime import datetime, timedelta

def plot_scatter_snapshot(graph_data, year):

    filtered_data = remove_outliers(graph_data)

    custom_style = Style(
        font_family='googlefont:Poppins',
        foreground='#04588C',
        foreground_strong='#EE6945',
        foreground_subtle='#A9BFD0',
        background='transparent',
        plot_background='transparent',
        colors=('#000000', '#dd2020', '#4078B7', '#545454', '#E98E19', '#A2A2A2', '#d2d2d2')
    )

    xy_chart = pygal.XY(style=custom_style, legend_at_bottom=True, stroke=False, dots_size=2)
    xy_chart.title = f'Figure A: Mileage vs Value Scatter Plot for Vehicles from {year} listed on Autotrader Today, sorted by colour'
    xy_chart.x_title = "Mileage (km)"
    xy_chart.y_title = "Value (Rand)"

    for color in filtered_data:
        xy_chart.add(color.capitalize(), filtered_data[color])

    return xy_chart.render_data_uri()

def plot_density_snapshot(graph_data, year):
    
    custom_style = Style(
        font_family='googlefont:Poppins',
        foreground='#04588C',
        foreground_strong='#EE6945',
        foreground_subtle='#A9BFD0',
        background='transparent',
        plot_background='transparent',
        colors=('#000000', '#dd2020', '#4078B7', '#545454', '#E98E19', '#A2A2A2', '#d2d2d2'),
        opacity='.3'
    )

    filtered_data = remove_outliers(graph_data)
    max_mileage = 0
    for color in filtered_data:
        for dp in filtered_data[color]:
            if dp[0] > max_mileage:
                max_mileage = dp[0]
    batches = 6
    batch_size = max_mileage / 10
    density_data = {}
    for color in filtered_data:
        line = []
        for batch in range(batches):
            batch_values = []
            for dp in filtered_data[color]:
                if dp[0] < batch_size*(batch+1) and dp[0] > batch_size*batch:
                    batch_values.append(int(dp[1]))
            if len(batch_values) > 1:
                median_val = np.median(batch_values)
                std = np.std(batch_values)
                line.append((batch_size*(batch+1), median_val))
        density_data[color] = line

    xy_chart = pygal.XY(style=custom_style, fill=False, interpolate='cubic', legend_at_bottom=True, stroke=True, dots_size=2)
    xy_chart.title = f'Figure B: Median Distribution for Cars from {year} listed on Autotrader Today, sorted by colour'
    xy_chart.x_title = "Mileage (km)"
    xy_chart.y_title = "Median Value (Rand)"

    for color in density_data:
        xy_chart.add(color.capitalize(), density_data[color])

    return xy_chart.render_data_uri()


def plot_timeline(graph_data, year):

    custom_style = Style(
        font_family='googlefont:Poppins',
        foreground='#04588C',
        foreground_strong='#EE6945',
        foreground_subtle='#A9BFD0',
        background='transparent',
        plot_background='transparent',
        opacity='.1',
        colors=('#000000', '#dd2020', '#4078B7', '#545454', '#E98E19', '#A2A2A2', '#d2d2d2'),
        transition='200ms ease-in',
        # stroke_width='5'
    )
    stroke_style = {
        'width': 2,
        'linejoin': 'round',
        'linecap': 'round'
    }

    all_dates = []
    final_data = {}
    max_val = 0

    # reformat datapoints to dt_objects (from strings) and integers (from floats)
    for color in graph_data:
        line = []
        for tup in graph_data[color]:
            if int(tup[1]) > max_val:
                max_val = int(tup[1])
            date_obj = datetime.strptime(tup[0], '%d/%m/%Y')
            if date_obj not in all_dates:
                all_dates.append(date_obj)
            instance = (date_obj, int(tup[1]))
            line.append(instance)
        final_data[color] = line

    # Interpolate to add missing datapoints - Only for display! This is NOT written to db file
    for color in final_data:
        prev_date = final_data[color][0][0] # date of first dp
        prev_val = final_data[color][0][1] # value of first dp
        for i, dp in enumerate(final_data[color]):
            #start doing calculations from second dp in the line onwards
            if i > 0:
                date = dp[0]
                val = dp[1]
                gap_len = (date - prev_date).days - 1 # gap_len = 0 for consecutive days
                # len > 0 means there are missing datapoints
                if gap_len > 0:
                    val_diff = val - prev_val
                    val_increment = val_diff / (gap_len+1)
                    for x in range(gap_len):
                        new_date = prev_date + timedelta(days=x+1)
                        new_val = prev_val + val_increment*(x+1)
                        new_dp = (new_date, new_val)
                        final_data[color].insert(i+x, new_dp)
                        if new_date not in all_dates:
                            all_dates.append(new_date)
                prev_date = date
                prev_val = val

    # Define Plot
    dateline = pygal.DateLine(style=custom_style, show_dots=False, stroke_style=stroke_style, fill=False, legend_at_bottom=True, x_value_formatter=lambda dt: dt.strftime('%d/%m/%Y'), range=(0, max_val + 100000), min_scale=max_val*0.0001)
    dateline.title = f'Figure C: Daily median values of cars from {year}, per colour (Historical Data)'
    dateline.x_title = "Time"
    dateline.y_title = "Value (Rand)"

    # Add lines and labels
    for color in final_data:
        dateline.add(color.capitalize(), final_data[color])

    # Format x-labels to not show every date
    all_dates = sorted(all_dates)
    x_labels = []
    num_dates = len(all_dates)
    if num_dates > 8:
        divider = round(num_dates/8, 0)
    else:
        divider = 1
    for count, date in enumerate(all_dates):
        if count % divider == 0:
            x_labels.append(date) # This is a datetime object
    dateline.x_labels = x_labels

    # Return completed plot
    return dateline.render_data_uri()

def remove_outliers(data):
    filtered_data = {}
    for color in data:
        df = DataFrame(data[color], columns=["mileage", "value"])
        z_scores = stats.zscore(df)
        abs_z_scores = np.abs(z_scores)
        filtered_entries = (abs_z_scores < 3).all(axis=1)
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