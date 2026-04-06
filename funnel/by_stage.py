import numpy as np
import pandas as pd
from datetime import date

from bokeh.layouts import row, column
from bokeh.models.widgets import MultiSelect, RadioGroup, Select
from bokeh.plotting import figure, curdoc
from bokeh.palettes import Set1_9, Bokeh8, Colorblind8

# PowerCampus utilities
import powercampus as pc

start_term = "2018.Spring"

current_yt_df = pc.current_yearterm()
current_term = current_yt_df['term'].iloc[0]
current_year = current_yt_df['year'].iloc[0]
current_yt = current_yt_df['yearterm'].iloc[0]
current_yt_sort = current_yt_df['yearterm_sort'].iloc[0]

def next_fall_yearterm(yearterm):
    """
    returns the next Fall yearterm in the sequence of yearterms
    """
    if "Spring" in yearterm:
        return yearterm.replace("Spring", "Fall")
    elif "Summer" in yearterm:
        return yearterm.replace("Summer", "Fall")
    elif "Fall" in yearterm:
        return yearterm.replace("Fall", "Spring").replace(str(int(yearterm[:4])), str(int(yearterm[:4]) + 1))
    else:
        raise ValueError(f"Invalid yearterm: {yearterm}")

def date_diff_weeks(start, end):
    """
    returns the difference between two dates in integer weeks
    """
    diff = (pd.to_datetime(end) - pd.to_datetime(start))
    return int( diff / np.timedelta64(1,'W'))


def adm_week(d):
    """
    returns calendar week number and Admissions Week Number for a given date, d
    """
    year = d.year
    week_number = d.isocalendar()[1]

    if d >= date(year, 9, 1):
        adm_start = date(year, 9, 1)
    else:
        adm_start = date(year - 1, 9, 1)

    adm_week_number = min(date_diff_weeks(adm_start, d), 53)

    return week_number, adm_week_number


def create_figure(df):

    stage = stage_list[stage_rg.active]

    title = (
        f"{stage} - Admissions Weekly Summary - Week {adm_week_number:d} ({today_str})"
    )

    term = select_term.value

    term_list = list(terms.value)
    term_list.reverse()

    y_max = df[(term, stage)].max()
    for t in term_list:
        ym = df[(t, stage)].max()
        if ym > y_max:
            y_max = ym

    TOOLS = "pan,wheel_zoom,box_zoom,save,reset"
    # TOOLS="crosshair,pan,wheel_zoom,box_zoom,save,reset"

    p = figure(
        width=800,
        height=600,
        title=title,
        x_axis_label="Admissions Week Number (year starts Sept 1)",
        y_axis_label=stage,
        tools=TOOLS,
        x_range=(0, 54),
        y_range=(0, y_max * 1.05),
        background_fill_color="white",
        background_fill_alpha=0.7,  
    )

    p.line(df.index, df[(term, stage)], color="red", line_width=3.5, legend_label=term)

    c = 0 # set to 1 to skip red for certaion color pallettes like Set1_9
    for t in term_list:
        p.line(df.index, df[(t, stage)], color=Colorblind8[c], line_width=1.5, legend_label=t)
        if c <= 7:
            c += 1
        else:
            c = 0 # set to 1 to skip red

    # week_number line
    p.line(
        (adm_week_number, adm_week_number),
        (-1000, 5000),
        color="green",
        line_width=0.8,
        line_dash="dashed",
        legend_label=f"Week {adm_week_number:d}",
        alpha=0.8,
    )

    p.legend.location = "top_left"

    return p


def update(attr, old, new):
    layout.children[1] = create_figure(summ_t)


def update_term(attr, old, new):
    terms_opt = all_terms.copy()
    terms_opt.remove(select_term.value)
    terms.options = terms_opt
    terms.value = terms_opt
    layout.children[1] = create_figure(summ_t)


today = date.today()
today_str = today.strftime("%Y%m%d")

df = pd.read_hdf("data/stage_data", key="weekly")
df = df[(df["year_term"] > start_term)]

# curr_list = sorted(list(df['curriculum'].dropna().unique()))

summ = df.groupby(["year_term", "stage"]).sum(numeric_only=True)
summ_t = summ.transpose()

week_number, adm_week_number = adm_week(today)

# widgets
stage_list = ["Applied", "Accepted", "Deposited"]
stage_rg = RadioGroup(name="Stage:", labels=stage_list, active=2)
stage_rg.on_change("active", update)

all_terms = sorted(list(df["year_term"].dropna().unique()))
all_terms = [l for l in all_terms if "Fall" in l]
print(all_terms)
next_fall = next_fall_yearterm(current_yt)
print(f"Current term: {current_yt}, Next Fall term: {next_fall}")

select_term = Select(title="Selected Term:", value=all_terms[all_terms.index(next_fall) if next_fall in all_terms else -1], options=all_terms)
select_term.on_change("value", update_term)

terms_opt = all_terms.copy()
terms_opt.remove(select_term.value)
terms = MultiSelect(
    title="Other Displayed Terms: (ctrl-click to select/de-select)",
    options=terms_opt,
    size=5,
    value=terms_opt,
)
terms.on_change("value", update)


# layout
controls = column([stage_rg, select_term, terms])
layout = row(controls, create_figure(summ_t))

curdoc().add_root(layout)
curdoc().title = "Admissions Weekly Report"
