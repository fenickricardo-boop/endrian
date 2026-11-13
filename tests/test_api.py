from fastapi.testclient import TestClient
from app.main import app

def test_api_begins_definition_before_identity():
    with TestClient(app) as c:
        r=c.post('/api/chat',json={'message':'Necesito organizar correos ficticios'}); assert r.status_code==200
        assert r.json()['event']=='DETERMINISTIC_SCRIPT_REQUIRED'
        assert r.json()['summary']['full_flow']['state']=='S1'
        assert r.json()['summary']['full_flow']['orientation_summary'] is None

def test_api_rejects_real_email_registration():
    with TestClient(app) as c:
        r=c.post('/api/full-flow/registration',json={'name':'QA','email':'real@example.com','country_code':'CL','country_name':'Chile','data_processing':True,'operational_comms':True,'marketing':False})
        assert r.status_code in {400,409}

def test_config_is_qa_only():
    with TestClient(app) as c:
        body=c.get('/api/config').json(); assert body['qa'] is True and body['full_flow'] is True
