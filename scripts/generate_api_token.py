

import argparse
import sys
import os
import asyncio



sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.api.utilities import generate_jwt_secret_key


if __name__ == "__main__":
  """
  
  python scripts/generate_jwt_secret_key.py \
    --jwt_secret_key_path /tmp/jwt_secret_key.txt
  
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--jwt_secret_key_path", type=str, required=True)

  args = parser.parse_args()

  with open(args.jwt_secret_key_path, "r") as f:
    jwt_secret_key = f.read().strip()
  token = jwt.encode(payload, jwt_secret_key, algorithm="HS256")
  print(token)