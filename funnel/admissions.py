import pandas as pd
import numpy as np
from datetime import datetime, date


# read VWSTAGERANKING.csv and drop unused fields
stgrnk = pd.read_csv('VWSTAGERANKING.csv')
stgrnk.drop(['code_table', 'MEDIUM_DESC',
             'Converted/Confirmed/Accepted/Require SepDate'],
            inplace=True, axis=1)

# read STAGEHISTORY.csv
stg_hist_dtype = {'PEOPLE_CODE_ID': str, 'ACADEMIC_YEAR': str,
                  'ACADEMIC_TERM': str, 'ACADEMIC_SESSION': str,
                  'FIELD_ID': np.int64}
date_cols = ['FIELD_DATE']
stg_hist = pd.read_csv('STAGEHISTORY.csv', dtype=stg_hist_dtype,
                       parse_dates=date_cols,
                       usecols=['PEOPLE_CODE_ID', 'ACADEMIC_YEAR',
                                'ACADEMIC_TERM', 'ACADEMIC_SESSION',
                                'FIELD_ID', 'FIELD_DATE'])
stg_hist['create_date'] = stg_hist['FIELD_DATE']
stage_data = pd.merge(stg_hist, stgrnk, left_on=['FIELD_ID'],
                      right_on=['STAGERANKING_ID'], how='left')
keep_fields = ['PEOPLE_CODE_ID', 'ACADEMIC_YEAR', 'ACADEMIC_TERM',
               'ACADEMIC_SESSION', 'field_name', 'field_value', 'create_date']
stage_data = stage_data.loc[~stage_data['create_date'].isnull(), keep_fields]

# Academic Data
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

adm_df = (adm_df.loc[(adm_df['ACADEMIC_TERM'].isin(['FALL', 'SPRING'])) &
                     (adm_df['ACADEMIC_SESSION'] == 'MAIN')]
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
                   'TRDP', 'TRPD', 'TRNS', 'WAIT']
adm_keep_cols = ['PEOPLE_CODE_ID', 'year_term', 'Admissions_Week',
                 'field_value']
adm_df = adm_df.loc[(adm_df['field_value'].isin(adm_keep_values)),
                    adm_keep_cols]

# admissions status table
admission_status = {'300': 'Applied', 'ACC': 'Accepted', 'ACXL': 'Canceled',
                    'CANC': 'Canceled', 'DEF': 'Canceled', 'DEFR': 'Canceled',
                    'DENY': 'Canceled', 'DPAC': 'Deposited',
                    'TRDP': 'Deposited', 'TRPD': 'Deposited',
                    'TRNS': 'Accepted', 'WAIT': 'Accepted'}
adm_stat = pd.DataFrame(list(admission_status.items()),
                        columns=['field_value', 'admission_status'])

adm_df1 = (pd.merge(adm_df, adm_stat, on=['field_value'], how='left')
           .drop(['field_value'], axis=1)
           .drop_duplicates(['PEOPLE_CODE_ID', 'year_term', 'Admissions_Week',
                             'admission_status'])
           )

adm_df1 = (adm_df1.sort_values(['year_term', 'PEOPLE_CODE_ID',
                                'Admissions_Week'])
           .drop_duplicates(['year_term', 'PEOPLE_CODE_ID',
                             'admission_status'],
                            keep='first')
           )
