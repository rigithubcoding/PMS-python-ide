import pickle
from sklearn import tree
from sklearn.feature_extraction.text import CountVectorizer

keywords=["with", "import", "try", "except", "True", "False", "def", "class", "as", "from", "await", "pass",    "None", "break", "raise"]

builtins=["abs", "ascii", "bin","open", "__import__"]
comment=["#"]
test_texts=["import", "abs", "ascii"]

training_texts = keywords + builtins + comment
training_labels = ["keyword"] * len(keywords) + ["builtin"] * len(builtins) +comment*len(comment)

vectorizer = CountVectorizer()
vectorizer.fit(training_texts)
training_vectors = vectorizer.transform(training_texts)
testing_vectors = vectorizer.transform(test_texts)
classifier = tree.DecisionTreeClassifier()
classifier.fit(training_vectors, training_labels)
predictions = classifier.predict(testing_vectors)
print(predictions)

# Dump the trained decision tree classifier with Pickle
decision_tree_pkl_filename = 'ai.pkl'
# Open the file to save as pkl file
decision_tree_model_pkl = open(decision_tree_pkl_filename, 'wb')
pickle.dump(classifier, decision_tree_model_pkl)
# Close the pickle instances
decision_tree_model_pkl.close()
# Dump the trained decision tree classifier with Pickle
decision_tree_pkl_filename = 'decision_tree_classifier_20170212.pkl'
decision_tree_model_pkl.close()