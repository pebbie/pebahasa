"""

Frequent Term Extraction

Author: Peb Ruswono Aryan
Description: modified from topia.termextract (KamusTagger & Indonesian dict-based tag)

"""
from kamus import KamusEksternal as Kamus
from tokenization import *
import re

"""
Term Extractor
"""

SEARCH = 0
NOUN = 1

EXTRACTOR = None
TAGGER = None

def permissiveFilter(word, occur, strength):
    return True

class DefaultFilter(object):

    def __init__(self, singleStrengthMinOccur=3, noLimitStrength=2):
        self.singleStrengthMinOccur = singleStrengthMinOccur
        self.noLimitStrength = noLimitStrength

    def __call__(self, word, occur, strength):
        return ((strength == 1 and occur >= self.singleStrengthMinOccur) or
                (strength >= self.noLimitStrength)) and (len(word)>1)

def _add(term, norm, multiterm, terms):
    multiterm.append((term, norm))
    terms.setdefault(norm, 0)
    terms[norm] += 1

class TermExtractor(object):

    def __init__(self, tagger=None, filter=None):
        if filter is None:
            filter = DefaultFilter()
            #filter = permissiveFilter
        self.filter = filter

    def extract(self, taggedTerms):
        """See interfaces.ITermExtractor"""
        terms = {}
        # Phase 1: A little state machine is used to build simple and
        # composite terms.
        multiterm = []
        state = SEARCH
        while taggedTerms:
            term, tag, norm = taggedTerms.pop(0)
            if state == SEARCH and tag.startswith('N'):
                state = NOUN
                _add(term, norm, multiterm, terms)
            elif state == SEARCH and tag == 'JJ' and term[0].isupper():
                state = NOUN
                _add(term, norm, multiterm, terms)
            elif state == NOUN and tag.startswith('N'):
                _add(term, norm, multiterm, terms)
            elif state == NOUN and not tag.startswith('N'):
                state = SEARCH
                if len(multiterm) > 1:
                    word = ' '.join([word for word, norm in multiterm])
                    terms.setdefault(word, 0)
                    terms[word] += 1
                multiterm = []
        # Phase 2: Only select the terms that fulfill the filter criteria.
        # Also create the term strength.
        return [
            (word, occur, len(word.split()))
            for word, occur in terms.items()
            if self.filter(word, occur, len(word.split()))]

    def __repr__(self):
        return '<%s using %r>' %(self.__class__.__name__, self.tagger)

class KamusTagger:
    def __init__(self, fkamus, ftagidx):
        self.k = Kamus(fkamus)
        f = open(ftagidx)
        self.tags = [t.strip() for t in f.readlines()]
        f.close()
        
    def tag(self, terms):
        result = []
        for tok in terms:
            if len(tok)==0:continue
            t1 = self.k[tok]
            t2 = self.k[tok.lower()]
            if t1==t2:
                t = t1
            else:
                if t1 is None:
                    if terms.index(tok)>1:
                        t = t1
                    else:
                        t = t1
                else:
                    t = t2
            tag = ''
            if tok in ['&']:
                t = 0
            if t is None:
                tag = 'NN'
                if tok[0] == tok[0].upper():
                    tag = 'NNP'
            else:
                tag = self.tags[t]
                
            yield (tok, tag, tok.lower())
            #result.append((tok, tag, tok))
        #return result
        
def extract_terms(text):
    global EXTRACTOR, TAGGER
    if EXTRACTOR is None:
        EXTRACTOR = TermExtractor()
    if TAGGER is None:
        TAGGER = KamusTagger('inlex.dic', 'taglist.txt')
    lines = re.sub('[\x80-\xff]','',text).split('\n')
    tagterms = []
    for l in lines:
        if len(l) == 0: continue
        out = sentence_extraction(cleaning(l))
        
        for o in out:
            toks = tokenisasi_kalimat(o)
            for tagterm in TAGGER.tag(toks):
                term, tag, nterm = tagterm
                #print term, tag
                tagterms.append(tagterm)
                
    return [tx[0] for tx in sorted(EXTRACTOR.extract(tagterms), key=lambda d: d[1], reverse=True) if tx[1]>1]

if __name__ == '__main__':
    import sys
    if len(sys.argv)>1:
        f = open(sys.argv[1], 'rb')
    else:
        f = open('data.txt', 'rb')
    text = f.read()
    f.close()

    
                
    print "\n".join(extract_terms(text))