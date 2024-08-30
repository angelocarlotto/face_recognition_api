#sudo docker buildx build --platform=linux/arm64,linux/amd64/v2 -t angelocarlotto/face_recognition_api_1th:latest_mult . --load 
#sudo docker buildx build --platform=linux/amd64/v2 -t angelocarlotto/face_recognition_api_1th:latest_amd64 . --load
#sudo docker buildx build --platform=linux/arm64 -t angelocarlotto/face_recognition_api_1th:latest_arm64 . --load
FROM ubuntu


# Update the package list and install dependencies
RUN apt-get update && apt-get install -y -q --allow-unauthenticated \
    cmake \
    python3 \
    python3-pip \
    python3-dev \
    python3.12-venv

RUN  python3 -m venv venv && \
    . venv/bin/activate && \
    pip3 install --upgrade pip && \
    pip3 install face_recognition setuptools