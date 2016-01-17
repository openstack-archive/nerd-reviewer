#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import logging
import select
import threading

import notifier
import paramiko

LOG = logging.getLogger(__name__)


class Watcher(threading.Thread):

    GERRIT_ACTIVITY = "GERRIT_ACTIVITY"

    def __init__(self, hostname, username, port=29418, keyfile=None):
        super(Watcher, self).__init__()
        self.dead = threading.Event()
        self.notifier = notifier.Notifier()
        self._keyfile = keyfile
        self._hostname = hostname
        self._username = username
        self._port = port
        self._client = None

    def connect(self):
        self._client = paramiko.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.WarningPolicy())
        self._client.connect(self._hostname,
                             username=self._username,
                             port=self._port,
                             key_filename=self._keyfile)

    def run(self):
        client = self._client
        if not client:
            raise RuntimeError("Connect must be called before run")
        _stdin, stdout, _stderr = client.exec_command("gerrit stream-events")
        poll = select.poll()
        poll.register(stdout.channel)
        while not self.dead.is_set():
            for (fd, event) in poll.poll(0.1):
                if fd == stdout.channel.fileno():
                    if event == select.POLLIN:
                        event_data = {"event": json.loads(stdout.readline())}
                        self.notifier.notify(self.GERRIT_ACTIVITY, event_data)
                    else:
                        LOG.warn("Unknown event %s received on stdout"
                                 " descriptor %s [%s]", event, stdout, fd)


if __name__ == "__main__":
    import sys
    import time

    def on_event(event_type, details):
        print("Received event %s with details %s" % (event_type, details))

    logging.basicConfig(level=logging.DEBUG)
    w = Watcher(sys.argv[1], sys.argv[2])
    w.connect()
    w.notifier.register(Watcher.GERRIT_ACTIVITY, on_event)
    w.run()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        w.dead.set()
        w.join()
