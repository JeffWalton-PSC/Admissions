import pandas as pd
import numpy as np
from datetime import datetime, date

from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Blues8

today = datetime.now()
today_str = today.strftime('%Y%m%d')

def adm_week(d):
    """
    returns week_number and Admissions Week Number for a given date, d
    """
    year = xdate.year
    if dxdate >= (date(year, 9, 1):
        adm_year_start = year
    else:
        adm_year_start = year - 1
    
    week_number = xdate.isocalendar()[1]
    adm_week_number = week_number - (date((int(r['ACADEMIC_YEAR'])-1), 9, 1)
                              .isocalendar()[1])
    return (week_number, adm_week_number)

df = pd.read_hdf('data/stage_data', key='weekly')



p = figure(plot_width=800, plot_height=600, title=f"Admissions Weekly ({today})",
           x_axis_label="Week Number", y_axis_label="Deposits",
           tools="pan,wheel_zoom,box_zoom,save,reset",
          )

c=7
for t in terms:
    p.line(summ_t.index, summ_t[(t, 'Deposited')], color=Blues8[c], legend=t)
    c -= 1

p.line(summ_t.index, summ_t[(this_term, 'Deposited')], color='red', legend=this_term)

p.legend.location = "top_left"

output_file("weekly_deposits.html")

show(p)