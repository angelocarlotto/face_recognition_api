# Use the official Ubuntu base image
FROM api_2nd:Dockerfile

ARG CACHEBUST=1

# Prevents prompts during package installations
ENV DEBIAN_FRONTEND=noninteractive
ENV FLASK_APP=face_login_api/api/main.py
ENV FLASK_DEBUG=1


EXPOSE 5000


RUN echo "Cache bust value: ${CACHEBUST}" && git clone https://github.com/angelocarlotto/face_login_api.git
RUN cd face_login_api


#COPY entrypoint.sh .
#RUN chmod +x entrypoint.sh

RUN chmod -R 777 .
# Set the default command to run the application

#ENTRYPOINT ["./entrypoint.sh"]