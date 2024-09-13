CLASSIFY_URL = "classify_url"


CLASSIFICATION_FUNCTION = {
  "type": "function",
  "function": {
    "name": CLASSIFY_URL,
    "description": "Navigate to a new url",
    "parameters": {
        "type": "object",
        "properties": {
          "page_summary": {
            "type": "string",
            "description": "A detailed summary of the page content, including the purpose, components, and interesting features of the page. This description is not intended for a security audience - if the page is not malicious then you don't need to state that in this summary."
          },
          "impersonation_strategy": {
            "type": "string",
            "description": "If the page is impersonating a known brand page, briefly describe the brands that the page is imitating. Otherwise this should be an empty string."
          },
          "credential_theft_strategy": {
            "type": "string",
            "description": "If the page has a mechanism to steal credentials page, briefly describe it. Otherwise this should be an empty string."
          },
          "thought_process": {
            "type": "string",
            "description": "Think step by step about this url. What are the features of this url that could imply it is phishing or not phishing?"
          },
          "is_domain_unused_or_for_sale": {
            "type": "string",
            "enum": ["true", "false"],
            "description": "Your decision about whether the page content indicates that the domain is unused or for sale."
          },
          "is_phishing": {
            "type": "string",
            "enum": ["true", "false"],
            "description": "Your decision about whether the url is phishing or not phishing."
          },
          "justification": {
            "type": "string",
            "description": "A description of your decision, including the relevant points that led you to this conclusion."
          }
        },
        "required": [
          "page_summary",
          "impersonation_strategy",
          "credential_theft_strategy",
          "thought_process",
          "is_domain_unused_or_for_sale",
          "is_phishing",
          "justification"
        ]
    }
  }
}

DOMAIN_DATA_DESCRIPTION_STRING_TEMPLATE = """
A basic analysis of the url FQDN returned:
```
{domain_data_json_dump}
```
"""
  
IMAGE_DESCRIPTION_STRING_TEMPLATE = """
An LLM-written description of a screenshot of the page is:
```
{llm_written_screenshot_description}
```
"""

URL_TO_CLASSIFY_PROMPT_STRING_TEMPLATE = """
The url of the page is: {url}

{domain_data_description_string}

{image_description_string}

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


# TODO: Change this to instead be multiclass classification of some sort
# TODO: Add in a space for the LLM to specify the brands that the page is imitating
PHISHING_CLASSIFICATION_PROMPT_TEMPLATE = """
You are a security analyst at a large company. You have been tasked with classifying the following url as either phishing or not phishing.

Here are some tips for making this decision
- Phishing pages are designed to gather the user's credentials. If there is no place for the user to input credentials then it is likely not a phishing page.
- Phishing pages often impersonate well-known websites. Look closely for signs of impersonation in the page content.
- Expired domains are generally not phishing pages.

Here is a description of the url
=== Start Description ===
{url_to_classify_string}
=== End Description ===

Please classify the url as either phishing or not phishing.
"""

IMAGE_DESCRIPTION_PROMPT_TEMPLATE = """
You are a security analyst at a large company. You are working with a team of analysts who have been tasked with classifying the url {url} as either phishing or not phishing.

Your role is to view a screenshot of the page and write a description of the page. Another team member will review your description alongside a summary of the page HTML to make a final decision about whether the page is phishing or not phishing. Please ensure that your description covers all relevant features of the screenshot.

However, do not indicate in your description whether you believe this to be a phishing page. Your description should be objective and descriptive.
"""