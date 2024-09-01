"""
The goal of this file is to store helper methods for representing page content to an LLM in a way that the LLM can then communicate this context back to the playwright driver

"""
import asyncio
import os
import sys

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import urllib.parse
import json
import time
import re
from typing import List, Optional, Union

import os
import sys

from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
import urllib.parse
import json
import time
import re
from typing import List, Optional, Union

from playwright.async_api import async_playwright
from playwright.async_api._generated import ElementHandle
from playwright_stealth import stealth_async
import inscriptis

from unidecode import unidecode

from url_analyzer.browser_automation.playwright_page_manager import PlaywrightPageManager
from url_analyzer.browser_automation.utilities import get_outer_html_list_from_locator_list, get_url_screenshot_response_from_loaded_page, remove_hidden_elements, remove_html_comments, remove_html_metadata
from url_analyzer.browser_automation.datamodel import BrowserUrlVisit, UrlScreenshotResponse, scroll_page_and_wait
from url_analyzer.browser_automation.playwright_driver import ActionResponse, PlaywrightDriver

from url_analyzer.utilities.utilities import Maybe, json_dumps_safe, safe_to_int
from url_analyzer.utilities.utilities import Maybe
from url_analyzer.llm.formatting_utils import find_json_string
from url_analyzer.llm.utilities import cutoff_string_at_token_count, get_diff_string_from_html_strings


SUSPICIOUS_KEYWORDS = ['password', 'login', 'verify', 'account', 'bank', 'urgent', 'security', 'update']


@dataclass
class LLMFormContent:
  """
  A data structure that stores the interactable elements on a webpage
  """
  form_html: str
  form_text: str
  form_field_text_to_options: Dict[str, List[str]]
  form_field_text_to_html: Dict[str, str]


  @classmethod
  async def from_playwright_driver(cls, playwright_driver: PlaywrightDriver) -> "Optional[InteractableElements]":
    """
    Extract the interactable elements from the page and convert them to an LLM-visible text format
    """
    form_fields = await playwright_driver.get_form_fields_from_single_visible_form()
    
    if form_fields.content:
      form_html = "" if form_fields.content.form_locator is None else await get_outer_html_list_from_locator_list([form_fields.content.form_locator])

      user_supplied_form_field_options_list = await asyncio.gather(*[
        form_field.get_options() for form_field in form_fields.content.user_supplied_form_field_list
      ])
      user_supplied_form_field_html_list = await get_outer_html_list_from_locator_list(
        form_field.locator for form_field in form_fields.content.user_supplied_form_field_list
      )
      llm_form_content = cls(
        form_html=form_html,
        form_text=inscriptis.get_text(form_html),
        form_field_text_to_options = {
          form_field.text: options for form_field, options in zip(form_fields.content.user_supplied_form_field_list, user_supplied_form_field_options_list)
        },
        form_field_text_to_html = {
          form_field.text: html for form_field, html in zip(form_fields.content.user_supplied_form_field_list, user_supplied_form_field_html_list)
        }
      )
    else:
      llm_form_content = None


    print(f"llm_form_content: {llm_form_content}")
    return llm_form_content

@dataclass
class LLMNonFormInputFields:
  """
  Represents the input fields on a page that are not part of a form
  """

  # These will be empty dicts if there are no non-form input fields on the page
  non_form_field_text_to_options: Dict[str, List[str]]
  non_form_input_field_to_html: Dict[str, str]

  @classmethod
  async def from_playwright_driver(cls, playwright_driver: PlaywrightDriver) -> "Optional[LLMNonFormInputFields]":
    
    non_form_fields = await playwright_driver.get_non_form_input_form_fields_from_page_directly()
    user_supplied_non_form_field_options_list = await asyncio.gather(*[
      form_field.get_options() for form_field in non_form_fields.content.user_supplied_form_field_list
    ])
    user_supplied_non_form_field_html_list = await get_outer_html_list_from_locator_list(
      [form_field.locator for form_field in non_form_fields.content.user_supplied_form_field_list]
    )
    non_form_field_text_to_options = {
      non_form_field.text: options for non_form_field, options in zip(non_form_fields.content.user_supplied_form_field_list, user_supplied_non_form_field_options_list)
    }
    non_form_input_field_to_html = {
      non_form_field.text: html for non_form_field, html in zip(non_form_fields.content.user_supplied_form_field_list, user_supplied_non_form_field_html_list)
    }
    return cls(
      non_form_field_text_to_options=non_form_field_text_to_options,
      non_form_input_field_to_html=non_form_input_field_to_html
    )


@dataclass
class LLMPageContent:
  """
  A data structure that stores the interactable elements on a webpage
  """
  url: str
  html: str
  llm_form_content: Optional[LLMFormContent]
  llm_non_form_input_fields: LLMNonFormInputFields
  button_text_to_html: Dict[str, str]

  @property
  def button_text_list(self) -> List[str]:
    return list(self.button_text_to_html.keys())
  
  @property 
  def form_field_text_to_options(self) -> Optional[Dict[str, List[str]]]:
    return None if self.llm_form_content is None else self.llm_form_content.form_field_text_to_options

  @property 
  def non_form_field_text_to_options(self) -> Optional[Dict[str, List[str]]]:
    # Get input fields from a page that are not part of a form
    return self.llm_non_form_input_fields.non_form_field_text_to_options

  @classmethod
  async def from_playwright_driver(cls, playwright_driver: PlaywrightDriver, **locator_is_interactable_kwargs) -> "LLMPageContent":
    """
    Extract the interactable elements from the page and convert them to an LLM-visible text format
    """
    
    llm_form_content = await LLMFormContent.from_playwright_driver(playwright_driver=playwright_driver)
    llm_non_form_input_fields = await LLMNonFormInputFields.from_playwright_driver(playwright_driver=playwright_driver)

    button_list = await playwright_driver.get_button_list(**locator_is_interactable_kwargs)
    button_html_list = await get_outer_html_list_from_locator_list(
      [button.locator for button in button_list]
    )


    return cls(
      url=playwright_driver.playwright_page_manager.page.url,
      html=await playwright_driver.playwright_page_manager.page.content(),
      llm_form_content=llm_form_content,
      llm_non_form_input_fields=llm_non_form_input_fields,
      button_text_to_html = {
        button.text: html
        for button, html in zip(button_list, button_html_list)
      }
    )
  
  def as_string_dict(
    self,
    max_url_token_count: Optional[int] = 200,
    max_button_html_token_count: Optional[int] = 100,
    max_form_field_html_token_count: Optional[int] = 100,
    max_html_token_count: Optional[int] = 100
  ) -> Dict[str, str]:
    
    # TODO: Decide whether to add non-form input fields too

    string_dict = {
      "url": cutoff_string_at_token_count(string=self.url, max_token_count=max_url_token_count),
      "html": cutoff_string_at_token_count(string=remove_html_comments(html=self.html), max_token_count=max_html_token_count)
    }
    if len(self.button_text_to_html) > 0:
      string_dict["buttons"] = "\n".join(
        cutoff_string_at_token_count(string=remove_html_comments(html=html), max_token_count=max_button_html_token_count)
        for html in self.button_text_to_html.values()
        if html is not None
      )
    
    if self.llm_form_content is not None:
      # TODO: Change to list if we decide to support multiple forms
      string_dict["form"] = "\n".join(
        cutoff_string_at_token_count(string=remove_html_comments(html=html), max_token_count=max_form_field_html_token_count)
        for html in self.llm_form_content.form_field_text_to_html.values()
        if html is not None
      )

    return string_dict

  def as_string(self, **kwargs) -> str:
    return json_dumps_safe(self.as_string_dict(**kwargs))






@dataclass
class WebsiteDescription:
  """
  A data structure that stores the details of a webpage

  TODO: Unify with UrlScreenshotResponse and maybe incoporate OCR
  """
  url: str
  visible_html: str
  visible_text: str
  url_screenshot_response: UrlScreenshotResponse
  ocr_screenshot_text: str



async def get_visible_html_and_text(playwright_page_manager: PlaywrightPageManager) -> Tuple[str, str]:

  # TODO: Switch visibility assessment to use javascript to increase accuracy
  # script = """
  #   Array.from(document.querySelectorAll('body *'))
  #     .filter(el => 
  #       el.offsetWidth > 0
  #       && el.offsetHeight > 0
  #       && el.getClientRects().length > 0
  #       && el.clientHeight > 0
  #       && window.getComputedStyle(el).display != 'none'
  #       && window.getComputedStyle(el).visibility === 'visible'
  #       && el.offsetParent !== null
  #       && el.checkVisibility()
  #     )
  #     .map(el => '*|*' + el.textContent)
      
  #     .join(' ')
  # """
  # result = await driver.playwright_page_manager.page.evaluate(script)
  # print(result.split("*|*")[:5])
  # html = await self.playwright_page_manager.page.content()
  
  html_description = ""
  text_description = ""
  for frame in playwright_page_manager.page.frames:
    html = await frame.content()
    html = remove_hidden_elements(html=html)
    html = remove_html_metadata(html=html)

    html_description += f"-----\nWithin frame {frame.name}:\n {html}\n----\n"
    text_description += f"-----\nWithin frame {frame.name}:\n {inscriptis.get_text(html)}\n----\n"

  return html_description, text_description


async def describe_website(playwright_driver: PlaywrightDriver) -> Maybe[WebsiteDescription]:

  # Let the page wait for load
  await scroll_page_and_wait(page=playwright_driver.playwright_page_manager.page, timeout=3000)

  try:
    # Extract main content
    visible_html, visible_text = await get_visible_html_and_text(playwright_page_manager=playwright_driver.playwright_page_manager)
  except Exception as e:
    maybe_website_description = Maybe(error=f"ERROR: Cannot load {playwright_driver.playwright_page_manager.page.url}. EXCEPTION: {e}")
  else:

    # Capture a screenshot of the page
    url_screenshot_response = await get_url_screenshot_response_from_loaded_page(page=playwright_driver.playwright_page_manager.page)

    # Get OCR text from the screenshot
    ocr_screenshot_text = await url_screenshot_response.get_screenshot_ocr_text()

    maybe_website_description = Maybe(content=WebsiteDescription(
      url=playwright_driver.playwright_page_manager.page.url,
      visible_html=visible_html,
      visible_text=visible_text,
      url_screenshot_response=url_screenshot_response,
      ocr_screenshot_text=ocr_screenshot_text
    ))
  return maybe_website_description



def find_context(text: str, start: int, length: int = 200) -> str:
  # Extract a portion of the text around a specific index
  start_index = max(start - length, 0)
  end_index = min(start + length, len(text))
  return text[start_index:end_index].strip()

def extract_links_context(html: str, soup: BeautifulSoup) -> List[str]:
  # Extract context around links (<a href>)
  contexts = []
  for a in soup.find_all('a', href=True):
    link = a['href']
    link_index = html.find(link)
    if link_index != -1:
      context = find_context(html, link_index)
      contexts.append(f"Link: {link}\nContext: {context}")
  return contexts

def extract_emails_context(html: str) -> List[str]:
  # Extract context around email addresses
  contexts = []
  for match in re.finditer(r'[\w\.-]+@[\w\.-]+', html):
    email = match.group(0)
    email_index = match.start()
    context = find_context(html, email_index)
    contexts.append(f"Email: {email}\nContext: {context}")
  return contexts

def extract_keywords_context(html: str) -> List[str]:
  # Example suspicious keywords for phishing detection
  contexts = []
  for keyword in SUSPICIOUS_KEYWORDS:
    for match in re.finditer(keyword, html, re.IGNORECASE):
      keyword_index = match.start()
      context = find_context(html, keyword_index)
      contexts.append(f"Keyword: {keyword}\nContext: {context}")
  return contexts

def process_html_for_llm(
  html_string: str,
  max_attribute_token_count: int = 1000
) -> Dict[str, List[str]]:
  # Parse the HTML
  soup = BeautifulSoup(html_string, 'html.parser')
  
  # Extract relevant contexts
  links_context = extract_links_context(html_string, soup)
  emails_context = extract_emails_context(html_string)
  keywords_context = extract_keywords_context(html_string)
  
  # Construct a compact representation
  return {
    "links": cutoff_string_at_token_count(str(links_context), max_token_count=max_attribute_token_count),
    "emails": cutoff_string_at_token_count(str(emails_context), max_token_count=max_attribute_token_count),
    "keywords": cutoff_string_at_token_count(str(keywords_context), max_token_count=max_attribute_token_count),
  }
