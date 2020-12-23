import pandas as pd
from datetime import date

from bokeh.layouts import widgetbox, row
from bokeh.models import HoverTool
from bokeh.models.widgets import Select
from bokeh.plotting import figure, curdoc, ColumnDataSource

start_term = "2014.Spring"

TOOLS = "pan,wheel_zoom,box_zoom,save,reset"

today = date.today()
today_str = today.strftime("%Y%m%d")

df = pd.read_hdf("data/stage_data", key="weekly")
df = df[(df["year_term"] > start_term)]

summ = df.groupby(["year_term", "stage"]).sum()
summ_t = summ.transpose()


def create_figure(df):

    term = select_term.value

    title = f"{term} - Admissions Annual Funnel  ({today_str})"

    hover = HoverTool(
        tooltips=[
            ("week", "@week"),
            #                                ("number", "$y{0}"),
            ("applied", "@app"),
            ("accepted", "@acc"),
            ("deposited", "@dep"),
        ]
    )

    p = figure(
        plot_width=800,
        plot_height=600,
        title=title,
        x_axis_label="Admissions Week Number (year starts Sept 1)",
        y_axis_label=None,
        tools=[TOOLS, hover],
    )

    source = ColumnDataSource(
        data=dict(
            week=df.index,
            app=df[(term, "Applied")].values,
            acc=df[(term, "Accepted")].values,
            dep=df[(term, "Deposited")].values,
        )
    )

    p.line("week", "app", source=source, color="green", legend="Applied")
    p.line("week", "acc", source=source, color="blue", legend="Accepted")
    p.line("week", "dep", source=source, color="red", legend="Deposited")

    p.legend.location = "top_left"

    return p


def update(attr, old, new):
    layout.children[1] = create_figure(summ_t)


all_terms = sorted(list(df["year_term"].dropna().unique()))
all_terms = [l for l in all_terms if "Fall" in l]
select_term = Select(title="Selected Term:", value=all_terms[-1], options=all_terms)
select_term.on_change("value", update)

controls = widgetbox([select_term])
layout = row(controls, create_figure(summ_t))

curdoc().add_root(layout)
curdoc().title = "Admissions Annual Funnel"
