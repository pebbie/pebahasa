from ngram import *
from prob import *
import math
from copy import copy

class Sequence:
    """
    Parameters:
        List<Integer> sequence
        double logProb
        Model model
    """
    def __init__(self, sequence, logProb, model):
        self.seq = sequence
        self.logProb = logProb
        self.numberTags = model.getNumberTags()

    def sequence(self):
        """
        Returns List<String>
        """
        # List<String>
        tagSequence = []
        for tagNumber in self.seq:
            tagSequence.append(self.numberTags[tagNumber])

        return tagSequence

    def logProb(self):
        return self.logProb

class Decoder:
    """
    Parameters:
        Model model
        WordProb WH
        NGramProb NG
        double beamFactor
        boolean debug
    """
    def __init__(self, model, WH, NG, beamFactor, debug):
        self.WH = WH
        self.model = model
        self.NG = NG
        self.beamFactor = math.log(beamFactor)
        self.debug = debug


class MatrixEntryBigram:
    """ Type:
        MatrixEntryBigram
    """
    bps = None


    """ Type:
        double
    """
    probs = 0.


    """
    Parameters:
        int tag
    """
    def __init__(self, tag):
        self.tag = tag


class MatrixEntryTrigram:
    """
    Type:
        Map<MatrixEntryTrigram, Double>
    """
    probs = {}

    """
    Type:
        Map<MatrixEntryTrigram, MatrixEntryTrigram>
    """
    bps = {}

    """
    Parameters:
        int tag
    """
    def __init__(self, tag):
        self.tag = tag

class BigramDecoder(Decoder):
    """
    Parameters:
        Model model
        WordProb WH
        NGramProb NG
        double beamFactor
        boolean debug
    """
    def __init__(self, model, WH, NG, beamFactor, debug):
        Decoder.__init__(self, model, WH, NG, beamFactor, debug)
        self.jumBigram = 0
        self.jumBigramOOV = 0

    def backtrack(self, tagMatrix, model):
        """
        Returns Sequence
        Parameters:
            tagMatrix: List<List<MatrixEntryBigram>>
            model: Model
        """
        # double
        highestProb = -1e300 #float('-inf')
        # List<MatrixEntryBigram>
        lastColumn = tagMatrix[len(tagMatrix) - 1]
        # MatrixEntryBigram
        tail = None
        # MatrixEntryBigram
        beforeTail = None
        for entry in lastColumn:
            if entry.probs > highestProb: 
                tail = entry
                beforeTail = entry.bps


        # List<Integer>
        tagSequence = []
        for i in xrange(0, len(tagMatrix)): 
            tagSequence.append(tail.tag)
            if beforeTail is not None: 
                tail = beforeTail
                beforeTail = tail.bps

        tagSequence.reverse()
        return Sequence(tagSequence, highestProb, model)

    def viterbi(self, sentence):
        """
        Returns List<List<MatrixEntryBigram>>
        Parameters:
            sentence: List<String>
        """
        # List<List<MatrixEntryBigram>>
        tagMatrix = []
        # int
        startTag = self.model.getTagNumbers()[sentence[1]]

        # MatrixEntryBigram
        firstEntry = MatrixEntryBigram(startTag);
        tagMatrix.append([]);
        tagMatrix[0].append(MatrixEntryBigram(startTag))
        tagMatrix[0][0].probs = 0.0
        tagMatrix[0][0].bps = None
        
        for i in xrange(2, len(sentence)): 
            tagMatrix.append([])
            if self.debug: 
                print "###"
            for tagEntry in self.WH.tagProbs(sentence[i]): 
                # MatrixEntryBigram
                newEntry = MatrixEntryBigram(tagEntry)
                # double
                highestProb = -1e300 #float('-inf')
                # MatrixEntryBigram
                maxEntry = None
                if self.debug: 
                    print "@cari max prev:"
                for t in tagMatrix[i - 2]: 
                    # BiGram
                    bg = BiGram(t.tag, tagEntry)
                    self.jumBigram += 1
                    if not self.NG.isBigramExist(bg): 
                        self.jumBigramOOV += 1
                    
                    # double
                    bigramProb = self.NG.BigramProb(bg)
                    # double
                    
                    prob = bigramProb + self.WH.tagProbs(sentence[i])[tagEntry] + t.probs
                    if prob > highestProb: 
                        highestProb = prob
                        maxEntry = t
                        newEntry.probs = prob
                    
                    if self.debug: 
                        print "BigramDecode : " , sentence[i] , "\nTag:" , tagEntry , "\nnow:", prob , " prev:" , t.probs , " " , bigramProb , " " , self.WH.tagProbs(sentence[i])[tagEntry]

                newEntry.bps = maxEntry
                tagMatrix[i - 1].append(newEntry)

            if self.debug: 
                print "--"
        
        return tagMatrix

class TrigramDecoder(Decoder):
    """
    Parameters:
        Model model
        WordProb WH
        NGramProb NG
        double beamFactor
        boolean debug
    """
    def __init__(self, model, WH, NG, beamFactor, debug):
        Decoder.__init__(self, model, WH, NG, beamFactor, debug)
        self.jumTrigram = 0
        self.jumTrigramOOV = 0

    def backtrack(self, tagMatrix, model):
        """
        Returns Sequence
        Parameters:
            tagMatrix: List<List<MatrixEntryTrigram>>model: Model
        """
        try:
            # double
            highestProb = -1e300 #float('-inf')
            # MatrixEntryTrigram
            tail = None
            # MatrixEntryTrigram
            beforeTail = None
            # List<MatrixEntryTrigram>
            lastColumn = tagMatrix[-1]
            for entry in lastColumn: 
                for probEntry in entry.probs: 
                    if entry.probs[probEntry] > highestProb: 
                        highestProb = entry.probs[probEntry]
                        tail = entry
                        beforeTail = probEntry

            # List<Integer>
            tagSequence = []
            for i in xrange(0, len(tagMatrix)): 
                tagSequence.append(tail.tag)
                if beforeTail != None: 
                    # MatrixEntryTrigram
                    tmp = tail.bps[beforeTail]
                    tail = beforeTail
                    beforeTail = tmp


            tagSequence.reverse()
            return Sequence(tagSequence, highestProb, model)
        except:
            print "backtrack error"

    def viterbi(self, sentence):
        """
        Returns List<List<MatrixEntryTrigram>>
        Parameters:
            sentence: List<String>
        """
        # List<List<MatrixEntryTrigram>>
        tagMatrix = []
        # int
        startTag = self.model.getTagNumbers()[sentence[0]]
        # MatrixEntryTrigram
        firstEntry = MatrixEntryTrigram(startTag)
        tagMatrix.append([])
        tagMatrix[0].append(firstEntry)
        tagMatrix.append([])
        tagMatrix[1].append(MatrixEntryTrigram(startTag))
        tagMatrix[1][0].probs[firstEntry] = 0.0
        tagMatrix[1][0].bps[firstEntry] = None
        # double
        beam = 0.0
        for i in xrange(2, len(sentence)): 
            # double
            columnHighestProb = -1e300 #float('-inf')
            tagMatrix.append([])
            for tagEntry in self.WH.tagProbs(sentence[i]): 
                # MatrixEntryTrigram
                newEntry = MatrixEntryTrigram(tagEntry)
                for t2 in tagMatrix[i - 1]: 
                    # double
                    highestProb = -1e300 #float('-inf')
                    # MatrixEntryTrigram
                    highestProbBp = None;
                    for t1Entry in t2.probs: 
                        if t2.probs[t1Entry] < beam: 
                            continue
                        # TriGram
                        curTriGram = TriGram(t1Entry.tag, t2.tag, tagEntry)
                        self.jumTrigram += 1
                        if not self.NG.isTrigramExist(curTriGram): 
                            self.jumTrigramOOV += 1
                        # double
                        triGramProb = self.NG.TrigramProb(curTriGram)
                        # double
                        prob = triGramProb + self.WH.tagProbs(sentence[i])[tagEntry] + t2.probs[t1Entry]
                        if prob > highestProb: 
                            highestProb = prob
                            highestProbBp = t1Entry


                    newEntry.probs[t2] = highestProb
                    newEntry.bps[t2] = highestProbBp
                    if highestProb > columnHighestProb: 
                        columnHighestProb = highestProb

                tagMatrix[i].append(newEntry)

            beam = columnHighestProb - self.beamFactor

        return tagMatrix


class BigramSucceedDecoder(Decoder):
    """

    Parameters:
        Model model
        WordProb WH
        NGramProb NG
        double beamFactor
        boolean debug
    """
    def __init__(self, model, WH, NG, beamFactor, debug):
        Decoder.__init__(self, model, WH, NG, beamFactor, debug)


    def backtrack(self, tagMatrix, model):
        """
        Returns Sequence
        Parameters:
            tagMatrix: List<List<MatrixEntryBigram>>model: Model


        """
        # double
        highestProb = -1e300 #float('-inf')
        # List<MatrixEntryBigram>
        lastColumn = tagMatrix[-1]
        # MatrixEntryBigram
        tail = None
        # MatrixEntryBigram
        beforeTail = None
        for entry in lastColumn: 
            if entry.probs > highestProb: 
                tail = entry
                beforeTail = entry.bps


        # List<Integer>
        tagSequence = []
        for i in xrange(0, len(tagMatrix)): 
            tagSequence.append(tail.tag)
            if beforeTail != None: 
                tail = beforeTail
                beforeTail = tail.bps


        tagSequence.reverse()
        return Sequence(tagSequence, highestProb, model)


    def viterbi(self, sentence):
        """
        Returns List<List<MatrixEntryBigram>>
        Parameters:
            sentence: List<String>
        """
        # List<List<MatrixEntryBigram>>
        tagMatrix = []
        # int
        startTag = self.model.getTagNumbers()[sentence[1]]
        # MatrixEntryBigram
        firstEntry = MatrixEntryBigram(startTag);
        tagMatrix.append([]);
        tagMatrix[0].append(MatrixEntryBigram(startTag))
        tagMatrix[0][0].probs = 0.0
        tagMatrix[0][0].bps = None
        for i in xrange(2, len(sentence)): 
            tagMatrix.append([])
            # int
            sepIndexCurr = sentence[i].rfind('/')
            # int
            sepIndexSucc = -2;
            if i < len(sentence) - 1: 
                sepIndexSucc = sentence[i + 1].rfind('/')
            if sepIndexCurr == -1 or sepIndexSucc == -1: 
                print "Error BigramSucceedDecoder: curr/succeed-ing POS tag missing.."
                return

            # String
            word = sentence[i][0:sepIndexCurr]
            # String
            Succeedtag = None
            if sepIndexSucc != -2: 
                Succeedtag = sentence[i + 1][sepIndexSucc + 1:]
            if self.debug: 
                print "###"
            for tagEntry in self.WH.tagProbs(word): 
                # MatrixEntryBigram
                newEntry = MatrixEntryBigram(tagEntry)
                # double
                highestProb = -1e300 #float('-inf')
                # MatrixEntryBigram
                maxEntry = None
                if self.debug: 
                    print "@cari max prev:\n"
                for t in tagMatrix[i - 2]: 
                    # double
                    prob = 0.0
                    if (i < len(sentence) - 1) and (self.WH.isOOV(word)): 
                        # int
                        succ = self.model.getTagNumbers()[Succeedtag]
                        # TriGram
                        tg = TriGram(t.tag, tagEntry, succ)
                        # double
                        trigramSuccedProb = self.NG.TrigramProbSucceed(tg)
                        prob = trigramSuccedProb + self.WH.tagProbs(word)[tagEntry] + t.probs
                    else:
                        # BiGram
                        bg = BiGram(t.tag, tagEntry)
                        # double
                        bigramProb = self.NG.BigramProb(bg)
                        prob = bigramProb + self.WH.tagProbs(word)[tagEntry] + t.probs

                    if prob > highestProb: 
                        highestProb = prob
                        maxEntry = t
                        newEntry.probs = prob


                newEntry.bps = maxEntry
                tagMatrix[i - 1].append(newEntry)

            if self.debug: 
                print "\n"
        return tagMatrix

class TrigramSucceedDecoder(Decoder):
    """
    Parameters:
        Model model
        WordProb WH
        NGramProb NG
        double beamFactor
        boolean debug
    """
    def __init__(self, model, WH, NG, beamFactor, debug):
        Decoder.__init__(self, model, WH, NG, beamFactor, debug)

    def backtrack(self, tagMatrix, model):
        """
        Returns Sequence
        Parameters:
            tagMatrix: List<List<MatrixEntryTrigram>>model: Model
        """
        try:
            # double
            highestProb = -1e300 #float('-inf')
            # MatrixEntryTrigram
            tail = None
            # MatrixEntryTrigram
            beforeTail = None
            # List<MatrixEntryTrigram>
            lastColumn = tagMatrix[-1]
            for entry in lastColumn: 
                for probEntry in entry.probs: 
                    if entry.probs[probEntry] > highestProb: 
                        highestProb = entry.probs[probEntry]
                        tail = entry
                        beforeTail = probEntry

            # List<Integer>
            tagSequence = []
            for i in xrange(0, len(tagMatrix)): 
                tagSequence.append(tail.tag)
                if beforeTail is not None: 
                    # MatrixEntryTrigram
                    tmp = tail.bps[beforeTail]
                    tail = beforeTail
                    beforeTail = tmp


            tagSequence.reverse()
            return Sequence(tagSequence, highestProb, model)
        except:
            print "TrigramSucceedDecoder.backtrack error"

    def viterbi(self, sentence):
        """
        Returns List<List<MatrixEntryTrigram>>
        Parameters:
            sentence: List<String>
        """
        # List<List<MatrixEntryTrigram>>
        tagMatrix = []
        # int
        startTag = self.model.getTagNumbers()[sentence[0]]
        # MatrixEntryTrigram
        firstEntry = MatrixEntryTrigram(startTag);
        tagMatrix.append([])
        tagMatrix[0].append(firstEntry)
        tagMatrix.append([])
        tagMatrix[1].append(MatrixEntryTrigram(startTag))
        tagMatrix[1][0].probs[firstEntry] = 0.0
        tagMatrix[1][0].bps[firstEntry] = None
        # double
        beam = 0.0
        for i in xrange(2, len(sentence)): 
            # double
            columnHighestProb = -1e300 #float('-inf')
            tagMatrix.append([])
            # int
            sepIndexCurr = sentence[i].rfind('/');
            # int
            sepIndexSucc = -2
            if i < len(sentence) - 1: 
                sepIndexSucc = sentence[i + 1].rfind('/')
            if sepIndexCurr == -1 or sepIndexSucc == -1: 
                print "Error BigramSucceedDecoder: curr/succeed-ing POS tag missing.."
                return

            # String
            word = sentence[i][0: sepIndexCurr]
            # String
            Succeedtag = None
            if sepIndexSucc != -2: 
                Succeedtag = sentence[i + 1][sepIndexSucc + 1:]
            for tagEntry in self.WH.tagProbs(word): 
                # MatrixEntryTrigram
                newEntry = MatrixEntryTrigram(tagEntry)
                for t2 in tagMatrix[i - 1]: 
                    # double
                    highestProb = -1e300 #float('-inf')
                    # MatrixEntryTrigram
                    highestProbBp = None
                    for t1Entry in t2.probs: 
                        if t2.probs[t1Entry] < beam: 
                            continue
                        # double
                        prob = 0.0
                        if (i < len(sentence) - 1) and (self.WH.isOOV(word)): 
                            # int
                            succ = self.model.getTagNumbers()[Succeedtag]
                            # QuatoGram
                            qg = QuatoGram(t1Entry.tag, t2.tag, tagEntry, succ)
                            # double
                            quatoProb = self.NG.QuatogramProbSucceed(qg)
                            prob = quatoProb + self.WH.tagProbs(word)[tagEntry] + t2.probs[t1Entry]
                        else:
                            # TriGram
                            curTriGram = TriGram(t1Entry.tag, t2.tag, tagEntry)
                            # double
                            triGramProb = self.NG.TrigramProb(curTriGram)
                            prob = triGramProb + self.WH.tagProbs(word)[tagEntry] + t2.probs[t1Entry]

                        if prob > highestProb: 
                            highestProb = prob
                            highestProbBp = t1Entry


                    newEntry.probs[t2] = highestProb
                    newEntry.bps[t2] = highestProbBp
                    if highestProb > columnHighestProb: 
                        columnHighestProb = highestProb

                tagMatrix[i].append(newEntry);

            beam = columnHighestProb - self.beamFactor

        return tagMatrix



class MainTagger:
    # Model
    model = None 

    # OOVWordProb
    ovp = None

    # DicLexicon
    dl = None

    # WordProb
    wp = None

    # NGramProb
    np = None

    # TrigramDecoder
    td = None

    # BigramDecoder
    bd = None

    # BigramSucceedDecoder
    bsd = None

    # TrigramSucceedDecoder
    tsd = None

    # int
    minWordFreq = None

    """
    Parameters:
        String fileLexicon
        String fileNGram
        int NGramType
        int maxAffixLength
        int Treshold
        int minWordFreq
        int modeAffixTree
        boolean debug
        double LambdaBigram
        int TwoPhaseType
        double beamFactor
        int useLexicon
    """
    def __init__(self, fileLexicon, fileNGram, NGramType, maxAffixLength=3, Treshold=3, minWordFreq=0, modeAffixTree=0, debug=False, LambdaBigram=0.2, TwoPhaseType=0, beamFactor=500.0, useLexicon=0):
        self.fileLexicon = fileLexicon
        self.fileNGram = fileNGram
        self.maxAffixLength = maxAffixLength
        self.Treshold = Treshold
        self.minWordFreq = minWordFreq
        self.modeAffixTree = modeAffixTree
        self.debug = debug
        self.LambdaBigram = LambdaBigram
        self.beamFactor = beamFactor
        self.NGramType = NGramType
        self.TwoPhaseType = TwoPhaseType
        self.useLexicon = useLexicon
        self.loadData()

    def loadData(self):
        try:
            self.model = Model(open(self.fileLexicon, "r"), open(self.fileNGram, "r"))
            self.dl = None
            if self.useLexicon != 0: 
                self.dl = DicLexicon("resource/inlex.txt", "resource/cattable.txt", self.model.getNumberTags())

        except:
            print "Training file doesn't exist !\n"
            return
            
        
        self.ovp = None
        
        #print "starting phase"
        
        if self.modeAffixTree != 3: 
            self.ovp = OOVWordProb(self.model.getLexicon(), self.model.getUniGrams(), self.maxAffixLength, self.Treshold, self.minWordFreq, self.modeAffixTree, self.debug)
        
        #print "phase0 OK"
        
        self.wp = KnownWordProb(self.model.getLexicon(), self.model.getUniGrams(), self.model.getNumberTags(), self.ovp, self.dl, self.debug)
        self.np = NGramProb(self.model.getUniGrams(), self.model.getBiGrams(), self.model.getTriGrams(), self.model.getQuatoGrams(), self.LambdaBigram)
        
        #print "phase1 OK"
        
        if self.NGramType == 1: 
            self.td = TrigramDecoder(self.model, self.wp, self.np, self.beamFactor, self.debug)
        else:
            self.bd = BigramDecoder(self.model, self.wp, self.np, self.beamFactor, self.debug)

        #print "phase2 OK"
        
        if self.TwoPhaseType == 1: 
            self.bsd = BigramSucceedDecoder(self.model, self.wp, self.np, self.beamFactor, self.debug)
        elif self.TwoPhaseType == 2: 
            self.tsd = TrigramSucceedDecoder(self.model, self.wp, self.np, self.beamFactor, self.debug)

    def taggingStr(self, str):
        """
        Returns ArrayList<String>
        Parameters:
            str: String
        """
        # ArrayList<String>
        temp = []
        # ArrayList<String>
        ret = []
        # byte[]
        input = str #???
        # int
        n = 0
        while (n < len(input)):
            # String
            line = ""
            while n < len(input) and (input[n] != '\n'):
                line += input[n]
                n += 1

            # String
            tokens = re.split("\\s+", line)
            # List<String>
            tokenList = copy(tokens)
            if len(tokens) == 1: 
                n += 1
                continue

            tokenList.insert(0, "<STARTTAG>")
            tokenList.insert(0, "<STARTTAG>")
            tokenList.append("<ENDTAG>")
            # List<String>
            tags = None
            if self.NGramType == 1: 
                seq = self.td.backtrack(self.td.viterbi(tokenList), self.model)
                if seq is not None:
                    tags = seq.sequence()
            else:
                seq = self.bd.backtrack(self.bd.viterbi(tokenList), self.model)
                if seq is not None:
                    tags = seq.sequence()

            # int
            i = None
            # int
            j = 2
            # List<String>
            temp2 = []
            if tags is not None:
                for i in xrange(1, len(tags) - 1): 
                    if not (tags[i] == "<STARTTAG>") and not (tags[i] == "<ENDTAG>"): 
                        temp.append(tokenList[j] + "/" + tags[i])
                        temp2.append(tokenList[j] + "/" + tags[i])
                        j += 1

            if self.TwoPhaseType >= 1: 
                # ArrayList<String>
                p = self.tagging2Phase(temp2)
                for k in xrange(0, len(p)): 
                    ret.append(p[k]);

            n += 1

        if self.TwoPhaseType == 0: 
            ret = temp;
        return ret


    def taggingFile(self, tagFile):
        """
        Returns ArrayList<String>
        Parameters:
            tagFile: String
        """
        try:
            # BufferedReader
            reader = open(tagFile, 'r');
            # String
            line = None
            # ArrayList<String>
            temp = []
            # ArrayList<String>
            ret = []
            for line in reader.readlines():
                # String
                tokens = re.split("\\s+", line.strip())
                
                # List<String>
                tokenList = tokens
                if len(tokens) == 1: 
                    continue
                tokenList.insert(0, "<STARTTAG>")
                tokenList.insert(0, "<STARTTAG>")
                tokenList.append("<ENDTAG>")
                
                # List<String>
                tags = None
                if self.NGramType == 1:
                    tags = self.td.backtrack(self.td.viterbi(tokenList), self.model).sequence()
                else:
                    tags = self.bd.backtrack(self.bd.viterbi(tokenList), self.model).sequence()
                
                # int
                i = None
                # int
                j = 2
                # List<String>
                temp2 = []
                for i in xrange(1,len(tags) - 1):
                    if (tags[i] <> "<STARTTAG>") and (tags[i] <> "<ENDTAG>"): 
                        temp.append(tokenList[j] + "/" + tags[i])
                        temp2.append(tokenList[j] + "/" + tags[i])
                        j += 1

                if self.TwoPhaseType >= 1: 
                    # ArrayList<String>
                    p = self.tagging2Phase(temp2)
                    for k in xrange(0, len(p)): 
                        ret.append(p[k]);

            if self.TwoPhaseType == 0: 
                ret = temp;
            return ret
            
        except:
            print "taggingFile error"
            return None



    def taggingTaggedFile(self, tagFile):
        """
        Returns ArrayList<String>
        Parameters:
            tagFile: String
        """
        try:
            # BufferedReader
            reader = open(tagFile, "r");
            # ArrayList<String>
            temp = []
            # ArrayList<String>
            ret = []
            for line in reader.readlines():
                # String
                tokens = re.split("\\s+", line)
                if len(tokens) == 1: 
                    continue
                for j in xrange(0, len(tokens)): 
                    # int
                    sepIndex = tokens[j].rfind('/')
                    tokens[j] = tokens[j][0: sepIndex]

                # List<String>
                tokenList = copy(tokens)
                tokenList.insert(0, "<STARTTAG>")
                tokenList.insert(0, "<STARTTAG>")
                tokenList.append("<ENDTAG>")
                # List<String>
                tags = None
                if self.NGramType == 1: 
                    tags = self.td.backtrack(self.td.viterbi(tokenList), self.model).sequence()
                else:
                    tags = self.bd.backtrack(self.bd.viterbi(tokenList), self.model).sequence()

                # int
                i = None
                # int
                j = 2
                # List<String>
                temp2 = []
                for i in xrange(1, len(tags) - 1) :
                    if not (tags[i] == "<STARTTAG>") and not (tags[i] == "<ENDTAG>"): 
                        temp.append(tokenList[j] + "/" + tags[i])
                        temp2.append(tokenList[j] + "/" + tags[i])
                        j += 1

                if self.TwoPhaseType >= 1: 
                    # ArrayList<String>
                    p = self.tagging2Phase(temp2)
                    for k in xrange(0, len(p)):
                        ret.append(p[k])

            if self.TwoPhaseType == 0: 
                ret = temp
            return ret
            
        except:
            print "MainTagger.taggingTaggedFile error"
            return None

    def isOOV(self, word):
        """
        Returns boolean
        Parameters:
            word: String
        """
        return self.wp.isOOV(word)


    def tagging2Phase(self, input):
        """
        Returns ArrayList<String>
        Parameters:
            input: List<String>
        """
        # List<String>
        tokenList = input
        # ArrayList<String>
        ret = []
        tokenList.insert(0, "<STARTTAG>")
        tokenList.insert(0, "<STARTTAG>")
        tokenList.append("<ENDTAG>/<ENDTAG>")
        
        # List<String>
        tags = None
        if self.TwoPhaseType == 1: 
            tags = self.bsd.backtrack(self.bsd.viterbi(tokenList), self.model).sequence()
        elif self.TwoPhaseType == 2: 
            tags = self.tsd.backtrack(self.tsd.viterbi(tokenList), self.model).sequence()

        # int
        i = None
        # int
        j = 2
        for i in xrange(1, len(tags) - 1): 
            if not (tags[i] == "<STARTTAG>") and not (tags[i] == "<ENDTAG>"): 
                # int
                sepIndex = tokenList[j].rfind('/');
                # String
                token = tokenList[j][0: sepIndex];
                ret.append(token + "/" + tags[i]);
                j += 1


        return ret



