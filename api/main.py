import cv2
import face_recognition
import base64
from flask import Flask, request, send_file,jsonify
from flask_cors import CORS
import numpy as np
import uuid
import datetime
import os
import pickle
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
    
CORS(app)

known_faces={}
@app.route("/api/save",methods=["GET"])
def save():

    try:
        if "key_enviroment_url" not in request.args:
            return  jsonify("you must especify the key_enviroment"), 400
        
        key_enviroment_url=request.args["key_enviroment_url"]
                
        with open(os.path.join("enviroments",key_enviroment_url,'dataset_faces.dat'), 'wb') as f:
            pickle.dump(known_faces[key_enviroment_url], f)
        
        return jsonify("database saved"),200
    except Exception as e:
        return jsonify(e),200

@app.route("/api/load",methods=["GET"])
def load():
    global known_faces
    if "key_enviroment_url" not in request.args:
        return  jsonify("you must especify the key_enviroment"), 400

    key_enviroment_url=request.args["key_enviroment_url"]

    with open(os.path.join("enviroments",key_enviroment_url,'dataset_faces.dat'), 'rb') as f:
        known_faces[key_enviroment_url] = pickle.load(f)
        
    return jsonify(remove_propertye(known_faces[key_enviroment_url])),200

@app.route("/api/recognizeFace",methods=["POST"])
def recognizeFace():
    try:
        if "key_enviroment_url" not in request.args:
            return  jsonify("you must especify the key_enviroment"), 400
        
        key_enviroment_url=request.args["key_enviroment_url"]
        
        if key_enviroment_url not in known_faces:
            known_faces[key_enviroment_url]=[]
        
        if not os.path.isdir(os.path.join("enviroments",key_enviroment_url)):
            os.mkdir(os.path.join("enviroments",key_enviroment_url))
                            
        if not os.path.isdir(os.path.join("enviroments",key_enviroment_url,"faces")):
            os.mkdir(os.path.join("enviroments",key_enviroment_url,"faces"))
            
        if  "files" in request.files :
            image64=request.files["files"]
            image64.save(os.path.join("enviroments",key_enviroment_url,"imageToProcess.png"))
            #save file
        elif "face42" in request.get_json() :
            data=request.get_json()
            image64=data["face42"]
            image64=image64.replace("data:image/jpeg;base64,","")
            image_64_decode = base64.b64decode(image64) 

            with open(os.path.join("enviroments",key_enviroment_url, "imageToProcess.png"), "wb") as fh:
                fh.write(image_64_decode) 

        lastRegonizedFaces=getface_encoding(known_faces[key_enviroment_url],key_enviroment_url,"imageToProcess.png")
        return  jsonify({"qtdFaceDetected":len(lastRegonizedFaces),"faces_know":remove_propertye(known_faces[key_enviroment_url])})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/update_face_name",methods=["POST"])
def update_face_name():
    if "key_enviroment_url" not in request.args:
            return  jsonify("you must especify the key_enviroment"), 400
        
    key_enviroment_url=request.args["key_enviroment_url"]
    
    if key_enviroment_url not in known_faces:
        known_faces[key_enviroment_url]=[]
        
    try:
        data=request.get_json()
        uuid=data["uuid"]
        new_name=data["new_name"]
        for x in known_faces[key_enviroment_url]:
            if x["uuid"]==uuid:
                x["name"]=new_name
        #return  jsonify([{"uuid":x["uuid"],"name":x["name"],"qtd":x["qtd"],"first_detected":x["first_detected"],"last_detected":x["last_detected"],"last_know_shot":x["last_know_shot"],"encoded64_last_pic":x["encoded64_last_pic"]} for x in known_faces])
        return remove_propertye(known_faces[key_enviroment_url])
    except Exception as e:
          return jsonify({"error": str(e)}), 500
def remove_propertye(data, exclude_property=["encoding_face"]):
  new_data = []
  for item in data:
    new_item = {k: v for k, v in item.items() if k not in exclude_property}
    new_data.append(new_item)
  return new_data

def createFile(frame,enviroment, countFrameIndex, l, uuid):
    obj=[x for x in known_faces[enviroment] if x["uuid"]==uuid][0]
    index=obj["index"]
    ampliar=50
    (top,right,bottom,left)=l
    cropped = frame[top-ampliar if top-ampliar>=0 else top:bottom+ampliar,left-ampliar if left-ampliar>=0 else left or left:right+ampliar]
    fileName=f'face_{index}_{obj["short_uuid"]}_{countFrameIndex}.jpeg'
    path=os.path.join("enviroments",enviroment, "faces",fileName)
    cv2.imwrite(path, cropped)
    return path
    
def getface_encoding(known_faces_env,enviroment,imageToProess):
    
    picture = face_recognition.load_image_file(os.path.join("enviroments",enviroment, imageToProess))
    
    frame = cv2.resize(picture, (0, 0), fx = 1, fy = 1)
    machs=[]
    rgb_frame = frame[:, :, ::-1]
    rgb_frame = np.ascontiguousarray(rgb_frame)
    
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame,face_locations)
    for l,e in zip(face_locations,face_encodings):
        machs = face_recognition.compare_faces([ x["encoding_face"] for x in known_faces_env], e, tolerance=0.6)
        trueMatchIndexes=[i for i in range(0,len(machs),1) if machs[i]==True]
        if len(trueMatchIndexes)>=1:
            #this is a problem because means the algorithm understand the face maths with more then one preivous face.
            for x in trueMatchIndexes:
                know_one=known_faces_env[x]
                know_one["qtd"]+=1
                know_one["last_detected"]=datetime.datetime.now()
                
                path=createFile(picture,enviroment,2,l,know_one["uuid"])
                with open(path, "rb") as image_file:
                    encoded_string ="data:image/jpeg;base64,"+str( base64.b64encode(image_file.read()), encoding='ascii')
                know_one["last_know_shot"]=path
                know_one["encoded64_last_pic"]=encoded_string
                
        else:
            #means it is a new face detected
            new_uuid=uuid.uuid4().urn
            obj={"index":len(known_faces_env),"uuid":new_uuid,"short_uuid":new_uuid.split("-")[-1],"encoding_face":e,"name": f"annonymous_{len(known_faces_env)}","qtd":1,"first_detected":datetime.datetime.now(),"last_detected":datetime.datetime.now()}
            known_faces_env.append(obj)
            path=createFile(picture,enviroment,2,l,new_uuid)
            with open(path, "rb") as image_file:
                encoded_string ="data:image/jpeg;base64,"+str( base64.b64encode(image_file.read()), encoding='ascii')
            obj["last_know_shot"]=path
            obj["encoded64_last_pic"]=encoded_string
            
    
    # my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!
    return face_locations

  



SWAGGER_URL="/swagger"
API_URL="/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Access API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0",port=8080)
