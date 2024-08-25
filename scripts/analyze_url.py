

import argparse
from collections import defaultdict
import random
import time
import traceback
from pydantic import BaseModel, ValidationError, field_validator
import sys
import os
from typing import Any, Dict, List, Optional, Set, Tuple, TypeVar
import uuid
from playwright.async_api import async_playwright
import asyncio
import re
import w3lib.url



sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.browser_automation.playwright_dynamic_spider import explore_page

from url_analyzer.browser_automation.playwright_page_manager import PlaywrightPageManager, PlaywrightPageManagerCloneContext, PlaywrightPageManagerContext
from url_analyzer.browser_automation.utilities import get_href_links_from_page, get_image_links_from_page, get_url_screenshot_response_from_loaded_page
from url_analyzer.browser_automation.datamodel import BrowserUrlVisit, UrlScreenshotResponse
from url_analyzer.browser_automation.playwright_driver import FormField, PlaywrightDriver
from url_analyzer.browser_automation.run_calling_context import fill_form_on_page_worker_with_context, open_url_with_context

from url_analyzer.browser_automation.playwright_spider import PlaywrightSpider
from url_analyzer.utilities.single_visit_queue import PrefixOptimizedSingleVisitQueue
from url_analyzer.utilities.utilities import Maybe, filter_url, get_base_url_from_url, load_pydantic_model_from_directory_path, pydantic_create, pydantic_validate, run_with_logs, url_to_filepath
from url_analyzer.utilities.constants import URL_ASSET_REGEX
from url_analyzer.utilities.logger import BASE_LOG_DIRECTORY, Logger



async def main(args):

  playwright_spider = await PlaywrightSpider.construct(
    url_list=[args.target_url],
    included_fqdn_regex=(".*" if args.included_fqdn_regex is None else args.included_fqdn_regex),
    capture_screenshot=True,
  )
  async with PlaywrightPageManagerContext(playwright_page_manager=(
    await PlaywrightPageManager.construct(headless=not args.not_headless)
  )) as playwright_page_manager:
    visited_url = await playwright_spider.get_visited_url(
      url=args.target_url,
      playwright_page_manager=playwright_page_manager
    )
    visited_url.write_to_directory(directory=playwright_spider.directory)



if __name__ == "__main__":
  """
  
  python scripts/analyze_url.py \
    --target_url=http://danshiebler.com/ \
    --not_headless
  
  python scripts/analyze_url.py \
    --target_url=http://5hpf7vz.nickleonardson.com/ \
    --not_headless
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--target_url", type=str, required=True)
  parser.add_argument("--included_fqdn_regex", type=str, default=None)
  parser.add_argument("--not_headless",  action="store_true")


  args = parser.parse_args()

  asyncio.run(main(args=args))
  