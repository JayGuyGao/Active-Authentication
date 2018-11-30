import numpy as np
from sklearn import mixture
from features import FeatureExtractor
from monitors import ProcessMonitor, NetworkMonitor, FileMonitor
import constants
import pickle
import time


if __name__ == "__main__":
    with open(constants.model_path, "rb") as f:
        clf = pickle.load(f)

    feature_extractor = FeatureExtractor(
        features=constants.features,
        window_size=300
    )

    print("Initializing...")
    process_monitor = ProcessMonitor(verbose=False, log_path="test.log", callback=feature_extractor.extract)
    network_monitor = NetworkMonitor(verbose=False, log_path="test.log", callback=feature_extractor.extract)
    file_monitor = FileMonitor(path="/Users/JayGuy/Documents", verbose=False, log_path="test.log", callback=feature_extractor.extract)

    print("Monitoring...")
    while True:
        process_monitor.update()
        network_monitor.update()
        file_monitor.update()
        if feature_extractor.results is not None:
            score = clf.score(feature_extractor.results)
            if score > constants.threshold:
                print("Yes")
            else:
                print("No!!!!!!!!!!!!!!!!!")
            feature_extractor.clear_results()
        time.sleep(1)