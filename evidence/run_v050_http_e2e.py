import json
from pathlib import Path
import httpx

BASE="http://127.0.0.1:8050"
INITIAL="Necesito algo para ordenar los correos que nos llegan de clientes porque se nos pierden cosas. Somos cuatro personas y usamos correo para consultas, reclamos y solicitudes. Me gustaría que pudiera responder y hacer seguimiento."
REPLY="Son unos 80 correos al día. Mejor que no responda solo. Quiero que clasifique, priorice y nos ayude a llevar seguimiento, pero que una persona revise las respuestas. Lo de responder automáticamente descártalo."

def post(client,path,payload=None):
    response=client.post(BASE+path,json=payload or {},headers={"X-ENDRIAN-QA":"1"})
    return response,response.json()

with httpx.Client(follow_redirects=True,timeout=20,trust_env=False) as client:
    client.get(BASE+"/")
    post(client,"/api/chat",{"message":INITIAL}); post(client,"/api/chat",{"message":REPLY})
    post(client,"/api/full-flow/confirmation/action",{"action":"confirm"})
    post(client,"/api/full-flow/proposal/action",{"action":"continue"})
    post(client,"/api/full-flow/registration",{"name":"Persona Ensayo","email":"persona.ensayo@pruebas.test","country_code":"CL","country_name":"Chile","phone_country_code":"","phone_country_name":"","phone_calling_code":"","phone_national_number":""})
    post(client,"/api/full-flow/contracting",{"contract_terms_accepted":True,"privacy_authorization_accepted":True})
    _,started=post(client,"/api/full-flow/payment/start"); reference=started["summary"]["full_flow"]["payment_qa"]["reference"]
    post(client,"/api/full-flow/payment/return")
    pending=client.get(BASE+"/api/session").json()
    assert pending["full_flow"]["state"]=="S6" and pending["full_flow"]["order_qa"] is None
    first_response,first=post(client,"/api/qa-control/payment/resolve",{"reference":reference,"outcome":"confirmed"})
    assert first_response.status_code==200
    flow=first["summary"]["full_flow"]; order=flow["order_qa"]; order_id=order["order_id"]
    assert flow["state"]=="S7" and order["status"]=="RECIBIDA"
    snapshot_before=json.dumps(order["construction_request_snapshot"],ensure_ascii=False,sort_keys=True)
    repeat_response,_=post(client,"/api/qa-control/payment/resolve",{"reference":reference,"outcome":"confirmed"})
    assert repeat_response.status_code==409
    reloaded=client.get(BASE+"/api/session").json()["full_flow"]
    assert reloaded["order_qa"]["order_id"]==order_id
    finalize_response,finalized=post(client,"/api/full-flow/conversation/finalize")
    assert finalize_response.status_code==200 and finalized["event"]=="CONVERSATION_FINALIZED"
    clean=finalized["summary"]
    assert clean["full_flow"]["state"]=="S0" and clean["history"]==[] and clean["full_flow"]["qa_identity"] is None and clean["full_flow"]["order_qa"] is None
    after_reload=client.get(BASE+"/api/session").json()
    assert after_reload["session_id"]==clean["session_id"] and after_reload["history"]==[] and after_reload["full_flow"]["state"]=="S0"
    archive_response=client.get(BASE+f"/api/qa-control/orders/{order_id}")
    assert archive_response.status_code==200
    archived=archive_response.json()["archived_order"]
    assert archived["order"]["order_id"]==order_id
    assert json.dumps(archived["order"]["construction_request_snapshot"],ensure_ascii=False,sort_keys=True)==snapshot_before
    assert archived["email_preview"]["sent"] is False
    serialized=json.dumps(archived,ensure_ascii=False).lower()
    assert "transcript" not in serialized and INITIAL.lower() not in serialized
    result={
      "build":"ENDRIAN_LAB_FULL_FLOW_QA_v0.5.0",
      "pending":{"state":"S6","order":None,"reference":reference},
      "confirmed":{"state":"S7","order_id":order_id,"status":"RECIBIDA"},
      "repeated_confirmation":{"http_status":repeat_response.status_code,"same_order":True},
      "finalization":{"event":finalized["event"],"new_session_id":clean["session_id"],"clean_state":"S0","history_count":0,"contact_present":False,"order_visible_in_new_session":False},
      "archive":{"consultable":True,"snapshot_identical":True,"transcript_found":False,"email_preview_sent":False,"snapshot_sha256":archived["snapshot_sha256"]}
    }
    Path("qa_results/V050_LIVE_HTTP_E2E_RESULTS.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))
