import pandas as pd
from datetime import date

from bokeh.layouts import widgetbox, row
from bokeh.models.widgets import MultiSelect, RadioGroup, Select
from bokeh.plotting import figure, curdoc
from bokeh.palettes import Blues9


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

    TOOLS="pan,wheel_zoom,box_zoom,save,reset"
    #TOOLS="crosshair,pan,wheel_zoom,box_zoom,save,reset"

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
           (-1000,5000), color='green', line_width=0.8, line_dash='dashed',
           legend=f'Week {adm_week_number:d}', alpha=0.8)

    p.legend.location = "top_left"
    
    return p


def update(attr, old, new):
    layout.children[1] = create_figure(summ_t)


def update_term(attr, old, new):
    terms_opt = all_terms.copy()
    terms_opt.remove(select_term.value)
    terms.options = terms_opt
    terms.value=terms_opt
    layout.children[1] = create_figure(summ_t)


today = date.today()
today_str = today.strftime('%Y%m%d')

df = pd.read_hdf('data/stage_data', key='weekly')
df = df[(df['year_term']>'2011.Spring')]

# curr_list = sorted(list(df['curriculum'].dropna().unique()))

summ = df.groupby(['year_term', 'stage']).sum()
summ_t = summ.transpose()

week_number, adm_week_number = adm_week(today)

# widgets
stage_list = ['Applied', 'Accepted', 'Deposited']
stage_rg = RadioGroup(name='Stage:', labels=stage_list, active=2)
stage_rg.on_change('active', update)

all_terms = sorted(list(df['year_term'].dropna().unique()))
all_terms = [l for l in all_terms if 'Fall' in l]
select_term = Select(title="Selected Term:", value=all_terms[-1], options=all_terms)
select_term.on_change('value', update_term)

terms_opt = all_terms.copy()
terms_opt.remove(select_term.value)
terms = MultiSelect(title="Other Displayed Terms: (ctrl-click to select/de-select)",
                      options=terms_opt,
                      size=5,
                      value=terms_opt)
terms.on_change('value', update)


# layout
controls = widgetbox([stage_rg, select_term, terms])
layout = row(controls, create_figure(summ_t))

curdoc().add_root(layout)
curdoc().title = "Admissions Weekly Report"
