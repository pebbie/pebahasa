# package NLP_ITB.POSTagger.HMM
from copy import deepcopy
import re
import math

class WordFreq:
    def __init__(self, wordTagFreq={}):
        self.wordTagFreq = wordTagFreq

    def getWordTagFreq(self):
        #Returns Map<String, Map<Integer, Integer>>
        return self.wordTagFreq

def readWordTagFreq(reader, tagNumbers):
    """
    Returns WordFreq
    Parameters:
        reader: file object
        tagNumbers: Map<String, Integer>
    """
    # Map<String, Map<Integer, Integer>>
    wordTagFreq = {}
    for line in reader.readlines():
        lineParts = re.split("\\s+", line.strip())
        word = lineParts[0]
        wordTagFreq[word] = {};
        for i in xrange(1, len(lineParts), 2):
            wordTagFreq[word][tagNumbers[lineParts[i]]] = int(lineParts[i + 1])

    return WordFreq(wordTagFreq)
    
class NGram:
    def __init__(self, tagNumbers={}, numberTags={}, uniGramFreqs={}, biGramFreqs={}, triGramFreqs={}, quatoGramFreqs={}):
        self.tagNumbers = tagNumbers;
        self.numberTags = numberTags;
        self.uniGramFreqs = uniGramFreqs;
        self.biGramFreqs = biGramFreqs;
        self.triGramFreqs = triGramFreqs;
        self.quatoGramFreqs = quatoGramFreqs;

    def getTagNumber(self):
        #Returns Map<String, Integer>
        return self.tagNumbers

    def getNumberTag(self):
        #Returns Map<Integer, String>
        return self.numberTags

    def getUniGramFreq(self):
        #Returns Map<UniGram, Integer>
        return self.uniGramFreqs

    def getBiGramFreq(self):
        #Returns Map<BiGram, Integer>
        return self.biGramFreqs

    def getTriGramFreq(self):
        #Returns Map<TriGram, Integer>
        return self.triGramFreqs

    def getQuatoGramFreq(self):
        #Returns Map<QuatoGram, Integer>
        return self.quatoGramFreqs

def readNGrams(reader):
    """
    Returns NGram
    Parameters:
        reader: file object
    """
    # Map<String, Integer>
    tagNumbers = {}
    # Map<Integer, String>
    numberTags = {}
    # Map<UniGram, Integer>
    uniGramFreqs = {}
    # Map<BiGram, Integer>
    biGramFreqs = {}
    # Map<TriGram, Integer>
    triGramFreqs = {}
    # Map<QuatoGram, Integer>
    quatoGramFreqs = {}
    # int
    tagNumber = 0
    # String
    for line in reader.readlines():
        # String[]
        lineParts = re.split("\\s+", line.strip())
        # int
        freq = int(lineParts[-1])
        lplen = len(lineParts)
        if lplen == 2:
            tagNumbers[lineParts[0]] = tagNumber
            numberTags[tagNumber] = lineParts[0]
            uniGramFreqs[UniGram(tagNumber)] = freq
            tagNumber += 1
        elif lplen == 3: 
            biGramFreqs[BiGram(tagNumbers[lineParts[0]], tagNumbers[lineParts[1]])] = freq
        elif lplen == 4: 
            triGramFreqs[TriGram(tagNumbers[lineParts[0]], tagNumbers[lineParts[1]], tagNumbers[lineParts[2]])] = freq
        elif lplen == 5: 
            quatoGramFreqs[QuatoGram(tagNumbers[lineParts[0]], tagNumbers[lineParts[1]], tagNumbers[lineParts[2]], tagNumbers[lineParts[3]])] = freq
            
    return NGram(tagNumbers, numberTags, uniGramFreqs, biGramFreqs, triGramFreqs, quatoGramFreqs)

class Model:
    def __init__(self, wordTagFreqReader, nGramReader):
        """
        Parameters:
            wordTagFreqReader: file object
            nGramReader: file object
        """
        # NGram
        nGrams = readNGrams(nGramReader)
        # WordFreq
        wordTagFreqs = readWordTagFreq(wordTagFreqReader, nGrams.getTagNumber())

        self.wordTagFreqs = deepcopy(wordTagFreqs.getWordTagFreq())
        self.tagNumbers = deepcopy(nGrams.getTagNumber())
        self.numberTags = deepcopy(nGrams.getNumberTag())
        self.uniGramFreqs = deepcopy(nGrams.getUniGramFreq())
        self.biGramFreqs = deepcopy(nGrams.getBiGramFreq())
        self.triGramFreqs = deepcopy(nGrams.getTriGramFreq())
        self.quatoGramFreqs = deepcopy(nGrams.getQuatoGramFreq())

    def getBiGrams(self):
        #Returns Map<BiGram, Integer>
        return self.biGramFreqs

    def getLexicon(self):
        #Returns Map<String, Map<Integer, Integer>>
        return self.wordTagFreqs

    def getNumberTags(self):
        #Returns Map<Integer, String>
        return self.numberTags

    def getTagNumbers(self):
        #Returns Map<String, Integer>
        return self.tagNumbers

    def getTriGrams(self):
        #Returns Map<TriGram, Integer>
        return self.triGramFreqs

    def getQuatoGrams(self):
        #Returns Map<QuatoGram, Integer>
        return self.quatoGramFreqs

    def getUniGrams(self):
        #Returns Map<UniGram, Integer>
        return self.uniGramFreqs

class UniGram:
    def __init__(self, t1=-1):
        self.tag1 = t1

    def __eq__(self, other):
        if other == None or self.__class__ != other.__class__:
            return False
        return (self.tag1 == other.tag1)

    def __hash__(self):
        return self.tag1

    def t1(self):
        return self.tag1

class BiGram:
    def __init__(self, t1=-1, t2=-1):
        self.tag1 = t1
        self.tag2 = t2

    def __eq__(self, other):
        if other is None or self.__class__ != other.__class__: 
            return False
        # BiGram
        return self.tag1 == other.tag1 and self.tag2 == other.tag2

    def __hash__(self):
        # int
        seed = self.tag1
        seed ^= self.tag2 + -1640531527 + (seed << 6) + (seed >> 2)
        return seed

    def t1(self):
        return self.tag1

    def t2(self):
        return self.tag2

class TriGram:
    def __init__(self, t1, t2, t3):
        self.tag1 = t1
        self.tag2 = t2
        self.tag3 = t3

    def __eq__(self, other):
        if other == None or self.__class__ != other.__class__:
            return False
        # TriGram
        return (self.tag1 == other.tag1 and self.tag2 == other.tag2 and self.tag3 == other.tag3)

    def __hash__(self):
        # int
        seed = 0;
        seed = self.tag1
        seed ^= self.tag2 + -1640531527 + (seed << 6) + (seed >> 2)
        seed ^= self.tag3 + -1640531527 + (seed << 6) + (seed >> 2)
        return seed

    def t1(self):
        return self.tag1

    def t2(self):
        return self.tag2

    def t3(self):
        return self.tag3

class QuatoGram:
    def __init__(self, t1, t2, t3, t4):
        self.tag1 = t1
        self.tag2 = t2
        self.tag3 = t3
        self.tag4 = t4

    def __eq__(self, other):
        if other == None or self.__class__ != other.__class__:
            return False
        # QuatoGram
        return (self.tag1 == other.tag1 and self.tag2 == other.tag2 and self.tag3 == other.tag3 and self.tag4 == other.tag4)

    def __hash__(self):
        # int
        seed = 0;
        seed = self.tag1
        seed ^= self.tag2 + -1640531527 + (seed << 6) + (seed >> 2)
        seed ^= self.tag3 + -1640531527 + (seed << 6) + (seed >> 2)
        seed ^= self.tag4 + -1640531527 + (seed << 6) + (seed >> 2)
        return seed

    def t1(self):
        return self.tag1

    def t2(self):
        return self.tag2

    def t3(self):
        return self.tag3

    def t4(self):
        return self.tag4

class Smoother:
    """
    Parameters:
        Map<UniGram, Integer> UniGramFreqs
        Map<BiGram, Integer> BiGramFreqs
        Map<TriGram, Integer> TriGramFreqs
        Map<QuatoGram, Integer> QuatoGramFreqs
        double BigramLambda
    """
    def __init__(self, UniGramFreqs, BiGramFreqs, TriGramFreqs, QuatoGramFreqs, BigramLambda):
        self.UniGramFreq = UniGramFreqs
        self.BiGramFreq = BiGramFreqs
        self.TriGramFreq = TriGramFreqs
        self.QuatoGramFreq = QuatoGramFreqs
        self.TriGramCache = {}
        self.BiGramCache = {}
        self.BigramLambda = BigramLambda
        self.calculateCorpusSize()
        self.calculateLambdas()

    def uniGramProb(self, uniGram):
        """
        Returns double
        Parameters:
            uniGram: UniGram
        """
        # UniGram
        t1 = UniGram(uniGram.t1())
        # double
        uniGramProb = math.log(self.UniGramFreq[t1] / float(self.corpusSize))
        return uniGramProb

    def biGramProb(self, biGram):
        """
        Returns double
        Parameters:
            biGram: BiGram
        """
        try:
            if biGram in self.BiGramCache: 
                return self.BiGramCache[biGram]
            # UniGram
            t2 = UniGram(biGram.t2())
            
            # double
            uniGramProb = self.UniGramFreq[t2] / float(self.corpusSize)
            
            # BiGram
            t1t2 = BiGram(biGram.t1(), biGram.t2())
            # UniGram
            t1 = UniGram(biGram.t1())
            # double
            biGramProb = 0.0
            if t1 in self.UniGramFreq and t1t2 in self.BiGramFreq: 
                biGramProb = self.BiGramFreq[t1t2] / float(self.UniGramFreq[t1])
            # double
            prob = math.log(self.BigramLambda * uniGramProb + (1 - self.BigramLambda) * biGramProb)
            self.BiGramCache[biGram] = prob
            return prob
        except:
            pass

    def triGramProb(self, triGram):
        """
        Returns double
        Parameters:
            triGram: TriGram
        """
        if triGram in self.TriGramCache: 
            return self.TriGramCache[triGram]
        # UniGram
        t3 = UniGram(triGram.t3())
        # double
        uniGramProb = self.UniGramFreq[t3] / float(self.corpusSize)
        # BiGram
        t2t3 = BiGram(triGram.t2(), triGram.t3())
        # UniGram
        t2 = UniGram(triGram.t2())
        # double
        biGramProb = 0.0
        if t2 in self.UniGramFreq and t2t3 in self.BiGramFreq: 
            biGramProb = self.BiGramFreq[t2t3] / float(self.UniGramFreq[t2])
        # BiGram
        t1t2 = BiGram(triGram.t1(), triGram.t2())
        # double
        triGramProb = 0.0
        if t1t2 in self.BiGramFreq and triGram in self.TriGramFreq: 
            triGramProb = self.TriGramFreq[triGram] / float(self.BiGramFreq[t1t2])
        # double
        prob = math.log(self.d_l1 * uniGramProb + self.d_l2 * biGramProb + self.d_l3 * triGramProb)
        self.TriGramCache[triGram] = prob
        return prob

    def triGramProbSucceed(self, triGram):
        """
        Returns double
        Parameters:
            triGram: TriGram
        """
        # int
        B = 0
        # int
        N = 0
        # int
        X = 0
        if triGram in self.TriGramCache: 
            return self.TriGramCache[triGram]
        for entry in self.UniGramFreq:
            t1t2t3 = TriGram(triGram.t1(), entry.t1(), triGram.t3())
            if t1t2t3 in self.TriGramFreq: 
                B += 1
                N += self.TriGramFreq[t1t2t3]


        if triGram in self.TriGramFreq: 
            X = self.TriGramFreq[triGram]

        # double
        prob = 1.0E-8
        if N != 0: 
            prob = float( X + 0.5) / float(N + (0.5 * B))

        self.TriGramCache[triGram] = math.log(prob)
        return math.log(prob)

    def quatoGramProbSucceed(self, quatoGram):
        """
        Returns double
        Parameters:
            quatoGram: QuatoGram
        """
        # int
        B = 0
        # int
        N = 0
        # int
        X = 0
        for entry in self.UniGramFreq:
            t1t2t3t4 = QuatoGram(quatoGram.t1(), quatoGram.t2(), entry.t1(), quatoGram.t4())
            if t1t2t3t4 in self.QuatoGramFreq: 
                B += 1
                N += self.QuatoGramFreq[t1t2t3t4]


        if quatoGram in self.QuatoGramFreq: 
            X = self.QuatoGramFreq[quatoGram]

        # double
        prob = 1.0E-8
        if N != 0: 
            prob = float( X + BigramLambda) / float(N + (BigramLambda * B))
        return math.log(prob)

    def calculateCorpusSize(self):
        self.corpusSize = 0
        for entry in self.UniGramFreq:
            self.corpusSize += self.UniGramFreq[entry];

    def calculateLambdas(self):
        # int
        l1f = 0
        # int
        l2f = 0
        # int
        l3f = 0
        for triGramEntry in self.TriGramFreq:
            t1t2t3 = triGramEntry
            # BiGram
            t1t2 = BiGram(t1t2t3.t1(), t1t2t3.t2())
            # double
            l3p = 0.0;
            if t1t2 in self.BiGramFreq: 
                #l3p = (self.TriGramFreq[triGramEntry] - 1) / float(self.BiGramFreq[t1t2] - 1)
                l3p = (self.TriGramFreq[triGramEntry] - 1) / float(self.BiGramFreq[t1t2])
            # BiGram
            t2t3 = BiGram(t1t2t3.t2(), t1t2t3.t3())
            # UniGram
            t2 = UniGram(t1t2t3.t2())
            # double
            l2p = 0.0
            if t2 in self.UniGramFreq and t2t3 in self.BiGramFreq: 
                #l2p = (self.BiGramFreq[t2t3] - 1) / float(self.UniGramFreq[t2] - 1)
                l2p = (self.BiGramFreq[t2t3] - 1) / float(self.UniGramFreq[t2])
            # UniGram
            t3 = UniGram(t1t2t3.t3())
            # double
            l1p = 0.0
            if t3 in self.UniGramFreq: 
                l1p = (self.UniGramFreq[t3] - 1) / float(self.corpusSize - 1)
            if l1p > l2p and l1p > l3p: 
                l1f += self.TriGramFreq[triGramEntry]
            else:
                if l2p > l1p and l2p > l3p: 
                    l2f += self.TriGramFreq[triGramEntry]
                else:
                    l3f += self.TriGramFreq[triGramEntry]

        # double
        totalTriGrams = l1f + l2f + l3f
        if totalTriGrams == 0:
            self.d_l1 = 1e300 #float('inf')
            self.d_l2 = 1e300 #float('inf')
            self.d_l3 = 1e300 #float('inf')
        else:
            totalTriGrams = float(totalTriGrams)
            self.d_l1 = l1f / totalTriGrams
            self.d_l2 = l2f / totalTriGrams
            self.d_l3 = l3f / totalTriGrams

class NGramProb:
    """
    Parameters:
        Map<UniGram, Integer> uniGramFreqs
        Map<BiGram, Integer> biGramFreqs
        Map<TriGram, Integer> triGramFreqs
        Map<QuatoGram, Integer> quatoGramFreqs
        double BigramLambda
    """
    def __init__(self, uniGramFreqs, biGramFreqs, triGramFreqs, quatoGramFreqs, BigramLambda):
        self.uniGramFreqs = uniGramFreqs
        self.biGramFreqs = biGramFreqs
        self.triGramFreqs = triGramFreqs
        self.quatoGramFreqs = quatoGramFreqs
        self.sm = Smoother(self.uniGramFreqs, self.biGramFreqs, self.triGramFreqs, self.quatoGramFreqs, BigramLambda)

    def UnigramProb(self, u):
        return self.sm.uniGramProb(u)

    def BigramProb(self, b):
        return self.sm.biGramProb(b)

    def TrigramProb(self, t):
        return self.sm.triGramProb(t)

    def isBigramExist(self, b):
        return b in self.biGramFreqs

    def isTrigramExist(self, t):
        return t in self.triGramFreqs

    def TrigramProbSucceed(self, t):
        return self.sm.triGramProbSucceed(t)

    def QuatogramProbSucceed(self, t):
        return self.sm.quatoGramProbSucceed(t)
