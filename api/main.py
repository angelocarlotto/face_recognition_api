import csv
import io
import cv2
import face_recognition
import base64
from flask import Flask, Response, request, send_file,jsonify
from flask_cors import CORS
import numpy as np
import uuid
import datetime
import os
import pickle
from flasgger import Swagger


app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

known_faces={}

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
    """
    This methods tells you if the api is live and runing at the especific endpoint
    ---
    responses:
        200:
            description: success if it return "i am alive"
    """
    return  jsonify("I am alive"), 200

@app.route("/api/save",methods=["GET"])
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
        if "key_enviroment_url" not in request.args:
            return  jsonify("you must especify the key_enviroment"), 400
        
        
        key_enviroment_url=request.args["key_enviroment_url"]
        
        if key_enviroment_url not in known_faces:
            known_faces[key_enviroment_url]=[]
        
        if not os.path.isdir(os.path.join("enviroments")):
            os.mkdir(os.path.join("enviroments"))
            
        if not os.path.isdir(os.path.join("enviroments",key_enviroment_url)):
            os.mkdir(os.path.join("enviroments",key_enviroment_url))
                            
        if not os.path.isdir(os.path.join("enviroments",key_enviroment_url,"faces")):
            os.mkdir(os.path.join("enviroments",key_enviroment_url,"faces"))
            
                
        with open(os.path.join("enviroments",key_enviroment_url,'dataset_faces.dat'), 'wb') as f:
            pickle.dump(known_faces[key_enviroment_url], f)
        
        return jsonify("database saved"),200
    except Exception as e:
        return jsonify(e),200

@app.route("/api/load",methods=["GET"])
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

@app.route("/api/recognizeFace",methods=["POST"])
def recognizeFace():
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
        if "key_enviroment_url" not in request.args:
            return  jsonify("you must especify the key_enviroment"), 400
        
        key_enviroment_url=request.args["key_enviroment_url"]
        
        if key_enviroment_url not in known_faces:
            known_faces[key_enviroment_url]=[]
            
        if not os.path.isdir(os.path.join("enviroments")):
            os.mkdir(os.path.join("enviroments"))            
        
        if not os.path.isdir(os.path.join("enviroments",key_enviroment_url)):
            os.mkdir(os.path.join("enviroments",key_enviroment_url))
                            
        if not os.path.isdir(os.path.join("enviroments",key_enviroment_url,"faces")):
            os.mkdir(os.path.join("enviroments",key_enviroment_url,"faces"))
            
        if  "files" in request.files :
            image64=request.files["files"]
            image64.save(os.path.join("enviroments",key_enviroment_url,"imageToProcess.jpeg"))
            #save file
        elif "imageToRecognize" in request.get_json() :
            data=request.get_json()
            image64=data["imageToRecognize"]
            image64=image64.replace("data:image/jpeg;base64,","")
            image_64_decode = base64.b64decode(image64) 

            with open(os.path.join("enviroments",key_enviroment_url, "imageToProcess.jpeg"), "wb") as fh:
                fh.write(image_64_decode) 

        lastRegonizedFaces=getface_encoding(known_faces[key_enviroment_url],key_enviroment_url,"imageToProcess.jpeg")
      
        return  jsonify({"lastRegonizedFaces":lastRegonizedFaces,"faces_know":remove_propertye(known_faces[key_enviroment_url])})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download_csv",methods=["GET"])
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

    # Write the header row (keys of the first dictionary)
    writer.writerow(known_faces[key_enviroment_url][0].keys())

    # Write data rows
    for row in known_faces[key_enviroment_url]:
        writer.writerow(row.values())

    # Move the cursor to the start of the stream
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={"Content-Disposition": f"attachment;filename=data_{key_enviroment_url}.csv"})
  except Exception as e:
    return jsonify({"error": str(e)}), 500
    
  

   
@app.route("/api/update_face_name",methods=["POST"])
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
    justRecognizedIdsAndLocation=[]
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
                justRecognizedIdsAndLocation.append({"uuid":know_one["uuid"],"location":l})
                
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
            justRecognizedIdsAndLocation.append({"uuid":new_uuid,"location":l})
    
    # my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!
    return justRecognizedIdsAndLocation

  




if __name__=="__main__":
    app.run(debug=True,host="0.0.0.0",port=5001)
