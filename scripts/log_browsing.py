import argparse
import sys
import os
import time
import sys
import os
import asyncio


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from url_analyzer.browser_automation.playwright_page_manager import PlaywrightPageManager
from url_analyzer.utilities.utilities import run_with_logs


async def main(args):
  log_file = os.path.join(args.base_log_dir, str(int(time.time())))

  playwright_page_manager = await PlaywrightPageManager.construct(headless=False)

  await playwright_page_manager.open_url(url=args.base_url)

  if os.path.exists(log_file):
    await run_with_logs("rm -rf", log_file, process_name="mkdir")

  network_log_json = None


  start = time.time()
  while not playwright_page_manager.page.is_closed():

    # network_log = await playwright_page_manager.network_tracker.get_network_log()
    # new_network_log_json = network_log.model_dump_json(indent=2)
    # if hash(network_log_json) != hash(new_network_log_json):
    #   print(f"Logging network activity to {log_file}. Time elapsed: {time.time() - start}")
    #   network_log.write_to_file(filepath=log_file)
    #   network_log_json = new_network_log_json
    # else:
    #   print(f"No new network activity. Time elapsed: {time.time() - start}")
    await asyncio.sleep(2)
  print(f"Closing page. All logs written to {log_file}")

if __name__ == "__main__":
  """
  The goal of this script is to open a PlaywrightPageManager with network tracking and stay open until the user closes it
    
  export BASE_URL=https://deviceandbrowserinfo.com/info_device; \
  python3 scripts/log_browsing.py \
    --base_url=$BASE_URL \
    --base_log_dir=<path to where you want browsing logs to be recorded>

  """
  # Use one asynchronous process to crawl the urls
  parser = argparse.ArgumentParser()
  parser.add_argument("--base_url", type=str, required=True)
  parser.add_argument("--base_log_dir", type=str, required=True)

  args = parser.parse_args()

  asyncio.run(main(args=args))
  