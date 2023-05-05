import re
import pandas as pd
import numpy as np
import math
import os
from dotenv import dotenv_values
from pandas.errors import EmptyDataError, ParserError

BASEDIR_NODELAY = dotenv_values('.env')['BASEDIR_NODELAY']
BASEDIR_DELAY = dotenv_values('.env')['BASEDIR_DELAY']
CSV_STOREDIR = dotenv_values('.env')['CSV_STOREDIR']

group = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
oriincrement = [0.2, 0.4, 0.6, 0.8, 1.0, 1.20, 1.42, 1.68, 2.02, 2.42, 2.91, 3.49, 4.19, 5.02, 6.03, 7.23, 8.68, 10.4, 12.5, 15.0, 18.0, 21.6, 25.9, 31.1, 37.3, 44.8]
translateOriincrement = pd.DataFrame({'oriincrementid': group, 'oriincrement': oriincrement})

def extract_nodelay_data(infile, dataframe):    
    with open(infile, 'r') as f:
        data = f.read().strip().split('\n')
        # print(data)
        cnd = None
        filename = None
        for row in data:
            # using regular expression to extract data from strings
            condition_regex1 = re.search(r"\s+Sav\sfile\s:\s(\S+)\.?s?a?v?\s+c?o?a?n?d?i?\s?\s?\.?(\d+)", row)
            condition_regex2 = re.search(r"Datafile\s:.+co?ndi?\s*?(\d+)", row)
            savfile_regex = re.search(r"\s+Sav\sfile\s:\s(\S+)\.sav", row)
            score_regex = re.search(r"\s?+NS\s:\s+(\d).+JND\s:\s(\d+.\d?\d?)", row)
            
            if condition_regex1 is not None:
                filename, cnd = condition_regex1.groups()
            elif condition_regex2 is not None:
                cnd = condition_regex2.groups()[0]
            elif savfile_regex is not None:
                filename = savfile_regex.groups()[0]
            elif score_regex is not None:
                case, jnd = score_regex.groups()
            elif row.strip().startswith('Rps: '):
                df = pd.DataFrame([x for x in re.sub(' +',' ',row.strip().removeprefix('Rps:').strip()).split(' ')], columns=['oriincrementid']).astype('int')
                df = df.merge(translateOriincrement, on='oriincrementid', how='left')
                df['logn'] = df['oriincrement'].apply(float).apply(np.log)
                value = math.exp(df.logn.iloc[-10:].mean())
                points = df.logn.iloc[-10:].count()
                dataframe = pd.concat([dataframe, pd.DataFrame({
                    'Participant': participant.replace('pp', ''),
                    'Session': file.split('.')[-1],
                    # 'Part': part.replace(participant + ' - ', '').replace('p5 - ', '').replace('pp1- ', ''),
                    'Source': file,
                    # 'File': filename.replace('.sav', ''),
                    'Condition': cnd,
                    'Staircase': case,
                    'Score': jnd,
                    'Value': value,
                    'Points': points,
                    'Delay/No delay': 'No delay'}, index=[0])])
                # except (ValueError, UnboundLocalError):
                #     print(infile)
                    
    return dataframe


def extract_delay_data(infile, dataframe):
    try:
        df = pd.read_csv(infile, header=1)
        df['match'] = df.oriincrement.eq(df.oriincrement.shift())
        df = df[(df.match == False) & (df.targetSide.isin([-1,1]))].iloc[-10:]
        try:
            df['logn'] = df['oriincrement'].apply(float).apply(np.log)
            value = math.exp(df.logn.mean())
        except ValueError:
            print(infile)
            value = 'ValueError'
    except EmptyDataError:
        value = 'EmptyDataError'
    except ParserError:
        value = 'ParseError'
    
    with open(infile, 'r') as f:
        data = f.read().strip().split('\n')
        cnd = None
        for row in data:
            condition_regex1 = re.search(r'.*geometric=(\d+.\d*),*', row)
            if condition_regex1 is not None:
                cnd = condition_regex1.groups()
                dataframe = pd.concat([dataframe, pd.DataFrame({
                    'Participant': pp,
                    'Session': s,
                    'Condition': c,
                    'Staircase': r,
                    'Score': cnd,
                    'Value': value,
                    'Source': file,
                    'Delay/No delay': 'Delay'}, index=[0])])
            else:
                continue
    return dataframe

table = pd.DataFrame(columns=['Participant', 'Session', 'Source', 'File', 'Condition', 'Staircase', 'Score', 'Value', 'Points'])

# NO DELAY
for participant in os.listdir(BASEDIR_NODELAY):
    if not participant.startswith('.'):
        for part in os.listdir(os.path.join(BASEDIR_NODELAY, participant)):
            if not part.startswith('.'):
                for file in os.listdir(os.path.join(BASEDIR_NODELAY, participant, part)):
                    if not file.startswith('.'):
                        table = extract_nodelay_data(os.path.join(BASEDIR_NODELAY, participant, part, file), table)


# DELAY
# counter = 0
# for participant in os.listdir(BASEDIR_DELAY):
#     if os.path.isdir(os.path.join(BASEDIR_DELAY, participant)):
#         for part in os.listdir(os.path.join(BASEDIR_DELAY, participant)):
#             if os.path.isdir(os.path.join(BASEDIR_DELAY, participant, part)):
#                 for session in os.listdir(os.path.join(BASEDIR_DELAY, participant, part)):
#                     if os.path.isdir(os.path.join(BASEDIR_DELAY, participant, part, session)):
#                         for file in os.listdir(os.path.join(BASEDIR_DELAY, participant, part, session)):
#                             searchresult = re.match(r'pp(\d+)_s(\d+)_c(\d+)_r(\d+).*.csv', file.lower())
#                             if searchresult is not None:
#                                 pp, s, c, r = searchresult.groups()
#                                 table = extract_delay_data(
#                                     os.path.join(BASEDIR_DELAY, participant, part, session, file), table)
#                             elif '.csv' in file:
#                                 # print(file)
#                                 counter += 1
# print(counter)

experiment = pd.DataFrame({'Condition': ['12', '12', '16', '135', '15'],
                           'Delay/No delay': ['No delay', 'Delay', 'Delay', 'Delay', 'No delay'],
                           'Experiment': ['1', '1', '1', '1', '1']})

early_late = pd.DataFrame({'Session': ['1', '2', '3', '13', '14', '15'],
                           'Early/Late': ['Early', 'Early', 'Early', 'Late', 'Late', 'Late']})

table = table.merge(experiment, on=['Condition', 'Delay/No delay'], how='right')
table = table.merge(early_late, on='Session', how='right')

table.to_csv(os.path.join(CSV_STOREDIR, 'EXTRACTED_20230505.csv'), index=False, decimal=',')

#print(table)

