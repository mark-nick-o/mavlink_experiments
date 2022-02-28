#
# dockerfile to run web server 
#
# https://habr.com/ru/post/353234/
# https://qiita.com/nanakenashi/items/cbe8e8ef878121638514
#
# sudo docker build -t flask .

# Specifying the Base Image
FROM python:3.5.2-alpine

# home directory                                                 
ARG project_dir=/home/pi/cams/src/acp/sonyCam/docker

# Copy required files from local to container
#ADD requirements.txt $project_dir
#ADD web.py $project_dir
COPY web.py ./
ENV FLASK_APP web.py

# requirements.Install the package listed in txt                        
WORKDIR $project_dir
RUN pip install -r requirements.txt

# Install the required packages (when working in a container)
RUN apk update                  
RUN apk add zsh vim tmux git tig
