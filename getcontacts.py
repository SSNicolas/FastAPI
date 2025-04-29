import requests
import json
import os
import dotenv

dotenv.load_dotenv()

# skip = 0
# limit = 100


get_url_back = os.getenv("CENTRALBASE_GET")

headers = {
    'Authorization': f'{os.getenv("CENTRALBASE_PATRITOKEN")}',
    'Content-Type': 'application/json'
}

response = requests.get(url=os.getenv("CENTRALBASE_GET"), headers=headers)

back_data = response.json()
back_ids = [ids['id'] for ids in back_data]

get_url_patr = os.getenv("PATRI_DEV_GET_ENDPOINT")

headers = {
    'Authorization': f'Bearer {os.getenv("PATRI_DEVTOKEN")}',
    'Content-Type': 'application/json'
}
response = requests.get(url=get_url_patr, headers=headers)

patri_data = response.json()

for patri_user in patri_data['payload']['data']:
    if patri_user['id'] not in back_ids:
        payload = {
            "name": patri_user['name'],
            "clientUserId": patri_user['id'],
            "image": {
                "base64": patri_user['image']['base64'],
                "url": patri_user['image']['url']
            },
            "categoryId": patri_user['categoryId']
        }
        headers = {
            'Authorization': f'{os.getenv("CENTRALBASE_PATRITOKEN")}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url=f"{os.getenv("CENTRALBASE_GET")}create", json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Contato de {patri_user['name']} inserido")
        else:
            print(f"Falha na inserção")
            print(response.text)

    else:
        print("Ja cadastrado")
