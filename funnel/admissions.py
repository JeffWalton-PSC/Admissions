import pandas as pd
import numpy as np
from datetime import datetime, date

import os
from sqlalchemy import create_engine
# local connection information
db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASS')
db_host = os.environ.get('DB_HOST')
db_database = os.environ.get('DB_DATABASE')
db_driver = os.environ.get('DB_DRIVER')
engine = create_engine(f'mssql+pyodbc://{db_user}:{db_pass}' +
                       f'@{db_host}/{db_database}?' +
                       f'driver={db_driver}')
connection = engine.connect()

today = datetime.now().strftime('%Y%m%d')

begin_year = '2009'

# read VWSSTAGERANKING data
sql_str = "SELECT STAGERANKING_ID, field_name, field_value " + \
          "FROM VWSSTAGERANKING WHERE " + \
          "status = 'A' "
stgrnk = pd.read_sql_query(sql_str, connection)

# read STAGEHISTORY data
sql_str = "SELECT PEOPLE_CODE_ID, ACADEMIC_YEAR, ACADEMIC_TERM, " + \
          "ACADEMIC_SESSION, FIELD_ID, FIELD_DATE " + \
          "FROM STAGEHISTORY WHERE " + \
          f"ACADEMIC_YEAR >= '{begin_year}' "
stg_hist = pd.read_sql_query(sql_str, connection)

stg_hist['create_date'] = stg_hist['FIELD_DATE']
stage_data = pd.merge(stg_hist, stgrnk, left_on=['FIELD_ID'],
                      right_on=['STAGERANKING_ID'], how='left')
keep_fields = ['PEOPLE_CODE_ID', 'ACADEMIC_YEAR', 'ACADEMIC_TERM',
               'ACADEMIC_SESSION', 'field_name', 'field_value', 'create_date']
stage_data = stage_data.loc[~stage_data['create_date'].isnull(), keep_fields]

# read ACADEMIC data
academic_dtype = {'PEOPLE_CODE_ID': str, 'ACADEMIC_YEAR': str,
                  'ACADEMIC_TERM': str, 'ACADEMIC_SESSION': str,
                  'APPLICATION_FLAG': str, 'APP_STATUS': str}
date_cols = ['APPLICATION_DATE', 'APP_STATUS_DATE', 'APP_DECISION_DATE']
academic = pd.read_csv('ACADEMIC.csv', dtype=academic_dtype,
                       parse_dates=date_cols,
                       usecols=['PEOPLE_CODE_ID',
                                'ACADEMIC_YEAR', 'ACADEMIC_TERM',
                                'ACADEMIC_SESSION', 'POPULATION',
                                'INQUIRY_FLAG',
                                'APPLICATION_FLAG', 'APPLICATION_DATE',
                                'APP_STATUS', 'APP_STATUS_DATE',
                                'APP_DECISION', 'APP_DECISION_DATE'])

app_data = (academic.loc[~(academic['POPULATION'].isin(['ADVSTU', 'NOND'])) &
                         ((academic['INQUIRY_FLAG'] == 'Y') |
                          (academic['APPLICATION_FLAG'] == 'Y'))]
            )

applied = (app_data[app_data['APP_STATUS'].notnull()]
           .rename(columns={'APP_STATUS': 'field_value'})
           .rename(columns={'APP_STATUS_DATE': 'create_date'})
           )
applied.loc[:, 'field_name'] = 'Application Status'
applied = applied.loc[~applied['create_date'].isnull(), keep_fields]

accepted = (app_data[app_data['APP_DECISION'].notnull()]
            .rename(columns={'APP_DECISION': 'field_value'})
            .rename(columns={'APP_DECISION_DATE': 'create_date'})
            )
accepted.loc[:, 'field_name'] = 'Application Decision'
accepted = accepted.loc[~accepted['create_date'].isnull(), keep_fields]

# stack Stage History, Academic Applied and Academic Accepted
adm_df = stage_data.append(applied).append(accepted)

adm_df = (adm_df.loc[((adm_df['ACADEMIC_TERM'].isin(['FALL', 'SPRING'])) &
                      (adm_df['ACADEMIC_SESSION'] == 'MAIN') &
                      (adm_df['ACADEMIC_YEAR'] >= '2009')
                      )
                     ]
          )

# create new fields
adm_df['year_term'] = (adm_df['ACADEMIC_YEAR'] + '.' +
                       adm_df['ACADEMIC_TERM'].str.title())
adm_df['Week_Number'] = adm_df['create_date'].dt.week

# convert ACADEMIC_YEAR to numeric keep numeric-valued records
adm_df['ACADEMIC_YEAR'] = pd.to_numeric(adm_df['ACADEMIC_YEAR'],
                                        errors='coerce', downcast='integer')
adm_df = adm_df.loc[adm_df['ACADEMIC_YEAR'].notnull()]

adm_week_number = (lambda r: (r['Week_Number'] -
                              (date(int(r['ACADEMIC_YEAR']), 9, 1)
                               .isocalendar()[1])
                              )
                   if (r['Week_Number'] > (date(int(r['ACADEMIC_YEAR']), 9, 1)
                                           .isocalendar()[1]))
                   else (53 + r['Week_Number'] -
                         (date(int(r['ACADEMIC_YEAR']), 9, 1)
                          .isocalendar()[1])
                         )
                   )
adm_df['Admissions_Week'] = adm_df.apply(adm_week_number, axis=1)

adm_keep_values = ['300', 'ACC', 'ACXL', 'CANC', 'DEF', 'DEFR', 'DENY', 'DPAC',
                   'TRDP', 'TRPD', 'TRNS', 'WAIT', '500', 'PEND', 'COMP']
adm_keep_cols = ['PEOPLE_CODE_ID', 'year_term', 'Admissions_Week',
                 'field_value']
adm_df = adm_df.loc[(adm_df['field_value'].isin(adm_keep_values)),
                    adm_keep_cols]

# admissions status table
admission_status = {'300': 'Applied', 'ACC': 'Accepted', 'ACXL': 'Canceled',
                    'CANC': 'Canceled', 'DEF': 'Canceled', 'DEFR': 'Canceled',
                    'DENY': 'Canceled', 'DPAC': 'Deposited',
                    'TRDP': 'Deposited', 'TRPD': 'Deposited',
                    'TRNS': 'Accepted', 'WAIT': 'Accepted',
                    '500': 'Deposited', 'PEND': 'Applied',
                    'COMP': 'Applied',
                    }
adm_stat = pd.DataFrame(list(admission_status.items()),
                        columns=['field_value', 'admission_status'])

adm_df1 = (pd.merge(adm_df, adm_stat, on=['field_value'], how='left')
           .drop(['field_value'], axis=1)
           .drop_duplicates(['PEOPLE_CODE_ID', 'year_term', 'Admissions_Week',
                             'admission_status'])
           )

adm_df1 = (adm_df1.sort_values(['year_term', 'PEOPLE_CODE_ID',
                                'admission_status', 'Admissions_Week'])
           .drop_duplicates(['year_term', 'PEOPLE_CODE_ID',
                             'admission_status'],
                            keep='first')
           )

e = adm_df1.pivot_table(index=['year_term', 'PEOPLE_CODE_ID'],
                        columns=['admission_status'],
                        values=['Admissions_Week']
                        )


# function returns status for week
def f_status(field, data_frame, n):
    f_week = (lambda df: 1
              if ((df[('Admissions_Week', field)] <= n) &
                  (df[('Admissions_Week', 'Canceled')] > n))
              else 0
              )
    return data_frame.apply(f_week, axis=1)


# function returns DataFrame of 53 week status values
def fill_weeks(field, data_frame):
    weeks = range(1, 54)
    fld = field[:2]
    r = pd.DataFrame(np.zeros((data_frame.shape[0], 53)),
                     index=data_frame.index,
                     columns=[f'{fld}{w:02d}' for w in weeks])
    for w in weeks:
        f = f'{fld}{w:02d}'
        r.loc[:, f] = f_status(field, data_frame, w)

    return r


stage_list = ['Applied', 'Accepted', 'Deposited']
p = pd.DataFrame()
for s in stage_list:
    p = pd.concat([p, fill_weeks(s, e)], axis=1)
