import argparse
import asyncio
import json
import os
import time
from typing import Any, Dict
import sys
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.batch.analyze import classify_urls_in_text_file

OUTPUT_ROOT_PATH = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'scans')


async def main(args):
  log_file = os.path.join(OUTPUT_ROOT_PATH, f'{int(time.time())}_{str(uuid.uuid4())[:4]}.log')
  print(f"\n--------\nWriting to log file: {log_file}\n--------\n")
  url_to_maybe_rich_url_classification_response = await classify_urls_in_text_file(
    path=args.text_file,
    chunk_size=args.chunk_size
  )
  for url, maybe_rich_url_classification_response in url_to_maybe_rich_url_classification_response.items():
    if maybe_rich_url_classification_response.content is not None:
      with open(log_file, "w") as f:
        f.write(
          json.dumps({url: json.loads(maybe_rich_url_classification_response.content.model_dump_json())}, indent=2)
        )
        f.write("\n---------\n")


# Usage example:
if __name__ == '__main__':
  """
  python scripts/classify_urls_in_text_file.py --text_file /Users/danshiebler/workspace/personal/phishing/url_analyzer/data/test_safe_urls.txt
  """
  parser = argparse.ArgumentParser()
  parser.add_argument("--text_file", type=str, required=True)
  parser.add_argument("--chunk_size", type=int, default=5)
  args = parser.parse_args()

  asyncio.run(main(args=args))
    
