# Given a directory with a python tool, build a docker image that we can run that tool
import argparse
from typing import Optional
import uuid
from docker import DockerClient
import os
import shutil

CODE_DIR_NAME_NAME_TO_DOCKERFILE_CONTENT = {
  "url_analyzer": """
  FROM python:3.11.7
  COPY . /app
  WORKDIR /app
  RUN mkdir /workdir
  EXPOSE 8000
  RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; else echo "No requirements.txt, skipping pip install."; fi
  """
}



def build_image(
  docker_client: DockerClient,
  tag: str,
  path_to_code_dir: str,
  code_dir_name: str,
  repository: str,
  platform: Optional[str] = None
) -> str:
  tag = tag if tag is not None else str(uuid.uuid4())
  working_dir = f"/tmp/{str(uuid.uuid4())}"
  os.mkdir(working_dir)

  # Add the code that we will be working with
  if os.path.isdir(path_to_code_dir):
    shutil.copytree(path_to_code_dir, os.path.join(working_dir, code_dir_name))
  else:
    print(f"WARNING: Path to code dir {path_to_code_dir} does not exist. Not copying code.")

  dockerfile_content = CODE_DIR_NAME_NAME_TO_DOCKERFILE_CONTENT[code_dir_name]
  # create Dockerfile
  with open(f"{working_dir}/Dockerfile", "w") as f:
    f.write(dockerfile_content)

  # build docker image
  full_tag = f"{repository}:{tag}"
  

  kwargs = {"platform": platform} if platform is not None else {}
  try:
    print(f"kwargs: {kwargs}")
    docker_client.images.build(path=working_dir, tag=full_tag, **kwargs)[0]
  except Exception as e:
    print("Hey something went wrong with image build!")
    for line in e.build_log:
        if 'stream' in line:
          print(line['stream'].strip())
    raise e

  docker_client.images.push(repository, tag)
  # push to Docker hub
  # docker_client.images.push(image_name, tag=tag)
  return full_tag


if __name__ == "__main__":
  """
  Steps:
    1. Download the code to `path_to_code_dir` using git
    2. Add a requirements.txt file if needed to the target directory
    3. Run one of the below commands


  Build
    python scripts/build_docker_image.py \
      --tag url_analyzer \
      --code_dir_name url_analyzer \
      --path_to_code_dir /Users/danshiebler/workspace/personal/phishing/url_analyzer
  Run
    docker run danshiebler/private:url_analyzer fastapi run url_analyzer/api/start_api.py  --host localhost --port 8000

  """

  parser = argparse.ArgumentParser(description='Build a docker image')
  parser.add_argument('--tag', type=str, required=True)
  parser.add_argument('--path_to_code_dir', type=str, required=True)
  parser.add_argument('--code_dir_name', type=str, required=True)
  parser.add_argument('--repository', type=str, default="danshiebler/private")
  parser.add_argument('--platform', type=str, default=None)
  args = parser.parse_args()

  docker_client = DockerClient.from_env()
  docker_client.login(username=os.environ['DOCKER_USERNAME'], password=os.environ['DOCKER_PASSWORD'])

  full_tag = build_image(
    docker_client=docker_client,
    tag=args.tag,
    path_to_code_dir=args.path_to_code_dir,
    code_dir_name=args.code_dir_name,
    repository=args.repository,
    platform=args.platform
  )
  print(f"Successfully built docker image: {full_tag}")