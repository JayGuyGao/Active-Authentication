import psutil
import time
from collections import namedtuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from watchdog.events import EVENT_TYPE_MODIFIED, EVENT_TYPE_MOVED, EVENT_TYPE_CREATED, EVENT_TYPE_DELETED


LogEntry = namedtuple('LogEntry', ['timestamp', 'category', 'action', 'detail'])


class Monitor:
    def __init__(self, verbose=True, log_path="monitor.log", callback=None):
        self.verbose = verbose
        self.log_path = log_path
        self.callback = callback

    def update(self):
        raise NotImplementedError("update not implemented")

    def log(self, logs):
        if self.callback:
            self.callback(logs)
        for log_entry in logs:
            log_str = "{};{};{};{}".format(
                log_entry.timestamp,
                log_entry.category,
                log_entry.action,
                log_entry.detail
            )
            if self.verbose:
                print(log_str)
            with open(self.log_path, "a") as log_file:
                log_file.write(log_str + "\n")


class ProcessMonitor(Monitor):
    def __init__(self, verbose=True, log_path="monitor.log", callback=None):
        super(ProcessMonitor, self).__init__(verbose, log_path, callback)
        self.timestamp = time.time()
        self.previous_processes = {}
        self.current_processes = self.get_current_processes()

    def update(self):
        self.timestamp = time.time()
        self.previous_processes = self.current_processes
        self.current_processes = self.get_current_processes()
        for i in self.previous_processes:
            if i in self.current_processes:
                self.current_processes[i]['timestamp'] = self.previous_processes[i]['timestamp']
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
            detail='{},{},{},{},{}'.format(
                process['pid'],
                process['ppid'],
                process['exe'],
                process['status'],
                self.timestamp - process['timestamp']
            )
        )

    def get_current_processes(self):
        current_processes = {}
        for proc in psutil.process_iter(attrs=['pid', 'ppid', 'exe', 'status']):
            current_processes[proc.info['pid']] = proc.info
            current_processes[proc.info['pid']]['timestamp'] = self.timestamp
        return current_processes


class NetworkMonitor(Monitor):
    def __init__(self, verbose=True, log_path="monitor.log", callback=None):
        super(NetworkMonitor, self).__init__(verbose, log_path, callback)
        self.timestamp = time.time()
        self.previous_connections = {}
        self.current_connections = self.get_current_connections()

    def update(self):
        self.timestamp = time.time()
        self.previous_connections = self.current_connections
        self.current_connections = self.get_current_connections()
        for i in self.previous_connections:
            if i in self.current_connections:
                self.current_connections[i]['timestamp'] = self.previous_connections[i]['timestamp']
        logs = self.get_logs(self.previous_connections, self.current_connections)
        self.log(logs)

    def get_logs(self, previous_connections, current_connections):
        logs = []
        for key in previous_connections:
            if key not in current_connections:
                logs.append(self.gen_log(previous_connections[key], 'terminate'))

        for key in current_connections:
            if key not in previous_connections:
                logs.append(self.gen_log(current_connections[key], 'create'))
            elif current_connections[key]['status'] != previous_connections[key]['status']:
                logs.append(self.gen_log(current_connections[key], 'change_status'))

        return logs

    def gen_log(self, connection, action):
        return LogEntry(
            timestamp=self.timestamp,
            category='network',
            action=action,
            detail='{},{},{},{},{}'.format(
                connection['laddr'],
                connection['raddr'],
                connection['pid'],
                connection['status'],
                self.timestamp - connection['timestamp']
            )
        )

    def get_current_connections(self):
        current_connections = {}
        for conn in psutil.net_connections("tcp"):
            #print(conn)
            key = "{}:{}".format(
                conn.laddr.ip,
                conn.laddr.port,
            )
            current_connections[key] = {
                "laddr": conn.laddr,
                "raddr": conn.raddr,
                "status": conn.status,
                "pid": conn.pid,
                "timestamp": self.timestamp,
            }
        return current_connections


class CallbackEventHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super(CallbackEventHandler, self).__init__()
        self.callback = callback

    def on_any_event(self, event):
        super(CallbackEventHandler, self).on_any_event(event)
        self.callback(event)



class FileMonitor(Monitor):
    def __init__(self, path, verbose=True, log_path="monitor.log", callback=None):
        super(FileMonitor, self).__init__(verbose, log_path, callback)
        event_handler = CallbackEventHandler(self.handle_event)
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()

    def handle_event(self, event):
        #what = 'directory' if event.is_directory else 'file'
        if event.event_type is EVENT_TYPE_MODIFIED and event.src_path.find(self.log_path) != -1:
            return

        _log_detail_map = {
            EVENT_TYPE_MODIFIED: lambda evt: "{}".format(evt.src_path),
            EVENT_TYPE_MOVED: lambda evt: "{} to {}".format(evt.src_path, evt.dest_path),
            EVENT_TYPE_CREATED: lambda evt: "{}".format(evt.src_path),
            EVENT_TYPE_DELETED: lambda evt: "{}".format(evt.src_path),
        }
        log_entry = LogEntry(
            timestamp=time.time(),
            category="file",
            action=event.event_type,
            detail=_log_detail_map[event.event_type](event)
        )
        self.log([log_entry])

    def update(self):
        pass

    def __del__(self):
        pass
        #self.observer.stop()
        #self.observer.join()

if __name__ == '__main__':
    print("Initializing...")
    process_monitor = ProcessMonitor()
    network_monitor = NetworkMonitor()
    file_monitor = FileMonitor(path="/Users/JayGuy/Documents")
    print("Monitoring...")
    while True:
        process_monitor.update()
        network_monitor.update()
        file_monitor.update()
        time.sleep(1)