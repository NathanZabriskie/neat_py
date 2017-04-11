import arff
import numpy as np
import sklearn.preprocessing

DATA = 'data'

def load_arff(arff_file, one_hot=True, normalize=True):
    with open(arff_file, 'r') as f:
        obj = arff.load(f, encode_nominal=True)

    data = obj[DATA]

    labels = [x[-1] for x in (x for x in data)]
    data = np.array(data)
    data = data[:,:-1]
    if normalize:
        data = (data - data.min(axis=0)) / data.ptp(axis=0)

    if one_hot:
        label_binarizer = sklearn.preprocessing.LabelBinarizer()
        label_binarizer.fit(range(max(labels) + 1))
        labels = label_binarizer.transform(labels)

    labels = np.array(labels, dtype=np.float32)

    return data, labels
