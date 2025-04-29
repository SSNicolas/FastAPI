import os
import requests
import dotenv
import xmlrpc.client
import datetime
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from paho.mqtt import client as mqtt
import xml.etree.ElementTree as ET
from typing import Union

dotenv.load_dotenv()

app = FastAPI()
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
topic = os.environ.get('HRTA_TOPIC')
# topic_hml = os.environ.get('HRTA_TOPIC_HML')
hrta_ip = os.environ.get('PC_IP')

# Odoo Configs
url_odoo = os.getenv("ODOO_URL")
db = os.getenv("DB_ODOO")
username = os.getenv("USER_ODOO")
password = os.getenv("PASS_ODOO")


if not url_odoo or not db or not username:
    pass
else:
    try:
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_odoo))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_odoo))

    except xmlrpc.client.Fault as e:
        raise HTTPException(status_code=500, detail="Error connecting to Odoo")

# Pydantic Models
class InsertItem(BaseModel):
    user_id: Union[int, str]
    user_fname: str
    user_lname: str = None
    user_comments: int
    user_group: str = None
    subject_photo: str


class DeleteItem(BaseModel):
    user_id: Union[int, str]


class WriteItem(BaseModel):
    user_id: Union[int, str]
    user_fname: str
    user_lname: str = None
    user_comments: int
    user_group: str = None
    subject_photo: str


class SendMessage(BaseModel):
    user_id: Union[int, str]
    user_name: str
    user_photo: str
    user_category: str


# Odoo Funcs
def create_attachment(base64_image):
    attachment_id = models.execute_kw(db, uid, password, 'ir.attachment', 'create', [{
            'name': "image",
            'type': 'binary',
            'datas': base64_image,
            'res_model': 'mail.channel',
            'res_id': 0,
            'mimetype': 'image/png',
        }])
    return attachment_id


# Odoo Notify Receiver - 1
def create_message(message, attachment_id, bot_id, channel_id):
    models.execute_kw(db, uid, password, 'discuss.channel', 'message_post', [channel_id], {
            'body': message,
            'message_type': 'comment',
            'subtype_xmlid': 'mail.mt_comment',
            'author_id': bot_id,
            'attachment_ids': [attachment_id] if attachment_id else [],
        }
    )


# Odoo Notify Receiver - 2
def create_userlog(contact_id):
    message = f"Usuario apareceu as {datetime.datetime.now()}"
    models.execute_kw(db, uid, password, 'res.partner', 'message_post', [contact_id], {
        'body': message,
        'subtype_xmlid': 'mail.mt_note'
    })


# Odoo Notify Receiver - 3
def get_channel_id():
    channel_id = models.execute_kw(
        db, uid, password, 'discuss.channel', 'search', [[['name', '=', 'Administrator']]]
    )
    return channel_id[0] if channel_id else None

@app.get("/")
def home_validation():
    return "Home"

@app.post("/insert/")
def insert_user(item: InsertItem):
    user_photo = item.subject_photo
    payload = {
        "request": {
            "SubjectCode": item.user_id,
            "SubjectName": item.user_fname,
            "SubjectLastName": item.user_lname if item.user_lname else "-",
            "SubjectComments": str(item.user_comments),
            "SubjectGroup": item.user_group,
            "SubjectActive": "true",
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
    response = requests.post(url=os.getenv("INSERT_SUBJECT"), json=payload)
    if response.status_code == 200:
        try:
            return {"status": "success", "data": response.json()}
        except ValueError:
            return {"status": "success", "data": response.text}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@app.delete("/delete/")
def delete_user(item: DeleteItem):
    payload = {
        "SubjectCode": [
            item.user_id
        ]
    }
    response = requests.post(url=os.getenv("DELETE_SUBJECT"), json=payload)
    if response.status_code == 200:
        try:
            return {"status": "success", "data": response.json()}
        except ValueError:
            return {"status": "success", "data": response.text}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


@app.put("/write/")
def edit_user(item: WriteItem):
    user_photo = item.subject_photo
    payload = {
        "request": {
            "SubjectCode": item.user_id,
            "SubjectName": item.user_fname,
            "SubjectLastName": item.user_lname if item.user_lname else "-",
            "SubjectComments": str(item.user_comments),
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

    response = requests.post(url=os.getenv("INSERT_SUBJECT"), json=payload)
    if response.status_code == 200:
        try:
            return {"status": "success", "data": response.json()}
        except ValueError:
            return {"status": "success", "data": response.text}
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


# Main Odoo Notify Receiver
@app.post("/notify/")
async def send_message(item: SendMessage):
    try:
        channel_id = get_channel_id()
        attachment_id = await asyncio.to_thread(
            create_attachment,
            base64_image=item.user_photo
        )

        await asyncio.to_thread(
            create_message,
            message=f"O usuário {item.user_name} ({item.user_category}) chegou",
            attachment_id=attachment_id,
            bot_id=1,
            channel_id=channel_id
        )

        await asyncio.to_thread(
            create_userlog,
            contact_id=int(item.user_id)
        )
        return "Message Sent"
    except xmlrpc.client.Fault as e:
        return f"Failed to sent, error: {e}"


# MQTT Funcs
def on_connect(client, userdata, flags, rc, properties):
    print(f"Conectado com código de resultado {rc}")
    result, mid = client.subscribe(topic)
    # rst, mid = client.subscribe(topic_hml)
    if result == mqtt.MQTT_ERR_SUCCESS:
        print(f"Subscribed successfully with Message ID: {mid}")
    else:
        print(f"Failed to subscribe with error code: {result}")


def on_message(client, userdata, msg):
    print("Message received")
    xml_data = msg.payload.decode()
    asyncio.run(process_xml(xml_data))


def request_sender(subject_code, subject_comment):
    payload = {
        "clientUserId": subject_code,
        "developerId": int(subject_comment)
    }
    response = requests.post(url=os.getenv("CENTRALBASE_POST"), json=payload)
    if response.status_code != 200:
        return response.text
    else:
        return response.text


async def process_xml(xml_data):
    try:
        root = ET.fromstring(xml_data)
        namespace = {'i': 'http://schemas.datacontract.org/2004/07/BioComWebService'}

        bestcandidate_data = root.find('.//i:BestCandidate', namespace)
        if bestcandidate_data is not None:
            subject_code = bestcandidate_data.find('i:SubjectCode', namespace).text
            subject_comment = bestcandidate_data.find('i:SubjectComments', namespace).text
            request_sender(subject_code, subject_comment)

    except ET.ParseError as e:
        return f"Erro ao analisar o XML: {e}"


@app.on_event("startup")
async def startup_event():
    # Configurações do MQTT
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(hrta_ip, 1883, 30)
    client.loop_start()


@app.on_event("shutdown")
async def shutdown_event():
    client.loop_stop()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
