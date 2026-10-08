"""Reproduce finite checks accompanying complementation_exact_2n.tex.
Python 3, standard library only. Run: python3 witness_verification.py
The finite tests verify the source and upper-bound implementation; they do
not prove the lower bound, whose argument is in the accompanying note.
"""
import argparse
from itertools import product
from pathlib import Path

LEFT,RIGHT='L','R'
SYMS=(0,1,2,LEFT,RIGHT)

def run(delta,s,f,w,halt=False):
 tape=[LEFT]+list(w)+[RIGHT];q=s;i=0;seen=set();steps=0
 while (q,i) not in seen:
  if q==f and i==0:return True,steps,'accept'
  seen.add((q,i));t=delta.get((q,tape[i]))
  if t is None:return False,steps,'halt-reject'
  q,d=t;i+=d;steps+=1
  assert 0<=i<len(tape)
 if halt:raise AssertionError('constructed complement looped')
 return False,steps,'loop'

def comp(f,g):return tuple(f[g[i]] for i in range(len(g)))
def inv(f):return tuple(f.index(i) for i in range(len(f)))
def generators(k):
 c=list(range(k));t=k if k%2 else k-1
 for i in range(t):c[i]=(i+1)%t
 d=list(range(k));i,j=(0,1) if k%2 else (k-2,k-1);d[i],d[j]=d[j],d[i]
 e=list(range(k));e[0]=1
 return tuple(c),tuple(d),tuple(e)

def source(k,l):
 ck,dk,ek=generators(k);cl,dl,el=generators(l)
 fs=[ck,dk,ek];gs=[dl,inv(cl),el]
 delta={};n=k+l
 for a in range(3):
  for p in range(k):delta[p,a]=(fs[a][p],+1)
  for q in range(l):delta[k+q,a]=(k+gs[a][q],-1)
 delta[0,LEFT]=(0,+1)
 for p in range(k):delta[p,RIGHT]=(k if p==0 else k+1,-1)
 for q in range(1,l):delta[k+q,LEFT]=(1,+1)
 return delta,[+1]*k+[-1]*l,0,k,fs,gs

def build(delta,dirs,s,f):
 n=len(dirs);out={(f,LEFT):(f,+1)}
 def select(cands,a):
  for p in cands:
   if a==LEFT and p==s:return None
   if (a==LEFT and dirs[p]==+1) or (a==RIGHT and dirs[p]==-1):continue
   return p,-dirs[p]
  return 'exhausted'
 for q in range(n):
  for a in SYMS:
   if (a==LEFT and dirs[q]==-1) or (a==RIGHT and dirs[q]==+1):continue
   preds=[p for p in range(n) if not (a==LEFT and p==f) and delta.get((p,a))==(q,dirs[q])]
   val=select(preds,a)
   if val=='exhausted':val=n+q,dirs[q]
   if val is not None:out[q,a]=val
 for p in range(n):
  for a in SYMS:
   if a==LEFT and p==f:continue
   t=delta.get((p,a))
   if t is None:continue
   q,d=t
   preds=[pp for pp in range(p+1,n) if not (a==LEFT and pp==f) and delta.get((pp,a))==(q,d)]
   val=select(preds,a)
   if val=='exhausted':val=n+q,d
   if val is not None:out[n+p,a]=val
 return out,f,n+f

def main():
 if not __debug__:
  raise SystemExit("Run without -O or PYTHONOPTIMIZE: verification requires assertions.")
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output', type=Path,
                     default=Path(__file__).resolve().parent/'results'/'witness_verification.txt',
                     help='Result text path (default: results/ beside this script)')
 args=parser.parse_args()
 report=['Finite checks of the new ternary two-bank witness','',
  'Scope: exact transition tables in the manuscript model, with no stationary moves,',
  'inward endmarker moves, initial configuration at LEFT, and sole accepting',
  'configuration at LEFT. Every ordinary word over the three-letter alphabet',
  'of length at most 7 was checked, including the empty word.', '',
  'The expected source formula is g(t(f(1)))=1 or g(t(f(2)))=1,',
  'where t(1)=1 and t(i)=2 for i!=1, with backward composition reversed.', '',
  'k  l   source states  complement states  words  accepts  loops  max complement steps']
 total=0
 for k,l in [(3,3),(3,4),(4,4),(10,11),(11,11),(11,12),(12,12),(12,13)]:
  delta,dirs,s,f,fs,gs=source(k,l);n=k+l
  target,ts,tf=build(delta,dirs,s,f)
  assert len(dirs)==n
  assert all(d==dirs[q] for q,d in delta.values())
  assert max([ts,tf]+[q for key,val in target.items() for q in [key[0],val[0]]])<2*n
  for table in (delta,target):
   for (q,a),(qq,d) in table.items():
    assert a!=LEFT or d==+1
    assert a!=RIGHT or d==-1
  count=acc=loops=max_steps=0
  for length in range(8):
   for w in product(range(3),repeat=length):
    fw=tuple(range(k));gw=tuple(range(l))
    for a in w:fw=comp(fs[a],fw);gw=comp(gw,gs[a])
    expected=(gw[0 if fw[0]==0 else 1]==0 or gw[0 if fw[1]==0 else 1]==0)
    x,steps,kind=run(delta,s,f,w)
    y,steps2,kind2=run(target,ts,tf,w,halt=True)
    assert x==expected,(k,l,w,fw,gw,x,expected)
    assert y!=x,(k,l,w,x,y)
    assert x or kind=='loop',(k,l,w,kind)
    count+=1;acc+=x;loops+=not x;max_steps=max(max_steps,steps2)
  total+=count
  report.append(f'{k:2} {l:2} {n:15} {2*n:18} {count:6} {acc:8} {loops:6} {max_steps:21}')
 report+=['',f'Total: {total:,} source/formula/complement comparisons; all passed.',
  'Every source input outside the displayed language looped.',
  'Every constructed complement run halted and returned the opposite answer.',
  'Every displayed marker row moved inward, and all states stayed within the',
  'specified n-state source and 2n-state complement sets.', '',
  'These finite checks verify implementation consistency on the tested inputs.',
  'They do not prove the asymptotic lower bound or replace either formal proof.']
 text='\n'.join(report)+'\n';print(text)
 args.output.parent.mkdir(parents=True, exist_ok=True)
 args.output.write_text(text, encoding='utf-8')

if __name__ == '__main__':
 main()
