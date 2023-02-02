import re
import pandas as pd
import os


def extract_data(infile, dataframe):
    with open(infile, 'r') as f:
        data = f.read().strip().split('\n')
        cnd = None
        filename = None
        for row in data:
            # using regular expression to extract data from strings
            condition_regex1 = re.search(r"\s+Sav\sfile\s:\s(\S+)\.?s?a?v?\s+c?o?a?n?d?i?\s?\s?\.?(\d+)", row)
            condition_regex2 = re.search(r"Datafile\s:.+co?ndi?\s*?(\d+)", row)
            savfile_regex = re.search(r"\s+Sav\sfile\s:\s(\S+)\.sav", row)
            score_regex = re.search(r"\s+NS\s:\s+(\d).+JND\s:\s(\d+.\d?\d?)", row)
            if condition_regex1 is not None:
                filename, cnd = condition_regex1.groups()
            elif condition_regex2 is not None:
                cnd = condition_regex2.groups()[0]
            elif savfile_regex is not None:
                filename = savfile_regex.groups()[0]
            elif score_regex is not None:
                case, jnd = score_regex.groups()
                dataframe = pd.concat([dataframe, pd.DataFrame({
                    'Participant': participant,
                    'Part': part.replace(participant + ' - ', '').replace('p5 - ', '').replace('pp1- ', ''),
                    'Source': file,
                    'File': filename.replace('.sav', ''),
                    'Condition': cnd,
                    'Staircase': case,
                    'Score': jnd}, index=[0])])
            else:
                next
    return dataframe


if __name__ == '__main__':
    table = pd.DataFrame(columns=['Participant', 'Part', 'Source', 'File', 'Condition', 'Staircase', 'Score'])
    basedir = '/Users/ylka/Library/Mobile Documents/com~apple~CloudDocs/uni_work/raw_data_lange/DATA'
    for participant in os.listdir(basedir):
        if not participant.startswith('.'):
            for part in os.listdir(os.path.join(basedir, participant)):
                if not part.startswith('.'):
                    for file in os.listdir(os.path.join(basedir, participant, part)):
                        if not file.startswith('.'):
                            table = extract_data(os.path.join(basedir, participant, part, file), table)
    print(table)
    table.to_csv(os.path.join(basedir, '..', 'no_delay_extracted.csv'), index=False)
