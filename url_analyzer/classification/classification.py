

import json
import logging
import socket
from typing import Optional
from urllib.parse import urlparse

from url_analyzer.browser_automation.playwright_spider import PlaywrightSpider, ScreenshotType
from url_analyzer.classification.url_classification import UrlClassificationWithLLMResponse, classify_visited_url
from url_analyzer.browser_automation.playwright_page_manager import PlaywrightPageManager, PlaywrightPageManagerContext
import dns.resolver


def domain_resolves(url: str) -> bool:
  try:
    # Parse the domain from the URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Attempt to resolve the domain
    dns.resolver.resolve(domain, 'A')
    return True
  except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout, dns.exception.DNSException):
    return False

def validate_classification_inputs(url: str) -> Optional[str]:
  error = None
  parsed_url = urlparse(url)
  if parsed_url.scheme is None or len(parsed_url.scheme) == 0:
    error = "ERROR: URL must have a scheme (e.g. https://)"
  elif not domain_resolves(url):
    error = f"ERROR: The URL {url} was not found!"
  return error


async def spider_and_classify_url(
  url: str,
  headless: bool = True,
  included_fqdn_regex: Optional[str] = None,
  max_html_token_count: int = 2000,
  screenshot_type: str = ScreenshotType.VIEWPORT_SCREENSHOT
) -> UrlClassificationWithLLMResponse:
  
  playwright_spider = await PlaywrightSpider.construct(
    url_list=[url],
    included_fqdn_regex=(".*" if included_fqdn_regex is None else included_fqdn_regex),
    screenshot_type=screenshot_type,
  )
  async with PlaywrightPageManagerContext(playwright_page_manager=(
    await PlaywrightPageManager.construct(headless=headless)
  )) as playwright_page_manager:
    visited_url = await playwright_spider.get_visited_url(
      url=url,
      playwright_page_manager=playwright_page_manager
    )
    visited_url.write_to_directory(directory=playwright_spider.directory)

  url_classification_with_llm_response = await classify_visited_url(
    visited_url=visited_url,
    max_html_token_count=max_html_token_count,
  )
  return url_classification_with_llm_response

