# Given a directory with a python tool, build a docker image that we can run that tool
import argparse
from typing import Optional
import uuid
from docker import DockerClient
import os
import shutil


# TODO: Set environment variables

CODE_DIR_NAME_NAME_TO_DOCKERFILE_CONTENT = {
  "url_analyzer": """
  FROM python:slim
  COPY . /app
  RUN ls
  WORKDIR /app
  RUN ls
  RUN ls url_analyzer

  RUN mkdir /workdir
  RUN pip install "fastapi[standard]"
  RUN pip install -r url_analyzer/url_analyzer/requirements.txt
  EXPOSE 8000
  CMD fastapi run url_analyzer/url_analyzer/api/start_api.py  --host 0.0.0.0  --port 8000
  """
}



def build_image(
  docker_client: DockerClient,
  tag: str,
  path_to_code_dir_parent: str,
  code_dir_name: str,
  repository: str,
  platform: Optional[str] = None
) -> str:
  tag = tag if tag is not None else str(uuid.uuid4())
  working_dir = f"/tmp/{str(uuid.uuid4())}"
  os.mkdir(working_dir)

  # Add the code that we will be working with
  if os.path.isdir(path_to_code_dir_parent):
    shutil.copytree(path_to_code_dir_parent, os.path.join(working_dir, code_dir_name))
  else:
    print(f"WARNING: Path to code dir {path_to_code_dir_parent} does not exist. Not copying code.")

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
  return full_tag


if __name__ == "__main__":
  """

  Setup Docker (instructions below are just an example for an ARM Mac)
    docker login
    colima start -m 8

    # This symlink is required to enable the python DockerClient to work with colima (https://github.com/abiosoft/colima/issues/468)
    sudo ln -sf $HOME/.colima/default/docker.sock /var/run/docker.sock

  Build
    python scripts/build_docker_image.py \
      --tag url_analyzer \
      --code_dir_name url_analyzer \
      --repository <your docker repository> \
      --path_to_code_dir_parent <path to this directory>
  Run
    docker run <your docker repository>:url_analyzer fastapi run url_analyzer/url_analyzer/api/start_api.py  --host localhost --port 8000

  """

  parser = argparse.ArgumentParser(description='Build a docker image')
  parser.add_argument('--tag', type=str, required=True)
  parser.add_argument('--path_to_code_dir_parent', type=str, required=True)
  parser.add_argument('--code_dir_name', type=str, required=True)
  parser.add_argument('--repository', type=str, required=True)
  parser.add_argument('--platform', type=str, default=None)
  args = parser.parse_args()

  docker_client = DockerClient.from_env()
  docker_client.login(username=os.environ['DOCKER_USERNAME'], password=os.environ['DOCKER_PASSWORD'])

  full_tag = build_image(
    docker_client=docker_client,
    tag=args.tag,
    path_to_code_dir_parent=args.path_to_code_dir_parent,
    code_dir_name=args.code_dir_name,
    repository=args.repository,
    platform=args.platform
  )
  print(f"Successfully built docker image: {full_tag}")