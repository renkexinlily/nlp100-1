from stemming.porter2 import stem
import sys
import numpy as np
vocab = {}


foobar = [".", ",", "(", ")", '"', "'"]


def preprocess(s):
    words = s.lower().strip().split(" ")
    words = map(lambda x: x.strip(), words)
    words = filter(lambda x: x not in foobar, words)
    words = list(map(stem, words))
    return words


with open("sentiment.txt") as f:
    lines = f.readlines()
    for line in lines:
        line = line[2:-1]
        words = preprocess(line)
        for word in words:
            if word in foobar:
                continue
            if word in vocab:
                vocab[word] += 1
            else:
                vocab[word] = 1


def build_idx(vocab):
    word2idx = {}
    ind2word = {}
    count = 0
    for k, v in vocab.items():
        word2idx[k] = count
        ind2word[count] = k
        count += 1
    assert count == len(vocab)
    return word2idx, ind2word


def sentence2features(words, vocab, word2idx):
    N = len(vocab)
    x = np.zeros(N, dtype=np.int)
    for word in words:
        idx = word2idx[word]
        x[idx] += 1
    return x


K = 10
stopwords = sorted(vocab.items(), key=lambda x: x[1])[:: -1][: K]
stopwords_dict = dict(stopwords)

word2idx, idx2word = build_idx(vocab)


def is_stopword(x, stopwords_dict=stopwords_dict):
    if x in stopwords_dict:
        return True
    return False


def is_not_stopword(x, stopwords_dict=stopwords_dict):
    return not is_stopword(x, stopwords_dict)


X = []
Y = []
with open("sentiment.txt") as f:
    lines = f.readlines()
    for line in lines:
        y, line = line[:2], line[2:]
        words = preprocess(line)
        # 1 means possitive, 0 means negative
        y = 1 if (y == "+1") else 0
        words = list(filter(is_not_stopword, words))
        x = sentence2features(words, vocab, word2idx)

        X.append(x)
        Y.append(y)

X = np.array(X)
Y = np.array(Y)

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import classification_report

kf = KFold(n_splits=5)
for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    Y_train, Y_test = Y[train_index], Y[test_index]

    model = LogisticRegression(penalty="l2", random_state=12345)
    model.fit(X_train, Y_train)
    Y_hat = model.predict(X_test)
    print(classification_report(Y_test, Y_hat, digits=7))

sys.exit(0)
