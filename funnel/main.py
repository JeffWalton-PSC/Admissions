import pandas as pd
from datetime import date

from bokeh.layouts import widgetbox, row
from bokeh.models.widgets import RadioGroup
from bokeh.plotting import figure, curdoc
from bokeh.palettes import Blues8

today = date.today()
today_str = today.strftime('%Y%m%d')

def adm_week(d):
    """
    returns calendar week number and Admissions Week Number for a given date, d
    """
    year = d.year
    if d >= date(year, 9, 1):
        adm_year_start = year
    else:
        adm_year_start = year - 1
    
    week_number = d.isocalendar()[1]
    adm_start_week = date(adm_year_start, 9, 1).isocalendar()[1]

    if week_number >= adm_start_week:
        adm_week_number = week_number - adm_start_week
    else:
        adm_week_number = 53 + (week_number - adm_start_week)
    
    return (week_number, adm_week_number)


df = pd.read_hdf('funnel/data/stage_data', key='weekly')

terms = ['2012.Fall', '2013.Fall', '2014.Fall', '2015.Fall', '2016.Fall', '2017.Fall', '2018.Fall', ]
this_term = '2018.Fall'
terms.remove(this_term)

summ = df.groupby(['year_term', 'stage']).sum()
summ_t = summ.transpose()

week_number, adm_week_number = adm_week(today)
# curr_list = sorted(list(df['curriculum'].dropna().unique()))
title = f"Admissions Weekly Summary - Week {adm_week_number:d} ({today_str})"


def create_figure():
    stage = stage_list[stage_n.active]
    p = figure(plot_width=800, plot_height=600, title=title,
           x_axis_label="Week Number", y_axis_label=stage,
           tools="pan,wheel_zoom,box_zoom,save,reset",
          )
    c=5
    
    for t in terms:
        p.line(df.index, summ_t[(t, stage)], color=Blues8[c], legend=t)
        c -= 1

    p.line(summ_t.index, summ_t[(this_term, stage)], color='red', legend=this_term)
    # week_number line
    # p.line((adm_week_number,adm_week_number),
    #       (-1000,5000), color='green', legend=None)

    p.legend.location = "top_left"
    
    return p


def update(attr, old, new):
    layout.children[1] = create_figure()


stage_list = ['Applied', 'Accepted', 'Deposited']
stage_n = RadioGroup(labels=stage_list, active=2)
stage_n.on_change('active', update)

controls = widgetbox([stage_n])
layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "Admissions Weekly Report"
