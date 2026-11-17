#!/usr/bin/env python3
"""Re-score public Practice on exact pairs (Decimal normalization), no raw Gold is bundled.
Run after obtaining official public Practice answers locally.
Usage: python tools/score_practice.py --gold LOCAL_ONLY/practice_332_gold.jsonl
"""
import argparse,csv,json,re,sys
from decimal import Decimal,InvalidOperation
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ARMS=['BASELINE','P1_RAW_SCOPE','P2_SIGN_0015','P3_DIM_0117','P4_DIRECT_CALC_0126','P5_CONSERVATIVE_COMBINED']
def normalize_id(val):
    if isinstance(val,int):return f'DEV_{val:06d}'
    s=str(val).strip()
    if s.isdecimal():return f'DEV_{int(s):06d}'
    if re.fullmatch(r'DEV_\d+',s):return f'DEV_{int(s[4:]):06d}'
    raise ValueError('Unexpected id format: '+repr(val))
def load_jsonl(path):
    result={}
    for line in Path(path).read_text(encoding='utf-8-sig').splitlines():
        if not line.strip():continue
        row=json.loads(line);i=normalize_id(row['id'])
        if i in result:raise ValueError('duplicate id '+i)
        result[i]=row
    return result
def decimalize(n):
    s=str(n).strip().replace(',','')
    if s.startswith('(') and s.endswith(')'):s='-'+s[1:-1]
    v=Decimal(s)
    if not v.is_finite():raise ValueError('Non-finite value')
    return v
def pair_eq(a,b):
    return all(decimalize(a[k])==decimalize(b[k]) for k in ['extracted_value','calculated_value'])
def as_answers(raw):
    out={}
    for i,row in raw.items():
        a=row.get('answer',row)
        if isinstance(a,str):a=json.loads(a)
        if not isinstance(a,dict) or not all(x in a for x in ('extracted_value','calculated_value')):
            raise ValueError(f'Missing answer fields for {i}')
        out[i]=a
    return out
def evaluate(gold,arms,meta):
    ids=set(gold); assert len(ids)==332,('Gold cases',len(ids))
    for name,values in arms.items():
        if set(values)!=ids:raise ValueError(f'{name}: missing/extra IDs: {len(ids-set(values))}/{len(set(values)-ids)}')
    base={i:pair_eq(arms['BASELINE'][i],gold[i]) for i in ids}
    report={}
    for name,values in arms.items():
        ok={i:pair_eq(values[i],gold[i]) for i in ids}
        report[name]={'correct':sum(ok.values()),'n':332,'rescued_vs_frozen':sum(not base[i] and ok[i] for i in ids),'regressed_vs_frozen':sum(base[i] and not ok[i] for i in ids)}
        if name=='P2_SIGN_0015':
            sub={}
            for label in ['STRICT_XML_OK','RECOVERED_XML','TRAIN_DISCOVERY','TUNE_GROUPED','FROZEN_GROUPED_CHALLENGE']:
                col='parse_status' if label.endswith('XML_OK') or label=='RECOVERED_XML' else 'split'
                sl=[i for i in ids if meta[i][col]==label]
                sub[label]={'n':len(sl),'baseline_correct':sum(base[i] for i in sl),'p2_correct':sum(ok[i] for i in sl)}
            report[name]['strata']=sub
            report[name]['changed_pairs']=sum(not pair_eq(values[i],arms['BASELINE'][i]) for i in ids)
            report[name]['rescued_ids']=sorted(i for i in ids if not base[i] and ok[i])
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument('--gold',required=True,help='Public Practice 332 reference (not bundled)')
    p.add_argument('--out',default='LOCAL_ONLY/score_report.json');args=p.parse_args()
    gold=as_answers(load_jsonl(args.gold))
    arms={name:load_jsonl(ROOT/('DATA/BASELINE/EC_FROZEN_332.jsonl' if name=='BASELINE' else f'DATA/PREDICTIONS/{name}.jsonl')) for name in ARMS}
    with (ROOT/'DATA/METADATA/split_and_parse_status.csv').open(encoding='utf-8',newline='') as f:
        meta={x['id']:x for x in csv.DictReader(f)}
    if set(meta)!=set(gold):raise ValueError('Metadata ID mismatch')
    report=evaluate(gold,arms,meta)
    expected=json.loads((ROOT/'DATA/EXPECTED_AGGREGATES.json').read_text(encoding='utf-8'))
    for name,want in expected['per_arm_correct_on_practice'].items():
        if report[name]['correct']!=want:raise AssertionError((name,report[name]['correct'],want))
    if report['P2_SIGN_0015']['rescued_ids']!=expected['p2_vs_baseline']['rescued_case_ids']:raise AssertionError('Rescued case list changed')
    if report['P2_SIGN_0015']['changed_pairs']!=6:raise AssertionError('Changed pair count changed')
    if report['P2_SIGN_0015']['regressed_vs_frozen']!=0:raise AssertionError('Unexpected regression')
    for k,v in expected['p2_vs_baseline']['grouped_splits'].items():
        s=report['P2_SIGN_0015']['strata'][k]
        if s!={'n':v['n'],'baseline_correct':v['baseline'],'p2_correct':v['p2']}:raise AssertionError((k,s,v))
    for k,v in {'STRICT_XML_OK':{'n':147,'baseline_correct':119,'p2_correct':124},'RECOVERED_XML':{'n':185,'baseline_correct':34,'p2_correct':34}}.items():
        if report['P2_SIGN_0015']['strata'][k]!=v:raise AssertionError(k)
    dest=ROOT/args.out;dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('PASS: public Practice exact-pair scores and BASE158 provenance checks (retrospective).')
    for k,v in report.items():print(k,v['correct'],v['rescued_vs_frozen'],v['regressed_vs_frozen'])
    print('Report:',dest)
if __name__=='__main__':main()
