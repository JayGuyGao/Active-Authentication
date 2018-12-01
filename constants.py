from features import (
    NumberOfProcessesTerminated,
    NumberOfProcessesCreated,
    NumberOfFileChanges,
    NumberOfConnectionsOpened,
    NumberOfConnectionsClosed
)

log_path = "monitor.log"

features = [
    NumberOfProcessesTerminated(),
    NumberOfProcessesCreated(),
    NumberOfFileChanges(),
    NumberOfConnectionsOpened(),
    NumberOfConnectionsClosed(),
]

n_components = 5
covariance_type = 'full'
window_size = 300

threshold = -10

model_path = "model.pkl"