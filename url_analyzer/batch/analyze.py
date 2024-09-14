

from typing import Dict
from url_analyzer.classification.classification import BasicUrlClassifier, MaybeRichUrlClassificationResponse
from url_analyzer.utilities.utilities import chunked_gather


async def classify_urls_in_text_file(
  path: str,
  chunk_size: int = 20
) -> Dict[str, MaybeRichUrlClassificationResponse]:
  with open(path, 'r') as f:
    url_list = f.readlines()

  classifier = BasicUrlClassifier()
  maybe_rich_url_classification_response_list = await chunked_gather(
    awaitable_list=[classifier.classify_url(url=url) for url in url_list],
    chunk_size=chunk_size
  )

  url_to_maybe_rich_url_classification_response = {
    url: maybe_rich_url_classification_response
    for url, maybe_rich_url_classification_response in zip(url_list, maybe_rich_url_classification_response_list)
  }
  return url_to_maybe_rich_url_classification_response