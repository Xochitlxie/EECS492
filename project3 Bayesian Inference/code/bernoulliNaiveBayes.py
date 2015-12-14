from preprocessor import PreProcessor
from glob import glob
from math import log

class BernoulliNaiveBayes:

    MAX_CLASS = 40

    def __init__(self, train_test_dir, vocab, test_ground_truth_path):
        self.model = PreProcessor(train_test_dir, vocab)

        self.train_test_dir = train_test_dir
        self.test_ground_truth_path = test_ground_truth_path

        # { Class(int) : Prior Probability of class (double) }
        self.prior = {}

        # { (Class(int) , Feature (string)) : Conditional Probability (double) }
        self.condProb = {}

        # list of (Feature(string),CCE(double))
        self.featureCCE = []

        """
        ######## the variable following for extra part

        # { Class(int) : Prior Probability of class (double) }
        self.priorBi = {}

        # list of bigram tuple (feature1(string),feature2(string))
        self.biFeat = []

        # { (Class(int), Feature (tuple)) : multinomial Prob(double) }
        self.MulProb = {}
        """



    # Define Train function
    def train(self):
        for c in self.model.classes:
            self.prior[c] = len(self.model.trainFileNames[c]) * 1.0 / self.model.N

            counter = {}
            for feature in self.model.feature:
                counter[feature] = 0

            for filename in self.model.trainFileNames[c]:
                words = set()
                with open(filename, 'r') as file:
                    for line in file:
                        for word in self.model.word_tokenize(line):
                            words.add(word)

                for feature in self.model.feature:
                    if feature in words:
                        counter[feature] += 1

            for feature in self.model.feature:
                self.condProb[(c, feature)] = (counter[feature] * 1.0 + 1) / (len(self.model.trainFileNames[c]) + 2)


    # For Debugging
    def printCondProb(self):
        for c in self.model.classes:
            print "class " + str(c) + " : " + str(self.prior[c])
            for feature in self.model.feature:
                print feature + " : " + str(self.condProb[(c, feature)])



    # Define Test function
    # Return a list of test result as a int list
    def test(self, testfilename):

        maxProb = float("-Inf")
        c_star = 0

        words = set()
        with open(testfilename, 'r') as file:
            for line in file:
                for word in self.model.word_tokenize(line):
                    words.add(word)

        for c in self.model.classes:
            probability = log(2, self.prior[c])
            for feature in self.model.feature:
                if feature in words:
                    probability += log(self.condProb[(c, feature)], 2)
                else:
                    probability += log(1-self.condProb[(c, feature)], 2)
            if probability > maxProb:
                c_star = c
                maxProb = probability

        return c_star

    def testAll(self):
        testFileNames = glob(self.train_test_dir + "/*sample*")
        testFileNames.sort()

        testResult = []
        actualResult = []
        for testFileName in testFileNames:
            testResult.append(self.test(testFileName))

        problemNum = self.getProblemNumber()
        with open(self.test_ground_truth_path, 'r') as actualFile:
            for line in actualFile.readlines():
                if len(line) > 10 and line.startswith("problem" + problemNum):
                    actualResult.append(int(line[-3 : -1]))

        self.printAccuracy(actualResult,testResult)
        self.model.printConfMat(actualResult, testResult)
        self.rankFeature()
        print "Top 20 features:"
        self.printTop20()


    def printAccuracy(self,actualResult,testResult):
        accuracyNum = 0
        for i in range(len(testResult)):
            if actualResult[i] == testResult[i]:
                accuracyNum += 1
        accuracy = accuracyNum * 1.0 / len(actualResult)
        print accuracy


    def getProblemNumber(self):
        files = glob(self.train_test_dir + "/*")
        paths = files[0].split("/")
        return paths[-1][0]

    def rankFeature(self):
        for feature in self.model.feature:
            CCE = 0
            for c in self.model.classes:
                CCE -= self.prior[c] * self.condProb[(c,feature)] * log(self.condProb[(c,feature)],2)
            self.featureCCE.append((feature,CCE))


    def printTop20(self):
        sortedCCE = sorted(self.featureCCE, key=lambda item:item[1])[::-1]
        for i in range(20):
            feature = sortedCCE[i][0]
            CCE = sortedCCE[i][1]
            print feature +"  " + str(CCE)

    def featureFreq(self):
        words = {}
        featureTimes = []
        for c in self.model.classes:
            for filename in self.model.trainFileNames[c]:
                with open(filename, 'r') as file:
                    for line in file:
                        for word in self.model.word_tokenize(line):
                            words[word] = words.get(word, 0) + 1
        for feature in self.model.feature:
            words[feature] = words.get(feature,0)
            featureTimes.append((feature,words[feature]))
        self.featFreq = sorted(featureTimes, key=lambda item:item[1])[::-1]


    def resetFeatures(self,Num):
        features = []
        if Num > len(self.featFreq):
            Num = len(self.featFreq)
        for i in range(Num):
            features.append(self.featFreq[i][0])
        return features

    def featureCurve(self):
        self.featureFreq()
        # print self.featFreq
        Num = 0
        while Num <= 420:
            Num += 10
            self.model.feature = self.resetFeatures(Num)
            print "select " + str(len(self.model.feature)) + " features"
            self.train()

            testFileNames = glob(self.train_test_dir + "/*sample*")
            testFileNames.sort()

            testResult = []
            actualResult = []
            for testFileName in testFileNames:
                testResult.append(self.test(testFileName))

            problemNum = self.getProblemNumber()
            with open(self.test_ground_truth_path, 'r') as actualFile:
                for line in actualFile.readlines():
                    if len(line) > 10 and line.startswith("problem" + problemNum):
                        actualResult.append(int(line[-3 : -1]))

            self.printAccuracy(actualResult,testResult)


