import requests
import xmlrpc.client
import time
import dotenv
import os
import asyncio
from paho.mqtt import client as mqtt
import xml.etree.ElementTree as ET
from datetime import datetime

dotenv.load_dotenv()

url_odoo = os.getenv("ODOO_URL")
db = os.getenv("DB_ODOO")
username = os.getenv("USER_ODOO")
password = os.getenv("PASS_ODOO")

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url_odoo))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url_odoo))
last_alarm_id = []
url_last_alarm_id = "http://127.0.0.1:8005/BioService/v1/GetLastIdentificationAlarmID"
url_candidates_last_id = "http://127.0.0.1:8005/BioService/v1/GetCandidates"

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

def create_message(message, attachment_id, bot_id, channel_id):
    models.execute_kw(db, uid, password, 'discuss.channel', 'message_post', [channel_id], {
            'body': message,
            'message_type': 'comment',
            'subtype_xmlid': 'mail.mt_comment',
            'author_id': bot_id,
            'attachment_ids': [attachment_id] if attachment_id else [],
        }
    )

def create_userlog(contact_id):
    message = f"Usuario apareceu as {datetime.now()}"
    models.execute_kw(db, uid, password, 'res.partner', 'message_post', [contact_id], {
        'body': message,
        'subtype_xmlid': 'mail.mt_note'
    })

def get_channel_id():
    channel_id = models.execute_kw(
        db, uid, password, 'discuss.channel', 'search', [[['name', '=', 'Administrator']]]
    )
    return channel_id[0] if channel_id else None


def on_connect(client, userdata, flags, rc, properties):
    print(f"Conectado com código de resultado {rc}")
    client.subscribe("herta/v1/DESKTOP-HVMPAH2/Herta/fr_sources/H26X/Source1/in_progress/ident", qos=0)


def on_message(client, userdata, msg):
    xml_data = msg.payload.decode()
    asyncio.run(process_xml(xml_data))


async def process_xml(xml_data):
    try:
        root = ET.fromstring(xml_data)
        namespace = {'i': 'http://schemas.datacontract.org/2004/07/BioComWebService'}

        bestcandidate_data = root.find('.//i:BestCandidate', namespace)
        if bestcandidate_data is not None:
            subject_code = bestcandidate_data.find('i:SubjectCode', namespace).text
            print(subject_code)
            subject_fname = bestcandidate_data.find('i:SubjectName', namespace).text
            subject_lname = bestcandidate_data.find('i:SubjectLastName', namespace).text
            subject_group = bestcandidate_data.find('i:SubjectGroup', namespace).text
            subject_photo = bestcandidate_data.find('i:SubjectPhoto', namespace).text
            channel_id = get_channel_id()

            attachment_id = await asyncio.to_thread(create_attachment, subject_photo)


            await asyncio.to_thread(create_message,
                message=f"O usuário {subject_fname} {subject_lname} ({subject_group}) chegou",
                attachment_id=attachment_id,
                bot_id=1,
                channel_id=channel_id
                )

            await asyncio.to_thread(create_userlog,
                contact_id=int(subject_code)
            )

    except ET.ParseError as e:
        print(f"Erro ao analisar o XML: {e}")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 30)

client.loop_forever()