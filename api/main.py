import csv
from functools import wraps
import io
from PIL import Image
import face_recognition
import base64
from flask import Flask, Response, request, send_file,jsonify
from flask_cors import CORS
import numpy as np
import pickle
from flasgger import Swagger,swag_from
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
        
        '''
        if the face is not grouped, this property will have the same value as uuid property. If it is grouped this property will have the uuid value from the main face.
        '''
        self.principal_uuid=new_uuid
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
           "version": "0.0.1",
            "title": "Api v1",
            "description": 'This api is a proff of concept of the ability to has python face recognition on a REST API. You can find the whole source code on this repository: https://github.com/angelocarlotto/face_recognition_api',
            
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
@swag_from({
    'summary': 'Get OS information',
    'description': 'Allows dynamic interaction with the os module. Accepts module path and operation to perform.',
    'parameters': [
        {
            'name': 'module',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'The module path (e.g., "os.path").'
        },
        {
            'name': 'operation',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The operation to perform on the module (e.g., "listdir").'
        },
        {
            'name': 'arg',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Single argument for the operation.'
        },
        {
            'name': 'args',
            'in': 'query',
            'type': 'array',
            'items': {'type': 'string'},
            'required': False,
            'description': 'List of arguments for the operation.'
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'examples': {
                'application/json': {"operation": "result"}
            }
        },
        '400': {
            'description': 'Invalid operation'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def os_info():
    
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
@swag_from({
    'summary': 'Simple health check endpoint',
    'description': 'Returns a simple message with a count of how many times the endpoint has been hit.',
    'responses': {
        '200': {
            'description': 'Successful response',
            'examples': {
                'application/json': 'I am alive & counting: 1'
            }
        }
    }
})
def hi():
    global count
   
    count+=1
    returnStr=f"I am alive & counting:{count}"
    return  jsonify(returnStr), 200

@app.route("/api/save",methods=["POST"])
@validate_before_request
@swag_from({
    'summary': 'Save the known faces data',
    'description': 'Saves the face recognition data to a file.',
    'parameters': [
        {
            'name': 'key_enviroment_url',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The key for the environment to save the data.'
        }
    ],
    'responses': {
        '200': {
            'description': 'Database saved',
            'examples': {
                'application/json': 'database saved'
            }
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def save():
    
    try:
        key_enviroment_url=request.args["key_enviroment_url"]
        
        with open(os.path.join("enviroments",key_enviroment_url,'dataset_faces.dat'), 'wb') as f:
            pickle.dump(known_faces[key_enviroment_url], f)
        
        return jsonify("database saved"),200
    except Exception as e:
        return jsonify(e),200

@app.route("/api/load",methods=["GET"])
@validate_before_request
@swag_from({
    'summary': 'Load the known faces data',
    'description': 'Loads the face recognition data from a file.',
    'parameters': [
        {
            'name': 'key_enviroment_url',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The key for the environment to load the data.'
        }
    ],
    'responses': {
        '200': {
            'description': 'Data loaded successfully',
            'examples': {
                'application/json': 'Loaded data example here'
            }
        },
        '400': {
            'description': 'Invalid key_enviroment'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def load():
    
    global known_faces

    key_enviroment_url=request.args["key_enviroment_url"]

    if os.path.isfile(os.path.join("enviroments",key_enviroment_url,'dataset_faces.dat')):
        with open(os.path.join("enviroments",key_enviroment_url,'dataset_faces.dat'), 'rb') as f:
            known_faces[key_enviroment_url] = pickle.load(f)
        
    return remove_propertye(known_faces[key_enviroment_url])

@app.route("/api/load_from_memory",methods=["GET"])
@validate_before_request
@swag_from({
    'summary': 'Load the known faces memory server',
    'description': 'Loads the face recognition data from the server memory.',
    'parameters': [
        {
            'name': 'key_enviroment_url',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The key for the environment to load the data.'
        }
    ],
    'responses': {
        '200': {
            'description': 'Data loaded successfully',
            'examples': {
                'application/json': 'Loaded data example here'
            }
        },
        '400': {
            'description': 'Invalid key_enviroment'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def load_from_memory():
    global known_faces
    key_enviroment_url=request.args["key_enviroment_url"]
    return remove_propertye(known_faces[key_enviroment_url])

@app.route("/api/recognize_face",methods=["POST"])
@validate_before_request
@swag_from({
    'summary': 'Recognize a face in an uploaded image',
    'description': 'Recognizes and processes a face from a provided image.',
    'parameters': [
        {
            'name': 'key_enviroment_url',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The key for the environment.'
        },
        {
            'name': 'ipaddress',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'IP address of the client.'
        },
        {
            'name': 'files',
            'in': 'formData',
            'type': 'file',
            'required': False,
            'description': 'Image file to process.'
        },
        {
            'name': 'imageToRecognize',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'imageToRecognize': {'type': 'string', 'description': 'Base64 encoded image data'},
                    'nameNewFace': {'type': 'string', 'description': 'Name for the new face'}
                }
            },
            'required': False
        }
    ],
    'responses': {
        '200': {
            'description': 'Faces recognized successfully',
            'examples': {
                'application/json': {"lastRegonizedFaces": [], "faces_know": []}
            }
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def recognize_face():
   
    try:
        key_enviroment_url=request.args["key_enviroment_url"]
        ipaddress=request.args["ipaddress"]
        
        nameIamgeToBeProceced:str=f"imageToProcess{ipaddress}"
        if  "files" in request.files :
            nameIamgeToBeProceced+=".jpeg"
            image64=request.files["files"]
            image64.save(os.path.join("enviroments",key_enviroment_url,nameIamgeToBeProceced))
            nameNewFace=request.form["nameNewFace"] if "nameNewFace" in request.form else None
        elif "imageToRecognize" in request.get_json() :
            data=request.get_json()
            image64=data["imageToRecognize"]
            
            if  "png" in image64 :
                image64=image64.replace("data:image/png;base64,","")
                image64 = converte_PNG_TO_JPEG(image64)
                nameIamgeToBeProceced+=".png"
            elif "jpg" in image64 or "jpeg" in image64:
                nameIamgeToBeProceced+=".jpeg"
                image64=image64.replace("data:image/jpeg;base64,","")
            else:
                return jsonify({"error: ony PNG and JPEG or JPG are supported so far on this API"}), 500
              
            
            image_64_decode = base64.b64decode(image64)
            nameNewFace=data["nameNewFace"] if "nameNewFace" in data else None
           

            with open(os.path.join("enviroments",key_enviroment_url, nameIamgeToBeProceced), "wb") as fh:
                fh.write(image_64_decode) 

        lastRegonizedFaces=getface_encoding(known_faces[key_enviroment_url],key_enviroment_url,nameIamgeToBeProceced,nameNewFace)
      
        return  jsonify({"lastRegonizedFaces":lastRegonizedFaces,"faces_know":remove_propertye(known_faces[key_enviroment_url])})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def converte_PNG_TO_JPEG(image64):
    png_base64_string = image64#"your_base64_encoded_png_string_here"

            # Step 1: Decode the Base64 string into binary data
    png_data = base64.b64decode(png_base64_string)

            # Step 2: Open the binary data as an image using Pillow
    png_image = Image.open(io.BytesIO(png_data))

            # Step 3: Convert the image to JPEG format and save it to a bytes buffer
    jpeg_buffer = io.BytesIO()
    png_image.convert("RGB").save(jpeg_buffer, format="JPEG")

            # Step 4: Encode the JPEG image in the bytes buffer to a Base64 string
    jpeg_base64_string = base64.b64encode(jpeg_buffer.getvalue()).decode('utf-8')
    return jpeg_base64_string

@app.route("/api/download_csv",methods=["GET"])
@validate_before_request
@swag_from({
    'summary': 'Download face recognition data as CSV',
    'description': 'Generates and downloads face recognition data in CSV format.',
    'parameters': [
        {
            'name': 'key_enviroment_url',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The key for the environment to generate CSV.'
        }
    ],
    'responses': {
        '200': {
            'description': 'CSV file download',
            'examples': {
                'text/csv': 'CSV file content here'
            }
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def download_csv():
  
  try:
    if "key_enviroment_url" not in request.args:
        return  jsonify("you must especify the key_enviroment"), 400
      
    key_enviroment_url=request.args["key_enviroment_url"]
    
    output = io.StringIO()
    writer = csv.writer(output)

    arrayToBeSubmited=keep_propertye(known_faces[key_enviroment_url], included_properties=["index","uuid","name","qtd","first_detected","last_detected","enviroment","principal_uuid"])
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
    
@app.route("/api/bind_to_principal_face",methods=["POST"])
@validate_before_request
@swag_from({
    'summary': 'Bind a replicant face to a principal face',
    'description': 'Associates a replicant face UUID with a principal face UUID in the environment.',
    'parameters': [
        {
            'name': 'key_enviroment_url',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The key for the environment.'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'uuid': {'type': 'string', 'description': 'UUID of the face to bind'}
                }
            },
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Replicant bound successfully',
            'examples': {
                'application/json': 'Bound face data here'
            }
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def bind_to_principal_face():
  
  key_enviroment_url=request.args["key_enviroment_url"]
  request_data=request.get_json()
  
  enviromentFaces:list[faceRecognize]=known_faces[key_enviroment_url]
  #pricipalFace:faceRecognize=[x for x in enviromentFaces if x.uuid==request_data["uuidPrincipal"]]
  faceRepeated:faceRecognize=[x for x in enviromentFaces if x.uuid==request_data["uuid"]].pop()
  faceRepeated.principal_uuid=request_data["uuidPrincipal"]
  return remove_propertye(known_faces[key_enviroment_url])
  #principal uuid
  #replicante uuid
  #find int the database the principal object
  #append on the principal attr replicates_uuid the replicante uuid
   
@app.route("/api/delete_face",methods=["DELETE"])
@validate_before_request
@swag_from({
    'summary': 'Delete a face from the environment',
    'description': 'Deletes a face identified by UUID from the environment.',
    'parameters': [
        {
            'name': 'key_enviroment_url',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The key for the environment.'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'uuid': {'type': 'string', 'description': 'UUID of the face to delete'}
                }
            },
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Face deleted successfully',
            'examples': {
                'application/json': 'Updated face data here'
            }
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def delete_face():
    
    key_enviroment_url=request.args["key_enviroment_url"]
    
    try:
        data=request.get_json()
        uuidToBeRemoved=data["uuid"]
        known_faces[key_enviroment_url]=itemsToBeleted= [child for child in known_faces[key_enviroment_url] if child.principal_uuid!=uuidToBeRemoved]
        return remove_propertye(known_faces[key_enviroment_url])
    except Exception as e:
          return jsonify({"error": str(e)}), 500
        
@app.route("/api/update_face_name",methods=["POST"])
@validate_before_request
@swag_from({
    'summary': 'Update a face name in the environment',
    'description': 'Updates the name of a face identified by UUID in the environment.',
    'parameters': [
        {
            'name': 'key_enviroment_url',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The key for the environment.'
        },
        {
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'uuid': {'type': 'string', 'description': 'UUID of the face'},
                    'new_name': {'type': 'string', 'description': 'New name for the face'}
                }
            },
            'required': True
        }
    ],
    'responses': {
        '200': {
            'description': 'Face name updated successfully',
            'examples': {
                'application/json': 'Updated face data here'
            }
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def update_face_name():
    
        
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
    app.run(debug=True,host="0.0.0.0",port=5001,ssl_context='adhoc')
