import argparse
from datetime import datetime, timedelta
import sys
import os
import asyncio

import jwt

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.browser_automation.playwright_driver import PlaywrightDriver
from url_analyzer.html_understanding.html_understanding import LLMPageContent



async def main(args):
  playwright_driver = await PlaywrightDriver.construct(headless=False)
  await playwright_driver.playwright_page_manager.open_url(url=args.url)
  content = await LLMPageContent.from_playwright_driver(playwright_driver=playwright_driver)
  print(content.as_string())


if __name__ == "__main__":
  """
  
  python scripts/describe_website.py \
    --url https://danshiebler.com
  
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--url", type=int, required=True)

  args = parser.parse_args()

  asyncio.run(main(args=args))
