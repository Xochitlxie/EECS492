from preprocessor import PreProcessor
from bernoulliNaiveBayes import BernoulliNaiveBayes
import sys

dataPath = sys.argv[1]
b = BernoulliNaiveBayes(dataPath, "stopwords.txt", "test_ground_truth.txt")
b.train()
b.testAll()
b.featureCurve()
