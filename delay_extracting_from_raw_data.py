import re
import pandas as pd
import os


def extract_data(infile, dataframe):
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
                    'Source': file}, index=[0])])
            else:
                next
    return dataframe

if __name__ == '__main__':
    table = pd.DataFrame(columns=['Participant', 'Session', 'Condition', 'Staircase', 'Score', 'Source'])
    basedir = '/Users/ylka/Library/Mobile Documents/com~apple~CloudDocs/uni_work/raw_data_superlti/DATA_superlti'
    for participant in os.listdir(basedir):
        if os.path.isdir(os.path.join(basedir, participant)):
            for part in os.listdir(os.path.join(basedir, participant)):
                if os.path.isdir(os.path.join(basedir, participant, part)):
                    for session in os.listdir(os.path.join(basedir, participant, part)):
                        if os.path.isdir(os.path.join(basedir, participant, part, session)):
                            for file in os.listdir(os.path.join(basedir, participant, part, session)):
                                searchresult = re.match(r'pp(\d+)_s(\d+)_c(\d+)_r(\d+).*.csv', file)
                                if searchresult is not None:
                                    pp, s, c, r = searchresult.groups()
                                    # print(pp, s, c, r)
                                    table = extract_data(os.path.join(basedir, participant, part, session, file), table)
table.to_csv(os.path.join(basedir, '..', 'data_raw_superlti.csv'), index=False)

