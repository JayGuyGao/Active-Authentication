import numpy as np
from sklearn import mixture
import matplotlib.pyplot as plt
from features import extract_features_from_file
import constants
import pickle


if __name__ == "__main__":
    X_train = extract_features_from_file(constants.log_path, constants.features)
    print(X_train.shape)

    clf = mixture.GaussianMixture(
        n_components=constants.n_components,
        covariance_type=constants.covariance_type
    )
    clf.fit(X_train)
    with open(constants.model_path, "wb") as f:
        pickle.dump(clf, f)
    print(clf.score(X_train))
    print(clf.score_samples(X_train))
    x = clf.score_samples(X_train)
    print(x.reshape(-1, 1).shape)

    plt.hist(x, bins='auto')
    plt.title("Histogram with 'auto' bins")
    plt.show()
