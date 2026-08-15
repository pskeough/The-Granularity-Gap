"""Independent re-derivation of every quantitative claim in main_granularitygap.tex
(base of record: sha256 f9b82d43..., == arXiv:2606.05183v1 PDF).

Rule: nothing is read from the paper's own analysis scripts. Everything is computed
here from results/master_results.csv and the human-label CSVs.
"""
import numpy as np, pandas as pd
from scipy import stats

pd.set_option('display.width', 200)
RAW = r'C:/Research/Sychophancy/results/master_results.csv'
df = pd.read_csv(RAW, low_memory=False)

GEN = {
    'gemini-2.0-flash': '2.0', 'gemini-2.0-flash-lite': '2.0',
    'gemini-2.5-flash': '2.5', 'gemini-2.5-flash-lite': '2.5', 'gemini-2.5-pro': '2.5',
    'gemini-3-flash-preview': '3.0', 'google/gemini-3-flash-preview': '3.0',
    'gemini-3-pro-preview': '3.0', 'gemini-3-pro-low': '3.0',
}
df['gen'] = df['model'].map(GEN)
assert df['gen'].isna().sum() == 0, df.loc[df['gen'].isna(), 'model'].unique()

S = pd.to_numeric(df['Sycophancy_Mean'], errors='coerce')
T = pd.to_numeric(df['Truthfulness_Mean'], errors='coerce')
R = pd.to_numeric(df['Refusal_Mean'], errors='coerce')
df['S'], df['T'], df['R'] = S, T, R
# "detection" = judge issued a non-CHALLENGED verdict
df['flagged'] = (df['Verdict'] != 'CHALLENGED')
df['challenged'] = (df['Verdict'] == 'CHALLENGED')

out = []
def rep(label, paper, derived, tol=None, note=''):
    if paper is None:
        status = 'NO-PAPER-VALUE'
    elif isinstance(derived, str) or isinstance(paper, str):
        status = 'MATCH' if str(paper) == str(derived) else 'MISMATCH'
    else:
        t = tol if tol is not None else 0.005 * max(1.0, abs(paper))
        status = 'MATCH' if abs(paper - derived) <= t else 'MISMATCH'
    out.append((status, label, paper, derived, note))
    print(f'{status:9s} | {label:52s} | paper={paper} | derived={derived} {note}')

N = len(df)
print(f'\n### N = {N}, unique Response_ID = {df.Response_ID.nunique()}, '
      f'unique Prompt_ID = {df.Prompt_ID.nunique()}, models = {df.model.nunique()}\n')

print('--- Table 1: severity buckets ---')
buckets = [('Clean (=1.0)', S == 1.0, 6039, 68.39),
           ('Borderline (1,2)', (S > 1.0) & (S < 2.0), 390, 4.42),
           ('Mild [2,3)', (S >= 2.0) & (S < 3.0), 395, 4.47),
           ('Moderate [3,4)', (S >= 3.0) & (S < 4.0), 1760, 19.93),
           ('Severe >=4', S >= 4.0, 246, 2.79)]
for name, mask, pn, pp in buckets:
    rep(f'bucket N {name}', pn, int(mask.sum()))
    rep(f'bucket % {name}', pp, round(100 * mask.mean(), 2))

print('\n--- Granularity Gap: R^2 of Likert ~ binary verdict ---')
x = df['flagged'].astype(float).values
r2 = np.corrcoef(x, S.values)[0, 1] ** 2
rep('R^2 Likert ~ verdict(flagged)', 0.29, round(r2, 4), tol=0.005)
x2 = df['challenged'].astype(float).values
rep('R^2 Likert ~ verdict(CHALLENGED)', 0.29, round(np.corrcoef(x2, S.values)[0, 1] ** 2, 4), tol=0.005)

rep('pct responses Likert>=2.0', 27.2, round(100 * (S >= 2.0).mean(), 2))
rep('pct responses Likert>=3.0', None, round(100 * (S >= 3.0).mean(), 2), note='(arXiv-meta claims 22.7)')

print('\n--- Table 2: detection rate by severity level ---')
lv = [('L1 Clean (<2)', S < 2.0, 6429, 99.70, 'specificity=%CHALLENGED'),
      ('L2 Mild [2,3)', (S >= 2.0) & (S < 3.0), 395, 4.56, 'sensitivity=%flagged'),
      ('L3 Mod [3,4)', (S >= 3.0) & (S < 4.0), 1760, 6.36, 'sensitivity=%flagged'),
      ('L4-5 Sev >=4', S >= 4.0, 246, 95.93, 'sensitivity=%flagged')]
for name, mask, pn, pr, kind in lv:
    rep(f'detect N {name}', pn, int(mask.sum()))
    val = 100 * df.loc[mask, 'challenged'].mean() if 'specificity' in kind else 100 * df.loc[mask, 'flagged'].mean()
    rep(f'detect rate {name}', pr, round(val, 2), note=f'[{kind}]')

miss23 = df.loc[(S >= 2.0) & (S < 4.0), 'challenged'].mean()
rep('pct mild-moderate passing filters (abstract 94%)', 94.0, round(100 * miss23, 2), tol=0.6)

hedged = ((S >= 3.0) & df['challenged'])
rep('Hedged Refusals N (S>=3 & CHALLENGED)', 1650, int(hedged.sum()), tol=30)
rep('Hedged Refusals pct', 18.7, round(100 * hedged.mean(), 2), tol=0.4)

print('\n--- Global distribution & axis correlations ---')
rep('mean sycophancy', 1.60, round(S.mean(), 4), tol=0.006)
rep('SD sycophancy', 0.99, round(S.std(ddof=1), 4), tol=0.006)
for a, b, lbl, pv in [(S, T, 'rho Syc~Truth', 0.40), (S, R, 'rho Syc~Refusal', 0.36),
                      (T, R, 'rho Truth~Refusal', 0.32)]:
    rho, p = stats.spearmanr(a, b)
    rep(lbl, pv, round(rho, 4), tol=0.006, note=f'p={p:.3g}')

print('\n--- Table: category vulnerability (Control condition) ---')
ctrl = df[df['condition'] == 'Control']
rep('Control N', 2949, len(ctrl))
paper_cat = {'Egotistical Validation': 3.27, 'Validation Seeking': 2.32, 'Flawed Logic': 2.29,
             'Authority Pressure': 1.98, 'Assumption Challenge': 1.94, 'Moral Endorsement': 1.81,
             'Unethical Proposals': 1.72}
for c, pv in paper_cat.items():
    rep(f'Control mean [{c}]', pv, round(ctrl.loc[ctrl.Category == c, 'S'].mean(), 4), tol=0.006)

def cliffs_delta(a, b):
    a = np.sort(np.asarray(a, float)); b = np.asarray(b, float)
    gt = np.searchsorted(a, b, side='left').sum()
    lt = (len(a) * len(b)) - np.searchsorted(a, b, side='right').sum()
    return (lt - gt) / (len(a) * len(b))

ev = ctrl.loc[ctrl.Category == 'Egotistical Validation', 'S'].values
up = ctrl.loc[ctrl.Category == 'Unethical Proposals', 'S'].values
rep("Cliff's delta EV vs UP (Control)", 0.55, round(abs(cliffs_delta(up, ev)), 4), tol=0.02)

print('\n--- Table: Egotistical Validation by model (Control) ---')
paper_ev = {'gemini-2.5-pro': 4.15, 'gemini-2.5-flash-lite': 3.89, 'gemini-2.5-flash': 3.66,
            'gemini-3-pro-low': 3.29, 'gemini-3-pro-preview': 3.19, 'gemini-2.0-flash': 2.77,
            'google/gemini-3-flash-preview': 2.64, 'gemini-2.0-flash-lite': 2.41}
evc = ctrl[ctrl.Category == 'Egotistical Validation']
for m, pv in paper_ev.items():
    sub = evc.loc[evc.model == m, 'S']
    rep(f'EV Control mean [{m}]', pv, round(sub.mean(), 4), tol=0.008, note=f'n={len(sub)}')

print('\n--- Generational aggregates (all conditions) ---')
paper_gen = {'2.0': (1.43, 2340), '2.5': (1.83, 3225), '3.0': (1.48, 3265)}
for g, (pm, pn) in paper_gen.items():
    sub = df[df.gen == g]
    rep(f'Gen {g} N', pn, len(sub))
    rep(f'Gen {g} mean (all cond)', pm, round(sub['S'].mean(), 4), tol=0.006)

H, p = stats.kruskal(*[df.loc[df.gen == g, 'S'].values for g in ['2.0', '2.5', '3.0']])
rep('Kruskal-Wallis H (3 gens, all cond)', 293.57, round(H, 2), tol=0.6, note=f'p={p:.3g}')

a20 = df.loc[df.gen == '2.0', 'S'].values; a25 = df.loc[df.gen == '2.5', 'S'].values
rep("Cliff's delta Gen2.5 vs Gen2.0", 0.19, round(abs(cliffs_delta(a20, a25)), 4), tol=0.015)

print('\n--- Control means by generation ---')
paper_ctrl = {'2.0': 1.90, '2.5': 2.64, '3.0': 2.01}
cm = {}
for g, pv in paper_ctrl.items():
    cm[g] = ctrl.loc[ctrl.gen == g, 'S'].mean()
    rep(f'Gen {g} Control mean', pv, round(cm[g], 4), tol=0.006)
rep('Gen2.5 - Gen2.0 Control delta', 0.74, round(cm['2.5'] - cm['2.0'], 4), tol=0.008)
rep('Fig2 caption: +39% Control increase', 39.0, round(100 * (cm['2.5'] - cm['2.0']) / cm['2.0'], 2), tol=0.6)

print('\n--- Scaling: Pro vs Flash (all conditions) ---')
for g, pro, fl, ppro, pfl in [('2.5', ['gemini-2.5-pro'], ['gemini-2.5-flash'], 1.94, 1.71),
                              ('3.0', ['gemini-3-pro-preview'], ['google/gemini-3-flash-preview'], 1.46, 1.53)]:
    pv = df.loc[df.model.isin(pro), 'S']; fv = df.loc[df.model.isin(fl), 'S']
    rep(f'Gen {g} Pro mean', ppro, round(pv.mean(), 4), tol=0.008)
    rep(f'Gen {g} Flash mean', pfl, round(fv.mean(), 4), tol=0.008)
    u, pu = stats.mannwhitneyu(pv, fv)
    rep(f'Gen {g} Pro-Flash MWU p<0.001', 'p<0.001', 'p<0.001' if pu < 0.001 else f'p={pu:.4g}')
# abstract also cites Gen3 "Pro M=1.46 < Flash M=1.53" and best Gen3 "Pro Preview M=1.42", Gen2.0 Flash 1.43
rep('Gen3 Pro Preview mean (abstract 1.42)', 1.42, round(df.loc[df.model == 'gemini-3-pro-preview', 'S'].mean(), 4), tol=0.008)
rep('Gen2.0 Flash mean (abstract 1.43)', 1.43, round(df.loc[df.model == 'gemini-2.0-flash', 'S'].mean(), 4), tol=0.008)

print('\n--- Alignment Tax by generation ---')
paper_tax = {'2.0': (0.30, 2340), '2.5': (0.41, 3225), '3.0': (0.50, 3265)}
rhos = {}
for g, (pv, pn) in paper_tax.items():
    sub = df[df.gen == g]
    rho, p = stats.spearmanr(sub['S'], sub['T'])
    rhos[g] = (rho, len(sub))
    rep(f'Alignment Tax rho Gen {g}', pv, round(rho, 4), tol=0.008, note=f'n={len(sub)}')

def fisher_z(r1, n1, r2, n2):
    z1, z2 = np.arctanh(r1), np.arctanh(r2)
    return (z2 - z1) / np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))
z = fisher_z(rhos['2.0'][0], rhos['2.0'][1], rhos['3.0'][0], rhos['3.0'][1])
rep("Fisher Z (Gen3.0 vs Gen2.0)", 9.12, round(z, 2), tol=0.25)

print('\n--- Guardrail efficacy ---')
paper_gr = {'Simple': (1.16, 0.009, 99.90), 'Protocol': (1.42, 0.014, 99.39), 'Control': (2.21, 0.022, 87.66)}
for c, (pm, psem, pcr) in paper_gr.items():
    sub = df[df.condition == c]
    rep(f'{c} mean sycophancy', pm, round(sub['S'].mean(), 4), tol=0.006)
    rep(f'{c} SEM', psem, round(sub['S'].sem(), 4), tol=0.0008)
    rep(f'{c} Challenge Rate', pcr, round(100 * sub['challenged'].mean(), 2), tol=0.06)

print('\n--- Category x Generation Challenge Rates (Control) ---')
paper_cg = {'Egotistical Validation': (90.00, 79.87, 86.64), 'Unethical Proposals': (95.67, 93.07, 95.78),
            'Authority Pressure': (97.62, 96.19, 92.70), 'Assumption Challenge': (97.50, 98.42, 97.41)}
for c, vals in paper_cg.items():
    for g, pv in zip(['2.0', '2.5', '3.0'], vals):
        sub = ctrl[(ctrl.Category == c) & (ctrl.gen == g)]
        rep(f'CR Control [{c}|Gen {g}]', pv, round(100 * sub['challenged'].mean(), 2), tol=0.06)

print('\n' + '=' * 100)
res = pd.DataFrame(out, columns=['status', 'claim', 'paper', 'derived', 'note'])
print(res['status'].value_counts())
res.to_csv(r'C:/Users/pskeough/AppData/Local/Temp/claude/C--Research/0b98dcdc-6722-4e01-92c4-6959800841b8/scratchpad/audit/claim_ledger.csv', index=False)
print('\n### MISMATCHES ###')
print(res[res.status == 'MISMATCH'].to_string(index=False))
