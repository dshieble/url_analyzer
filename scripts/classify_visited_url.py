

import argparse
import sys
import os
import asyncio



sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.classification.url_classification import classify_visited_url
from url_analyzer.browser_automation.playwright_spider import load_visited_url_list_from_path



async def main(args):

  visited_url = load_visited_url_list_from_path(path=args.visited_url_json_path)[0]

  url_classification_with_llm_response = await classify_visited_url(
    visited_url=visited_url,
    max_html_token_count=2000,
  )
  print(url_classification_with_llm_response.url_classification.display())


if __name__ == "__main__":
  """
  
  python scripts/classify_visited_url.py \
    --visited_url_json_path=<path to the visited url json file>
  
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--visited_url_json_path", type=str, required=True)

  args = parser.parse_args()

  asyncio.run(main(args=args))
