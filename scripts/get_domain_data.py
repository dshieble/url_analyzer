
import argparse
import sys
import os
import asyncio

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.domain_analysis.domain_lookup import DomainLookupResponse
from url_analyzer.domain_analysis.domain_classification import DomainClassificationResponse


async def main(args):
  domain_classification_response = DomainClassificationResponse.from_fqdn(fqdn=args.fqdn)
  print(domain_classification_response.model_dump_json(indent=2))
  print("====================================")

  domain_lookup_response = await DomainLookupResponse.from_fqdn(fqdn=args.fqdn)
  print(domain_lookup_response.model_dump_json(indent=2))

if __name__ == "__main__":
  """
  python scripts/get_domain_data.py \
    --fqdn nyt.com 


  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--fqdn", type=str, required=True)

  args = parser.parse_args()

  asyncio.run(main(args=args))
