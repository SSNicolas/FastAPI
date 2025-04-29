from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class Item(BaseModel):
    user_id: int
    user_fname: str
    user_lname: str = None
    user_group: str
    subject_photo: str


@app.get("/")
def read_root():
    return "Hello World"

@app.get("/home")
def read_home():
    return "Home"


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
    try:
        response = requests.post(url="http://127.0.0.1:8005/BioService/v1/EnrollSubjectWithAlbum", json=payload)
        return response
    except Exception as e:
        print(e)
        return "Error"
