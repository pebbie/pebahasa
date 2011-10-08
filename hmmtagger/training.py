from copy import *
import re

class TaggedWord:
    def __init__(self, word='', tag=''):
        self.word = word
        self.tag = tag

    def getWord(self):
        return self.word

    def getTag(self):
        return self.tag

def replaceCharAt(str, pos, c):
    return str[:pos]+c+str[pos+1:]

class CorpusReaderException(Exception):
    pass

class AbsCorpusReader:
    """
    Parameters:
        List<TaggedWord> startMarkers
        List<TaggedWord> endMarkers
        TrainHandler TH
    """
    def __init__(self, startMarkers, endMarkers, TH):
        self.startMarkers = copy(startMarkers)
        self.endMarkers = copy(endMarkers)
        self.sentenceHandler = TH


    def parse(self, reader):
        pass

class CorpusReaderSatu(AbsCorpusReader):
    def __init__(self, startMarkers, endMarkers, TH):
        AbsCorpusReader.__init__(self, startMarkers, endMarkers, TH)

    def parse(self, reader):
        for line in reader.readlines():
            line = line.strip()
            if len(line) == 0: 
                continue

            # List<TaggedWord>
            sentence = copy(self.startMarkers)
            # String[]
            lineParts = re.split("\\s+", line)
            for i in xrange(0, len(lineParts)): 
                # String
                wordTag = lineParts[i]
                # int
                sepIndex = wordTag.rfind('/')
                if sepIndex == -1: 
                    raise CorpusReaderException("Tag is missing in '" + wordTag + "'", CorpusReaderException.CorpusReadError.MISSING_TAG)

                # String
                word = wordTag[:sepIndex]
                # String
                tag = wordTag[sepIndex + 1:]
                if len(word) == 0: 
                    raise CorpusReaderException("Zero-length word in '" + wordTag + "'", CorpusReaderException.CorpusReadError.ZERO_LENGTH_WORD)

                if i == 0: 
                    word = replaceCharAt(word, 0, word[0].lower());

                sentence.append(TaggedWord(word, tag))

            sentence += copy(self.endMarkers)
            self.sentenceHandler.handleSentence(sentence)

class TrainHandler:
    def __init__(self):
        self.lexicon = {}
        self.unigrams = {}
        self.bigrams = {}
        self.trigrams = {}
        self.quatograms = {}

    def getBigram(self):
        return self.bigrams

    def getLexicon(self):
        return self.lexicon

    def getQuatogram(self):
        return self.quatograms

    def getTrigram(self):
        return self.trigrams

    def getUnigram(self):
        return self.unigrams

    def handleSentence(self, sentence):
        """
        Returns void
        Parameters:
            sentence: List<TaggedWord>
        """
        for i in xrange(0, len(sentence)): 
            self.addLexiconEntry(sentence[i])
            self.addUniGram(sentence, i)
            if i > 0: 
                self.addBiGram(sentence, i)

            if i > 1: 
                self.addTriGram(sentence, i)
                if i < len(sentence) - 1: 
                    self.addQuatoGram(sentence, i)

    def addLexiconEntry(self, w):
        """
        Parameters:
            w: TaggedWord
        """
        # String
        word = w.getWord()
        # String
        tag = w.getTag()
        if word not in self.lexicon: 
            self.lexicon[word] = {}

        if tag not in self.lexicon[word]: 
            self.lexicon[word][tag] = 1
        else:
            self.lexicon[word][tag] += 1;

    def addUniGram(self, sentence, index):
        """
        Parameters:
            sentence: List<TaggedWord>index: int
        """
        # String
        unigram = sentence[index].getTag()
        if unigram not in self.unigrams: 
            self.unigrams[unigram] = 1
        else:
            self.unigrams[unigram] += 1

    def addBiGram(self, sentence, index):
        """
        Parameters:
            sentence: List<TaggedWord>index: int
        """
        # String
        bigram = sentence[index - 1].getTag() + " " + sentence[index].getTag()
        if bigram not in self.bigrams: 
            self.bigrams[bigram] = 1
        else:
            self.bigrams[bigram] += 1

    def addTriGram(self, sentence, index):
        """
        Parameters:
            sentence: List<TaggedWord>index: int
        """
        # String
        trigram = sentence[index - 2].getTag() + " " + sentence[index - 1].getTag() + " " + sentence[index].getTag()
        if trigram not in self.trigrams: 
            self.trigrams[trigram] = 1
        else:
            self.trigrams[trigram] += 1

    def addQuatoGram(self, sentence, index):
        """
        Parameters:
            sentence: List<TaggedWord>index: int
        """
        # String
        quatogram = sentence[index - 2].getTag() + " " + sentence[index - 1].getTag() + " " + sentence[index].getTag() + " " + sentence[index + 1].getTag();
        if quatogram not in self.quatograms: 
            self.quatograms[quatogram] = 1
        else:
            self.quatograms[quatogram] += 1

#MainTrainer
def writeNGrams(uniGrams, biGrams, triGrams, quatoGrams, writer):
    """
    Parameters:
        uniGrams: Map<String, Integer>
        biGrams: Map<String, Integer>
        triGrams: Map<String, Integer>
        quatoGrams: Map<String, Integer>
        writer: BufferedWriter
    """
    for entry in uniGrams: writer.write(entry + " " + str(uniGrams[entry]) + "\n")
    for entry in biGrams: writer.write(entry + " " + str(biGrams[entry]) + "\n")
    for entry in triGrams: writer.write(entry + " " + str(triGrams[entry]) + "\n")
    for entry in quatoGrams: writer.write(entry + " " + str(quatoGrams[entry]) + "\n")
    writer.flush()

def writeLexicon(lexicon, writer):
    """
    Parameters:
        lexicon: Map<String, Map<String, Integer>>writer: BufferedWriter
    """
    for wordEntry in lexicon: 
        # String
        word = wordEntry
        writer.write(word)
        for tagEntry in lexicon[word]: 
            writer.write(" ")
            writer.write(tagEntry)
            writer.write(" ")
            writer.write(str(lexicon[word][tagEntry]));

        writer.write("\n")

    writer.flush()


def Train(corpus):
    """
    Parameters:
        corpus: String
    """
    # List<TaggedWord>
    startMarkers = []
    startMarkers.append(TaggedWord("<STARTTAG>", "<STARTTAG>"))
    startMarkers.append(TaggedWord("<STARTTAG>", "<STARTTAG>"))
    # List<TaggedWord>
    endMarkers = []
    endMarkers.append(TaggedWord("<ENDTAG>", "<ENDTAG>"))
    # TrainHandler
    trainHandler = TrainHandler()
    # AbsCorpusReader<TaggedWord>
    corpusReader = CorpusReaderSatu(startMarkers, endMarkers, trainHandler)
    try:
        fcorpus = open(corpus, "r")
        corpusReader.parse(fcorpus)
        fcorpus.close()
    except IOError:
        print("Could not read corpus!\n")
        exit(1)
    except CorpusReaderException:
        print("Train Error!\n")
        exit(1)

    try:    
        flex = open("./resource/Lexicon.trn", "w")
        writeLexicon(trainHandler.getLexicon(), flex)
        flex.close()
        ftrain = open("./resource/Ngram.trn", "w")
        writeNGrams(trainHandler.getUnigram(), trainHandler.getBigram(), trainHandler.getTrigram(), trainHandler.getQuatogram(), ftrain)
    except:
        print("System Can not write training data!\n")
        exit(1)




