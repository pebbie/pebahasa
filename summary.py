"""

Simple Extractive Text Summarization

Author: Peb Ruswono Aryan
Description: extract N most-similar sentences with title (first sentence)

"""
from tokenization import *
f = open('indonesian')
stopwords = [w.strip() for w in f.readlines()]
f.close()

def distance(s1,s2):
    score = 0.
    for t in s1['tokens']:
        #ignore delimiters
        if t in [',".()[]']:continue
        if t.lower() in stopwords: continue
        if t in s2['tokens']:
            score += 1.
    return score / max(len(s1['tokens']),len(s2['tokens']))
    
def strip_stopword_affix(tmp):
    tl = tmp.split(' ')
    startidx = 0
    while tl[startidx].lower() in stopwords: startidx += 1
    endidx = -1
    while tl[endidx].lower() in stopwords: endidx -= 1
    return " ".join(tl[startidx:endidx]).strip()
    
def make_summary(text, title=None, maxresult=5, minthreshold=1e-5):
    lines = re.sub('[\x80-\xff]','',text).split('\n')
    sentences = []
    for l in lines:
        if len(l) == 0: continue
        out = sentence_extraction(cleaning(l))
        for o in out:
            sentences.append({'original': o, 'tokens': tokenisasi_kalimat(o)})
        
    #title
    if title is None:
        t = sentences[0]
    else:
        t = {'original': title, 'tokens': tokenisasi_kalimat(title)}
        
    #print t
    
    #calculate dot product of each sentence with title
    dist = []
    for si in xrange(1,len(sentences)):
        d = distance(t, sentences[si])
        dist.append((si, d))
    dist = sorted(dist, key=lambda d: d[1], reverse=True)
    result = []
    for dd in dist:
        si,d = dd
        result.append((si, sentences[si]))
        if len(result)>=maxresult or d < minthreshold:
            break
    summary = sorted(result, key=lambda ss:ss[0])
    output = []
    for sum in summary:
        otmp = sum[1]['original']
        tmp = sum[1]['tokens']
        if ',' in tmp:
            ci = tmp.index(',')
            cio = otmp.index(',')
            cc = ci*1.0/len(tmp)
            if cc < 0.4:
                otmp = otmp[cio+1:]
        output.append(strip_stopword_affix(otmp.strip()))
    return " ".join(output)
    
if __name__ == '__main__':
    f = open('data.txt', 'rb')
    teks = f.read()
    f.close()

    print make_summary(teks)