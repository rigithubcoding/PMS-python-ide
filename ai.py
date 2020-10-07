import pickle
from sklearn import tree
from sklearn.feature_extraction.text import CountVectorizer

keywords=["with", "import", "try", "except", "True", "False", "def", "class", "as", "from", "await", "pass",    "None", "break", "raise"]

builtins=["abs", "ascii", "bin","open"]

training_texts = keywords + builtins
training_labels = ["negative"] * len(negative_texts) + ["positive"] * len(positive_texts)

vectorizer = CountVectorizer()
vectorizer.fit(training_texts)
training_vectors = vectorizer.transform(training_texts)
testing_vectors = vectorizer.transform(test_texts)
classifier = tree.DecisionTreeClassifier()
classifier.fit(training_vectors, training_labels)
predictions = classifier.predict(testing_vectors)