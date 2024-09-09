

import argparse
import sys
import os
from playwright.async_api import async_playwright
import asyncio

sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), '..'), '..'))


from url_analyzer.browser_automation.playwright_spider import load_visited_url_list_from_path
from url_analyzer.classification.classification import open_and_classify_url



async def main(args):

  rich_url_classification_response = await open_and_classify_url(
    url=args.url,
    headless=not args.not_headless,
    max_html_token_count=2000,
  )

  print(rich_url_classification_response.url_classification.display())


if __name__ == "__main__":
  """
  
  python url_analyzer/local/classify_url.py \
    --url http://danshiebler.com/
  
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--url", type=str, required=True)
  parser.add_argument("--not_headless",  action="store_true")

  args = parser.parse_args()

  asyncio.run(main(args=args))
