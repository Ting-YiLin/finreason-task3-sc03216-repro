#!/usr/bin/env python3
"""Gold-free, retrospective FinMR prototype: explicit XBRL facts and linkbase evidence.
Uses only input-only queries and frozen E+C predictions; NEVER reads scorer or Gold.
Not a complete Arelle implementation. No external network.
"""
import argparse, json, re, csv, time, collections, os, hashlib
from decimal import Decimal, InvalidOperation
from pathlib import Path
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
XL='{http://www.w3.org/1999/xlink}'
XBRL='{http://www.xbrl.org/2003/instance}'
LINK='{http://www.xbrl.org/2003/linkbase}'
XBRLDI='{http://xbrl.org/2006/xbrldi}'
HEAD=re.compile(r'\n##([^\n]+)\n')
QUESTION=re.compile(r"Question1:.*?value of ([a-zA-Z0-9_\-]+):([A-Za-z0-9_\-]+) in the Instance document for the period (\d{4}-\d{2}-\d{2})(?: to (\d{4}-\d{2}-\d{2}))?",re.S)
NUM=re.compile(r'^\s*[-+]?\d+(?:\.\d+)?(?:[Ee][-+]?\d+)?\s*$')

def parse_num(v):
 try:
  s=str(v).replace(',','').strip(); d=Decimal(s)
  return d if d.is_finite() else None
 except Exception:return None

def nv(v):
 s=format(v,'f')
 return s.rstrip('0').rstrip('.') if '.' in s else s

def taglocal(tag):return tag.split('}')[-1]

def sections(q):
 ret={}; m=list(HEAD.finditer(q))
 for i,h in enumerate(m):ret[h.group(1).strip().lower()]=q[h.end():(m[i+1].start() if i+1<len(m) else len(q))].strip()
 return ret

def parsexml(text):
 if not text:return None,'missing'
 try:
  root=etree.fromstring(text.encode('utf-8'),parser=etree.XMLParser(recover=True,huge_tree=True,resolve_entities=False,load_dtd=False,no_network=True))
  return root,'recovered' if not text.rstrip().endswith('</xbrl>') else 'closed'
 except Exception as e:return None,'error:'+str(e)[:80]

def read_contexts(root):
 contexts={}; units={}
 if root is None:return contexts,units
 for el in root.iter():
  local=taglocal(el.tag) if isinstance(el.tag,str) else ''
  if local=='unit' and el.get('id'):
   units[el.get('id')]=' '.join(x.text.strip() for x in el.iter() if isinstance(x.tag,str) and taglocal(x.tag) in ['measure'] and x.text)
  if local!='context' or not el.get('id'):continue
  pp=[x for x in el.iter() if isinstance(x.tag,str) and taglocal(x.tag) in ('startDate','endDate','instant')]
  dates={taglocal(x.tag):x.text.strip() for x in pp if x.text}
  dims=[]
  for x in el.iter():
   if not isinstance(x.tag,str):continue
   if taglocal(x.tag)=='explicitMember':dims.append((x.get('dimension'),(x.text or '').strip()))
   if taglocal(x.tag)=='typedMember':dims.append((x.get('dimension'),etree.tostring(x,encoding='unicode')))
  entity=next((x.text.strip() for x in el.iter() if isinstance(x.tag,str) and taglocal(x.tag)=='identifier' and x.text),'')
  contexts[el.get('id')]=dict(period=(dates.get('startDate'),dates.get('endDate')) if 'startDate' in dates else (None,dates.get('instant')),dims=tuple(sorted(dims)),entity=entity)
 return contexts,units

def factrows(root,contexts):
 out=[]
 if root is None:return out
 for x in root:
  if not isinstance(x.tag,str) or not x.get('contextRef'):continue
  if x.get('{http://www.w3.org/2001/XMLSchema-instance}nil')=='true':continue
  raw=x.text or ''; val=parse_num(raw)
  if val is None:continue
  ctx=x.get('contextRef')
  out.append(dict(tag=x.tag,local=taglocal(x.tag),context_id=ctx,ctx=contexts.get(ctx),unit=x.get('unitRef'),val=val,decimals=x.get('decimals'),raw=raw.strip()))
 return out

def targetfacts(facts,prefix,local,period):
 z=[x for x in facts if x['local']==local and x['ctx'] and x['ctx']['period']==period]
 # correct namespace; taxonomy US GAAP namespace versions vary; do not equate foreign custom concepts
 if prefix=='us-gaap':z=[x for x in z if x['tag'].startswith('{http://fasb.org/us-gaap/')]
 return z

def strictfact(candidates):
 if not candidates:return None,'no_matching_fact'
 non_dim=[x for x in candidates if not x['ctx']['dims']]
 if non_dim:candidates=non_dim
 usds=[x for x in candidates if x['unit']=='USD']
 if usds:candidates=usds
 vals={x['val'] for x in candidates}
 if len(vals)==1:return candidates[0],('unique' if len(candidates)==1 else 'consistent_duplicates')
 return None,'ambiguous_values'

def calc_arcs(root,target):
 if root is None:return []
 roles=[]
 for link in root.iter():
  if not isinstance(link.tag,str) or taglocal(link.tag)!='calculationLink':continue
  role=link.get(XL+'role') or ''
  loc={}
  for l in link:
   if not isinstance(l.tag,str):continue
   if taglocal(l.tag)=='loc':
    href=l.get(XL+'href',''); label=l.get(XL+'label','')
    nm=href.split('#')[-1]
    loc[label]=nm.split('_',1)[-1] if '_' in nm else nm
  group=[]
  for a in link:
   if not isinstance(a.tag,str) or taglocal(a.tag)!='calculationArc':continue
   if (a.get('use') or '').lower()=='prohibited':continue
   parent=loc.get(a.get(XL+'from',''));child=loc.get(a.get(XL+'to',''))
   if parent==target and child:
    wt=parse_num(a.get('weight','1'))
    if wt is not None:group.append((child,wt,a.get('priority','0')))
  if group:roles.append((role,group))
 return roles

def childcalc(roles,facts,parent,period):
 if not parent:return None,'no_parent'
 # For safety, only child facts with exactly matching context ID: do not silently merge dimensional scopes.
 outputs=[]
 for role,arcs in roles:
  children={}
  for n,w,priority in arcs:children[(n,priority)]=w
  if not children:continue
  if len({n for n,p in children})!=len(children):continue
  acc=Decimal(0);receipts=[];ok=True
  for (child,_),w in children.items():
   matches=[f for f in facts if f['local']==child and f['context_id']==parent['context_id'] and f['unit']==parent['unit']]
   vals={f['val'] for f in matches}
   if len(vals)!=1:ok=False;break
   val=next(iter(vals));acc+=w*val;receipts.append((child,nv(w),nv(val)))
  if ok and len(receipts)>=2:outputs.append((acc,role,receipts))
 if not outputs:return None,'incomplete_or_absent_direct_children'
 if len({x[0] for x in outputs})!=1:return None,'conflicting_roles'
 return outputs[0],'complete_direct_children'

def dimensioncalc(facts,parent):
 if parent is None:return None,'no_parent'
 # equal target, period, entity, unit; choose a single homogeneous axis, distinct members, no extra dimensions
 f=[x for x in facts if x['tag']==parent['tag'] and x['ctx'] and x['ctx']['period']==parent['ctx']['period'] and x['ctx']['entity']==parent['ctx']['entity'] and x['unit']==parent['unit'] and len(x['ctx']['dims'])==1]
 groups=collections.defaultdict(list)
 for x in f:
  ax,mem=x['ctx']['dims'][0];groups[ax].append((mem,x))
 out=[]
 for ax,ls in groups.items():
  mems=collections.defaultdict(set)
  for mem,x in ls:mems[mem].add(x['val'])
  if len(mems)<2 or any(len(vals)!=1 for vals in mems.values()):continue
  v=sum((next(iter(a)) for a in mems.values()),Decimal(0));out.append((v,ax,len(mems)))
 if len(out)!=1:return None,('no_unique_axis' if not out else 'conflicting_axes')
 return out[0],'unique_axis'

def run(q,b):
 s=sections(q['query']); qm=QUESTION.search(q['query']);trace={'id':q['id'],'dqc':q['dqc_id'],'base_e':b['extracted_value'],'base_c':b['calculated_value']}
 if not qm:return {},dict(trace,reason='question_unreadable')
 prefix,local,start,end=qm.groups();period=(start,end) if end else (None,start)
 root,mode=parsexml(s.get('instance document',''));ctx,units=read_contexts(root); facts=factrows(root,ctx)
 candidates=targetfacts(facts,prefix,local,period);f,reason=strictfact(candidates)
 trace.update(target=prefix+':'+local,xml_status=mode,n_contexts=len(ctx),n_facts=len(facts),n_target_period=len(candidates),reason=reason)
 proposals={}
 if f is not None:
  extracted=nv(f['val']);trace['source_context']=f['context_id'];trace['source_dims']=len(f['ctx']['dims']);trace['new_extraction']=extracted
  # Prototype P1 independent raw extraction; leave baseline calculated number unchanged
  if parse_num(b['extracted_value'])!=f['val']:
   proposals['P1_RAW_SCOPE']=(extracted,b['calculated_value'])
  if q['dqc_id']=='DQC_US_0015':
   proposals['P2_SIGN_0015']=(extracted,nv(abs(f['val'])))
  if q['dqc_id']=='DQC_US_0117' and not f['ctx']['dims']:
   dx,why=dimensioncalc(facts,f);trace['dim_reason']=why
   if dx is not None:proposals['P3_DIM_0117']=(extracted,nv(dx[0]));trace['dim_axis']=dx[1];trace['dim_members']=dx[2]
  if q['dqc_id']=='DQC_US_0126':
   ca,why=childcalc(calc_arcs(parsexml(s.get('calculation linkbase document',''))[0],local),facts,f,period);trace['calc_reason']=why
   if ca is not None:proposals['P4_DIRECT_CALC_0126']=(extracted,nv(ca[0]));trace['calc_role']=ca[1];trace['calc_receipts']=ca[2]
 trace['proposals']={k:list(v) for k,v in proposals.items()}
 return proposals,trace

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',default='OUTPUT'); args=ap.parse_args();out=ROOT/args.output_dir;out.mkdir(exist_ok=True)
 t0=time.perf_counter();Q=[json.loads(l) for l in open(ROOT/'DATA/INPUT_ONLY/practice_332_questions.jsonl')]
 B={x['id']:x for x in (json.loads(l) for l in open(ROOT/'DATA/BASELINE/EC_FROZEN_332.jsonl'))}
 methods=['P1_RAW_SCOPE','P2_SIGN_0015','P3_DIM_0117','P4_DIRECT_CALC_0126','P5_CONSERVATIVE_COMBINED']
 rows={m:[] for m in methods}; diag=[];changed=collections.Counter()
 for q in Q:
  i=q['id'];p,t=run(q,B[i]);diag.append(t)
  # With each rule-specific method, fallback to E+C. Combined gives priority rule-native, then raw extraction.
  for method in methods:
   proposal=(p.get(method) if method!='P5_CONSERVATIVE_COMBINED' else next((p[k] for k in ['P2_SIGN_0015','P3_DIM_0117','P4_DIRECT_CALC_0126','P1_RAW_SCOPE'] if k in p),None))
   if proposal is None:proposal=(B[i]['extracted_value'],B[i]['calculated_value'])
   if parse_num(proposal[0])!=parse_num(B[i]['extracted_value']) or parse_num(proposal[1])!=parse_num(B[i]['calculated_value']):changed[method]+=1
   rows[method].append(dict(id=i,extracted_value=proposal[0],calculated_value=proposal[1]))
 for m in methods:
  d=out/m;d.mkdir(exist_ok=True)
  with (d/'predictions.jsonl').open('w') as f:
   for r in rows[m]:f.write(json.dumps(r,ensure_ascii=False)+'\n')
 with (out/'PROTOTYPE_DIAGNOSTICS.jsonl').open('w') as f:
  for d in diag:f.write(json.dumps(d,ensure_ascii=False)+'\n')
 summary=dict(runtime_sec=round(time.perf_counter()-t0,3),changed=dict(changed),xml_status=dict(collections.Counter(d['xml_status'] for d in diag if 'xml_status' in d)),extraction_reasons=dict(collections.Counter(d.get('reason') for d in diag)),proposal_counts=dict(collections.Counter(k for d in diag for k in d.get('proposals',{}))),methods=methods)
 (out/'PROTOTYPE_RUN_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
