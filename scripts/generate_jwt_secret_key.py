

import argparse
import sys
import os
import asyncio



sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from url_analyzer.api.utilities import generate_jwt_secret_key


if __name__ == "__main__":
  """
  
  python scripts/generate_jwt_secret_key.py \
    --path /tmp/jwt_secret_key.txt
  
  """

  parser = argparse.ArgumentParser()
  parser.add_argument("--path", type=str, required=True)

  args = parser.parse_args()

  jwt_secret_key = generate_jwt_secret_key()
  print(jwt_secret_key)