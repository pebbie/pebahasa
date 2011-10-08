from ngram import *
import math
import re
import java2python_runtime

class WordProb:
    """
    Parameters:
        Map<String, Map<Integer, Integer>> wordTagFreqs
        Map<UniGram, Integer> uniGramFreqs
        Map<Integer, String> NumberTags
        OOVWordProb OOV
        DicLexicon dl
        boolean debug
    """
    def __init__(self, wordTagFreqs={}, uniGramFreqs={}, NumberTags={}, OOV=None, dl=None, debug=False):
        self.wordTagProbs = {}
        self.debug = debug
        self.NumberTags = NumberTags
        self.TagCount = len(uniGramFreqs)
        self.OOVWord = OOV
        self.DL = dl
        self.sumWordTagProbs(wordTagFreqs, uniGramFreqs)

    def isOOV(self, word):
        return word not in self.wordTagProbs

    def sumWordTagProbs(self, wordTagFreqs, uniGramFreqs):
        """
        Parameters:
            wordTagFreqs: Map<String, Map<Integer, Integer>>
            uniGramFreqs: Map<UniGram, Integer>
        """
        for wordEntry in wordTagFreqs:
            word = wordEntry
            if word not in self.wordTagProbs: 
                self.wordTagProbs[word] = {}

            for tagEntry in wordTagFreqs[wordEntry]:
                tag = tagEntry;
                # double
                freq = float(wordTagFreqs[wordEntry][tagEntry])
                # double
                p = 0.0
                if self.debug: 
                    print "WordProb : ", word , " " , freq , " " , uniGramFreqs[UniGram(tag)] , "#"
                p = math.log(freq / float(uniGramFreqs[UniGram(tag)]));
                self.wordTagProbs[word][tag] = p

    def tagProbs(self, word):
        """
        Returns Map<Integer, Double>
        Parameters:
            word: String
        """
        pass

class DicLexicon:
    """
    Parameters:
        String namaFileKamus
        String namaFileTable
        Map<Integer, String> numberTags
    """
    def __init__(self, namaFileKamus, namaFileTable, numberTags):
        self.catTable = {}
        self.lexicon = {}
        self.loadCatTable(namaFileTable)
        self.loadDicLexicon(namaFileKamus)
        self.numberTags = numberTags
        self.jumAccess = 0

    def usingLexicon(self, word, initVector):
        """
        Returns Map<Integer, Double>
        Parameters:
            word: StringinitVector: Map<Integer, Double>
        """
        # Map<Integer, Double>
        ret = {}
        # List<String>
        temp = []
        # List<String>
        poslex = self.getPosLexicon(word)
        if poslex != None: 
            for i in xrange(0, len(poslex)): # List<String>
                sub = self.getSubCat(poslex[i])
                for j in xrange(0, len(sub)): 
                    temp.append(sub[j])

        for e in initVector: 
            if self.numberTags[e] in temp: 
                ret[e] = initVector[e]


        if len(ret) == 0: 
            return initVector
        return ret


    def getPosLexicon(self, word):
        """
        Returns List<String>
        Parameters:
            word: String
        """
        # List<String>
        ret = None
        if word in self.lexicon: 
            ret = self.lexicon[word]
            self.jumAccess += 1

        return ret


    def getSubCat(self, dicpos):
        """
        Returns List<String>
        Parameters:
            dicpos: String
        """
        # List<String>
        ret = None
        if dicpos in self.catTable: 
            ret = self.catTable[dicpos]

        return ret


    def isInList(self, pos, L):
        """
        Returns boolean
        Parameters:
            pos: String
            L: List<String>
        """
        return pos in L


    def loadDicLexicon(self, namaFileKamus):
        """
        Returns void
        Parameters:
            namaFileKamus: String
        """
        try:
            reader = open(namaFileKamus, "r")
            for line in reader.readlines():
                line = line.strip()
                if len(line) <= 1: 
                    continue
                lineParts = re.split("\\s+", line)
                if lineParts[1] in self.catTable: 
                    lex = str(lineParts[0])
                    pos = []
                    for i in xrange(0, len(lineParts)): 
                        if lineParts[i] in self.catTable: 
                            pos.append(lineParts[i])
                            
                    self.lexicon[lex] = pos


        except:
            pass

    def loadCatTable(self, namaFile):
        """
        Returns void
        Parameters:
            namaFile: String
        """
        try:
            reader = open(namaFile, "r");
            for line in reader.readlines():
                line = line.strip()
                if len(line) <= 1: 
                    continue
                # String[]
                lineParts = re.split("\\s+", line)
                # List<String>
                subcat = []
                for i in xrange( 1, len(lineParts)):
                    subcat.append(lineParts[i])

                self.catTable[lineParts[0]] = subcat

        except:
            print("Failed to read category table")
            print(e)
            exit(1)

class AffixTree:
    class node:
        """
        Type:
            Map<Integer, Integer>
        """
        tagFreq = None

        """
        Type:
            double
        """
        IG = None

        def __init__(self):
            self.childs = {}
            self.tagFreq = {}
            self.totalTagFreq = 0
            self.deleted = False


        def getDeleted(self):
            return self.deleted

        def setDeleted(self, n):
            self.deleted = n

        def getIG(self):
            return self.IG

        def setIG(self, n):
            self.IG = n

        def getTagFreq(self):
            return self.tagFreq

        def getTotalTagFreq(self):
            return self.totalTagFreq

        def getChilds(self):
            return self.childs

        def addAffix(self, reverseAffix, tagFreqs):
            """
            Returns void
            Parameters:
                reverseAffix: String
                tagFreqs: Map<Integer, Integer>
            """
            for entry in tagFreqs: 
                # Integer
                tag = entry
                # int
                tagFrequency = tagFreqs[entry]
                if tag not in self.tagFreq: 
                    self.tagFreq[tag] = tagFrequency
                else:
                    self.tagFreq[tag] += tagFrequency

                self.totalTagFreq += tagFrequency

            if len(reverseAffix) == 0: return

            # Character
            transitionChar = reverseAffix[0]
            if transitionChar not in self.childs: 
                self.childs[transitionChar] = AffixTree.node()

            self.childs[transitionChar].addAffix(reverseAffix[1:], tagFreqs)


        def affixTagProbs(self, reverseAffix, tagProbs):
            """
            Returns Map<Integer, Double>
            Parameters:
                reverseAffix: StringtagProbs: Map<Integer, Double>
            """
            return {}
    #END of inner class AffixTree.node
            
    """
    Parameters:
        Map<UniGram, Integer> uniGrams
        int Treshold
        int maxAffixLength
    """
    def __init__(self, uniGrams, Treshold, maxAffixLength):
        self.Root = AffixTree.node()
        self.maxAffixLength = maxAffixLength
        self.Treshold = Treshold
        self.uniGrams = uniGrams #copy?

    def getRoot(self):
        return self.Root

    def addWord(self, word, tagFreqs):
        """
        Returns void
        Parameters:
            word: String
            tagFreqs: Map<Integer, Integer>
        """
        # String
        reverseWord = self.reverseWord(word)
        if len(reverseWord) > self.maxAffixLength: 
            reverseWord = reverseWord[0:self.maxAffixLength]

        self.Root.addAffix(reverseWord, tagFreqs)

    def affixTagProbs(self, word):
        """
        Returns Map<Integer, Double>
        Parameters:
            word: String
        """
        # String
        reverseWord = self.reverseWord(word);
        if len(reverseWord) > self.maxAffixLength: 
            reverseWord = reverseWord[0: self.maxAffixLength]

        if self.Root.getTotalTagFreq() == 0: 
            print("Error: no tree constructed, you should decrease parameter \"minWordFreq\"")
            exit(1)

        return self.affixTagProbsRecc(reverseWord, self.Root)

    def affixTagProbsRecc(self, reverseAffix, n):
        """
        Returns Map<Integer, Double>
        Parameters:
            reverseAffix: String
            n: node
        """
        transitionChar = "\0"
        childExist = False;
        childExistAndCharInDeleted = False
        isDeletedAreaExist = False
        jumFreqDeleted = 0
        tagFreqDeleted = {}
        if len(reverseAffix) != 0: 
            transitionChar = reverseAffix[0];
            for entry in n.getChilds(): 
                # node
                temp = n.getChilds()[entry]
                # Character
                c = entry
                if not temp.getDeleted(): 
                    childExist = True
                if temp.getDeleted() and (transitionChar == c): 
                    childExistAndCharInDeleted = True
                if temp.getDeleted(): 
                    isDeletedAreaExist = True;
                    jumFreqDeleted += temp.getTotalTagFreq()
                    for e in temp.getTagFreq(): 
                        if e not in tagFreqDeleted: 
                            tagFreqDeleted[e] = 0

                        tagFreqDeleted[e] += temp.getTagFreq()[e]

        if not childExist or len(reverseAffix) == 0: 
            return self.changeToTagProb(n.getTagFreq(), n.getTotalTagFreq())
        else:
            if transitionChar not in n.getChilds() or childExistAndCharInDeleted: 
                if isDeletedAreaExist: 
                    return self.changeToTagProb(tagFreqDeleted, jumFreqDeleted)
                else:
                    return self.changeToTagProb(n.getTagFreq(), n.getTotalTagFreq())
            else:
                return self.affixTagProbsRecc(reverseAffix[1:], n.getChilds()[transitionChar])

    def Pruning(self):
        self.PruningRecc(self.Root, 1e300) #float('inf'))

    def PruningRecc(self, n, IMparent):
        """
        Returns void
        Parameters:
            n: node
            IMparent: double
        """
        IM = self.computeIM(n.getTagFreq(), n.getTotalTagFreq())
        childDeletedAll = True
        for entry in n.getChilds(): 
            self.PruningRecc(n.getChilds()[entry], IM)
            childDeletedAll = childDeletedAll and n.getChilds()[entry].getDeleted()

        # double
        IG = n.getTotalTagFreq() * (IMparent - IM)
        n.setIG(IG)
        if IG < self.Treshold: 
            if len(n.getChilds()) == 0 or childDeletedAll: 
                n.setDeleted(True)

    def computeIM(self, tagFreq, totalFreq):
        """
        Returns double
        Parameters:
            tagFreq: Map<Integer, Integer>
            totalFreq: int
        """
        # double
        i = 0.
        for entry in tagFreq: # double
            temp = tagFreq[entry] / float(totalFreq)
            i += (temp) * self.log2(temp)

        return -1 * i

    def changeToTagProb(self, tagFreq, totalFreq):
        """
        Returns Map<Integer, Double>
        Parameters:
            tagFreq: Map<Integer, Integer>
            totalFreq: int
        """
        # Map<Integer, Double>
        TagProb = {}
        for entry in tagFreq: # double
            prob = tagFreq[entry] / float(totalFreq)
            TagProb[entry] = prob

        return TagProb

    def log2(self, x):
        return math.log(x) / math.log(2)

    def viewAffixTree(self):
        print("#")
        viewAffixTreeRecc(self.Root, 3)

    def viewAffixTreeRecc(self, n, indentasi):
        """
        Returns void
        Parameters:
            n: node
            indentasi: int
        """
        # int
        i = None
        for entry in n.getChilds(): 
            if not n.getChilds()[entry].getDeleted(): 
                print " "*indentasi,

                print(entry + "|" + n.getChilds()[entry].getIG() + "|" + n.getChilds()[entry].getDeleted())
                for e in n.getChilds()[entry].getTagFreq(): 
                    print("+" + e + ":" + n.getChilds()[entry].getTagFreq()[e] + "|")

                print("=" , n.getChilds()[entry].getTotalTagFreq() , "")

            viewAffixTreeRecc(n.getChilds()[entry], 3 + indentasi)

    def reverseWord(self, src):
        return src[::-1]

# package NLP_ITB.POSTagger.HMM.WordProb
class KnownWordProb(WordProb):
    """
    Parameters:
        Map<String, Map<Integer, Integer>> wordTagFreqs
        Map<UniGram, Integer> uniGramFreqs
        Map<Integer, String> NumberTags
        OOVWordProb OOV
        DicLexicon dl
        boolean debug
    """
    def __init__(self, wordTagFreqs, uniGramFreqs, NumberTags, OOV, dl, debug):
        WordProb.__init__(self, wordTagFreqs, uniGramFreqs, NumberTags, OOV, dl, debug)


    def tagProbs(self, word):
        """
        Returns Map<Integer, Double>
        Parameters:
            word: String
        """
        if word in self.wordTagProbs: 
            return self.wordTagProbs[word]

        if self.OOVWord == None: 
            wp = {}
            i = 0
            for i in xrange(0, self.TagCount): 
                if (this.NumberTags[i] == "NN"): 
                    wp[i] = 1.0

            return wp

        if word[0].isupper(): 
            # String
            lowWord = word.lower();
            if lowWord in self.wordTagProbs: 
                return self.wordTagProbs[lowWord]

        if self.DL != None: 
            return self.DL.usingLexicon(word, self.OOVWord.tagProbs(word))
        else:
            return self.OOVWord.tagProbs(word)

# package NLP_ITB.POSTagger.HMM.WordProb
class OOVWordProb(WordProb):
    """
    Parameters:
        Map<String, Map<Integer, Integer>> lexicon
        Map<UniGram, Integer> uniGrams
        int maxAffixLength
        int Treshold
        int minWordFreq
        int mode
        boolean debug
    """
    def __init__(self, lexicon, uniGrams, maxAffixLength, Treshold, minWordFreq, mode, dbg):
        WordProb.__init__(self, debug=dbg)
        self.mode = mode
        self.UPsuffixTree = AffixTree(uniGrams, Treshold, maxAffixLength)
        self.UPprefixTree = AffixTree(uniGrams, Treshold, maxAffixLength)
        self.LOWsuffixTree = AffixTree(uniGrams, Treshold, maxAffixLength)
        self.LOWprefixTree = AffixTree(uniGrams, Treshold, maxAffixLength)
        self.CARprefixTree = AffixTree(uniGrams, Treshold, maxAffixLength)
        for wordEntry in lexicon: # String
            word = wordEntry
            wordFreq = 0
            if len(word) == 0 or (word == "<STARTTAG>") or (word == "<ENDTAG>"): 
                continue

            for tagEntry in lexicon[wordEntry]: 
                wordFreq += lexicon[wordEntry][tagEntry]

            # AffixTree
            suffixtree = None
            # AffixTree
            prefixtree = None
            if self.cardinalPattern.match(word) is not None: 
                prefixtree = self.CARprefixTree
            else:
                # boolean
                isUpper = word[0].isupper()
                if self.mode == 1 or self.mode == 2: 
                    suffixtree = java2python_runtime.ternary(isUpper, self.UPsuffixTree, self.LOWsuffixTree)
                if self.mode == 0 or self.mode == 2: 
                    prefixtree = java2python_runtime.ternary(isUpper, self.UPprefixTree, self.LOWprefixTree)

            if wordFreq > minWordFreq: 
                if suffixtree is not None: 
                    suffixtree.addWord(word, lexicon[wordEntry]);
                if prefixtree is not None: 
                    prefixtree.addWord(self.reverseWord(word), lexicon[wordEntry])


        if self.UPsuffixTree is not None: self.UPsuffixTree.Pruning()
        if self.UPprefixTree is not None: self.UPprefixTree.Pruning()
        if self.LOWsuffixTree is not None: self.LOWsuffixTree.Pruning()
        if self.LOWprefixTree is not None: self.LOWprefixTree.Pruning()
        if self.CARprefixTree is not None: self.CARprefixTree.Pruning()

    """
    Type:
        int
    """
    mode = None

    """
    Type:
        AffixTree
    """
    UPsuffixTree = None

    """
    Type:
        AffixTree
    """
    UPprefixTree = None

    """
    Type:
        AffixTree
    """
    LOWsuffixTree = None

    """
    Type:
        AffixTree
    """
    LOWprefixTree = None

    """
    Type:
        AffixTree
    """
    CARprefixTree = None

    #cardinalPattern = re.compile(r"^(\d+)|(\d+\\.)|([0-9.,:-]+\d+)|([a-zA-Z]{1,5}+[.,:-]+\d+)|(\d+[a-zA-Z]{1,3})$")
    cardinalPattern = re.compile(r"^(\d+)|(\d+\\.)|([0-9.,:-]+\d+)|(\d+[a-zA-Z]{1,3})$")

    def getUPSuffixTree(self):
        return self.UPsuffixTree

    def getUPPrefixTree(self):
        return self.UPprefixTree

    def getLOWSuffixTree(self):
        return self.LOWsuffixTree

    def getLOWPrefixTree(self):
        return self.LOWprefixTree

    def getCARPrefixTree(self):
        return self.CARprefixTree

    def tagProbs(self, word):
        """
        Returns Map<Integer, Double>
        Parameters:
            word: String
        """
        # AffixTree
        suffixtree = None
        # AffixTree
        prefixtree = None
        # Map<Integer, Double>
        preProbVec = None
        # Map<Integer, Double>
        sufProbVec = None
        if self.cardinalPattern.match(word) is not None: 
            prefixtree = self.CARprefixTree
            preProbVec = prefixtree.affixTagProbs(word)
        else:
            # boolean
            isUpper = word[0].isupper();
            if self.mode == 1 or self.mode == 2: 
                suffixtree = java2python_runtime.ternary(isUpper, self.UPsuffixTree, self.LOWsuffixTree)
                sufProbVec = suffixtree.affixTagProbs(word)

            if self.mode == 0 or self.mode == 2: 
                prefixtree = java2python_runtime.ternary(isUpper, self.UPprefixTree, self.LOWprefixTree)
                preProbVec = prefixtree.affixTagProbs(self.reverseWord(word))


        if suffixtree is not None and prefixtree is not None: 
            return self.CombinePreSuff(preProbVec, sufProbVec)
        else:
            if suffixtree == None: 
                return self.ChangeIntoLog(preProbVec)
            else:
                return self.ChangeIntoLog(sufProbVec)



    def CombinePreSuff(self, prefix, suffix):
        """
        Returns Map<Integer, Double>
        Parameters:
            prefix: Map<Integer, Double>suffix: Map<Integer, Double>
        """
        # Map<Integer, Double>
        combine = {}
        for e1 in prefix: combine[e1] = prefix[e1]

        for e2 in suffix: 
            if e2 not in combine: 
                combine[e2] = 0.0
            combine[e2] += suffix[e2]

        return self.Normalizing(combine)


    def Normalizing(self, v):
        """
        Returns Map<Integer, Double>
        Parameters:
            v: Map<Integer, Double>
        """
        total = 0
        for entry in v: total += v[entry]

        for entry in v: 
            v[entry] = math.log(float(v[entry]) / float(total));

        return v


    def ChangeIntoLog(self, v):
        """
        Returns Map<Integer, Double>
        Parameters:
            v: Map<Integer, Double>
        """
        for entry in v: 
            v[entry] = math.log(v[entry]);

        return v


    def reverseWord(self, src):
        return src[::-1]



