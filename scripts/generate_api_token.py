

import argparse
from datetime import datetime, timedelta
import sys
import os
import asyncio

import jwt


JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")

# Function to create JWT token
def create_api_key(num_hours: int):
  payload = {
    "exp": int((datetime.now() + timedelta(hours=num_hours)).timestamp()),
    "iat": int(datetime.now().timestamp())
  }
  return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")


if __name__ == "__main__":
  """
  
  python scripts/generate_api_token.py \
    --num_hours 24
  
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--num_hours", type=int, required=True)

  args = parser.parse_args()

  token = create_api_key(num_hours=args.num_hours)
  print(token)