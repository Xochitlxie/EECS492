import re, string, glob

class PreProcessor:
    MAX_CLASS = 99
    test_train_dir = None

    def __init__(self, train_test_dir, vocabPath):
        self.vocalPath = vocabPath
        self.trainTestDir = train_test_dir
        self.trainFileNames = {}
        self.classes = []
        self.feature = []
        self.N = 0

        self.get_classes()
        self.get_features()


    # get test data path
    def get_classes(self):
        for i in range(self.MAX_CLASS):
            digit = str(i).zfill(2)
            filenames = glob.glob(self.trainTestDir + "/*train" + digit + "*")
            self.N += len(filenames)
            if len(filenames) > 0:
                self.classes.append(i)
                self.trainFileNames[i] = filenames


    def print_classes(self):
        for c in self.classes:
            print "class : " + str(c)
            for path in self.trainFileNames[c]:
                print path

    # read in features
    def get_features(self):
        with open(self.vocalPath) as featureFile:
            for line in featureFile.readlines():
                self.feature.append(line.split()[0])

    # Function to print the confusion matrix.
    # Argument 1: "actual" is a list of integer class labels, one for each test example.
    # Argument 2: "predicted" is a list of integer class labels, one for each test example.
    # "actual" is the list of actual (ground truth) labels.
    # "predicted" is the list of labels predicted by your classifier.
    # "actual" and "predicted" MUST be in one-to-one correspondence.
    # That is, actual[i] and predicted[i] stand for testfile[i].
    def printConfMat(self, actual, predicted):
        all_labels = sorted(set(actual + predicted))
        assert(len(actual) == len(predicted))
        confmat = {}
        for i,a in enumerate(actual): confmat[(a, predicted[i])] = confmat.get((a, predicted[i]), 0) + 1
        print
        print
        print "0",  # Actual labels column (aka first column)
        for label2 in all_labels:
            print label2,
        print
        for label in all_labels:
            print label,
            for label2 in all_labels:
                print confmat.get((label, label2), 0),
            print

    # Function to remove leading, trailing, and extra space from a string.
    # Inputs a string with extra spaces.
    # Outputs a string with no extra spaces.
    def remove_extra_space(self, input_string):
        return re.sub("\s+", " ", input_string.strip())

    # Tokenizer.
    # Input: string
    # Output: list of lowercased words from the string
    def word_tokenize(self, input_string):
        extra_space_removed = self.remove_extra_space(input_string)
        punctuation_removed = "".join([x for x in extra_space_removed if x not in string.punctuation])
        lowercased = punctuation_removed.lower()
        return lowercased.split()

