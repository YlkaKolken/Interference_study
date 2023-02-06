import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
lti = pd.read_csv('/Users/ylka/desktop/dataset_experiment1_h1.csv')
lti = lti.dropna()

def numeric_experiment(x):
    if x == 'Delay':
        return 0
    elif x == 'No delay':
        return 1
    else:
        return x

lti['Experiment'] = lti['Experiment'].apply(numeric_experiment)

def numeric_time(y):
    if y == 'Early':
        return 0
    elif y == 'Late':
        return 1
    else:
        return y


lti['Time'] = lti['Time'].apply(numeric_time)

# Run LMER
md = smf.mixedlm("Experiment ~ Time", lti, groups=lti["Participant"], re_formula="~Score")
mdf = md.fit(method=["lbfgs"])
print(mdf.summary())