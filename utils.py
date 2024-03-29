import http.client
import logging
import os
import queue as Queue
import ssl
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
from pathlib import Path
import yaml


def enable_requests_logging():
    http.client.HTTPConnection.debuglevel = 4

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def is_remote_session():
    return os.environ.get("SSH_TTY", os.environ.get("SSH_CONNECTION"))


class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"You're all set, you can close this window!")

        code = parse_qs(urlparse(self.path).query).get("code", [""])[0]
        self.server.return_code(code)

    def log_message(self, format, *args):
        return


class RedirectHTTPServer(HTTPServer, object):
    def __init__(self, listen, handler_class, https=False):
        super(RedirectHTTPServer, self).__init__(listen, handler_class)

        self._auth_code_queue = Queue.Queue()

        if https:
            self.socket = ssl.wrap_socket(
                self.socket, certfile="./ssl/server.pem", server_side=True
            )

    def return_code(self, code):
        self._auth_code_queue.put_nowait(code)

    def wait_for_code(self):
        return self._auth_code_queue.get(block=True)


def start_local_server(listen=("", 4443)):
    server = RedirectHTTPServer(listen, RedirectHandler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server


def directory_parser(directory):
    import platform
    if platform.system() == 'Windows':
        import re
        print("Windows user detected")
        directory = tuple([re.sub(r'(:)/', r'\1', path) for path in directory])
    return directory


class YAMLReader(dict):
    def __init__(self, SCRIPT_PATH):
        self.yaml_file = f'{SCRIPT_PATH}/config.yaml'
        with open(self.yaml_file) as f:
            yaml_dict = yaml.safe_load(f)
            super().__init__(yaml_dict)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        with open(self.yaml_file, 'w') as f:
            yaml.dump(dict(self), f)
