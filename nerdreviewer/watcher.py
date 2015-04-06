# Copyright 2015: Joshua Harlow
#
# All Rights Reserved.
#
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

import logging
import os
import threading
import time

from gerritlib import gerrit
from six.moves import queue  # noqa
from six.moves import range as compat_range  # noqa

LOG = logging.getLogger(__name__)


class ProxyGerrit(object):
    def __init__(self):
        self.event_queue = queue.Queue()

    def addEvent(self, data):
        self.event_queue.put(data)


class Watcher(threading.Thread):
    def __init__(self, server, username, port=29418, keyfile=None):
        super(Watcher, self).__init__()
        self._dead = threading.Event()
        self._server = server
        self._username = username
        self._port = port
        self._keyfile = keyfile
        self._gerrit = None
        self._gerrit_reciever = None
        self._subscribers = []

    def stop(self):
        self._dead.set()

    def join(self):
        super(Watcher, self).join()
        # This doesn't seem to work...
        # if self._gerrit_receiver is not None:
        #     self._gerrit_receiver.join()
        self._gerrit = self._gerrit_receiver = None

    def subscribe(self, filter_cb, call_cb):
        self._subscribers.append((filter_cb, call_cb))

    def _broadcast(self, event):
        LOG.debug("Broadcasting %s", event)
        call_into = []
        for (filter_cb, call_cb) in self._subscribers:
            if filter_cb(event):
                call_into.append(call_cb)
        for call_cb in call_into:
            call_cb(event)

    def connect(self):
        if self._gerrit is not None:
            raise RuntimeError("Can only connect to gerrit once")
        else:
            self._gerrit = ProxyGerrit()
            self._gerrit_receiver = gerrit.GerritWatcher(
                self._gerrit,
                username=self._username,
                hostname=self._server,
                port=self._port,
                keyfile=self._keyfile)
            self._gerrit_receiver.daemon = True
            self._gerrit_receiver.start()

    def run(self):
        while not self._dead.is_set():
            try:
                self._broadcast(self._gerrit.event_queue.get_nowait())
            except queue.Empty:
                self._dead.wait(0.1)
            except Exception:
                LOG.exception("Exception encountered in event loop")


def _main():
    # Little test program to make sure this works...
    import getpass

    logging.basicConfig(level=logging.DEBUG)

    keyfile = os.path.join(os.path.expanduser("~"), ".ssh", "id_rsa")

    if not os.path.isfile(keyfile):
        raise RuntimeError("No 'id_rsa' keyfile found at '%s'" % keyfile)

    g = Watcher("review.openstack.org", getpass.getuser(), keyfile=keyfile)
    g.connect()
    g.daemon = True
    g.start()
    try:
        while True:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                print("Dying...")
                g.stop()
                break
    finally:
        print("Joining...")
        g.join()


if __name__ == "__main__":
    _main()
