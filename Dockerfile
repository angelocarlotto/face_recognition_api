# Use the official Ubuntu base image
FROM ubuntu

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
WORKDIR /face_login_api

# Copy the requirements file into the container

# Copy the rest of the application code into the container
RUN git clone https://github.com/angelocarlotto/face_login_api.git
RUN cd face_login_api

# Install the Python packages from the requirements file
RUN python3 -m venv venv && \
    . venv/bin/activate && \
    pip3 install --upgrade pip && \
    pip3 install Flask flask_cors flask_swagger_ui opencv-python opencv-python-headless wheel dlib face_recognition setuptools

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

RUN chmod -R 777 .
# Set the default command to run the application

ENTRYPOINT ["./entrypoint.sh"]



# FROM ubuntu

# RUN apt update && apt install build-essential curl file git python3 python3-pip net-tools git-all cmake python3.12-venv  python3-opencv libgl1 libglib2.0-0 -y
# RUN git clone https://github.com/angelocarlotto/face_login_api.git
# RUN cd face_login_api
# RUN ls
# CMD ["export", "FLASK_APP=api/main.py"]
# CMD ["python3", "-m", "venv", "venv"]
# CMD [".", "venv/bin/activate"]
# #CMD  pip install --no-cache-dir  -r requirements.txt
# #RUN pip3 install Flask flask_cors flask_swagger_ui opencv-python opencv-python-headless face_recognition setuptools

# #CMD export FLASK_DEBUG=1

# WORKDIR /face_login_api

# #RUN flask run


# # pip3 install numpy opencv-python  opencv-python-headless
# # pip3 install Flask flask_cors flask_swagger_ui
# # pip3 install setuptools
# # pip3 install cmake wheel dlib
# # pip3 install git+https://github.com/ageitgey/face_recognition_models
# # pip3 install face_recognition
