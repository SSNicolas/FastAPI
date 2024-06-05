from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()


class Item(BaseModel):
    user_id: int
    user_fname: str
    user_lname: str = None
    user_group: str
    subject_photo: str

class DeleteItem(BaseModel):
    user_id: int

class WriteItem(BaseModel):
    user_id: int
    user_fname: str
    user_lname: str = None
    user_group: str
    subject_photo: str


@app.get("/")
def read_root():
    return "Hello World"


@app.post("/insert/")
def insert_user(item: Item):
    payload = {
        "request": {
            "SubjectCode": item.user_id,
            "SubjectName": item.user_fname,
            "SubjectLastName": item.user_lname,
            "SubjectGroup": item.user_group,
            "SubjectActive": True,
            "SubjectProfilePhoto": item.subject_photo,
            "UsedImages": [
                item.subject_photo
            ],
            "Settings": {
                "DetectionThreshold": 25,
                "QualityThreshold": 40,
                "MinimumFaceSize": 30
            }
        }
    }
    response = requests.post(url="http://127.0.0.1:8005/BioService/v1/EnrollSubjectWithAlbum", json=payload)

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
                    "SubjectActive": "true",
                    "SubjectProfilePhoto": item.subject_photo,
                    "UsedImages": [
                        item.subject_photo
                    ],
                    "Settings": {
                        "DetectionThreshold": 25,
                        "QualityThreshold": 40,
                        "MinimumFaceSize": 30
                    }
                }
            }
        }

        response = requests.post(url="http://127.0.0.1:8005/BioService/v1/UpdateSubjectWithAlbum", json=payload)
        return "Sucess"

    else:
        return "User code not found"
