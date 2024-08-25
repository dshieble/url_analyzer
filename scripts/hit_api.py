import sys
import os
import argparse

import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.classification.url_classification import UrlClassificationWithLLMResponse

def classify_url_with_requests(url: str, token: str):
  # Prepare the JSON payload
  payload = {
    "url": url
  }

  # Set the Authorization header
  headers = {
    # "Authorization": f"Bearer {token}"
  }

  # Send the POST request
  response = requests.post("http://localhost:8000/classify", json=payload, headers=headers)

  response.raise_for_status()
  data = response.json()
  url_classification_with_llm_response = UrlClassificationWithLLMResponse(**data)
  print(url_classification_with_llm_response.url_classification.display())

if __name__ == "__main__":
  
  """
  python scripts/hit_api.py \
    --url http://danshiebler.com/ \
    --token='5yV`maleM6a8)OfrCnE);{@jt)fZgLaG'
  """
  parser = argparse.ArgumentParser()
  parser.add_argument("--url", type=str, required=True)
  parser.add_argument("--token", type=str, required=True)

  args = parser.parse_args()

  result = classify_url_with_requests(url=args.url, token=args.token)
  print(result)