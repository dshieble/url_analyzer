import sys
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from pydantic import BaseModel

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utilities.utilities import Maybe

OPEN_URL_ACTION_NAME = "open_url"

# This is the message that we instruct the LLM to put in the alert message
XSS_ALERT_MESSAGE_SIGNAL = "101101"


class LLMOption:
  LOCAL = "local"
  OPENAI = "openai"
  TOGETHER = "together"


class LLMResponse(BaseModel):
  prompt: str
  prompt_tokens: int
  response: Optional[str]
  error: Optional[str] = None
  messages_json_string: Optional[str] = None
