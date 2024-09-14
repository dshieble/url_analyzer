import argparse
import json
import os
from typing import Any, Dict
import requests


class UrlChecker:
  def __init__(self, use_local: bool):
    self.base_path = (
      'http://0.0.0.0:8000' if use_local else 'https://container-service-1.26jqins83oj16.us-east-1.cs.amazonlightsail.com'
    )
    self.api_key = self.get_api_key()

  def get_api_key(self):
    path = f'{self.base_path}/get_api_key'
    response = requests.get(path)
    response.raise_for_status()
    data = response.json()
    return data.get('api_key')

  def check_url(self, url_to_check: str, api_key: str) -> Dict[str, Any]:
    try:
      print(f'Checking URL: {url_to_check}')
      headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
      }

      params = {
        "url": "https://danshiebler.com"
      }

      path = f'{self.base_path}/classify'
      print(
        f"""
        Sending request!
        ----target----
        {path}
        ---headers-----
        {headers}
        ----params----
        {params}
        --------
        """
      )
      response = requests.post(path, params=params,  headers=headers)
    except requests.RequestException as e:
      print(f'Error checking URL: {e}')
      result = {'error': 'Failed to check URL'}
    else:
      print(f'Response: {response}')
      data = response.json()

      if response.status_code != 200:
        print(f'Setting error: {data.get("detail")}')
        result = {'error': data.get('detail')}
      else:
        print(f'Setting result: {data}')
        result = data

    return result


# Usage example:
if __name__ == '__main__':
  """
  python scripts/hit_api.py --target_url=https://danshiebler.com --use_local
  
  """
  parser = argparse.ArgumentParser()
  parser.add_argument("--target_url", type=str, required=True)
  parser.add_argument("--use_local", action="store_true")
  args = parser.parse_args()

  checker = UrlChecker(use_local=args.use_local)  # Initialize the checker
  api_key = checker.get_api_key()  # Get the API key
  result = checker.check_url(args.target_url, api_key=api_key)  # Check the URL
  print(json.dumps(result, indent=2))
    
