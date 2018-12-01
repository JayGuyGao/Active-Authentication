import numpy as np
from monitors import LogEntry

class Feature:
    def __init__(self):
        pass

    def extract(self, log_entries):
        raise NotImplementedError("extract not implemented")


class NumberOfProcessesTerminated(Feature):
    def extract(self, log_entries):
        count = 0
        for log_entry in log_entries:
            if log_entry.category == "process" and log_entry.action == "terminate":
                count += 1
        return count


class NumberOfProcessesCreated(Feature):
    def extract(self, log_entries):
        count = 0
        for log_entry in log_entries:
            if log_entry.category == "process" and log_entry.action == "create":
                count += 1
        return count


class NumberOfFileChanges(Feature):
    def extract(self, log_entries):
        count = 0
        for log_entry in log_entries:
            if log_entry.category == "file" and log_entry.action == "modified":
                count += 1
        return count


class NumberOfConnectionsOpened(Feature):
    def extract(self, log_entries):
        count = 0
        for log_entry in log_entries:
            if log_entry.category == "network" and log_entry.action == "create":
                count += 1
        return count


class NumberOfConnectionsClosed(Feature):
    def extract(self, log_entries):
        count = 0
        for log_entry in log_entries:
            if log_entry.category == "network" and log_entry.action == "terminate":
                count += 1
        return count


class FeatureExtractor:
    def __init__(self, features, window_size=300):
        self.features = features
        self.window_size = window_size
        self.window = []
        self.results = None

    def extract(self, log_entries):
        if log_entries == []:
            return []

        #self.window = []
        results = []
        i = 0
        n = len(log_entries)
        while i < n:
            while self.window != [] and log_entries[i].timestamp - self.window[0].timestamp > self.window_size:
                self.window = self.window[1:]
            while i < n and (self.window == [] or log_entries[i].timestamp - self.window[0].timestamp <= self.window_size):
                self.window.append(log_entries[i])
                i += 1
            print((self.window[-1].timestamp - self.window[0].timestamp) / 60)
            results.append(self.compute_feature(self.window))

        if self.results is None:
            self.results = np.array(results)
        else:
            self.results = np.concatenate((self.results, results))
        return np.array(results)

    def clear_results(self):
        self.results = None

    def compute_feature(self, window):
        return [np.log(feat.extract(window) + 1) for feat in self.features]


def str2logentry(string):
    strs = string.split(";")
    return LogEntry(
        timestamp=float(strs[0]),
        category=strs[1],
        action=strs[2],
        detail=strs[3]
    )


def extract_features_from_file(file_path, features):
    with open(file_path, "r") as f:
        log_entries = [str2logentry(line.strip()) for line in f.readlines()]
    feature_extractor = FeatureExtractor(
        features=features,
        window_size=300
    )
    return feature_extractor.extract(log_entries)
