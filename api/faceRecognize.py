import base64
import datetime
import os
import uuid

import cv2


class faceRecognize():
    def __init__(self,enviroment:str,known_faces_env:list['faceRecognize'],encod, location,picture) :
        new_uuid=uuid.uuid4().urn
        index=len(known_faces_env)
        self.index=index
        self.uuid=new_uuid
        self.short_uuid=new_uuid.split("-")[-1]
        self.encoding_face=encod
        self.name=f"annonymous_{index}"
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

