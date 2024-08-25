CLASSIFY_URL = "classify_url"

CLASSIFICATION_FUNCTION = {
  "type": "function",
  "function": {
    "name": CLASSIFY_URL,
    "description": "Navigate to a new url",
    "parameters": {
        "type": "object",
        "properties": {
          "thought_process": {
            "type": "string",
            "description": "Think step by step about this url. What are the features of this url that could imply it is phishing or not phishing?"
          },
          "is_phishing": {
            "type": "string",
            "enum": ["true", "false"],
            "description": "Your decision about whether the url is phishing or not phishing"
          },
          "justification": {
            "type": "string",
            "description": "A description of your decision, including the relevant points that led you to this conclusion."
          }
        },
        "required": ['thought_process', 'is_phishing', 'justification']
    }
  }
}
  

VISITED_URL_PROMPT_STRING_TEMPLATE = """
The url of the page is: {url}

The raw (truncated) html of the page is:
```
{trimmed_html}
```

The following urls were extracted from the page html:
```
{urls_on_page_string}
```

When we open the page we see the following network activity:
```
{network_log_string}
```
"""

PHISHING_CLASSIFICATION_PROMPT_TEMPLATE = """
You are a security analyst at a large company. You have been tasked with classifying the following url as either phishing or not phishing.


Here is a description of the url
=== Start Description ===
{visited_url_string}
=== End Description ===

Please classify the url as either phishing or not phishing.
"""