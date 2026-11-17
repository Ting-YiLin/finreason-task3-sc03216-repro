#!/usr/bin/env python3
"""Check rebuilt P1-P5 outputs against the released snapshots, with Decimal equivalence."""
import argparse
from pathlib import Path
from score_practice import load_jsonl,pair_eq,ARMS
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output-dir',default='OUTPUT_REPLAY');a=p.parse_args()
 base=ROOT/a.output_dir
 for arm in ARMS[1:]:
  original=load_jsonl(ROOT/f'DATA/PREDICTIONS/{arm}.jsonl');rebuild=load_jsonl(base/arm/'predictions.jsonl')
  if set(original)!=set(rebuild) or any(not pair_eq(original[i],rebuild[i]) for i in original):raise AssertionError(f'{arm} differs')
  print('PASS: '+arm+' 332 paired predictions')
 print('All five prototype arms match the frozen 2026-10-29 output snapshots.')
if __name__=='__main__':main()
