# Inspired by https://github.com/x0rz/phishing_catcher
import datetime
import os
import ssl
import sys
import uuid

import certifi
import certstream
from termcolor import colored

from url_analyzer.phishing_stream.processor import Processor

CERTSTREAM_URL = 'wss://certstream.calidog.io'

if __name__ == '__main__':
  """
  python scripts/find_phishing.py
  """
  sslopt = {"cert_reqs": ssl.CERT_REQUIRED, "ca_certs": certifi.where()}
  processor = Processor()
  certstream.listen_for_events(processor.callback, url=CERTSTREAM_URL, sslopt=sslopt)
