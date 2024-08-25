from urllib.request import Request
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import asyncio
from urllib.parse import urlparse
import uvicorn

from url_analyzer.api.utilities import generate_jwt_secret_key


app = FastAPI()
jwt_secret_key = generate_jwt_secret_key()
print(f"******\nGenerated jwt_secret_key: {jwt_secret_key}\n******")

class UrlClassificationWithLLMResponse(BaseModel):
  url: str
  classification_result: str
  confidence_score: float

class UrlClassificationRequest(BaseModel):
  url: str

class JWTBearer(HTTPBearer):
  async def __call__(self, request: Request):
    credentials: HTTPAuthorizationCredentials = await super().__call__(request)
    if credentials:
      if not credentials.scheme == "Bearer":
        raise HTTPException(status_code=403, detail="Invalid authentication scheme")
      if not self.verify_jwt(credentials.credentials):
        raise HTTPException(status_code=403, detail="Invalid token or expired token")
      return credentials.credentials
    else:
      raise HTTPException(status_code=403, detail="Invalid authorization code")

  def verify_jwt(self, jwtoken: str) -> bool:
    try:
      payload = jwt.decode(jwtoken, jwt_secret_key, algorithms=["HS256"])
      return True
    except jwt.ExpiredSignatureError:
      return False
    except jwt.InvalidTokenError:
      return False
    return False

@app.post("/classify", dependencies=[Depends(JWTBearer())])
async def classify_url(url_request: UrlClassificationRequest):
  url = url_request.url
  parsed_url = urlparse(url)
  domain = parsed_url.netloc
  
  # Simulating the classification process
  classification_result = f"Classified {domain} as a website"
  confidence_score = 0.8
  
  return UrlClassificationWithLLMResponse(
    url=url,
    classification_result=classification_result,
    confidence_score=confidence_score
  )

if __name__ == "__main__":
  """
  uvicorn /Users/danshiebler/workspace/personal/phishing/url_analyzer/api/start_api.py:app --host 0.0.0.0 --port 8000
  """
  uvicorn.run(app, host="0.0.0.0", port=8000)