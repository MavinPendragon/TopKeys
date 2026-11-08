"""Convert the simple LilyPond subset used in the Czerny Op.599 Mutopia files to JSON note events."""
import re, sys, json, glob, os
STEP={'c':0,'d':1,'e':2,'f':3,'g':4,'a':5,'b':6}
SEMI=[0,2,4,5,7,9,11]

def strip_cmds(body):
    body=re.sub(r'%.*','',body)
    body=re.sub(r'\\override\s+\S+\s*=\s*#\S+','',body)
    body=re.sub(r"\\set\s+\S+\s*=\s*#'\([^)]*\)",'',body)
    body=re.sub(r'\\set\s+\S+\s*=\s*#\S+','',body)
    body=re.sub(r'\\clef\s+\S+','',body)
    body=re.sub(r'\\key\s+\S+\s+\\\S+','',body)
    body=re.sub(r'\\time\s+\S+','',body)
    body=re.sub(r'\\bar\s+"([^"]*)"',lambda m:' BAR'+('REP' if ':' in m.group(1) else '')+' ',body)
    body=re.sub(r'\\(global|break|voice\w+|numericTimeSignature|stemUp|stemDown|stemNeutral|oneVoice)\b','',body)
    body=re.sub(r'\\(p|pp|f|ff|mf|mp|cresc|decresc|dim|fermata|staccato|accent|tenuto|marcato|sf|sfz|fz|<|>|!)\b','',body)
    body=re.sub(r'([a-g][^\s<>]*)\s+\\rest',r'\1\\rest',body)
    return body

TOK=re.compile(r"BARREP|BAR|<|>\d*\.*|q\d*\.*|[a-g](?:ss|ff|s|f)?[',]*[!?]?\d*\.*(?:\\rest)?|[rRs]\d*\.*|[-^_]\d|[-^_]?[()]|~|\||\\\w+|[-^_][.>^_!-]")
def parse(body,ref):
    # ref like c'' -> absolute diatonic number
    def absd(letter,octs): return STEP[letter]+7*(4+octs)  # c' (one ') = C4 -> octave 4 ; c = C3
    rl=ref[0]; ro=ref.count("'")-ref.count(',')
    prev=absd(rl,ro-1)  # c' -> C4
    events=[]; t=0.0; dur=1.0; lastchord=None; inchord=False; chord=[]; chordfirst=None
    sections=[0.0]
    def resolve(tok):
        nonlocal prev
        m=re.match(r"([a-g])(ss|ff|s|f)?([',]*)",tok)
        L=m.group(1); acc=m.group(2) or ''; marks=m.group(3)
        # nearest placement within a fourth
        base=prev; cand=base - ((base-STEP[L])%7)
        if base-cand>3: cand+=7
        cand+=marks.count("'")*7-marks.count(',')*7
        prev=cand
        octave=cand//7; step=cand%7
        alt={'s':1,'ss':2,'f':-1,'ff':-2,'':0}[acc]
        return 12*(octave+1)+SEMI[step]+alt, cand
    def durof(tok):
        nonlocal dur
        m=re.search(r'(\d+)(\.*)$',tok)
        if m:
            d=4.0/int(m.group(1)); dd=d
            for _ in m.group(2): dd/=2; d+=dd
            dur=d
        return dur
    toks=TOK.findall(body)
    tie=False
    for tok in toks:
        if tok in ('BAR','|'): continue
        if tok=='BARREP': sections.append(t); continue
        if tok=='<': inchord=True; chord=[]; chordfirst=None; continue
        if tok.startswith('>'):
            inchord=False; d=durof(tok[1:] or '')
            events.append({'t':t,'d':d,'n':[c[0] for c in chord],'f':[c[1] for c in chord]}); lastchord=[c[0] for c in chord]
            prev=chordfirst; t+=d; continue
        if tok.startswith('q'):
            d=durof(tok[1:]); events.append({'t':t,'d':d,'n':list(lastchord),'f':[None]*len(lastchord)}); t+=d; continue
        if re.match(r'[-^_]\d',tok):
            tgt=chord[-1] if inchord and chord else (events[-1] if events else None)
            if tgt is not None:
                if isinstance(tgt,list): tgt[1]=int(tok[1])
                else: tgt['f'][-1]=int(tok[1])
            continue
        if tok=='~': tie=True; continue
        if tok[0] in 'rRs' and not re.match(r'[a-g]',tok):
            d=durof(tok[1:]); t+=d; continue
        if re.match(r'[a-g]',tok):
            isrest='\\rest' in tok
            core=tok.replace('\\rest','')
            midi,cand=resolve(core)
            if inchord:
                if chordfirst is None: chordfirst=cand
                chord.append([midi,None]); continue
            d=durof(core)
            if isrest: t+=d; continue
            if tie and events and events[-1]['n']==[midi]:
                events[-1]['d']+=d; tie=False; t+=d; continue
            tie=False
            events.append({'t':t,'d':d,'n':[midi],'f':[None]}); t+=d; continue
    return events,t,sections

out={}
for fn in sorted(glob.glob(sys.argv[1]+'/*no*.ly')):
    n=int(re.search(r'no(\d+)',fn).group(1)); s=open(fn).read()
    parts={}
    for name in ['RHI','RHII','LHI','LHII']:
        m=re.search(name+r'\s*=\s*\\relative\s+(\S+)\s*\{(.*?)\n\}',s,re.S)
        ev,total,sec=parse(strip_cmds(m.group(2)),m.group(1))
        if ev: parts[name]=dict(ev=ev,total=total,sections=sec)
    tm=re.search(r'\\tempo\s+(\d+)\s*=\s*(\d+)',s)
    out[n]=dict(parts=parts,tempo=[int(tm.group(1)),int(tm.group(2))] if tm else None)
json.dump(out,open(sys.argv[2],'w'))
for n,v in out.items():
    print(n,v['tempo'],{k:(len(p['ev']),p['total'],p['sections'],max(len(e['n']) for e in p['ev'])) for k,p in v['parts'].items()})
