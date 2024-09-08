import argparse
import sys
import os
import asyncio


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.browser_automation.playwright_driver import PlaywrightDriver
from url_analyzer.html_understanding.html_understanding import HTMLEncoding, LLMPageContent
from url_analyzer.browser_automation.playwright_page_manager import PlaywrightPageManager, PlaywrightPageManagerContext
from url_analyzer.browser_automation.playwright_spider import PlaywrightSpider, ScreenshotType
from url_analyzer.classification.url_classification import get_phishing_classification_prompt_from_visited_url
from url_analyzer.llm.utilities import get_token_count_from_prompt
from url_analyzer.classification.domain_data import DomainData

async def main(args):
  # playwright_driver = await PlaywrightDriver.construct(headless=False)
  # await playwright_driver.playwright_page_manager.open_url(url=args.url)
  # content = await LLMPageContent.from_playwright_driver(playwright_driver=playwright_driver)
  # print(content.as_string())
  playwright_spider = await PlaywrightSpider.construct(
    url_list=[args.url],
    included_fqdn_regex=".*",
    screenshot_type=args.screenshot_type
  )
  
  async with PlaywrightPageManagerContext(playwright_page_manager=(
    await PlaywrightPageManager.construct(headless=False)
  )) as playwright_page_manager:
    visited_url = await playwright_spider.get_visited_url(
      url=args.url,
      playwright_page_manager=playwright_page_manager
    )
    visited_url.write_to_directory(directory=playwright_spider.directory)

  domain_data = await DomainData.from_url(fqdn=visited_url.url)

  phishing_classification_prompt = await get_phishing_classification_prompt_from_visited_url(
    visited_url=visited_url,
    domain_data=domain_data,
    max_html_token_count=int(args.max_html_token_count),
    html_encoding=args.html_encoding
  )
  print(phishing_classification_prompt)
  print("token count", get_token_count_from_prompt(phishing_classification_prompt))

if __name__ == "__main__":
  """
  python scripts/get_website_prompt.py \
    --url https://nyt.com \
    --html-encoding trafilatura \
    --max-html-token-count 4000

  python scripts/get_website_prompt.py \
    --url https://danshiebler.com \
    --html-encoding trafilatura \
    --max-html-token-count 4000
  
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--url", type=str, required=True)
  parser.add_argument("--html-encoding", type=str, default="raw")
  parser.add_argument("--max-html-token-count", type=int, default=4000)
  parser.add_argument("--screenshot_type", type=str, default=ScreenshotType.VIEWPORT_SCREENSHOT)


  args = parser.parse_args()

  asyncio.run(main(args=args))
