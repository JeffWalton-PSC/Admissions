import pandas as pd
from datetime import date

from bokeh.layouts import widgetbox, row
from bokeh.models.widgets import MultiSelect, RadioGroup, Select
from bokeh.plotting import figure, curdoc
from bokeh.palettes import Blues9

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


df = pd.read_hdf('data/stage_data', key='weekly')
df = df[(df['year_term']>'2011.Spring')]


summ = df.groupby(['year_term', 'stage']).sum()
summ_t = summ.transpose()

week_number, adm_week_number = adm_week(today)
# curr_list = sorted(list(df['curriculum'].dropna().unique()))


def create_figure(df):
    
    stage = stage_list[stage_rg.active]

    title = f"{stage} - Admissions Weekly Summary - Week {adm_week_number:d} ({today_str})"

    term = select_term.value

    term_list = list(terms.value)
    term_list.reverse()
    
    y_max = df[(term, stage)].max()
    for t in term_list:
        ym = df[(t, stage)].max()
        if ym > y_max:
            y_max = ym
    print('y_max', y_max)

    TOOLS="pan,wheel_zoom,box_zoom,save,reset"
    #TOOLS="crosshair,pan,wheel_zoom,box_zoom,save,reset"

    print('create_figure', stage_rg.active, stage, term)
    p = figure(plot_width=800, plot_height=600, title=title,
           x_axis_label="Admissions Week Number (year starts Sept 1)",
           y_axis_label=stage,
           tools=TOOLS,
           x_range=(0,54),
           y_range=(0,y_max*1.05)
          )

    p.line(df.index, df[(term, stage)], 
           color='red', line_width=2, legend=term)

    c=0
    for t in term_list:
        p.line(df.index, df[(t, stage)], color=Blues9[c], legend=t)
        if c <= 7:
            c += 1

    # week_number line
    p.line((adm_week_number,adm_week_number),
           (-1000,5000), color='green', line_width=0.8, legend=None, alpha=0.6)

    p.legend.location = "top_left"
    
    return p


def update(attr, old, new):
    #global terms_opt
    #terms_opt = update_terms(all_terms)
    print('update', stage_rg.active, stage_list[stage_rg.active], select_term.value, terms_opt, terms.value)
    layout.children[1] = create_figure(summ_t)


def update_terms(all_terms):
    other_terms = all_terms.copy()
    if select_term.value in other_terms:
        other_terms.remove(select_term.value)
    terms_opt = [(i,i) for i in other_terms ]
    print('update_terms', terms_opt)
    return terms_opt


stage_list = ['Applied', 'Accepted', 'Deposited']
stage_rg = RadioGroup(name='Stage:', labels=stage_list, active=2)
stage_rg.on_change('active', update)

all_terms = sorted(list(df['year_term'].dropna().unique()))
all_terms = [l for l in all_terms if 'Fall' in l]
select_term = Select(title="Selected Term:", value=all_terms[-1], options=all_terms)
select_term.on_change('value', update)

terms_opt = all_terms.copy()
terms_opt.remove(select_term.value)
terms = MultiSelect(title="Other Display Terms:",
                      options=terms_opt,
                      size=5,
                      value=terms_opt)
terms.on_change('value', update)


controls = widgetbox([stage_rg, select_term, terms])
layout = row(controls, create_figure(summ_t))

curdoc().add_root(layout)
curdoc().title = "Admissions Weekly Report"
