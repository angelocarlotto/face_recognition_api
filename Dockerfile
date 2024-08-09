#sudo docker build --build-arg CACHEBUST=$(date +%s) -t "api_full:Dockerfile" .
#docker stop $(docker ps -qa)  &&  docker run --rm  -p 5001:5000  api_full:Dockerfile
#docker stop $(docker ps -qa) 
# Use the official Ubuntu base image
FROM ubuntu

ARG CACHEBUST=1

# Prevents prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive
ENV FLASK_APP=face_login_api/api/main.py
ENV FLASK_DEBUG=1

EXPOSE 5000

# Update the package list and install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    git-all\
    wget \
    unzip \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-python-dev \
    python3 \
    python3-pip \
    python3-dev \
    python3.12-venv\
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


    # Set the working directory
WORKDIR /app

# Install the Python packages from the requirements file
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip3 install --upgrade pip && \
    pip3 install Flask flask_cors flask_swagger_ui opencv-python opencv-python-headless wheel dlib face_recognition setuptools



RUN echo "Cache bust value: ${CACHEBUST}" && git clone https://github.com/angelocarlotto/face_login_api.git
RUN cd face_login_api

RUN chmod +x face_login_api/entrypoint.sh

RUN chmod -R 777 .
# Set the default command to run the application

ENTRYPOINT ["face_login_api/entrypoint.sh"]