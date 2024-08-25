

import argparse
from datetime import datetime, timedelta
import sys
import os
import asyncio

import jwt



# Function to create JWT token
def create_api_key(jwt_secret_key_path: str, num_hours: int):
  # Load the JWT secret key
  with open(jwt_secret_key_path, "r") as f:
    jwt_secret_key = f.read().strip()

  payload = {
    "exp": int((datetime.now() + timedelta(hours=num_hours)).timestamp()),
    "iat": int(datetime.now().timestamp())
  }
  return jwt.encode(payload, jwt_secret_key, algorithm="HS256")


if __name__ == "__main__":
  """
  
  python scripts/generate_api_token.py \
    --jwt_secret_key_path /tmp/jwt_secret_key.txt \
    --num_hours 24
  
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--jwt_secret_key_path", type=str, required=True)
  parser.add_argument("--num_hours", type=int, required=True)

  args = parser.parse_args()

  with open(args.jwt_secret_key_path, "r") as f:
    jwt_secret_key = f.read().strip()
  token = create_api_key(jwt_secret_key_path=args.jwt_secret_key_path, num_hours=args.num_hours)
  print(token)