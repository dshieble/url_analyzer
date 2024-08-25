from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from typing import Optional

from url_analyzer.api.utilities import generate_jwt_secret_key
from url_analyzer.classification.classification import spider_and_classify_url
from url_analyzer.classification.url_classification import UrlClassificationWithLLMResponse


app = FastAPI()

JWT_SECRET_KEY_PATH = "/tmp/jwt_secret_key.txt"
with open(JWT_SECRET_KEY_PATH, "r") as f:
  JWT_SECRET_KEY = f.read().strip()

# JWT bearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/classify")
async def classify_url(url: str, token: str = Depends(oauth2_scheme)):
  print(f"[classify_url] url: {url}, token: {token}")
  try:
    # Validate token
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    print("[classify_url] payload", payload)
    url_classification_with_llm_response = await spider_and_classify_url(
      url=url
    )
    # return url_classification_with_llm_response.model_dump_json()
    return url_classification_with_llm_response
  except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=403, detail="Token has expired")
  except jwt.JWTClaimsError:
    raise HTTPException(status_code=403, detail="Invalid token claims")
  except jwt.JWTError:
    raise HTTPException(status_code=403, detail="Invalid token")

if __name__ == "__main__":
  pass
