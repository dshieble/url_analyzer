

from typing import Optional
from url_analyzer.classification.prompts import PHISHING_CLASSIFICATION_PROMPT_TEMPLATE
from url_analyzer.llm.openai_interface import DEFAULT_VISION_MODEL_NAME, get_response_from_prompt_one_shot
from url_analyzer.browser_automation.playwright_spider import VisitedUrl
from url_analyzer.utilities.utilities import Maybe


async def get_image_summary(
  url: str,
  image_path: str,
  model_name: str = DEFAULT_VISION_MODEL_NAME
) -> Optional[str]:
  
  prompt = PHISHING_CLASSIFICATION_PROMPT_TEMPLATE.format(url=url)
  llm_response = await get_response_from_prompt_one_shot(
    prompt=prompt,
    image_path=image_path,
    model_name=model_name
  )
  if llm_response.error is not None:
    print(f"[get_image_summary] Error getting image summary: {llm_response.error}")
  return llm_response.response

async def get_image_description_string_from_visited_url(
  visited_url: VisitedUrl,
  model_name: str = DEFAULT_VISION_MODEL_NAME
) -> Optional[str]:
  return await get_image_summary(
    url=visited_url.url,
    image_path=visited_url.screenshot_path,
    model_name=model_name
  )