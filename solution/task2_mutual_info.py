import time
t=time.time()

import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_selection import mutual_info_classif
import matplotlib.pyplot as plt

#Assign column name
columns = ['F' + str(i) for i in range(130)]

#Read data and store in a DataFrame
data = pd.read_csv('../data/data.csv', sep=' ', header=None, names = columns)
target = pd.read_csv('../data/target.csv', header=None)


#Convert DataFrame to an array
X = data.to_numpy()
y = target.to_numpy().flatten()

# Separate data into training and validation sets
X_train, X_valid, y_train, y_valid = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

#Feature Normalization (data standardization) of train and test data using only TRAINING DATA for both Training set and Validation Set,
#to sure our model generalize well on new, unseen data.

scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_valid = scaler.transform(X_valid)

#Define function for Mutual Information (MI) Score
def make_mi_scores(X, y):
    mi_scores = mutual_info_classif(X, y)
    mi_scores = pd.Series(mi_scores, name="MI Scores", index=X.columns)
    mi_scores = mi_scores.sort_values(ascending=False)
    return mi_scores

# Convert train and validation data to dataframe
X_train_mi= pd.DataFrame(X_train, columns=columns)

X_valid_mi = pd.DataFrame(X_valid, columns=columns)

#Calculate MI Scores
mi_scores = make_mi_scores(X_train_mi, y_train)

#Choose the best features according to MI Score
best_features=mi_scores[mi_scores>0.05].index

#Feature Selection on Training Data and Validation Data
X_compact=X_train_mi[best_features]
X_valid_compact=X_valid_mi[best_features]

#Plot Mutual Scores
def plot_mi_scores(scores):
    scores = scores.sort_values(ascending=True)
    width = np.arange(len(scores))
    ticks = list(scores.index)
    plt.barh(width, scores)
    plt.yticks(width, ticks)
    plt.title("Mutual Information Scores")

plt.figure(dpi=100, figsize=(8, 5))
plot_mi_scores(mi_scores[mi_scores>0.05])

#Define a function to train many classifier at once
def valid_classifier(clf, X_train, y_train, X_valid, y_valid):
    clf.fit(X_train, y_train)
    acc_train = clf.score(X_train, y_train)
    acc_valid = clf.score(X_valid, y_valid)
    return acc_train, acc_valid


names = [
    "Linear SVM",
    "SVM Classifier",
    "Decision Tree",
    "Random Forest",
    "Neural Net",
    "AdaBoost",
    "Naive Bayes"
]

classifiers = [
    SVC(kernel="linear", C=0.025),
    SVC(),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=100, max_features=1),
    #to avoid overfitting define early_stopping
    MLPClassifier(hidden_layer_sizes=(100), alpha=1, max_iter=1000, early_stopping=True),
    AdaBoostClassifier(),
    GaussianNB()
]

#iterate over classifiers
for name, clf in zip(names, classifiers):
    acc_train, acc_valid = valid_classifier(clf, X_compact, y_train, X_valid_compact, y_valid)
    print(name, "Train Accuracy: %.2f%% Validation Accuracy: %.2f%%" % (acc_train * 100.0,acc_valid * 100.0 ))
    
elapsed=time.time()-t
elapsed