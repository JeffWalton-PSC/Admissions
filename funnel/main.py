import pandas as pd
from datetime import date

from bokeh.layouts import widgetbox, row
from bokeh.models.widgets import MultiSelect, RadioGroup, Select
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

summ = df.groupby(['year_term', 'stage']).sum()
summ_t = summ.transpose()

week_number, adm_week_number = adm_week(today)
# curr_list = sorted(list(df['curriculum'].dropna().unique()))


def create_figure(df, title, stage, term):
    
    

    p = figure(plot_width=800, plot_height=600, title=title,
           x_axis_label="Week Number", y_axis_label=stage,
           tools="pan,wheel_zoom,box_zoom,save,reset",
          )
    #c=5
    
#    for t in terms.value:
#        p.line(df.index, summ_t[(t, stage)], color=Blues8[c], legend=t)
#        c -= 1

    p.line(df.index, df[(term, stage)], color='red', legend=term)
    # week_number line
    # p.line((adm_week_number,adm_week_number),
    #       (-1000,5000), color='green', legend=None)

    p.legend.location = "top_left"
    
    return p


def update(attr, old, new):
    layout.children[1] = create_figure(summ_t, title, stage, current_term.value)


stage_list = ['Applied', 'Accepted', 'Deposited']
stage_rg = RadioGroup(name='Stage:', labels=stage_list, active=2)
stage_rg.on_change('active', update)
stage = stage_list[stage_rg.active]

title = f"{stage} - Admissions Weekly Summary - Week {adm_week_number:d} ({today_str})"

all_terms = sorted(list(df['year_term'].dropna().unique()))
current_term = Select(title="Current Term:", value=all_terms[-2], options=all_terms)

other_terms = all_terms.copy()
if current_term.value in other_terms:
    other_terms.remove(current_term.value)
terms_opt = [(i,i) for i in other_terms ]
print('terms_opt', terms_opt)
# terms = MultiSelect(title="Display Other Terms:", value=None,
#                     options=terms_opt)


controls = widgetbox([stage_rg, current_term])
##print('controls', controls)
layout = row(controls, create_figure(summ_t, title, stage, current_term.value))
##print ('layout', layout)

curdoc().add_root(layout)
curdoc().title = "Admissions Weekly Report"
