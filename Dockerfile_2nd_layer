#sudo docker build  -t "face_recognition_api_2nd:v0.1" .
#sudo docker buildx build --platform=linux/arm64,linux/amd64/v2 -t angelocarlotto/face_recognition_api_2nd:latest_mult . --push
#sudo docker buildx build --platform=linux/arm64 -t angelocarlotto/face_recognition_api_2nd:latest_arm64 . --push
#sudo docker buildx build --platform=linux/amd64/v2 -t angelocarlotto/face_recognition_api_2nd:latest_amd64 . --push
#FROM face_recognition_api_1th:v0.1
FROM angelocarlotto/face_recognition_api_1th:latest_arm64

# Set the working directory
WORKDIR /app

# Install the Python packages from the requirements file
RUN  python3 -m venv venv && \
    . venv/bin/activate && \
    pip3 install --upgrade pip && \
    pip3 install Flask flask_cors Pillow flasgger opencv-python opencv-python-headless wheel dlib face_recognition setuptools

