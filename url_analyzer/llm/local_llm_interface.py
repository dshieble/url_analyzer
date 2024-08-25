"""
TODO: Try hooking up to pytorch so you can use jsonformer and similar tech
TODO: Try switching to Mistral, maybe dockerized (https://ollama.ai/blog/ollama-is-now-available-as-an-official-docker-image)

"""

import asyncio

from dataclasses import dataclass
import json
import os
import subprocess
from typing import Any, Dict, List, Optional
import sys
import time
import uuid

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utilities.utilities import Maybe
from llm.formatting_utils import find_json_string
from url_analyzer.classification.url_classification import get_prompt_from_llama_instruction_template_with_function
from llm.constants import LLMResponse

BASE_LLAMA_CODE_PATH = "/Users/danshiebler/workspace/personal/pentesting/llama-mlx"
BASE_LLAMA_WEIGHTS_PATH = "/Users/danshiebler/workspace/llm_weights/Llama-2-7b-chat-mlx/"


DEFAULT_LLAMA_FUNCTION_CALL_PREFIX_PROMPT = "Based on the information provided here is the answer in json format: "
async def call_llama_with_openai_function_list(
  pre_function_prompt: str,
  openai_function_list: List[Dict[str, Any]],
  post_function_prompt: Optional[str] = None,
  system_prompt: Optional[str] = None,
  prefix_prompt: Optional[str] = None,
  **kwargs
) -> LLMResponse:
  prompt = get_prompt_from_llama_instruction_template_with_function(
    pre_function_prompt=pre_function_prompt,
    openai_function_list=openai_function_list,
    post_function_prompt=post_function_prompt,
    system_prompt=system_prompt,
    prefix_prompt=prefix_prompt if prefix_prompt is not None else DEFAULT_LLAMA_FUNCTION_CALL_PREFIX_PROMPT
  )
  llama_response = await call_llama(
    prompt=prompt,
    stop_on_valid_json=True,
    **kwargs
  )

  # Add the formatting response
  llama_response.maybe_formatted_response = llama_response.maybe_response.monad_join(
    lambda string_with_json: find_json_string(string_with_json=string_with_json)
  )
  return llama_response


# async def call_llama_instruct(
#   instruction_prompt: str,
#   system_prompt: Optional[str] = None,
#   prefix_prompt: Optional[str] = None,
#   **kwargs
# ) -> LLMResponse:
#   prompt = get_prompt_from_llama_instruction_template(
#     instruction_prompt=instruction_prompt,
#     system_prompt=system_prompt,
#     prefix_prompt=prefix_prompt
#   )
#   return await call_llama(
#     prompt=prompt,
#     **kwargs
#   )

  
async def call_llama(
  prompt: str,
  base_llama_code_path: str = BASE_LLAMA_CODE_PATH,
  base_llama_weights_path: str = BASE_LLAMA_WEIGHTS_PATH,
  verbose: bool = False,
  stop_on_valid_json: bool = False,
  max_num_tokens: int = 1000,
) -> LLMResponse:
  """
  Call LLAMA in a subprocess so that we can use a different python version/venv configuration

  Args:
    prompt: The prompt to use
    base_llama_code_path: The path to a directory that contains both
      - the virtualenv (named env) with all packages correctly installed to run llama
      - llama.py file
    base_llama_weights_path: The path to a directory that contains the weights for llama
    stop_on_valid_json: If True, then we will stop the llama run as soon as we get a valid json response
  Returns:
    The response from llama
  """

  # Write prompt to prompt_path
  timestamp = int(time.time())
  prompt_path = f"/tmp/prompt-{timestamp}"
  output_path = f"/tmp/output-{timestamp}"

  with open(prompt_path, "w") as f:
    f.write(prompt)

  arg_list = [
      f"{base_llama_code_path}/env/bin/python", f"{base_llama_code_path}/llama.py",
      "--model", f"{base_llama_weights_path}/Llama-2-7b-chat.npz",
      "--tokenizer", f"{base_llama_weights_path}/tokenizer.model",
      "--output_path", output_path,
      "--prompt_path", prompt_path,
      "--max_num_tokens", f"{max_num_tokens}"
    ]
  if stop_on_valid_json:
    arg_list += ["--stop_on_valid_json"]
  try:
    # We set this up to pipe a newline to the subprocess when it asks for the enter key
    # read, write = os.pipe()
    # os.write(write, b"\n")
    # os.close(write)

    # content = subprocess.check_output(arg_list, stderr=subprocess.STDOUT, text=True, stdin=read)
    # content = subprocess.check_output(arg_list, stderr=subprocess.STDOUT, text=True)
    # Run the command
    # result = subprocess.run(arg_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    process = await asyncio.create_subprocess_exec(*arg_list, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()

    try:
      with open(os.path.join(output_path,  "response.txt"), "r") as f:
        content = f.read().strip()
    except Exception as e:
      print(f"LLAMA output: {stdout.decode()} \n LLAMA error: {stderr.decode()}")
      raise e
    else:
      if verbose:
        print(f"LLAMA output: {stdout.decode()} \n LLAMA error: {stderr.decode()}")

  except subprocess.CalledProcessError as e:
    # Handle errors in the called executable
    maybe_response = Maybe(error=f"Error: {e.output}")
  else:
    maybe_response = Maybe(content=content)
  finally:
    # Load the token count and other information from llama
    with open(os.path.join(output_path,  "prompt_metadata.json"), "r") as f:
      prompt_metadata = json.load(f)
  return LLMResponse(
    maybe_response=maybe_response,
    prompt=prompt_metadata['raw_prompt'],
    prompt_tokens=prompt_metadata['prompt_token_length']
  )




  # return """
  # You can take any of the actions in the following list""" + str(openai_function_list) + """
  # Your response must be a json string in one of the following formats. DO NOT OUTPUT ANYTHING OTEHR THAN THE JSON STRING!
  # ```
  # {
  #   "name": <One of """ + str(name_options) + """: 
  #   "properties": {
  #     <property_1>: <your output>,
  #     <property_2>: <your output>,
  #     ...
  #   }
  # }
  # ```
  # Where `property_1`, `property_2`, etc. are the properties listed in the action instructions above

  # Your action in json format: 
  # """