# Documentação da Aplicação FastAPI

## Introdução

Bem-vindo à documentação do código que realiza a formatação e passagem dos dados ao Herta, além de fazer o recebimento e envio das notificações do mesmo. 
Esta aplicação foi desenvolvida utilizando o framework FastAPI para facilitar caso sejam necessárias manutenções ou modificações no futuro.

Abaixo, você encontrará detalhes sobre como configurar e utilizar API .

## Índice

1. [Instalação](#instalação)
2. [Configuração](#configuração)
3. [Execução](#execução)
4. [Endpoints](#endpoints)
5. [Referência](#referências)


## Instalação

Para instalar a aplicação, siga os passos abaixo:

```bash
git clone 
pip install -r requirements.txt
```

## Configuração

Adicione as variáveis de ambiente abaixo em um arquivo _.env_, passando também os dados necessários:

Obs: Para descobrir o topico/rota do mqtt, utilize o [MQTT.fx](https://iotcore-dev-tool.gz.bcebos.com/mqttfx/1.7.1/mqttfx-1.7.1-windows-x64.exe)


* **ODOO_URL**=IP do Odoo que será utilizado (se for utilizado)
* **DB_ODOO**=Nome do database do Odoo
* **USER_ODOO**=Usuário para acesso no Odoo
* **PASS_ODOO**=Senha para acesso no Odoo
### As váriaveis do Odoo acima, serão utilizadas apenas se o CRM em uso for o Odoo, caso não seja, não as coloque.
* **INSERT_SUBJECT**=Endpoint POST de inserção de usuário no Herta
* **DELETE_SUBJECT**=Endpoint POST de exclusão de usuário no Herta
* **HRTA_TOPIC**=Tópico/rota que o MQTT vai ouvir as notificações do reconhecimento
* **PC_IP**=IP do PC que está hospedando o Herta
* **CENTRALBASE_POST**=Endpoint usada para fazer o envio das notificações para o outro backend
* **CENTRALBASE_GET**=Endpoint get usada para fazer a comparação dos usuários do CRM e do Herta


Exemplo do arquivo **.env**:
```dotenv
ODOO_URL=http://127.0.0.1:8069/
DB_ODOO=odoo_testedb
USER_ODOO=admin
PASS_ODOO=admin
INSERT_SUBJECT=http://127.0.0.1:8005/BioService/v1/EnrollSubjectWithAlbum
DELETE_SUBJECT=http://127.0.0.1:8005/BioService/v1/DeleteSubjects
HRTA_TOPIC=herta/v1/DESKTOP-HVMPAH2/Herta/fr_sources/H26X/Patriani/in_progress/ident
PC_IP=127.0.0.1
CENTRALBASE_POST=https://face-recognition-engine.onrender.com/client/notify
CENTRALBASE_GET=https://face-recognition-engine.onrender.com/client/
```

## Execução

Para executar o código local é necessário executar o código por meio do da lib **Uvicorn**, segue comando abaixo:
```bash
# Caso necessário troque a porta em que o código é executado
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

### POST /insert/

**Descrição**

Faz a inserção de um novo usuário no Herta.

**Corpo da requisição**

```json
{
  "user_id": int / "string",
  "user_fname": "string",
  "user_lname": "string" / None,
  "user_comments": "string",
  "user_group": "string" / None,
  "subject_photo": "string"
}
```

### POST /delete/

**Descrição**

Faz a exclusão de um usuário do Herta.

**Corpo da requisição**

```json
{
  "user_id": int / "string"
}
```

### POST /write/

**Descrição**

Faz a edição de um usuário do Herta.

Obs: Do jeito que o Herta funciona somos obrigados a apagar o registro e criar um novo ao invés de usar a API de update que não funciona.

**Corpo da requisição**

```json
{
  "user_id": int / "string",
  "user_fname": "string",
  "user_lname": "string" / None,
  "user_comments": "string",
  "user_group": "string" / None,
  "subject_photo": "string"
}
```

### POST /notify/

**Descrição**

Faz o envio das notificações para o Odoo e faz o envio do log de passagem do usuário já cadastrado.

Só é usado quando o CRM for o Odoo.

**Corpo da requisição**

```json
{
  "user_id": int / "string",
  "user_fname": "string",
  "user_lname": "string" / None,
  "user_comments": "string",
  "user_group": "string" / None,
  "subject_photo": "string"
}
```


## Referências

 - [Instalação de Repositórios (github/bitbucket)](https://docs.github.com/pt/repositories/creating-and-managing-repositories/cloning-a-repository)
 - [FastAPI](https://fastapi.tiangolo.com/tutorial/)
 - [MQTT](https://mosquitto.org/)
 - [Paho client (MQTT Lib)](https://pypi.org/project/paho-mqtt/)
 - [Odoo External API](https://www.odoo.com/documentation/17.0/developer/reference/external_api.html)
 - [Async Functions](https://superfastpython.com/python-async-function/)

