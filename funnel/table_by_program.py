import numpy as np
import pandas as pd
from datetime import date

from bokeh.io import curdoc, show
from bokeh.layouts import widgetbox, column
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, TableColumn, RadioGroup


start_term = "2014.Spring"
this_yearterm = "2021.Fall"
last_yearterm = "2020.Fall"
twoyrago_yearterm = "2019.Fall"


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


# def update(attr, old, new):
#    table.children[0] = create_table(tab_df)


def create_table(df):
    #    stage = stage_list[stage_rg.active]
    stage = "Deposited"

    d = df.loc[(stage,)]
    source = ColumnDataSource(d)

    c = []
    c.append(this_yearterm + "_Week" + str(week))
    c.append(this_yearterm + "_LastWeek" + str(week - 1))
    c.append(last_yearterm + "_Week" + str(week))
    c.append(twoyrago_yearterm + "_Week" + str(week))
    c.append(last_yearterm + "_Total")
    c.append(twoyrago_yearterm + "_Total")

    columns = [
        TableColumn(field="curriculum", title="Program", width=120),
        TableColumn(field=c[0], title=c[0]),
        TableColumn(field=c[1], title=c[1]),
        TableColumn(field=c[2], title=c[2]),
        TableColumn(field=c[3], title=c[3]),
        TableColumn(field=c[4], title=c[4]),
        TableColumn(field=c[5], title=c[5]),
    ]
    data_table = DataTable(
        source=source,
        columns=columns,
        width=680,
        height=600,
        index_position=None,
        reorderable=True,
        sortable=True,
    )
    return data_table


today = date.today()
today_str = today.strftime("%Y%m%d")
week = adm_week(today)[1]

title = f"Table By Program  {today_str}  (Week {week:d})"

# widgets
# stage_list = ['Applied', 'Accepted', 'Deposited']
# stage_rg = RadioGroup(name='Stage:', labels=stage_list, active=2)
# stage_rg.on_change('active', update)

# prepare data
df = pd.read_hdf("data/stage_data", key="weekly")
df = df.loc[df["year_term"].isin([this_yearterm, last_yearterm, twoyrago_yearterm])]
df["curriculum"] = df["curriculum"].fillna("unknown")
summ = df.groupby(["year_term", "stage", "curriculum"]).sum()

tab_df = pd.DataFrame(
    {this_yearterm + "_Week" + str(week): summ.loc[(this_yearterm,)][str(week)]}
)
tab_df = pd.concat(
    [
        tab_df,
        pd.DataFrame(
            {
                this_yearterm
                + "_LastWeek"
                + str(week - 1): summ.loc[(this_yearterm,)][str(week - 1)]
            }
        ),
    ],
    axis=1,
    sort=True,
)
tab_df = pd.concat(
    [
        tab_df,
        pd.DataFrame(
            {last_yearterm + "_Week" + str(week): summ.loc[(last_yearterm,)][str(week)]}
        ),
    ],
    axis=1,
    sort=True,
)
tab_df = pd.concat(
    [
        tab_df,
        pd.DataFrame(
            {
                twoyrago_yearterm
                + "_Week"
                + str(week): summ.loc[(twoyrago_yearterm,)][str(week)]
            }
        ),
    ],
    axis=1,
    sort=True,
)
tab_df = pd.concat(
    [
        tab_df,
        pd.DataFrame({last_yearterm + "_Total": summ.loc[(last_yearterm,)]["53"]}),
    ],
    axis=1,
    sort=True,
)
tab_df = pd.concat(
    [
        tab_df,
        pd.DataFrame(
            {twoyrago_yearterm + "_Total": summ.loc[(twoyrago_yearterm,)]["53"]}
        ),
    ],
    axis=1,
    sort=True,
)
tab_df = tab_df.fillna(0).astype(int)


# controls = widgetbox(stage_rg)
table = widgetbox(create_table(tab_df))

# curdoc().add_root(column(controls, table))
curdoc().add_root(table)
curdoc().title = title
