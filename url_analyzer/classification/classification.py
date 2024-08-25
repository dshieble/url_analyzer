

import json
import logging
from typing import Optional

from url_analyzer.browser_automation.playwright_spider import PlaywrightSpider
from url_analyzer.classification.url_classification import UrlClassificationWithLLMResponse, classify_visited_url
from url_analyzer.browser_automation.playwright_page_manager import PlaywrightPageManager, PlaywrightPageManagerContext


async def spider_and_classify_url(
  url: str,
  headless: bool = True,
  included_fqdn_regex: Optional[str] = None,
  max_html_token_count: int = 2000,
) -> UrlClassificationWithLLMResponse:
  
  playwright_spider = await PlaywrightSpider.construct(
    url_list=[url],
    included_fqdn_regex=(".*" if included_fqdn_regex is None else included_fqdn_regex),
    capture_screenshot=True,
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

