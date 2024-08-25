from typing import Any, Dict,Optional, List
import together
import os
import sys
from dataclasses import dataclass
import tiktoken

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utilities.utilities import Maybe
from url_analyzer.classification.url_classification import get_prompt_from_llama_instruction_template_with_function
from llm.constants import LLMResponse
from llm.utilities import DEFAULT_ENCODER


DEFAULT_MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"
async def get_response_from_prompt_one_shot(
  prompt: str,
  model: str = DEFAULT_MODEL_NAME,
  **kwargs
) -> Maybe[str]:
  together.api_key = os.environ['TOGETHER_AI_API_KEY']

  try:
    output = together.Complete.create(
      prompt=prompt,
      model=model, 
      **kwargs
    )
    maybe_output = Maybe(content=output['output']['choices'][0]['text'])
  except Exception as e:
    maybe_output = Maybe(error=str(e))
  return maybe_output


@dataclass
class TogetherPromptResponse:
  prompt: str
  maybe_response: Maybe[str]

async def call_together_with_openai_function_list(
  pre_function_prompt: str,
  openai_function_list: List[Dict[str, Any]],
  post_function_prompt: Optional[str] = None,
  system_prompt: Optional[str] = None,
  prefix_prompt: Optional[str] = None,
  **kwargs
) -> TogetherPromptResponse:
  
  prompt = get_prompt_from_llama_instruction_template_with_function(
    pre_function_prompt=pre_function_prompt,
    openai_function_list=openai_function_list,
    post_function_prompt=post_function_prompt,
    system_prompt=system_prompt,
    prefix_prompt=prefix_prompt
  )
  
  maybe_response = await get_response_from_prompt_one_shot(
    prompt=prompt, **kwargs
  )
  return LLMResponse(
    prompt=prompt,
    maybe_response=maybe_response,
    prompt_tokens=len(DEFAULT_ENCODER.encode(prompt))
  )
