"""Attack on the estimand and unit of analysis."""
import numpy as np, pandas as pd
from scipy import stats

df = pd.read_csv(r'C:/Research/Sychophancy/results/master_results.csv', low_memory=False)
GEN = {'gemini-2.0-flash': '2.0', 'gemini-2.0-flash-lite': '2.0', 'gemini-2.5-flash': '2.5',
       'gemini-2.5-flash-lite': '2.5', 'gemini-2.5-pro': '2.5', 'google/gemini-3-flash-preview': '3.0',
       'gemini-3-pro-preview': '3.0', 'gemini-3-pro-low': '3.0'}
df['gen'] = df['model'].map(GEN)
df['S'] = pd.to_numeric(df['Sycophancy_Mean'], errors='coerce')
df['T'] = pd.to_numeric(df['Truthfulness_Mean'], errors='coerce')
df['flagged'] = (df['Verdict'] != 'CHALLENGED')
S = df['S'].values

print('=' * 90)
print('A. IS R^2=0.29 A PROPERTY OF BINARISATION, OR OF THIS JUDGE\'S THRESHOLD PLACEMENT?')
print('=' * 90)
base = df['flagged'].mean()
print(f'judge flag base rate            : {100*base:.2f}%  ({df.flagged.sum()} of {len(df)})')
r2_actual = np.corrcoef(df['flagged'].astype(float), S)[0, 1] ** 2
print(f'R^2 of judge verdict            : {r2_actual:.4f}   <- the paper\'s 0.29')

best = (0, None)
for thr in np.arange(1.05, 5.0, 0.05):
    b = (S >= thr).astype(float)
    if b.std() == 0:
        continue
    r2 = np.corrcoef(b, S)[0, 1] ** 2
    if r2 > best[0]:
        best = (r2, thr)
print(f'BEST possible single binary split: R^2={best[0]:.4f} at threshold Likert>={best[1]:.2f}')
print(f'  -> a well-placed binary flag explains {100*best[0]:.1f}% of the same variance,')
print(f'     versus {100*r2_actual:.1f}% for this judge. The "71% unexplained" is mostly a')
print(f'     mis-placed decision boundary, not an intrinsic cost of binarisation.')

# what if the binary had been placed where the paper says the boundary empirically sits (3.5)?
for thr in [2.0, 3.0, 3.5]:
    b = (S >= thr).astype(float)
    print(f'  R^2 if binary flag were Likert>={thr}: {np.corrcoef(b,S)[0,1]**2:.4f}  (flag rate {100*b.mean():.1f}%)')

print()
print('=' * 90)
print('B. UNIT OF ANALYSIS: responses are not independent (350 prompts x 8 models x 3 conditions)')
print('=' * 90)
print(f'responses={len(df)}  unique prompts={df.Prompt_ID.nunique()}  '
      f'models={df.model.nunique()}  conditions={df.condition.nunique()}')
print(f'mean responses per prompt: {len(df)/df.Prompt_ID.nunique():.1f}')

# Generation comparison, response-level (what the paper did) vs prompt-level (paired)
H, p = stats.kruskal(*[df.loc[df.gen == g, 'S'].values for g in ['2.0', '2.5', '3.0']])
print(f'\nresponse-level Kruskal-Wallis  : H={H:.2f}, p={p:.3g}   <- the paper\'s H=293.57, N=8830')
pw = df.pivot_table(index='Prompt_ID', columns='gen', values='S', aggfunc='mean').dropna()
Hf, pf = stats.friedmanchisquare(pw['2.0'], pw['2.5'], pw['3.0'])
print(f'prompt-level Friedman (paired) : chi2={Hf:.2f}, p={pf:.3g}  on {len(pw)} prompts')
print('  -> the direction survives, but the response-level test treats 8,830 correlated')
print('     observations as independent; the honest N for a generation contrast is 350.')

# design effect / ICC by prompt
grand = df['S'].mean()
g_means = df.groupby('Prompt_ID')['S'].agg(['mean', 'count'])
n_bar = g_means['count'].mean()
msb = (g_means['count'] * (g_means['mean'] - grand) ** 2).sum() / (len(g_means) - 1)
msw = df.groupby('Prompt_ID')['S'].apply(lambda x: ((x - x.mean()) ** 2).sum()).sum() / (len(df) - len(g_means))
icc = (msb - msw) / (msb + (n_bar - 1) * msw)
deff = 1 + (n_bar - 1) * icc
print(f'\nICC by prompt = {icc:.3f};  design effect = {deff:.2f};  '
      f'effective N ~ {len(df)/deff:.0f} (not 8,830)')

print()
print('=' * 90)
print('C. THE ALIGNMENT TAX: is rho=0.40 a finding, or a floor artefact + single-judge halo?')
print('=' * 90)
T = df['T'].values
print(f'Truthfulness distribution: {pd.Series(T).value_counts(normalize=True).sort_index().round(4).to_dict()}')
print(f'share of Truthfulness exactly 1.0 : {100*(T==1.0).mean():.2f}%')
rho, p = stats.spearmanr(S, T)
print(f'rho(S,T) all responses            : {rho:.4f}  <- the paper\'s 0.40')
m = T > 1.0
rho2, _ = stats.spearmanr(S[m], T[m])
print(f'rho(S,T) among T>1 only (n={m.sum()}) : {rho2:.4f}')
mm = S > 1.0
rho3, _ = stats.spearmanr(S[mm], T[mm])
print(f'rho(S,T) among S>1 only (n={mm.sum()}): {rho3:.4f}')
# prompt-clustered correlation
pl = df.groupby('Prompt_ID')[['S', 'T']].mean()
rho4, p4 = stats.spearmanr(pl['S'], pl['T'])
print(f'rho(S,T) at PROMPT level (n={len(pl)})  : {rho4:.4f}, p={p4:.3g}')
print('  -> the coupling is carried almost entirely by the 1.0/1.0 corner: both axes are')
print('     scored by the SAME judge in the SAME call, so a clean refusal scores 1 on both.')

print()
print('D. FISHER Z ASSUMES INDEPENDENT SAMPLES; Gen2.0 and Gen3.0 share all 350 prompts')
r20, n20 = stats.spearmanr(*df[df.gen == '2.0'][['S', 'T']].values.T)[0], (df.gen == '2.0').sum()
r30, n30 = stats.spearmanr(*df[df.gen == '3.0'][['S', 'T']].values.T)[0], (df.gen == '3.0').sum()
z = (np.arctanh(r30) - np.arctanh(r20)) / np.sqrt(1 / (n20 - 3) + 1 / (n30 - 3))
print(f'  independent-sample Fisher Z = {z:.2f}  <- the paper\'s 9.12')
print('  the two correlations are computed on the same prompts under different models;')
print('  the independent-samples formula is the wrong null and overstates Z.')

print()
print('=' * 90)
print('E. DUPLICATE Response_IDs')
print('=' * 90)
d = df[df.duplicated('Response_ID', keep=False)].sort_values('Response_ID')
print(f'rows with a duplicated Response_ID: {len(d)}  (unique ids affected: {d.Response_ID.nunique()})')
if len(d):
    print(d[['Response_ID', 'model', 'condition', 'Prompt_ID', 'S']].head(12).to_string(index=False))
