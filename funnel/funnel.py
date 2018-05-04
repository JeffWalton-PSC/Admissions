import pandas as pd
from datetime import date

from bokeh.layouts import widgetbox, row
from bokeh.models.widgets import Select
from bokeh.plotting import figure, curdoc

today = date.today()
today_str = today.strftime('%Y%m%d')

df = pd.read_hdf('data/stage_data', key='weekly')
df = df[(df['year_term']>'2012.Spring')]

summ = df.groupby(['year_term', 'stage']).sum()
summ_t = summ.transpose()


def create_figure(df):
    
    term = select_term.value

    title = f"{term} - Admissions Annual Funnel  ({today_str})"

    p = figure(plot_width=800, plot_height=600, title=title,
           x_axis_label="Admissions Week Number (year starts Sept 1)", y_axis_label=None,
           tools="pan,wheel_zoom,box_zoom,save,reset",
          )

    p.line(df.index, df[(term, 'Applied')], color='green', legend='Applied')
    p.line(df.index, df[(term, 'Accepted')], color='blue', legend='Accepted')
    p.line(df.index, df[(term, 'Deposited')], color='red', legend='Deposited')

    p.legend.location = "top_left"
    
    return p


def update(attr, old, new):
    layout.children[1] = create_figure(summ_t)


all_terms = sorted(list(df['year_term'].dropna().unique()))
all_terms = [l for l in all_terms if 'Fall' in l]
select_term = Select(title="Selected Term:", value=all_terms[-1], options=all_terms)
select_term.on_change('value', update)

controls = widgetbox([select_term])
layout = row(controls, create_figure(summ_t))

curdoc().add_root(layout)
curdoc().title = "Admissions Annual Funnel"
