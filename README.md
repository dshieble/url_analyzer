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


# Building Docker

## Build dependency image
docker buildx build -t   danshiebler/private:url_analyzer_build -f dockerfiles/urlanalyzer_build . --platform linux/amd64,linux/arm64  --push --progress plain


## Build execution image
export CURRENT_PATH=$(pwd); \
docker buildx build -t   danshiebler/private:url_analyzer_run -f dockerfiles/urlanalyzer_run . --platform linux/amd64,linux/arm64  --push --progress plain --secret id=aws,src=$HOME/.aws/credentials --secret id=env,src=$CURRENT_PATH/.env;

## Push execution image to lightsail

Run
```
aws lightsail push-container-image --region us-east-1 --service-name container-service-1 --label url-analyzer --image danshiebler/private:url_analyzer_run
```

Then look at the message 
```
...
Refer to this image as ":container-service-1.url-analyzer.1" in deployments.
```

And use that as the reference to the image in lightsail container service

## Deploy docker image in lightsail
Use 


# Run Docker Image Locally
docker pull danshiebler/private:url_analyzer_run && docker run -p 8000:8000  danshiebler/private:url_analyzer_run

# HTTP Endpoint
You should have the following environment variables set
```
OPENAI_API_KEY
DOCKER_USERNAME
DOCKER_PASSWORD
```

TODO