"""

Simple Caps-based chunking

Author: Peb Ruswono Aryan
Description: groups tokens based on Cap similarity (usually names)

"""
import re

def isfirstcap(tok):
    return tok[0] == tok[0].upper()
    
def iscap(tok):
    return tok == tok.upper()
    
def isnum(tok):
    return isnumroman(tok) or (len(re.findall(r"\d\.?\d*", tok))==1)
            
def isnumroman(tok):
    for t in tok:
        if t not in "MCXVI":
            return False
    return True
    
def group_caps(sent):
    caps = [c for c in re.findall("([A-Z]\w*\.?)+", sent) if not isnumroman(c)]
    tok = sent.split(' ')
    tmp = []
    out = []
    i = 0
    tl = len(tok)
    skip = 0
    for t in tok:
        if skip>0:
            skip -= 1
            i += 1
            continue
        if t in caps:
            tmp += [t]
        elif (t in ['and', 'dan', 'of', ','] and tok[i-1] in caps and tok[i+1] in caps and len(tmp)>0) :
            tmp += [t]
        elif isnum(t) and (tok[(i+1)%tl] in caps or tok[i-1] in caps or tok[i-1] in "-/" or tok[(i+1)%tl] in "-/"):
            tmp += [t]
            if t[-1] == '.':
                tmp[-1] = tmp[-1][:-1]
                out += [tmp]
                tmp = []
        elif t in ['-', '/'] and isnum(tok[i-1]) and isnum(tok[(i+1)%tl]):
            if len(tmp)==0 or not isnum(tmp[-1]):
                tmp += [tok[i-1]]
            tmp += [t]
        elif t in '(' and tok[i+2] in ')':
            tmp += [t, tok[i+1], tok[i+2]]
            skip = 2
        else:
            if len(tmp)>0:
                out += [tmp]
                tmp = []
            out += [[t]]
        i += 1
    if len(tmp)>0:
        out += [tmp]
    return out    
    