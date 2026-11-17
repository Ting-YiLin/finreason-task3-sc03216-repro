#!/usr/bin/env python3
"""Offline checksum and structural checks; no reference labels or network required."""
import hashlib,json,csv,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from score_practice import load_jsonl,pair_eq,ARMS

def main():
    for line in (ROOT/'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        if not line.strip():continue
        digest,name=line.split('  ',1);p=ROOT/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:raise AssertionError('Checksum failed: '+name)
    arms={n:load_jsonl(ROOT/('DATA/BASELINE/EC_FROZEN_332.jsonl' if n=='BASELINE' else f'DATA/PREDICTIONS/{n}.jsonl')) for n in ARMS}
    ids=set(arms['BASELINE']); assert len(ids)==332
    for n,a in arms.items():
        if set(a)!=ids:raise AssertionError((n,'not 332 matching IDs'))
        if any(set(x)!={'id','extracted_value','calculated_value'} for x in a.values()):raise AssertionError(n+' has unexpected fields')
    with (ROOT/'DATA/METADATA/split_and_parse_status.csv').open(newline='',encoding='utf-8') as f:
        meta=list(csv.DictReader(f))
    if len(meta)!=332 or {x['id'] for x in meta}!=ids:raise AssertionError('Metadata mismatch')
    changed=sorted(i for i in ids if not pair_eq(arms['BASELINE'][i],arms['P2_SIGN_0015'][i]))
    assert changed==['DEV_000048','DEV_000058','DEV_000082','DEV_000083','DEV_000099','DEV_000105'],changed
    print('PASS: checksums, 332 cases per arm, no extra fields, six changed P2 cases.')
if __name__=='__main__':main()
