
import argparse
from datetime import datetime, timedelta
import sys
import os
import asyncio
from typing import List

import jwt




sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.domain_analysis.domain_lookup import DomainLookupResponse


async def main(args):
  domain_lookup_response = await DomainLookupResponse.from_fqdn(fqdn=args.fqdn)
  print(domain_lookup_response.model_dump_json(indent=2))

if __name__ == "__main__":
  """
  python scripts/get_domain_lookup_response.py \
    --fqdn nyt.com 


  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--fqdn", type=str, required=True)

  args = parser.parse_args()

  asyncio.run(main(args=args))
