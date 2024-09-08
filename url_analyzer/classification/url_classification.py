


import base64
import json
import logging
from typing import Optional
import trafilatura

from pydantic import BaseModel
from url_analyzer.browser_automation.playwright_spider import VisitedUrl
from url_analyzer.browser_automation.response_record import ResponseRecord
from url_analyzer.browser_automation.utilities import remove_html_comments
from url_analyzer.classification.prompts import CLASSIFICATION_FUNCTION, CLASSIFY_URL, PHISHING_CLASSIFICATION_PROMPT_TEMPLATE, VISITED_URL_PROMPT_STRING_TEMPLATE
from url_analyzer.llm.utilities import cutoff_string_at_token_count
from url_analyzer.llm.openai_interface import get_response_from_prompt_one_shot
from url_analyzer.llm.constants import LLMResponse
from url_analyzer.llm.formatting_utils import load_function_call
from url_analyzer.html_understanding.html_understanding import HTMLEncoding, get_processed_html_string
from url_analyzer.classification.image_understanding import get_image_description_string_from_visited_url
from url_analyzer.utilities.utilities import Maybe

class UrlClassification(BaseModel):
  thought_process: str
  is_phishing: bool
  justification: str

  def display(self) -> str:
    return f"Thought process: {self.thought_process}\nPhishing: {self.is_phishing}\nJustification: {self.justification}"

class PageData(BaseModel):
  base64_encoded_image: Optional[bytes] = None

  @classmethod
  async def from_visited_url(cls, visited_url: VisitedUrl) -> "PageData":
    screenshot_bytes = await visited_url.url_screenshot_response.get_screenshot_bytes()
    base64_encoded_image = base64.b64encode(screenshot_bytes).decode("utf-8")
    return cls(
      base64_encoded_image=base64_encoded_image
    )

class UrlClassificationWithLLMResponse(BaseModel):
  page_data: PageData
  url_classification: Optional[UrlClassification] = None
  llm_response: LLMResponse

  @classmethod
  async def from_visited_url_and_llm_response(
    cls,
    visited_url: VisitedUrl,
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
      page_data=await PageData.from_visited_url(visited_url=visited_url),
      url_classification=url_classification,
      llm_response=llm_response
    )

def get_network_log_string_from_response_log(
  response_log: list[ResponseRecord],
  link_token_count_max: int = 100,
  total_token_count_max: int = 5000
) -> str:
  
  processed_response_record_list = [
    f"{response_record.request_method} to "
      + cutoff_string_at_token_count(
        string=response_record.request_url,
        max_token_count=link_token_count_max
      )
      + ("" if response_record.request_post_data is None else f"with data {response_record.request_post_data}")
    for response_record in response_log
  ]
  raw_processed_response_record_list_string = "\n".join(
    processed_response_record_list
  )
  return cutoff_string_at_token_count(
    string=raw_processed_response_record_list_string,
    max_token_count=total_token_count_max
  )



async def convert_visited_url_to_string(
  visited_url: VisitedUrl,
  max_html_token_count: int = 4000,
  max_urls_on_page_string_token_count: int = 4000,
  max_network_log_string_token_count: int = 4000,
  html_encoding: str = HTMLEncoding.RAW,
  generate_llm_screenshot_description: bool = True
) -> str:
  """
  A method to convert a VisitedUrl object to a string that can be used as a prompt for an LLM
  """
  logging.info(f"Converting visited url to string: {visited_url.url}")

  if generate_llm_screenshot_description:
    logging.info(f"Generating an LLM image description of the url screenshot for {visited_url.url}")
    optional_image_description_string = await get_image_description_string_from_visited_url(visited_url=visited_url)

    image_description_string = "" if optional_image_description_string is None else optional_image_description_string
  else:
    logging.info(f"Skipping image description generation for {visited_url.url}")
    image_description_string = ""

  # HTML String
  processed_html_string = get_processed_html_string(
    html=visited_url.open_url_browser_url_visit.ending_html,
    html_encoding=html_encoding
  )
  trimmed_ending_html = cutoff_string_at_token_count(
    string=processed_html_string, max_token_count=max_html_token_count)

  # Urls on Page String 
  # TODO: Do something smarter where you order urls by domain in a way that you preferentially cut off urls from domains where other urls are in the prompt
  trimmed_urls_on_page_string = cutoff_string_at_token_count(
    string="\n".join(visited_url.urls_on_page),
    max_token_count=max_urls_on_page_string_token_count
  )

  # Network Log String
  network_log_string = get_network_log_string_from_response_log(response_log=visited_url.open_url_browser_url_visit.response_log)
  trimmed_network_log_string = cutoff_string_at_token_count(
    string=network_log_string,
    max_token_count=max_network_log_string_token_count
  )

  return VISITED_URL_PROMPT_STRING_TEMPLATE.format(
    url=visited_url.url,
    image_description_string=image_description_string,
    trimmed_html=trimmed_ending_html,
    urls_on_page_string=trimmed_urls_on_page_string,
    network_log_string=trimmed_network_log_string
  )


async def get_phishing_classification_prompt_from_visited_url(
  visited_url: VisitedUrl,
  max_html_token_count: int = 4000,
  html_encoding: str = HTMLEncoding.RAW
) -> str:
  visited_url_string = await convert_visited_url_to_string(
    visited_url=visited_url,
    max_html_token_count=max_html_token_count,
    html_encoding=html_encoding)
  return PHISHING_CLASSIFICATION_PROMPT_TEMPLATE.format(visited_url_string=visited_url_string)

async def get_raw_url_classification_llm_response_from_visited_url(
  visited_url: VisitedUrl,
  max_html_token_count: int = 2000,
  html_encoding: str = HTMLEncoding.RAW
) -> LLMResponse:

  phishing_classification_prompt = await get_phishing_classification_prompt_from_visited_url(
    visited_url=visited_url,
    max_html_token_count=max_html_token_count,
    html_encoding=html_encoding
  )
  llm_response = await get_response_from_prompt_one_shot(
    prompt=phishing_classification_prompt,
    tools=[CLASSIFICATION_FUNCTION],
    tool_choice="auto",
  )
  return llm_response
  

async def classify_visited_url(
  visited_url: VisitedUrl,
  max_html_token_count: int = 2000,
  html_encoding: str = HTMLEncoding.RAW
) -> UrlClassificationWithLLMResponse:
  llm_response = await get_raw_url_classification_llm_response_from_visited_url(
    visited_url=visited_url,
    max_html_token_count=max_html_token_count,
    html_encoding=html_encoding
  )
  return await UrlClassificationWithLLMResponse.from_visited_url_and_llm_response(visited_url=visited_url, llm_response=llm_response)

