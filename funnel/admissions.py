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
date_cols = ['FIELD_DATE', 'REVISION_DATE', 'REVISION_TIME']
stg_hist = pd.read_csv('STAGEHISTORY.csv', dtype=stg_hist_dtype,
                       parse_dates=date_cols,
                       usecols=['PEOPLE_CODE_ID', 'ACADEMIC_YEAR',
                                'ACADEMIC_TERM', 'ACADEMIC_SESSION',
                                'FIELD_ID', 'FIELD_DATE', 'REVISION_DATE',
                                'REVISION_TIME'])
# create new fields
stg_hist['year_term'] = (stg_hist['ACADEMIC_YEAR'] + '.' +
                         stg_hist['ACADEMIC_TERM'].str.title())
# creation datetime
stg_hist['create_date'] = stg_hist['FIELD_DATE']
# convert ACADEMIC_YEAR to numeric keep numeric-valued records
stg_hist['ACADEMIC_YEAR'] = pd.to_numeric(stg_hist['ACADEMIC_YEAR'],
                                          errors='coerce', downcast='integer')
stg_hist = stg_hist.loc[pd.to_numeric(stg_hist['ACADEMIC_YEAR'],
                                      errors='coerce',
                                      downcast='integer'
                                      ).notnull()]
# drop unused fields
stg_hist.drop(['FIELD_DATE', 'REVISION_DATE', 'REVISION_TIME'],
              inplace=True, axis=1)
# calculate new fields
stg_hist['Week_Number'] = stg_hist['create_date'].dt.week
stg_hist['Admissions_Week'] = stg_hist.apply(lambda r: (r['Week_Number'] -
                                                        (date(int(
                                                         r['ACADEMIC_YEAR']),
                                                            9, 1
                                                        ).isocalendar()[1])
                                                        )
                                             if (r['Week_Number'] >
                                                 (date(int(r['ACADEMIC_YEAR']),
                                                       9, 1).isocalendar()[1]))
                                             else (53 + r['Week_Number'] -
                                                   (date(int(
                                                       r['ACADEMIC_YEAR']),
                                                    9, 1).isocalendar()[1])),
                                             axis=1)

stage_data = pd.merge(stg_hist, stgrnk, left_on=['FIELD_ID'],
                      right_on=['STAGERANKING_ID'], how='left')

ad_keep_values = ['300', 'ACC', 'ACXL', 'CANC', 'DEF', 'DEFR', 'DENY', 'DPAC',
                  'TRDP', 'TRPD', 'TRNS', 'WAIT']
ad_keep_cols = ['PEOPLE_CODE_ID', 'year_term', 'Admissions_Week',
                'field_value', 'status']
sd1 = stage_data.loc[(stage_data['field_value'].isin(ad_keep_values))]
sd1 = sd1[ad_keep_cols]

admission_status = {'300': 'Applied', 'ACC': 'Accepted', 'ACXL': 'Canceled',
                    'CANC': 'Canceled', 'DEF': 'Canceled', 'DEFR': 'Canceled',
                    'DENY': 'Canceled', 'DPAC': 'Deposited',
                    'TRDP': 'Deposited', 'TRPD': 'Deposited',
                    'TRNS': 'Accepted', 'WAIT': 'Accepted'}
adm_stat = pd.DataFrame(list(admission_status.items()),
                        columns=['field_value', 'admission_status'])

sd1 = (pd.merge(sd1, adm_stat, on=['field_value'], how='left')
       .drop(['field_value', 'status'], axis=1)
       .drop_duplicates(['PEOPLE_CODE_ID', 'year_term', 'Admissions_Week',
                         'admission_status'])
       .reset_index()
       .set_index(['year_term', 'PEOPLE_CODE_ID', 'admission_status'])
       .drop(['index'], axis=1)
       )

# Academic Data
academic_dtype = {'PEOPLE_CODE_ID': str, 'ACADEMIC_YEAR': str,
                  'ACADEMIC_TERM': str, 'ACADEMIC_SESSION': str,
                  'APPLICATION_FLAG': str, 'APP_STATUS': str}
date_cols = ['APPLICATION_DATE', 'APP_STATUS_DATE', 'APP_DECISION_DATE',
             'REVISION_DATE', 'REVISION_TIME']
academic = pd.read_csv('ACADEMIC.csv', dtype=academic_dtype,
                       parse_dates=date_cols,
                       usecols=['PEOPLE_CODE_ID',
                                'ACADEMIC_YEAR', 'ACADEMIC_TERM',
                                'ACADEMIC_SESSION', 'POPULATION',
                                'INQUIRY_FLAG',
                                'APPLICATION_FLAG', 'APPLICATION_DATE',
                                'APP_STATUS', 'APP_STATUS_DATE',
                                'APP_DECISION', 'APP_DECISION_DATE',
                                'REVISION_DATE', 'REVISION_TIME'])

app_data = (academic.loc[~(academic['POPULATION'].isin(['ADVSTU', 'NOND'])) &
                         ((academic['INQUIRY_FLAG'] == 'Y') |
                          (academic['APPLICATION_FLAG'] == 'Y'))]
            )

applied = (app_data[app_data['APP_STATUS'].notnull()]
           .rename(columns={'APP_STATUS': 'field_value'})
           .rename(columns={'APP_STATUS_DATE': 'Revision'})
           )
applied.loc[:, 'field_name'] = 'Application Status'

accepted = (app_data[app_data['APP_DECISION'].notnull()]
            .rename(columns={'APP_DECISION': 'field_value'})
            .rename(columns={'APP_DECISION_DATE': 'Revision'})
            )
accepted.loc[:, 'field_name'] = 'Application Decision'

# stack Stage History, Academic Applied and Academic Accepted
adm_df = applied.append(accepted)
