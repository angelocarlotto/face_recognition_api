import csv
from functools import wraps
import io
import face_recognition
import base64
from flask import Flask, Response, request, send_file,jsonify
from flask_cors import CORS
import numpy as np
import pickle
from flasgger import Swagger
import base64
import datetime
import os
import uuid

import cv2


class faceRecognize():
    def __init__(self,enviroment:str,known_faces_env:list['faceRecognize'],encod, location,picture,nameNewFace) :
        new_uuid=uuid.uuid4().urn
        index=len(known_faces_env)
        self.index=index
        self.uuid=new_uuid
        self.short_uuid=new_uuid.split("-")[-1]
        self.encoding_face=encod
        self.name=nameNewFace or  f"annonymous_{index}"
        self.qtd=1
        self.first_detected=datetime.datetime.now()
        self.last_detected=datetime.datetime.now()
        self.replicates_uuid=[]
        self.enviroment=enviroment
        
        [path,encoded_string]=self.createFile(picture,location)
        self.last_know_shot=path
        self.encoded64_last_pic=encoded_string
        self.first_know_shot=path
        self.encoded64_first_pic=encoded_string

    def __str__(self):
        return f"{self.name}-({self.short_uuid})"
    
    def updateObject(self,picture,l):
        self.qtd+=1
        self.last_detected=datetime.datetime.now()
        [path,encoded_string]=self.createFile(picture,l)
        self.last_know_shot=path
        self.encoded64_last_pic=encoded_string
    
    def createFile(self,picture, l)->tuple[str,str]:
        obj=self
        index=self.index
        ampliar=50
        (top,right,bottom,left)=l
        cropped = picture[top-ampliar if top-ampliar>=0 else top:bottom+ampliar,left-ampliar if left-ampliar>=0 else left or left:right+ampliar]
        fileName=f'face_{index}_{obj.short_uuid}.jpeg'
        path=os.path.join("enviroments",self.enviroment, "faces",fileName)
        cv2.imwrite(path, cropped)
        
        with open(path, "rb") as image_file:
            encoded_string ="data:image/jpeg;base64,"+str( base64.b64encode(image_file.read()), encoding='ascii')
        return path,encoded_string



app = Flask(__name__)
swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    # "static_folder": "static",  # must be set by user
    "swagger_ui": True,
    "specs_route": "/"
}

swagger = Swagger(app,config=swagger_config)
CORS(app)
count:int=0
known_faces={}

  
def validate_before_request(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
      if "key_enviroment_url" not in request.args:
        return  jsonify("you must especify the key_enviroment"), 401
        
      key_enviroment_url: str=request.args["key_enviroment_url"]

      if key_enviroment_url not in known_faces:
          known_faces[key_enviroment_url]=[]

      if not os.path.isdir(os.path.join("enviroments")):
          os.mkdir(os.path.join("enviroments"))
          
      if not os.path.isdir(os.path.join("enviroments",key_enviroment_url)):
          os.mkdir(os.path.join("enviroments",key_enviroment_url))
                          
      if not os.path.isdir(os.path.join("enviroments",key_enviroment_url,"faces")):
          os.mkdir(os.path.join("enviroments",key_enviroment_url,"faces"))
      return f(*args, **kwargs)
  return decorated_function
        
@app.route('/api/os', methods=['GET'])
def os_info():
    """
    Execute OS Module Operations
    ---
    parameters:
      - name: module
        in: query
        type: string
        required: false
        description: "The submodule of the os module (e.g., 'path' for os.path). If not provided, defaults to the os module."
      - name: operation
        in: query
        type: string
        required: true
        description: "The operation or method to perform (e.g., 'listdir' for os.listdir)."
      - name: arg
        in: query
        type: string
        required: false
        description: "A single argument to pass to the operation."
      - name: args
        in: query
        type: array
        items:
          type: string
        required: false
        description: "A list of arguments to pass to the operation. Use this for multiple arguments."
    responses:
      200:
        description: "Successfully executed the OS operation."
        schema:
          type: object
      400:
        description: "Invalid operation or input."
      500:
        description: "Server error while processing the request."
    """
    # Get the module path and operation from the query parameters
    module_path = request.args.get('module', '')  # Use '' if no module is specified
    operation = request.args.get('operation')  # e.g., 'listdir'
    arg = request.args.get('arg')  # Single argument
    args = request.args.getlist('args')  # List of arguments

    try:
        # Start with the os module
        module = os
        if module_path:  # Navigate to submodules if a module path is provided
            for attr in module_path.split('.'):
                module = getattr(module, attr)

        if operation in dir(module):
            # Get the property or function from the module
            attr = getattr(module, operation)

            if callable(attr):
                # If it's a function, execute it with arguments if provided
                if arg:
                    value = attr(arg)
                elif args:
                    value = attr(*args)
                else:
                    value = attr()
            else:
                # If it's a property, return its value
                value = attr
        else:
            return jsonify({"error": "Invalid operation"}), 400

        return jsonify({f"{module_path}.{operation}" if module_path else operation: value}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/api/hi",methods=["GET"])
def hi():
    global count
    """
    This methods tells you if the api is live and runing at the especific endpoint
    ---
    responses:
        200:
            description: success if it return "i am alive"
    """
    count+=1
    returnStr=f"I am alive & counting:{count}"
    return  jsonify(returnStr), 200

@app.route("/api/save",methods=["GET"])
@validate_before_request
def save():
    """
    Save Known Faces to the Environment Directory
    ---
    parameters:
      - name: key_enviroment_url
        in: query
        type: string
        required: true
        description: "The environment key URL used to save the face data. This key will be used to create a directory structure to store the face data."
    responses:
      200:
        description: "Database saved successfully."
        schema:
          type: string
          example: "database saved"
      400:
        description: "Missing or incorrect parameters."
        schema:
          type: string
          example: "you must specify the key_enviroment"
      500:
        description: "Internal server error."
        schema:
          type: string
          example: "Error message"
    """
    try:
        key_enviroment_url=request.args["key_enviroment_url"]
        
        with open(os.path.join("enviroments",key_enviroment_url,'dataset_faces.dat'), 'wb') as f:
            pickle.dump(known_faces[key_enviroment_url], f)
        
        return jsonify("database saved"),200
    except Exception as e:
        return jsonify(e),200

@app.route("/api/load",methods=["GET"])
@validate_before_request
def load():
    """
    Load Known Faces from the Environment Directory
    ---
    parameters:
      - name: key_enviroment_url
        in: query
        type: string
        required: true
        description: "The environment key URL used to load the face data. This key corresponds to the directory structure where the face data is stored."
    responses:
      200:
        description: "Successfully loaded the face data."
        schema:
          type: array
          items:
            type: object
            description: "A list of known faces loaded from the specified environment."
      400:
        description: "Missing or incorrect parameters."
        schema:
          type: string
          example: "you must specify the key_enviroment"
      500:
        description: "Internal server error."
        schema:
          type: string
          example: "Error message"
    """    
    global known_faces
    if "key_enviroment_url" not in request.args:
        return  jsonify("you must especify the key_enviroment"), 400

    key_enviroment_url=request.args["key_enviroment_url"]

    with open(os.path.join("enviroments",key_enviroment_url,'dataset_faces.dat'), 'rb') as f:
        known_faces[key_enviroment_url] = pickle.load(f)
        
    return jsonify(remove_propertye(known_faces[key_enviroment_url])),200

@app.route("/api/recognize_face",methods=["POST"])
@validate_before_request
def recognize_face():
    """
    Recognize Faces from an Uploaded Image or Base64 Encoded String
    ---
    parameters:
      - name: key_enviroment_url
        in: query
        type: string
        required: true
        description: "The environment key URL used to store and recognize the face data. This key will be used to create or reference an existing directory structure."
      - name: files
        in: formData
        type: file
        required: false
        description: "The image file to process for face recognition. Either 'files' or 'imageToRecognize' must be provided."
      - name: imageToRecognize
        in: body
        required: false
        description: "Base64 encoded string of the image to process for face recognition. Either 'files' or 'imageToRecognize' must be provided."
        schema:
          type: object
          properties:
            imageToRecognize:
              type: string
              description: "Base64 encoded image string"
    responses:
      200:
        description: "Successfully recognized faces in the image."
        schema:
          type: object
          properties:
            qtdFaceDetected:
              type: integer
              description: "Number of faces detected in the image."
            faces_know:
              type: array
              description: "List of known faces."
              items:
                type: object
      400:
        description: "Missing or incorrect parameters."
        schema:
          type: string
          example: "you must specify the key_enviroment"
      500:
        description: "Internal server error."
        schema:
          type: string
          example: "Error message"
    """
    try:
        key_enviroment_url=request.args["key_enviroment_url"]
        ipaddress=request.args["ipaddress"]
        
        nameIamgeToBeProceced:str=f"imageToProcess{ipaddress}.jpeg"
        if  "files" in request.files :
            image64=request.files["files"]
            image64.save(os.path.join("enviroments",key_enviroment_url,nameIamgeToBeProceced))
            #save file
        elif "imageToRecognize" in request.get_json() :
            data=request.get_json()
            image64=data["imageToRecognize"]
            image64=image64.replace("data:image/jpeg;base64,","")
            image_64_decode = base64.b64decode(image64) 
            nameNewFace=data["nameNewFace"] if "nameNewFace" in data else None

            with open(os.path.join("enviroments",key_enviroment_url, nameIamgeToBeProceced), "wb") as fh:
                fh.write(image_64_decode) 

        lastRegonizedFaces=getface_encoding(known_faces[key_enviroment_url],key_enviroment_url,nameIamgeToBeProceced,nameNewFace)
      
        return  jsonify({"lastRegonizedFaces":lastRegonizedFaces,"faces_know":remove_propertye(known_faces[key_enviroment_url])})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download_csv",methods=["GET"])
@validate_before_request
def download_csv():
  """
    This method will return a csv file with all the content form current enviroment
    ---
    parameters:
      - name: key_enviroment_url
        in: query
        type: string
        required: true
        description: "The environment key URL used to store and recognize the face data. This key will be used to create or reference an existing directory structure."
    responses:
        200:
            description: success if it return the file it self
  """
  try:
    if "key_enviroment_url" not in request.args:
        return  jsonify("you must especify the key_enviroment"), 400
      
    key_enviroment_url=request.args["key_enviroment_url"]
    
    output = io.StringIO()
    writer = csv.writer(output)

    arrayToBeSubmited=keep_propertye(known_faces[key_enviroment_url], included_properties=["index","uuid","name","qtd","first_detected","last_detected","enviroment"])
    # Write the header row (keys of the first dictionary)
    writer.writerow(arrayToBeSubmited[0].keys())

    # Write data rows
    for row in arrayToBeSubmited:
        writer.writerow(row.values())

    # Move the cursor to the start of the stream
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": f"attachment;filename=data_{key_enviroment_url}.csv"})
  except Exception as e:
    return jsonify({"error": str(e)}), 500
    
@app.route("/api/bind_replicante",methods=["POST"])
@validate_before_request
def bind_replicante():
  """_summary_
  ---
  parameters:
    - name: key_enviroment_url
      in: query
      type: string
      required: true
      description: "The environment key URL used to identify the environment containing the face data to be updated."
  Returns:
      _type_: _description_
  """
  key_enviroment_url=request.args["key_enviroment_url"]
  request_data=request.get_json()
  enviromentFaces:list[faceRecognize]=known_faces[key_enviroment_url]
  result=[x for x in enviromentFaces if x.uuid==request_data.uuid]
  return  jsonify(result)
  #principal uuid
  #replicante uuid
  #find int the database the principal object
  #append on the principal attr replicates_uuid the replicante uuid
   
@app.route("/api/delete_face",methods=["DELETE"])
@validate_before_request
def delete_face():
    """
    Delete a face from the database
    ---
    parameters:
      - name: key_enviroment_url
        in: query
        type: string
        required: true
        description: "The environment key URL used to identify the environment containing the face data to be updated."
      - name: body
        in: body
        required: true
        description: "JSON object containing the UUID of the face to update and the new name."
        schema:
          type: object
          required:
            - uuid
            - new_name
          properties:
            uuid:
              type: string
              description: "The unique identifier of the face whose name is to be updated."
            new_name:
              type: string
              description: "The new name to assign to the face."
    responses:
      200:
        description: "Successfully updated the face name."
        schema:
          type: array
          items:
            type: object
            properties:
              uuid:
                type: string
                description: "The unique identifier of the face."
              name:
                type: string
                description: "The updated name of the face."
              qtd:
                type: integer
                description: "The number of times the face was detected."
              first_detected:
                type: string
                description: "The timestamp of when the face was first detected."
              last_detected:
                type: string
                description: "The timestamp of when the face was last detected."
              last_know_shot:
                type: string
                description: "The path to the last known shot of the face."
              encoded64_last_pic:
                type: string
                description: "The Base64 encoded string of the last known picture of the face."
      400:
        description: "Missing or incorrect parameters."
        schema:
          type: string
          example: "you must specify the key_enviroment"
      500:
        description: "Internal server error."
        schema:
          type: string
          example: "Error message"
    """
        
    key_enviroment_url=request.args["key_enviroment_url"]
    
    try:
        data=request.get_json()
        uuid=data["uuid"]
        itemToBeRemoved=None
        for x in known_faces[key_enviroment_url]:
            if x.uuid==uuid:
                itemToBeRemoved=x
        known_faces[key_enviroment_url].remove(itemToBeRemoved)
        return remove_propertye(known_faces[key_enviroment_url])
    except Exception as e:
          return jsonify({"error": str(e)}), 500
        
@app.route("/api/update_face_name",methods=["POST"])
@validate_before_request
def update_face_name():
    """
    Update the Name of a Recognized Face
    ---
    parameters:
      - name: key_enviroment_url
        in: query
        type: string
        required: true
        description: "The environment key URL used to identify the environment containing the face data to be updated."
      - name: body
        in: body
        required: true
        description: "JSON object containing the UUID of the face to update and the new name."
        schema:
          type: object
          required:
            - uuid
            - new_name
          properties:
            uuid:
              type: string
              description: "The unique identifier of the face whose name is to be updated."
            new_name:
              type: string
              description: "The new name to assign to the face."
    responses:
      200:
        description: "Successfully updated the face name."
        schema:
          type: array
          items:
            type: object
            properties:
              uuid:
                type: string
                description: "The unique identifier of the face."
              name:
                type: string
                description: "The updated name of the face."
              qtd:
                type: integer
                description: "The number of times the face was detected."
              first_detected:
                type: string
                description: "The timestamp of when the face was first detected."
              last_detected:
                type: string
                description: "The timestamp of when the face was last detected."
              last_know_shot:
                type: string
                description: "The path to the last known shot of the face."
              encoded64_last_pic:
                type: string
                description: "The Base64 encoded string of the last known picture of the face."
      400:
        description: "Missing or incorrect parameters."
        schema:
          type: string
          example: "you must specify the key_enviroment"
      500:
        description: "Internal server error."
        schema:
          type: string
          example: "Error message"
    """
        
    key_enviroment_url=request.args["key_enviroment_url"]
    
    try:
        data=request.get_json()
        uuid=data["uuid"]
        new_name=data["new_name"]
        for x in known_faces[key_enviroment_url]:
            if x.uuid==uuid:
                x.name=new_name
        return remove_propertye(known_faces[key_enviroment_url])
    except Exception as e:
          return jsonify({"error": str(e)}), 500
        
def remove_propertye(data:list[faceRecognize],exclude_property:list[str]=["encoding_face"], included_properties:list[str]=[]):
  #, included_properties:list[str]=["index","uuid","name","qtd","first_detected","last_detected","enviroment"]):
  """
  This method returns a the input array without especifics propertis on it's objects
  """
  new_data = []
  for item in data:
    #(len(included_properties)>0 and k in included_properties) or 
    new_item = {k: v for k, v in vars(item).items() if  k not in exclude_property}
    new_data.append(new_item)
  return new_data

def keep_propertye(data:list[faceRecognize], included_properties:list[str]=["index","uuid","name","qtd","first_detected","last_detected","enviroment"]):
  #, included_properties:list[str]=["index","uuid","name","qtd","first_detected","last_detected","enviroment"]):
  """
  This method returns a the input array without especifics propertis on it's objects
  """
  new_data = []
  for item in data:
    #(len(included_properties)>0 and k in included_properties) or 
    new_item = {k: v for k, v in vars(item).items() if  k  in included_properties}
    new_data.append(new_item)
  return new_data

def getface_encoding(known_faces_env:list[faceRecognize],enviroment:str,imageToProess:str,nameNewFace:str)->[]:
    
    picture = face_recognition.load_image_file(os.path.join("enviroments",enviroment, imageToProess))
    
    frame = cv2.resize(picture, (0, 0), fx = 1, fy = 1)
    machs=[]
    rgb_frame = frame[:, :, ::-1]
    rgb_frame = np.ascontiguousarray(rgb_frame)
    
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame,face_locations)
    justRecognizedIdsAndLocation=[]
    for l,e in zip(face_locations,face_encodings):
        machs = face_recognition.compare_faces([ facesFromInviroment.encoding_face for facesFromInviroment in known_faces_env], e, tolerance=0.6)
        trueMatchIndexes=[i for i in range(0,len(machs),1) if machs[i]==True]
        if len(trueMatchIndexes)>=1:
            #this is a problem because means the algorithm understand the face maths with more then one preivous face.
            for x in trueMatchIndexes:
                obj=known_faces_env[x]
                obj.updateObject(picture,l)
                #justRecognizedIdsAndLocation.append({"uuid":obj.uuid,"location":l})
        else:
            #means it is a new face detected
            obj=faceRecognize(enviroment,known_faces_env,e,l,picture,nameNewFace)
            known_faces_env.append(obj)
        justRecognizedIdsAndLocation.append({"uuid":obj.uuid,"location":l})
    # my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!
    return justRecognizedIdsAndLocation

  
if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0",port=5001)
