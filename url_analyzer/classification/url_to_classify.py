import base64
import logging
from typing import Optional

from pydantic import BaseModel
from url_analyzer.browser_automation.playwright_spider import VisitedUrl
from url_analyzer.browser_automation.response_record import ResponseRecord
from url_analyzer.classification.prompts import CLASSIFICATION_FUNCTION, CLASSIFY_URL, DOMAIN_DATA_DESCRIPTION_STRING_TEMPLATE, PHISHING_CLASSIFICATION_PROMPT_TEMPLATE, URL_TO_CLASSIFY_PROMPT_STRING_TEMPLATE
from url_analyzer.llm.utilities import cutoff_string_at_token_count
from url_analyzer.llm.openai_interface import get_response_from_prompt_one_shot
from url_analyzer.llm.constants import LLMResponse
from url_analyzer.llm.formatting_utils import load_function_call
from url_analyzer.html_understanding.html_understanding import HTMLEncoding, get_processed_html_string
from url_analyzer.classification.image_understanding import get_image_description_string_from_visited_url
from url_analyzer.classification.domain_data import DomainData
from url_analyzer.browser_automation.datamodel import UrlScreenshotResponse


class UrlToClassify(BaseModel):
  url: str
  html: str
  url_screenshot_response: Optional[UrlScreenshotResponse] = None
  urls_on_page: Optional[list[str]] = None
  response_log: Optional[ResponseRecord] = None

  @classmethod
  def from_visited_url(cls, visited_url: VisitedUrl) -> "UrlToClassify":
    return cls(
      url=visited_url.url,
      html=visited_url.open_url_browser_url_visit.ending_html,
      url_screenshot_response=visited_url.url_screenshot_response,  
      urls_on_page=visited_url.urls_on_page,
      response_log=visited_url.open_url_browser_url_visit.response_log
    )