from datetime import datetime, timedelta
import json
import logging
import sys
import os
import argparse
import jwt
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.classification.url_classification import RichUrlClassificationResponse


LOCAL_URL = "http://0.0.0.0:8000"
REMOTE_URL = "https://container-service-1.26jqins83oj16.us-east-1.cs.amazonlightsail.com/classify"

def classify_url_with_requests(url: str, api_key: str):


  params = {
      "url": "https://danshiebler.com"
  }

  # Set the Authorization header
  headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
  }

  target = LOCAL_URL if args.use_local else REMOTE_URL
  print(
    f"""
    Sending request!
    ----target----
    {target}
    ---headers-----
    {json.dumps(headers, indent=2)}
    ----params----
    {json.dumps(params, indent=2)}
    --------
    """
  )
  response = requests.post(target, params=params, headers=headers)

  response.raise_for_status()
  data = response.json()
  rich_url_classification_response = RichUrlClassificationResponse(**data)
  print(rich_url_classification_response.url_classification.display())

if __name__ == "__main__":
  
  """
  python scripts/hit_api.py \
    --url http://danshiebler.com/ \
    --api_key=<your api key>
  """
  parser = argparse.ArgumentParser()
  parser.add_argument("--url", type=str, required=True)
  parser.add_argument("--api_key", type=str, required=True)
  parser.add_argument("--use_local", action="store_true")

  args = parser.parse_args()

  result = classify_url_with_requests(url=args.url, api_key=args.api_key)
  print(result)