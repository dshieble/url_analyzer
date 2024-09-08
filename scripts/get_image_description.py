
import argparse
from datetime import datetime, timedelta
import sys
import os
import asyncio
from typing import List

import jwt



sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.classification.image_understanding import get_image_summary


async def main(args):
  await get_image_summary(
    url=args.url,
    image_path=args.image_path
  )

if __name__ == "__main__":
  """
  python scripts/get_image_description.py \
    --url https://nyt.com \
    --image_path /Users/danshiebler/workspace/personal/phishing/url_analyzer/url_analyzer/browser_automation/../../outputs/playwright_scanner_outputs/1725803067___https___nyt.com59d02cdc-2037-4244-b188-f13b3e5f6d98/spider/images/7108398784481993050.png


  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--url", type=str, required=True)
  parser.add_argument("--image_path", type=str, required=True)

  args = parser.parse_args()

  asyncio.run(main(args=args))
