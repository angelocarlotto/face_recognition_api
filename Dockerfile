#sudo docker build  -t "face_login_api_3rd:v0.1" .
#docker run --rm  -p 5001:5000  face_login_api_3rd:v0.1
# Use the official Ubuntu base image
FROM face_login_api_2nd:v0.1

ARG CACHEBUST=1

# Prevents prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive
ENV FLASK_APP=face_login_api/api/main.py
ENV FLASK_DEBUG=1


EXPOSE 5000


RUN echo "Cache bust value: ${CACHEBUST}s" && git clone https://github.com/angelocarlotto/face_login_api.git


#COPY entrypoint.sh .
RUN chmod +x face_login_api/entrypoint.sh

RUN mkdir enviroments
RUN chmod -R 777 enviroments
# Set the default command to run the application

#CMD [".", "venv/bin/activate", "&&", "flask", "run", "--host=0.0.0.0"]
ENTRYPOINT ["face_login_api/entrypoint.sh"]