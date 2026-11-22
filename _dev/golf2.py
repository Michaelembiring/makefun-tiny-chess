import os,sys,json,urllib.request as Q,zlib,base64
E=os.environ["MAKEFUN_ENV_URL"]
def post(p,d):
 r=Q.Request(E+p,json.dumps(d).encode(),{"content-type":"application/json"});return json.load(Q.urlopen(r))
V=[0,100,320,330,500,900,20000]
N=[-33,-31,-18,-14,14,18,31,33];B=[-17,-15,15,17];R=[-16,-1,1,16];K=[-17,-16,-15,-1,1,15,16,17]
T=[v-64 for v in zlib.decompress(base64.b64decode("eNqFUKEWAzEI+4PqajQag8FgMGcwZ06f3v+LBXp9M9tbRNPmEUIxW/AI5gh3FTNRh5RZusd5Qo7I68qI14PHZmMSMMdklBpP8jiOcCI7Mg8j8uJ6l26EOoDn9rE0WLynEImGiBUZGNHeDBQ3ZPt6RBy6dP3Hvvr7nh99VCvfWhLxlaMrT+3hL/ntyyvM4speFlYm3BDG5/BFxjlG3X7woAao/LhJ7VmINO879cNbf+q27w2/V2Xo"))]
M=99999;I=1<<30
def on(s):return 0<=s<128 and not s&0x88
class P:
 def __init__(s,f):
  s.b=[0]*128;s.c=1;s.e=-1;z=f.split()
  for i,row in enumerate(z[0].split("/")):
   k=7-i;j=0
   for ch in row:
    if ch.isdigit():j+=int(ch)
    else:t="pnbrqk".index(ch.lower())+1;s.b[k*16+j]=t if ch.isupper() else-t;j+=1
  s.c=1 if z[1]=="w" else-1
  if len(z)>3 and z[3]!="-":s.e="abcdefgh".index(z[3][0])+(int(z[3][1])-1)*16
  s.wk=s.b.index(6);s.bk=s.b.index(-6)
 def a(s,q,by):
  b=s.b
  for o in(-15*by,-17*by):
   t=q+o
   if on(t)and b[t]==by:return 1
  for o in N:
   t=q+o
   if on(t)and b[t]==2*by:return 1
  for o in K:
   t=q+o
   if on(t)and b[t]==6*by:return 1
  for os,ts in((R,(4,5)),(B,(3,5))):
   for o in os:
    t=q+o
    while on(t):
     p=b[t]
     if p:
      if p*by>0 and abs(p)in ts:return 1
      break
     t+=o
  return 0
 def ck(s,c):return s.a(s.wk if c>0 else s.bk,-c)
 def g(s):
  b=s.b;c=s.c;M=[]
  for q in range(128):
   p=b[q]
   if not p or p*c<0:continue
   t=abs(p)
   if t==1:
    d=16*c;fw=q+d
    if on(fw)and b[fw]==0:
     M+=[q*128+fw]
     if q>>4==(1 if c>0 else 6)and on(q+2*d)and b[q+2*d]==0:M+=[q*128+q+2*d]
    for df in(-1,1):
     to=fw+df
     if on(to)and((b[to]and b[to]*c<0)or(to==s.e and not b[to])):M+=[q*128+to]
   elif t==2:
    for o in N:
     to=q+o
     if on(to)and b[to]*c<=0:M+=[q*128+to]
   elif t<6:
    for o in(B if t==3 else R if t==4 else K):
     to=q+o
     while on(to):
      p=b[to]
      if p:
       if p*c<0:M+=[q*128+to]
       break
      M+=[q*128+to];to+=o
   else:
    for o in K:
     to=q+o
     if on(to)and b[to]*c<=0:M+=[q*128+to]
  return M
 def mk(s,m):
  f=m>>7;to=m&127;b=s.b;c=s.c;p=b[f];u=(b[to],s.e,s.wk,s.bk,p);b[f]=0;cs=to
  if abs(p)==1 and(f&7)!=(to&7)and not b[to]:cs=to-16*c
  cap=b[cs];b[cs]=0
  if abs(p)==1 and to>>4 in(0,7):p=5*c
  b[to]=p
  if abs(p)==6 and abs(to-f)==2:
   if to>f:b[to-1]=b[to+1];b[to+1]=0
   else:b[to+1]=b[to-2];b[to-2]=0
  if p==6:s.wk=to
  elif p==-6:s.bk=to
  s.e=(f+to)//2 if abs(p)==1 and abs(to-f)==32 else-1;s.c=-c
  return(cap,cs,u)
 def uk(s,m,u):
  cap,cs,u=u;s.c=-s.c;f=m>>7;to=m&127;b=s.b;p=b[to];b[to]=0;b[cs]=cap;b[f]=u[4]
  if abs(p)==6 and abs(to-f)==2:
   if to>f:b[to+1]=b[to-1];b[to-1]=0
   else:b[to-2]=b[to+1];b[to+1]=0
  s.e=u[1];s.wk=u[2];s.bk=u[3]
 def ev(s):
  b=s.b;sc=0;np=0;bi=0
  for q in range(128):
   if q&0x88:continue
   p=b[q]
   if not p or abs(p)==6:continue
   t=abs(p);idx=(q>>4)*8+(q&7)if p>0 else(7-(q>>4))*8+(q&7)
   v=V[t]+T[(t-1)*64+idx];sc+=v if p>0 else-v
   if t!=1:np+=V[t]
   if t==3:bi+=1 if p>0 else-1
  ph=np if np<6800 else 6800
  wi=(s.wk>>4)*8+(s.wk&7);bk=(7-(s.bk>>4))*8+(s.bk&7)
  sc+=(T[384+wi]-T[384+bk])*(6800-ph)//6800+(T[6*64+wi]-T[6*64+bk])*ph//6800
  if bi>=2:sc+=30
  if bi<=-2:sc-=30
  return sc*s.c
kill={}
def mv(s,m):
 f=m>>7;to=m&127;v=s.b[to];a=abs(s.b[f])
 if not v and a==1 and(f&7)!=(to&7):v=1
 return V[abs(v)]*16-V[a]
def qs(s,al,be,pc):
 s.n+=1
 if s.n>=s.bud:s.ab=1;return 0
 p=s;ck=p.ck(p.c);bst=-M-1
 if pc>=40:return p.ev()
 if not ck:
  st=p.ev()
  if st>=be:return st
  bst=st
  if st>al:al=st
 b=p.b;c=p.c;cp=[]
 for m in p.g():
  f=m>>7;to=m&127;tp=b[to]
  if ck or(tp and tp*c<0)or(abs(b[f])==1 and(f&7)!=(to&7)and not tp)or(abs(b[f])==1 and to>>4 in(0,7)):cp+=[m]
 cp.sort(key=lambda m:mv(p,m),reverse=1)
 lg=0
 for m in cp:
  u=p.mk(m)
  if p.ck(c):p.uk(m,u);continue
  lg+=1;sc=-qs(p,-be,-al,pc+1);p.uk(m,u)
  if s.ab:return 0
  if sc>bst:bst=sc
  if sc>=be:return sc
  if sc>al:al=sc
 if ck and lg==0:return-M+pc
 return bst
def nm(s,d,al,be,pc):
 if d<=0:return qs(s,al,be,pc)
 s.n+=1
 if s.n>=s.bud:s.ab=1;return 0
 p=s;ck=p.ck(p.c);c=p.c;L=[]
 for m in p.g():
  u=p.mk(m)
  if not p.ck(c):L+=[m]
  p.uk(m,u)
 if not L:return-M+pc if ck else 0
 k0,k1=kill.get(pc,(0,0))
 def od(m):
  f=m>>7;to=m&127;cap=p.b[to]or(abs(p.b[f])==1 and(f&7)!=(to&7)and not p.b[to])
  if cap or(abs(p.b[f])==1 and to>>4 in(0,7)):return(2,mv(p,m))
  return(1,0)if m==k0 or m==k1 else(0,0)
 L.sort(key=od,reverse=1);bst=-I
 for m in L:
  u=p.mk(m);sc=-nm(s,d-1,-be,-al,pc+1);p.uk(m,u)
  if s.ab:return 0
  if sc>bst:bst=sc
  if sc>al:al=sc
  if al>=be:
   if not(p.b[m&127]):kill[pc]=(m,k0)
   break
 return bst
def sq(s):return"abcdefgh"[s&7]+str((s>>4)+1)
def uci(s,m):
 f=m>>7;to=m&127;pr="q"if abs(s.b[f])==1 and to>>4 in(0,7)else"";return sq(f)+sq(to)+pr
def best(s,ms,bud):
 s.bud=bud;s.n=0;s.ab=0;L=[]
 for u in ms:
  f="abcdefgh".index(u[0])+(int(u[1])-1)*16;t="abcdefgh".index(u[2])+(int(u[3])-1)*16;L+=[f*128+t]
 bm=L[0]
 for d in range(1,65):
  al=-I;lb=None;sc=[]
  for m in L:
   u=s.mk(m);v=-nm(s,d-1,-I,-al,1);s.uk(m,u)
   if s.ab:break
   sc+=[(v,m)]
   if v>al:al=v;lb=m
  if s.ab:break
  sc.sort(reverse=1);L=[m for _,m in sc]
  if lb is not None:bm=lb
  if bm and-al>=M-100:break
 return uci(s,bm)
while 1:
 g=post("/game",{})
 if g["status"]=="done":break
 while g["status"]=="your_move":
  s=P(g["fen"]);g=post("/move",{"game":g["game"],"move":best(s,g["legal_moves"],30000)})
print("done",file=sys.stderr)