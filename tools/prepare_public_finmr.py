#!/usr/bin/env python3
"""Prepare public FinMR Practice input and answers; downloaded data stay LOCAL and ignored by git.
  python -m pip install datasets
  python tools/prepare_public_finmr.py --huggingface
or use --jsonl PATH pointing to the user's officially obtained public Practice JSONL.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from score_practice import normalize_id

def main():
    p=argparse.ArgumentParser();grp=p.add_mutually_exclusive_group(required=True)
    grp.add_argument('--huggingface',action='store_true');grp.add_argument('--jsonl')
    args=p.parse_args()
    if args.huggingface:
        try:from datasets import load_dataset
        except ImportError:raise SystemExit('Install the optional datasets package: python -m pip install datasets')
        records=load_dataset('TheFinAI/FinMR',split='test')
    else:
        records=[json.loads(l) for l in Path(args.jsonl).read_text(encoding='utf-8-sig').splitlines() if l.strip()]
    rows=[];gold=[];seen=set()
    for row in records:
        rid=normalize_id(row['id'])
        if rid in seen:raise ValueError('Duplicate case id '+rid)
        seen.add(rid)
        if not all(x in row for x in ['query','dqc_id','answer']):raise ValueError(f'Missing query/dqc_id/answer for {rid}')
        answer=row['answer'];answer=json.loads(answer) if isinstance(answer,str) else answer
        rows.append({'id':rid,'dqc_id':row['dqc_id'],'query':row['query']})
        gold.append({'id':rid,'dqc_id':row['dqc_id'],'answer':answer})
    if len(rows)!=332:raise ValueError('Public FinMR must contain 332 examples; got '+str(len(rows)))
    indir=ROOT/'DATA/INPUT_ONLY'; indir.mkdir(parents=True,exist_ok=True)
    scoredir=ROOT/'LOCAL_ONLY';scoredir.mkdir(parents=True,exist_ok=True)
    for path,rs in [(indir/'practice_332_questions.jsonl',rows),(scoredir/'practice_332_gold.jsonl',gold)]:
        path.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rs),encoding='utf-8')
        print('Wrote local-only:',path)
    print('Data source: TheFinAI/FinMR, CC BY 4.0; cite FinAuditing. No public dataset bytes shipped in repository.')
if __name__=='__main__':main()
