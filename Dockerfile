# sudo docker build -t "angelocarlotto/face_login_ui:v1.0" .  

#docker push angelocarlotto/face_login_ui:v1.0

#docker run --rm -p 3001:3000 angelocarlotto/face_login_ui:v1.0

FROM ubuntu

RUN apt update

RUN apt install -y nodejs git git-all npm

RUN git clone https://github.com/angelocarlotto/face_login_ui.git && cd face_login_ui &&  npm install


WORKDIR face_login_ui

CMD ["npm","run","dev"]