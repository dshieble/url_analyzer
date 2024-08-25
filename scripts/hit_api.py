from datetime import datetime, timedelta
import sys
import os
import argparse
import jwt
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.classification.url_classification import UrlClassificationWithLLMResponse


# Function to create JWT token
def create_jwt_token(jwt_secret_key_path: str):
  # Load the JWT secret key
  with open(jwt_secret_key_path, "r") as f:
    jwt_secret_key = f.read().strip()

  payload = {
    "exp": int((datetime.now() + timedelta(hours=1)).timestamp()),  # Expire in 1 hour
    "iat": int(datetime.now().timestamp())
  }
  return jwt.encode(payload, jwt_secret_key, algorithm="HS256")

def classify_url_with_requests(url: str, jwt_secret_key_path: str):

  # Prepare the JSON payload
  payload = {
    "url": url
  }

  token = create_jwt_token(jwt_secret_key_path)

  # Set the Authorization header
  headers = {
    "Authorization": f"Bearer {token}"
  }

  # Send the POST request
  response = requests.post("http://localhost:8000/classify", params=payload, headers=headers)

  response.raise_for_status()
  data = response.json()
  url_classification_with_llm_response = UrlClassificationWithLLMResponse(**data)
  print(url_classification_with_llm_response.url_classification.display())

if __name__ == "__main__":
  
  """
  python scripts/hit_api.py \
    --url http://danshiebler.com/ \
    --jwt_secret_key_path=/tmp/jwt_secret_key.txt
  """
  parser = argparse.ArgumentParser()
  parser.add_argument("--url", type=str, required=True)
  parser.add_argument("--jwt_secret_key_path", type=str, required=True)

  args = parser.parse_args()

  result = classify_url_with_requests(url=args.url, jwt_secret_key_path=args.jwt_secret_key_path)
  print(result)