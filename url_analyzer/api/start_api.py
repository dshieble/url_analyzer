import os
from fastapi import FastAPI, status, Request, Depends, HTTPException
from pydantic import BaseModel

from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import jwt

from url_analyzer.api.api_key_generation import get_api_key_from_ip_address
from url_analyzer.classification.classification import spider_and_classify_url
from url_analyzer.classification.url_classification import UrlClassificationWithLLMResponse


class HealthCheck(BaseModel):
  """Response model to validate and return when performing a health check."""

  status: str = "OK"

class ApiKey(BaseModel):
  """Response model to validate and return when performing a health check."""

  api_key: str

app = FastAPI()

JWT_SECRET_KEY = str(os.environ.get("JWT_SECRET_KEY"))

# JWT bearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get(
  "/",
  tags=["healthcheck"],
  summary="Perform a Health Check",
  response_description="Return HTTP Status Code 200 (OK)",
  status_code=status.HTTP_200_OK,
  response_model=HealthCheck,
)
def get_health() -> HealthCheck:
  """
  ## Perform a Health Check
  Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
  to ensure a robust container orchestration and management is in place. Other
  services which rely on proper functioning of the API service will not deploy if this
  endpoint returns any other HTTP status code except 200 (OK).
  Returns:
      HealthCheck: Returns a JSON response with the health status
  """
  return HealthCheck(status="OK")

@app.post("/classify")
async def classify_url(url: str, token: str = Depends(oauth2_scheme)):
  print(f"[classify_url] url: {url}, token: {token} type(token): {type(token)} JWT_SECRET_KEY: {JWT_SECRET_KEY}")
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

@app.get("/get_api_key")
async def get_ip(request: Request):
  print(f"[get_ip] request.client.host: {request.client.host}")
  ip_address = request.client.host
  api_key = get_api_key_from_ip_address(ip_address=ip_address)
  return ApiKey(api_key=api_key)
  
if __name__ == "__main__":
  """
  fastapi run url_analyzer/api/start_api.py  --host 0.0.0.0 --port 8000
  """
  pass
