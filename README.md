# url_analyzer
A url maliciousness detector that operates by crawling the url with playwright and then passing the crawled data to an LLM

# Local Deployment
You should have the following environment variables set
```
OPENAI_API_KEY
```

Install prerequisites wiht
```
pip install -r requirements.txt
```

You can classify a url by running
```
python url_analyzer/local/classify_url.py \
  --url http://danshiebler.com/
```

# HTTP Endpoint
You should have the following environment variables set
```
OPENAI_API_KEY
DOCKER_USERNAME
DOCKER_PASSWORD
```

TODO