#sudo docker build --build-arg CACHEBUST=$(date +%s) -t "angelocarlotto/face_recognition_api:latest" .
#docker push angelocarlotto/face_recognition_api:latest
#docker run --rm  -p 5001:5000  angelocarlotto/face_recognition_api:latest
# Use the official Ubuntu base image
FROM face_recognition_api_1th:v0.1

ARG CACHEBUST=1

# Prevents prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive
ENV FLASK_APP=face_login_api/api/main.py
ENV FLASK_DEBUG=1


EXPOSE 5000


RUN echo "Cache bust value: ${CACHEBUST}" && git clone https://github.com/angelocarlotto/face_login_api.git


#COPY entrypoint.sh .
RUN chmod +x face_login_api/entrypoint.sh

RUN mkdir enviroments
RUN chmod -R 777 enviroments
# Set the default command to run the application

#CMD [".", "venv/bin/activate", "&&", "flask", "run", "--host=0.0.0.0"]
ENTRYPOINT ["face_login_api/entrypoint.sh"]