# Inspired by https://github.com/x0rz/phishing_catcher
import datetime
import os
import ssl
import sys
import uuid

import certifi
import certstream
from termcolor import colored

sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), ".."), ".."))
from url_analyzer.phishing_stream.processor import Processor

CERTSTREAM_URL = 'wss://certstream.calidog.io'

if __name__ == '__main__':
  # python url_analyzer/phishing_stream/find_phishing.py
  sslopt = {"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": certifi.where()}
  processor = Processor()
  certstream.listen_for_events(processor.callback, url=CERTSTREAM_URL, sslopt=sslopt)
