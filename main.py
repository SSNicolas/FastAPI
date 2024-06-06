from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import base64

app = FastAPI()


class Item(BaseModel):
    user_id: int
    user_fname: str
    user_lname: str = None
    user_group: str = None
    subject_photo: str = None

class DeleteItem(BaseModel):
    user_id: int

class WriteItem(BaseModel):
    user_id: int
    user_fname: str
    user_lname: str = None
    user_group: str = None
    subject_photo: str = None


@app.post("/insert/")
def insert_user(item: Item):
    user_photo = base64.b64decode(item.subject_photo).decode()
    # user_photo = item.subject_photo
    payload = {
        "request": {
            "SubjectCode": item.user_id,
            "SubjectName": item.user_fname,
            "SubjectLastName": item.user_lname,
            "SubjectGroup": item.user_group,
            "SubjectActive": True,
            "SubjectProfilePhoto": user_photo,
            "UsedImages": [
                user_photo
            ],
            "Settings": {
                "DetectionThreshold": 20,
                "QualityThreshold": 30,
                "MinimumFaceSize": 15
            }
        }
    }
    print(payload)
    response = requests.post(url="http://127.0.0.1:8005/BioService/v1/EnrollSubjectWithAlbum", json=payload)
    print(response)
    if response.status_code == 200:
        try:
            return {"status": "success", "data": response.json()}
        except ValueError:
            return {"status": "success", "data": response.text}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@app.post("/delete/")
def delete_user(item: DeleteItem):
    payload = {
        "SubjectCode": [
            item.user_id
        ]
    }
    print(f"Sending payload: {payload}")  # Log para verificar o payload
    response = requests.post(url="http://127.0.0.1:8005/BioService/v1/DeleteSubjects", json=payload)

    if response.status_code == 200:
        try:
            return {"status": "success", "data": response.json()}
        except ValueError:
            return {"status": "success", "data": response.text}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)

@app.post("/write/")
def edit_user(item: WriteItem):
    user_photo = base64.b64decode(item.subject_photo).decode()
    payload = {
        "SubjectCode": item.user_id
    }

    response = requests.post(url="http://127.0.0.1:8005/BioService/v1/GetSubjectInfo", json=payload).json()

    info_users = response['GetSubjectInfoResult']

    if info_users:
        payload = {
            "request": {
                "OldSubjectCode": item.user_id,
                "UpdateDetails": {
                    "SubjectCode": item.user_id,
                    "SubjectName": item.user_fname,
                    "SubjectLastName": item.user_lname,
                    "SubjectGroup": item.user_group,
                    "SubjectActive": True,
                    "SubjectProfilePhoto": user_photo,
                    "UsedImages": [
                        user_photo
                    ],
                    "Settings": {
                        "DetectionThreshold": 20,
                        "QualityThreshold": 30,
                        "MinimumFaceSize": 15
                    }
                }
            }
        }

        response = requests.post(url="http://127.0.0.1:8005/BioService/v1/UpdateSubjectWithAlbum", json=payload)
        return f"Sucess {response}"

    else:
        return "User code not found"
