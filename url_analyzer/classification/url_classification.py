


import json
import logging
from typing import Optional

from pydantic import BaseModel
from url_analyzer.browser_automation.playwright_spider import VisitedUrl
from url_analyzer.browser_automation.response_record import ResponseRecord
from url_analyzer.browser_automation.utilities import remove_html_comments
from url_analyzer.classification.prompts import CLASSIFICATION_FUNCTION, CLASSIFY_URL, PHISHING_CLASSIFICATION_PROMPT_TEMPLATE, VISITED_URL_PROMPT_STRING_TEMPLATE
from url_analyzer.llm.utilities import cutoff_string_at_token_count
from url_analyzer.llm.openai_interface import get_response_from_prompt_one_shot
from url_analyzer.llm.constants import LLMResponse
from url_analyzer.llm.formatting_utils import find_json_string, load_function_call
from url_analyzer.utilities.utilities import Maybe

class UrlClassification(BaseModel):
  thought_process: str
  is_phishing: bool
  justification: str

  def display(self) -> str:
    return f"Thought process: {self.thought_process}\nPhishing: {self.is_phishing}\nJustification: {self.justification}"

class UrlClassificationWithLLMResponse(BaseModel):
  url_classification: Optional[UrlClassification] = None
  llm_response: LLMResponse

  @classmethod
  def from_llm_response(
    cls,
    llm_response: LLMResponse
  ) -> "UrlClassificationWithLLMResponse":
    
    url_classification = None
    if llm_response.response is not None:
      maybe_formatted_response = load_function_call(raw_llm_response=llm_response.response, argument_name=CLASSIFY_URL)
      if (
        maybe_formatted_response.content is not None
        and set(["thought_process", "is_phishing", "justification"]) <= set(maybe_formatted_response.content.keys())
      ):
        url_classification = UrlClassification(
          thought_process=maybe_formatted_response.content.get("thought_process"),
          is_phishing=maybe_formatted_response.content.get("is_phishing"),
          justification=maybe_formatted_response.content.get("justification"),
        )
      else:
        logging.error(
          f"""Could not extract url classification from response!
          llm_response.response
          {llm_response.response}

          maybe_formatted_response
          {maybe_formatted_response}
          """
        )
    return cls(
      url_classification=url_classification,
      llm_response=llm_response
    )

def _response_record_to_string(response_record: ResponseRecord) -> str:
  return f"{response_record.request_method} to {response_record.request_url} with data {response_record.request_post_data}"

def convert_visited_url_to_string(
  visited_url: VisitedUrl,
  max_html_token_count: int = 2000,
) -> str:
  html = visited_url.open_url_browser_url_visit.ending_html
  
  trimmed_ending_html = cutoff_string_at_token_count(
    string=remove_html_comments(html=html), max_token_count=max_html_token_count)

  network_log_string = "\n".join(
    [_response_record_to_string(response_record) for response_record in visited_url.open_url_browser_url_visit.response_log]
  )
  return VISITED_URL_PROMPT_STRING_TEMPLATE.format(
    url=visited_url.url,
    trimmed_html=trimmed_ending_html,
    urls_on_page_string="\n".join(visited_url.urls_on_page),
    network_log_string=network_log_string
  )

async def get_raw_url_classification_llm_response_from_visited_url(
  visited_url: VisitedUrl,
  max_html_token_count: int = 2000,
) -> LLMResponse:
  visited_url_string = convert_visited_url_to_string(visited_url=visited_url, max_html_token_count=max_html_token_count)

  phishing_classification_prompt = PHISHING_CLASSIFICATION_PROMPT_TEMPLATE.format(visited_url_string=visited_url_string)
  llm_response = await get_response_from_prompt_one_shot(
    prompt=phishing_classification_prompt,
    tools=[CLASSIFICATION_FUNCTION],
    tool_choice="auto",
  )
  return llm_response
  

async def classify_visited_url(
  visited_url: VisitedUrl,
  max_html_token_count: int = 2000,
) -> UrlClassificationWithLLMResponse:
  llm_response = await get_raw_url_classification_llm_response_from_visited_url(
    visited_url=visited_url,
    max_html_token_count=max_html_token_count,
  )
  return UrlClassificationWithLLMResponse.from_llm_response(llm_response=llm_response)
