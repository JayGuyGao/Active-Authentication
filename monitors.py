import psutil
import time
from collections import namedtuple


LogEntry = namedtuple('LogEntry', ['timestamp', 'category', 'action', 'detail'], verbose=False)


class Monitor:
    def __init__(self):
        pass

    def run(self):
        raise NotImplementedError("run not implemented")

    def log(self, logs):
        for log_entry in logs:
            print("{}; {}; {}; {}".format(
                log_entry.timestamp,
                log_entry.category,
                log_entry.action,
                log_entry.detail
            ))


class ProcessMonitor(Monitor):
    def __init__(self):
        self.previous_processes = {}
        self.current_processes = self.get_current_processes()

    def run(self):
        self.timestamp = time.time()
        self.previous_processes = self.current_processes
        self.current_processes = self.get_current_processes()
        logs = self.get_logs(self.previous_processes, self.current_processes)
        self.log(logs)

    def get_logs(self, previous_processes, current_processes):
        logs = []
        for i in previous_processes:
            if i not in current_processes:
                logs.append(self.gen_log(previous_processes[i], 'terminate'))

        for i in current_processes:
            if i not in previous_processes:
                logs.append(self.gen_log(current_processes[i], 'create'))
            elif current_processes[i]['status'] != previous_processes[i]['status']:
                logs.append(self.gen_log(current_processes[i], 'change_status'))

        return logs

    def gen_log(self, process, action):
        return LogEntry(
            timestamp=self.timestamp,
            category='process',
            action=action,
            detail='{},{},{},{}'.format(process['pid'], process['ppid'], process['exe'], process['status'])
        )

    def get_current_processes(self):
        current_processes = {}
        for proc in psutil.process_iter(attrs=['pid', 'ppid', 'exe', 'status']):
            current_processes[proc.info['pid']] = proc.info
        return current_processes


class NetworkMonitor(Monitor):
    def __init__(self):
        self.previous_connections = {}
        self.current_connections = self.get_current_connections()

    def run(self):
        self.timestamp = time.time()
        self.previous_connections = self.current_connections
        self.current_connections = self.get_current_connections()
        logs = self.get_logs(self.previous_connections, self.current_connections)
        self.log(logs)

    def get_current_connections(self):
        pass


if __name__ == '__main__':
    process_monitor = ProcessMonitor()
    while True:
        process_monitor.run()
        time.sleep(1)