#!/usr/bin/env python3
"""Figure 2: manifest-bound no-defector noise comparisons; no paid API calls."""
import argparse
import collections
import copy
import csv
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.experiment_condition import read_final_run, condition_from_run, output_provenance
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

MODELS=['openai/gpt-5-nano','google/gemini-3.7-flash','anthropic/claude-sonnet-4.5']
LABELS=['GPT-5 Nano','Gemini 3.7 Flash','Claude Sonnet 4.5']
ORDERS=['game','game_myth','myth_game']
ORDER_LABELS=['Game only','Game → Myth','Myth → Game']
NOISES=['no_noise','noise_uninformed','noise_informed']
NOISE_LABELS=['No noise','Noise\n(uninformed)','Noise\n(informed)']
BOX_COLORS=['#999999','#e99675','#72b6a1']
DOT_COLORS=['#777777','#fc8d62','#66c2a5']
NOISE_COLORS=['#4C72B0','#DD8452','#55A868']

def write_csv(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def inputs():
    receipt=json.loads((ROOT/'data/json/noise_experiments/figure2_no_defectors_20260915/completion_receipt.json').read_text())
    hashes={r['path']:r['sha256'] for r in receipt['finals']}
    old=json.loads((ROOT/'docs/figures/negative_only_crossmodel_reasoning_rerun_20260909_resources_boxplots/provenance.json').read_text())
    old_hashes={r['path']:r['sha256'] for r in old['runs']}
    with (ROOT/'docs/figures/negative_only_crossmodel_reasoning_rerun_20260909/run_manifest.csv').open() as f:
        for r in csv.DictReader(f):
            if r['treatment']=='control':hashes[r['path']]=old_hashes[r['path']]
    assert len(hashes)==270
    rows=[];sources=[];matched={};implementations=collections.defaultdict(set)
    for path,sha in hashes.items():
        p=ROOT/path;assert hashlib.sha256(p.read_bytes()).hexdigest()==sha,path
        d=read_final_run(p);condition=condition_from_run(d);m=d['run_metadata']
        assert m['num_turns']==10 and m['defector_count']==0 and m['random_defection_probability']==0
        assert not m['punishment_enabled'] and m['noise_semantics']=='communication'
        for k,v in condition['implementation'].items():implementations[k].add(v)
        noise=m['noise_config']
        if not noise:n='no_noise'
        else:
            assert noise==dict(type='uniform',range=1.0,direction='negative',applies_to='both',inform_agents=noise['inform_agents'])
            n='noise_informed' if noise['inform_agents'] else 'noise_uninformed'
        order='_'.join(d['task_order']); key=(m['model'],m['num_agents'],order,m['replicate_id'])
        ci=copy.deepcopy(m['comparison_inputs']);ci['game_params'].pop('noise_config')
        if key in matched:assert ci==matched[key],(path,'non-noise input difference')
        else:matched[key]=ci
        rounds=d['conversation_history'];assert [r['round'] for r in rounds]==list(range(1,11))
        balances=rounds[-1]['balances'];assert len(balances)==m['num_agents']
        v=float(np.mean(list(balances.values())));assert np.isfinite(v)
        rows.append(dict(model=m['model'],num_agents=m['num_agents'],noise=n,task_order=order,replicate=m['replicate_id'],resources=v,pairing_seed=m['pairing_seed'],noise_seed=m['noise_seed'],source_path=path))
        sources.append(dict(path=path,sha256=sha,code_commit=m['code_commit'],condition_sha256=m['condition_sha256']))
    varied={k:sorted(v) for k,v in implementations.items() if len(v)>1}
    assert set(varied)<= {'src/utils.py','src/experiment_condition.py'},varied
    return rows,sources,varied

def write_provenance(out, sources, varied):
    previous = json.loads((ROOT / 'docs/figures/negative_only_crossmodel_reasoning_rerun_20260909_resources_boxplots/provenance.json').read_text())
    allowed = {key: reason for key, reason in previous['allowed_differences'].items()
               if not reason.startswith('Forced-defection treatment')}
    allowed.update({
        'protocol.game.game_prompt_addition': 'Myth task orders instruct agents to take myths into account; game-only runs omit that instruction.',
        'protocol.game.noise_config': 'Noise regime (none, uninformed, informed) is a design factor; matched comparison inputs differ only in noise_config.',
        'implementation.src/utils.py': 'Provider billing-retry fix stops retries on exhausted credits; completed-run requests, prompts, and simulation behavior are unchanged.',
    })
    outputs = sorted(path for path in out.rglob('*')
                     if path.is_file() and path != out / 'provenance.json')
    document = output_provenance(
        [ROOT / source['path'] for source in sources], outputs,
        allowed_differences=allowed, output_root=out,
    )
    for run, source in zip(document['runs'], sources):
        assert run['sha256'] == source['sha256'], source['path']
        run.update(source)
    document.update(
        implementation_differences=varied,
        comparison='Within each model/population/order/replicate only noise_config differs in comparison_inputs',
        bootstrap='Exact enumeration of 3125 paired five-run resamples; percentile 95% intervals; descriptive, unadjusted',
        script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    )
    (out / 'provenance.json').write_text(json.dumps(document, indent=2) + '\n')


def style(ax):
    ax.set_axisbelow(True);ax.grid(axis='y',alpha=.22);ax.spines[['top','right']].set_visible(False)

def save(fig,out,name):
    for ext in ['png','svg','pdf']:fig.savefig(out/f'{name}.{ext}',dpi=200,bbox_inches='tight')
    plt.close(fig)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=ROOT/'docs/figures/figure2_noise_comparison_20260916');ap.add_argument('--box-layout',choices=['two_columns','six_rows','population','separate'],default='two_columns');a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    rows,sources,varied=inputs();cells=collections.defaultdict(list)
    for r in rows:cells[(r['model'],r['num_agents'],r['noise'],r['task_order'])].append(r)
    assert len(cells)==54
    for cell in cells.values():
        cell.sort(key=lambda r:r['replicate']);assert [r['replicate'] for r in cell]==list(range(5))
    def values(m,n,z,o):return np.array([r['resources'] for r in cells[(m,n,z,o)]])
    layouts={'two_columns':[(n,m,l) for m,l in zip(MODELS,LABELS) for n in [2,8]],'six_rows':[(n,m,l) for n in [2,8] for m,l in zip(MODELS,LABELS)],'population':[(8,m,l) for m,l in zip(MODELS,LABELS)]}
    for z,title in [('no_noise','No noise'),('noise_uninformed','Uninformed negative-only noise')]:
        groups=[('',layouts[a.box_layout])] if a.box_layout!='separate' else [(f'_{n}agent',[(n,m,l) for m,l in zip(MODELS,LABELS)]) for n in [2,8]]
        for suffix,panels in groups:
            two_columns=a.box_layout=='two_columns'
            fig,axes=plt.subplots(3 if two_columns else len(panels),2 if two_columns else 1,figsize=(12,9) if two_columns else (7.6,2.25*len(panels)+1),sharey=True,squeeze=False)
            for ax,(n,m,label) in zip(axes.flat,panels):
                for pos,o in enumerate(ORDERS,1):
                    v=values(m,n,z,o)
                    ax.boxplot(v,positions=[pos],widths=.52,patch_artist=True,showfliers=False,whis=1.5,boxprops=dict(facecolor=BOX_COLORS[pos-1],edgecolor='#666666'),medianprops=dict(color='#222222',linewidth=1.6),whiskerprops=dict(color='#666666'),capprops=dict(color='#666666'))
                    ax.scatter(pos+np.linspace(-.1,.1,5),v,s=30,c=DOT_COLORS[pos-1],edgecolors='white',linewidths=.6,zorder=3)
                ax.set_xticks([1,2,3],ORDER_LABELS);ax.set_xlim(.5,3.5);ax.set_ylim(0,80);style(ax)
                if two_columns:
                    if n==2: ax.set_ylabel(label,fontsize=12,fontweight='bold',labelpad=12)
                    if m==MODELS[0]: ax.set_title(f'{n} agents',fontsize=13,fontweight='bold',loc='center',pad=12)
                else:
                    ax.set_title(f'{n} agents',fontsize=12,fontweight='bold',loc='center');ax.set_ylabel(label,fontsize=12,fontweight='bold')
            fig.suptitle(f'Final cumulative resources\n{title} · No defectors · Round 10',fontsize=15,fontweight='bold')
            fig.text(.5,.012,'Each dot = one run (n = 5 per box)\nBox = middle 50% · Line = median · Whiskers = up to 1.5 × IQR',ha='center',fontsize=9,color='#444444')
            fig.supylabel('Cumulative resources per agent',fontsize=12,x=.012)
            fig.tight_layout(rect=(.035,.055,1,.94),h_pad=1.8,w_pad=2);save(fig,a.out,f'boxplots_{z}{suffix}')
    # Seaborn summary with a shared neutral-to-teal resource scale.
    import seaborn as sns
    with sns.axes_style('white'), sns.plotting_context('notebook',font_scale=1):
        fig, axes = plt.subplots(3,2,figsize=(11.8,8.2))
        cmap=sns.blend_palette(['#f1f1ef','#cbded7','#72b6a1'],as_cmap=True)
        for i,(model,label) in enumerate(zip(MODELS,LABELS)):
            for j,n in enumerate([2,8]):
                ax=axes[i,j]
                matrix=np.array([[np.median(values(model,n,z,o)) for z in NOISES] for o in ORDERS])
                sns.heatmap(matrix,ax=ax,cmap=cmap,vmin=25,vmax=75,
                            annot=True,fmt='.1f',annot_kws={'fontsize':12,'color':'#303c38'},
                            linewidths=2,linecolor='white',cbar=False,
                            xticklabels=['No noise','Uninformed','Informed'],
                            yticklabels=ORDER_LABELS if j==0 else False)
                ax.tick_params(axis='both',length=0,labelsize=10,pad=7)
                ax.set_xticklabels(ax.get_xticklabels(),rotation=0)
                ax.set_yticklabels(ax.get_yticklabels(),rotation=0)
                if j==0: ax.set_ylabel(label,fontsize=12,fontweight='semibold',labelpad=16,color='#333333')
                if i==0: ax.set_title(f'{n} agents',fontsize=13,fontweight='semibold',pad=14,color='#333333')
        fig.suptitle('Final resources across noise conditions',fontsize=18,fontweight='semibold',y=.975,color='#303030')
        fig.text(.55,.927,'No defectors · Round 10 · Median of 5 runs',ha='center',fontsize=11,color='#666666')
        fig.subplots_adjust(left=.205,right=.97,top=.85,bottom=.17,hspace=.36,wspace=.12)
        cax=fig.add_axes([.36,.075,.43,.017])
        bar=fig.colorbar(axes[0,0].collections[0],cax=cax,orientation='horizontal',ticks=[25,50,75])
        bar.outline.set_visible(False);bar.ax.tick_params(length=0,labelsize=10)
        bar.set_label('Cumulative resources per agent',fontsize=10,color='#555555',labelpad=5)
        save(fig,a.out,'resources_summary_heatmap')
    # Exact paired empirical bootstrap: all 5^5 resamples, preserving protocol-seed pairing.
    indices=np.array(list(itertools.product(range(5),repeat=5)))
    effects=[]
    for n in [2,8]:
        for m in MODELS:
            for o in ORDERS[1:]:
                for z in NOISES:
                    baseline=values(m,n,z,'game');myth=values(m,n,z,o)
                    for br,mr in zip(cells[(m,n,z,'game')],cells[(m,n,z,o)]):
                        assert (br['pairing_seed'],br['noise_seed'])==(mr['pairing_seed'],mr['noise_seed'])
                    boot=np.median(myth[indices],axis=1)-np.median(baseline[indices],axis=1)
                    lo,hi=np.percentile(boot,[2.5,97.5]);delta=float(np.median(myth)-np.median(baseline))
                    effects.append(dict(model=m,num_agents=n,noise=z,task_order=o,delta_medians=delta,ci_low=float(lo),ci_high=float(hi),game_median=float(np.median(baseline)),myth_median=float(np.median(myth)),n=5))
    # Signed myth effects: orange is lower resources, teal is higher, grey is zero.
    with sns.axes_style('white'), sns.plotting_context('notebook',font_scale=1):
        fig,axes=plt.subplots(3,2,figsize=(11.8,7.2))
        limit=max(5,float(np.ceil(max(abs(r['delta_medians']) for r in effects)/5)*5))
        cmap=sns.blend_palette(['#e99675','#f1f1ef','#72b6a1'],as_cmap=True)
        for i,(model,label) in enumerate(zip(MODELS,LABELS)):
            for j,n in enumerate([2,8]):
                ax=axes[i,j]
                matrix=np.array([[next(r['delta_medians'] for r in effects
                    if (r['model'],r['num_agents'],r['noise'],r['task_order'])==(model,n,z,o))
                    for z in NOISES] for o in ORDERS[1:]])
                labels=np.array([[f'{v:+.1f}' if abs(v)>=.05 else '0.0' for v in row] for row in matrix])
                sns.heatmap(matrix,ax=ax,cmap=cmap,vmin=-limit,vmax=limit,center=0,
                            annot=labels,fmt='',annot_kws={'fontsize':12,'color':'#303c38'},
                            linewidths=2,linecolor='white',cbar=False,
                            xticklabels=['No noise','Uninformed','Informed'],
                            yticklabels=ORDER_LABELS[1:] if j==0 else False)
                ax.tick_params(axis='both',length=0,labelsize=10,pad=7)
                ax.set_xticklabels(ax.get_xticklabels(),rotation=0)
                ax.set_yticklabels(ax.get_yticklabels(),rotation=0)
                if j==0:ax.set_ylabel(label,fontsize=12,fontweight='semibold',labelpad=16,color='#333333')
                if i==0:ax.set_title(f'{n} agents',fontsize=13,fontweight='semibold',pad=14,color='#333333')
        fig.suptitle('Myth effect across noise conditions',fontsize=18,fontweight='semibold',y=.975,color='#303030')
        fig.text(.55,.925,'Median myth resources − median game-only resources',ha='center',fontsize=11,color='#555555')
        fig.text(.55,.889,'No defectors · Round 10 · 5 runs per condition',ha='center',fontsize=10,color='#777777')
        fig.subplots_adjust(left=.205,right=.97,top=.815,bottom=.19,hspace=.48,wspace=.12)
        cax=fig.add_axes([.36,.088,.43,.018])
        bar=fig.colorbar(axes[0,0].collections[0],cax=cax,orientation='horizontal',ticks=[-limit,0,limit])
        bar.outline.set_visible(False);bar.ax.tick_params(length=0,labelsize=10)
        bar.set_label('Lower resources ←   Change per agent   → Higher resources',fontsize=10,color='#555555',labelpad=5)
        save(fig,a.out,'myth_effect_summary_heatmap')
    bound=max(abs(r[k]) for r in effects for k in ['delta_medians','ci_low','ci_high']);bound=max(5,np.ceil((bound+3)/5)*5)
    for n in [2,8]:
        fig,axes=plt.subplots(3,2,figsize=(12,10),sharey=True)
        for i,(m,label) in enumerate(zip(MODELS,LABELS)):
            for j,o in enumerate(ORDERS[1:]):
                ax=axes[i,j];rs=[next(r for r in effects if (r['model'],r['num_agents'],r['noise'],r['task_order'])==(m,n,z,o)) for z in NOISES]
                for x,r in enumerate(rs):
                    v=r['delta_medians'];ax.bar(x,v,color=NOISE_COLORS[x],edgecolor='#555555',linewidth=.7,width=.6)
                    ax.vlines(x,r['ci_low'],r['ci_high'],color='#333333',linewidth=1.3);ax.hlines([r['ci_low'],r['ci_high']],x-.07,x+.07,color='#333333',linewidth=1.3)
                    ax.text(x+.13,v+(1 if v>=0 else -1),f'{v:+.1f}',ha='left',va='bottom' if v>=0 else 'top',fontsize=10,fontweight='bold')
                ax.set_xticks(range(3),NOISE_LABELS);ax.set_ylim(-bound,bound);ax.axhline(0,color='#555555',linewidth=1);style(ax)
                ax.set_title(f'{label}\n{ORDER_LABELS[j+1]} − Game only',fontsize=12,fontweight='bold')
                if j==0:ax.set_ylabel('Difference in median resources')
        fig.suptitle(f'Myth effect · {n} agents · No defectors\nPositive = higher resources with myth',fontsize=16,fontweight='bold')
        fig.text(.5,.015,'Round 10 · n = 5 runs per condition · Bars = difference of medians\nWhiskers = exploratory 95% paired-bootstrap intervals (not adjusted for multiple comparisons)',ha='center',fontsize=10,color='#444444')
        fig.tight_layout(rect=(0,.065,1,.93));save(fig,a.out,f'myth_effect_deltas_{n}agent')
    write_csv(a.out/'run_values.csv',rows);write_csv(a.out/'myth_effect_deltas.csv',effects)
    (a.out/'README.md').write_text('''# Figure 2 noise comparisons

All 270 source hashes and final states verified. No defector conditions.
Each observation is round-10 cumulative actual resources averaged over agents
in one run. Boxes summarize five runs; dots show all five observations.
Delta bars are median(myth runs) minus median(game-only runs), not the median
of paired differences. Intervals use exact paired empirical bootstrap (3125
resamples), preserving replicate/seed blocks. With five replicates they are
exploratory and not multiplicity-adjusted. A collapsed interval is not proof
of no effect beyond this sample.

Two-agent panels are fixed dyads; eight-agent panels rotate partners and include
current-partner history. Differences between panels cannot isolate agent count.
Noise is negative-only communication distortion, range one on sends and returns.
The informed condition reuses September control finals. Implementation differences
are the earlier condition-validator fix and the provider billing-retry fix;
all other recorded implementation hashes match. Exact noise-matched comparison
inputs were checked within each model/population/order/replicate block.
Two Claude population myth-first runs were resampled after role-key errors;
GPT partial attempts stopped on exhausted credits and unfinished runs were rerun.
Successful finals only are plotted. See researchlog 2026-09-16 for the run history.

PNG, SVG and PDF versions are supplied with source values and median deltas.
''')
    write_provenance(a.out, sources, varied)
    print(f'Verified {len(rows)} finals, {len(cells)} cells, {len(effects)} effects. Output: {a.out}')
if __name__=='__main__':main()
