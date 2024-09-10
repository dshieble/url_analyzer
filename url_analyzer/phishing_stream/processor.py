# Inspired by https://github.com/x0rz/phishing_catcher
import asyncio
import datetime
import os
from typing import Optional
import uuid

import httpx
import tqdm
from termcolor import colored

from url_analyzer.phishing_stream.keyword_domain_scorer import KeywordDomainScorer
from url_analyzer.domain_analysis.domain_lookup import DomainLookupResponse, DomainLookupTool

LOGS_ROOT_PATH = os.path.join(os.path.dirname(__file__), "../../outputs/suspicious_domains")

pbar = tqdm.tqdm(desc='certificate_update', unit='cert')

def get_log_file_name() -> str:
  return os.path.join(LOGS_ROOT_PATH, str(datetime.datetime.now()) + str(uuid.uuid4())[:4])


def is_created_or_updated_in_last_30_days(domain_lookup_response: DomainLookupResponse) -> Optional[bool]:
  # Parse the ISO formatted string into a datetime object
  # Get the current date and time
  current_date = datetime.datetime.now()
  if domain_lookup_response.created is None or domain_lookup_response.updated is None:
    output = None
  else:
    created_delta = current_date - datetime.datetime.fromisoformat(domain_lookup_response.created)
    
    updated_delta = current_date - datetime.datetime.fromisoformat(domain_lookup_response.updated)

    # Return True if the difference is more than 30 days, otherwise False
    output = created_delta < datetime.timedelta(days=30) or updated_delta < datetime.timedelta(days=30)
  return output

class Processor:
  # Wrapper class

  def __init__(self):
    self.domain_log = get_log_file_name()
    self.keyword_scorer = KeywordDomainScorer()
    self.score_cutoff = 100
    self.domain_lookup_tool = DomainLookupTool()
    self.httpx_client = httpx.AsyncClient(verify=False)

  def scale_score_by_whois_signal(self, score: float, domain: str) -> float:
    domain_lookup_response = asyncio.run(DomainLookupResponse.from_fqdn(fqdn=domain, try_rdap=False, try_async_whois=False))
    created_or_updated_recently = is_created_or_updated_in_last_30_days(domain_lookup_response=domain_lookup_response)
    if created_or_updated_recently is not None:
      if created_or_updated_recently:
        score = score * 1.2
      else:
        score = score * 0.8
    return score

  def score_domain(self, domain: str, message: dict) -> float:
    score = self.keyword_scorer.score_domain(domain=domain.lower())
    score = self.scale_score_by_whois_signal(score=score, domain=domain)

    # If issued from a free CA = more suspicious
    if "Let's Encrypt" == message['data']['leaf_cert']['issuer']['O']:
      score += 10
    return score

  def print_score(self, domain: str, score: int):
    if score >= 100:
      tqdm.tqdm.write(
        "[!] Suspicious: "
        "{} (score={})".format(colored(domain, 'red', attrs=['underline', 'bold']), score))
    elif score >= 90:
      tqdm.tqdm.write(
        "[!] Suspicious: "
        "{} (score={})".format(colored(domain, 'red', attrs=['underline']), score))
    elif score >= 80:
      tqdm.tqdm.write(
        "[!] Likely  : "
        "{} (score={})".format(colored(domain, 'yellow', attrs=['underline']), score))
    elif score >= 65:
      tqdm.tqdm.write(
        "[+] Potential : "
        "{} (score={})".format(colored(domain, attrs=['underline']), score))


  def callback(self, message, context):
    """Callback handler for certstream events."""
    if message['message_type'] == "heartbeat":
      return

    if message['message_type'] == "certificate_update":
      all_domains = message['data']['leaf_cert']['all_domains']

      for domain in all_domains:
        pbar.update(1)
        score = self.score_domain(domain=domain, message=message)

        self.print_score(domain=domain, score=score)

        if score >= self.score_cutoff:
          with open(self.domain_log, 'a') as f:
            f.write("{}\n".format(domain))

