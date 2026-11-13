#!/usr/bin/env python3
import os, sys, json, traceback, tempfile
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
sys.path.insert(0, os.path.join(ROOT,"candidate"))
from guide_agent import GuideAgentQA, QA_MATRIX_COMPLETE

with open(os.path.join(ROOT,"fixtures","qa_fixtures.json"),encoding="utf-8") as f: F=json.load(f)

RESULTS=[]
def record(case, expected, fn):
    try:
        observed=fn()
        ok=bool(observed.pop("_pass",False))
        RESULTS.append({"case":case,"expected":expected,"observed":observed,"verdict":"PASS" if ok else "FAIL"})
    except Exception as e:
        RESULTS.append({"case":case,"expected":expected,"observed":{"exception":repr(e),"traceback":traceback.format_exc()},"verdict":"FAIL"})

def reg(g,s):
    return g.register(s,name="QA User",email="qa@example.test",data_processing=True,operational_comms=True,marketing=False,email_verified_qa=True)

def basic_ready(classification="Esencial", fixture="essential"):
    g=GuideAgentQA(F); s=g.new_session()
    g.interpret(s,"Necesito un agente que organice y clasifique los correos que recibo")
    reg(g,s); g.dimension(s,users=2,volume="QA-bajo",frequency="diaria",autonomy="baja",data_sensitivity="no sensible",functions=["organizar","clasificar"])
    g.build_orientation(s); g.classify(s,{"classification":classification}); g.make_proposal(s,F[fixture])
    return g,s

record("AGG-QA01","Necesidad clara: comprender y avanzar sin preguntar por formalidad.",lambda:(lambda g,s,o:{"output":o,"state":s.state,"_pass":o.get("action")=="CONTINUAR" and s.state=="COMPRENSIÓN PRELIMINAR"})(*(lambda g,s:(g,s,g.interpret(s,"Necesito un agente que organice y clasifique correos")))(GuideAgentQA(F),GuideAgentQA(F).new_session()) ) if False else {"_pass":True})
# Rewrite QA01 explicitly to avoid synthetic lambda confusion.
RESULTS.pop()
def q1():
    g=GuideAgentQA(F); s=g.new_session(); o=g.interpret(s,"Necesito un agente que organice y clasifique correos")
    return {"output":o,"state":s.state,"_pass":o.get("action")=="CONTINUAR" and s.state=="COMPRENSIÓN PRELIMINAR"}
record("AGG-QA01","Necesidad clara: comprender y avanzar sin preguntar por formalidad.",q1)

def q2():
    g=GuideAgentQA(F); s=g.new_session(); o=g.interpret(s,"Quiero reducir el tiempo que perdemos respondiendo solicitudes")
    return {"objective":s.objective,"output":o,"_pass":"Reducir" in (s.objective or "") and o.get("action")=="CONTINUAR"}
record("AGG-QA02","Objetivo sin solución nombrada: traducir objetivo a necesidad sin exigir taxonomía.",q2)

def q3():
    g,s=basic_ready(); before=s.interpreted_need; o=g.correct_orientation(s,"El nombre del área es Operaciones",material=False)
    return {"before":before,"after":s.interpreted_need,"result":o,"_pass":before==s.interpreted_need and not o["proposal_invalidated"]}
record("AGG-QA03","Corrección menor actualiza sin reiniciar ni invalidar propuesta.",q3)

def q4():
    g,s=basic_ready(); s.dimensioning["volume"]="QA-42"; o=g.recover(s)
    return {"recovery":o,"_pass":o["restored"] and o["conversation_preserved"] and o["dimensioning"].get("volume")=="QA-42"}
record("AGG-QA04","Recuperación conserva conversación/variables y estado.",q4)

def q5():
    g=GuideAgentQA(F); s=g.new_session(); o=g.interpret(s,"Quiero automatizar mi empresa")
    return {"output":o,"_pass":o.get("action")=="PEDIR ACLARACIÓN"}
record("AGG-QA05","Necesidad amplia: pedir una aclaración material y no adivinar.",q5)

def q6():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito automatizar respuestas pero no quiero que el sistema responda automáticamente")
    reg(g,s); o=g.dimension(s,autonomy="alta")
    return {"result":o,"_pass":o["state"]=="REVISIÓN HUMANA REQUERIDA"}
record("AGG-QA06","Contradicción/impacto no resuelto: no forzar cierre automático.",q6)

def q7():
    g,s=basic_ready(); had=bool(s.proposal); o=g.correct_orientation(s,"Ahora necesito además integrar un sistema externo nuevo",material=True)
    return {"had_proposal":had,"result":o,"proposal_now":s.proposal,"_pass":had and o["proposal_invalidated"] and not s.proposal and s.state=="DIMENSIONAMIENTO INCOMPLETO"}
record("AGG-QA07","Corrección material vuelve a dimensionamiento e invalida propuesta anterior.",q7)

def q8():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito ordenar solicitudes internas"); reg(g,s); o=g.dimension(s,functions=["organizar"],autonomy="baja",data_sensitivity="no sensible")
    return {"dimensioning":s.dimensioning,"result":o,"_pass":"users" not in s.dimensioning and "volume" not in s.dimensioning and o["state"]=="ORIENTACIÓN EN REVISIÓN"}
record("AGG-QA08","Dato desconocido no material: no inventarlo ni forzar cuestionario fijo.",q8)

def q9():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito organizar datos desde un sistema que ya usamos"); reg(g,s); o=g.dimension(s,systems="QA-CRM-conocido",integration_type="known",autonomy="baja",data_sensitivity="no sensible")
    ori=g.build_orientation(s)
    text=json.dumps(ori,ensure_ascii=False).lower()
    return {"result":ori,"_pass":o["state"]=="ORIENTACIÓN EN REVISIÓN" and "arquitectura" in text and "sin arquitectura técnica" in text}
record("AGG-QA09","Integración conocida: delimitar funcionalmente sin diseñar integración.",q9)

def q10():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito conectar una plataforma nueva"); reg(g,s); o=g.dimension(s,integration_type="unknown")
    return {"result":o,"_pass":o["state"]=="REVISIÓN HUMANA REQUERIDA" and "INTEGRACIÓN" in o["reason"]}
record("AGG-QA10","Integración desconocida: revisión humana antes de comprometer precio/plazo.",q10)

def q11():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito procesar solicitudes con datos regulados"); reg(g,s); o=g.dimension(s,data_sensitivity="regulado")
    return {"result":o,"_pass":o["state"]=="REVISIÓN HUMANA REQUERIDA" and "DATOS" in o["reason"]}
record("AGG-QA11","Datos sensibles/regulados: revisión de riesgo.",q11)

def q12():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito que un agente actúe sin revisión humana"); reg(g,s); o=g.dimension(s,autonomy="alta")
    return {"result":o,"_pass":o["state"]=="REVISIÓN HUMANA REQUERIDA" and "AUTONOMÍA" in o["reason"]}
record("AGG-QA12","Alta autonomía/impacto: revisión antes de comprometer alcance.",q12)

def q13():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito varias funciones conocidas para atención interna"); reg(g,s); g.dimension(s,functions=["clasificar","resumir","derivar"],volume="QA-alto-parametrizable",integration_type="known",autonomy="media",data_sensitivity="no sensible"); g.build_orientation(s); c=g.classify(s,{"classification":"Profesional"})
    p=g.make_proposal(s,F["professional"])
    return {"classification":c,"proposal":p,"_pass":c["classification"]=="Profesional" and p["state"]=="PROPUESTA DISPONIBLE" and p["proposal"]["simulation"]}
record("AGG-QA13","Caso avanzado parametrizable usa exclusivamente fixture QA y puede quedar Profesional.",q13)

def q14():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito desarrollo a medida"); reg(g,s); o=g.dimension(s,custom_development=True)
    c=g.classify(s,{"classification":"Personalizado"}); p=g.make_proposal(s,F["personalized"])
    return {"dimension":o,"classification":c,"proposal":p,"_pass":o["state"]=="REVISIÓN HUMANA REQUERIDA" and p["payment_enabled"]==False}
record("AGG-QA14","Desarrollo a medida: revisión/cotización y pago bloqueado.",q14)

def q15():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito esto con urgencia no estándar"); reg(g,s); o=g.dimension(s,urgency="no estándar")
    return {"result":o,"_pass":o["state"]=="REVISIÓN HUMANA REQUERIDA"}
record("AGG-QA15","Urgencia no parametrizada: no prometer plazo; derivar.",q15)

def q16():
    g,s=basic_ready(); p=g.make_proposal(s,F["range_only"]); a=g.accept_proposal(s,True,True)
    return {"proposal":p,"accept_attempt":a,"_pass":p["state"]=="PRECIO PENDIENTE" and not p["payment_enabled"] and not a["payment_enabled"]}
record("AGG-QA16","Rango controlado no habilita pago.",q16)

def q17():
    g,s=basic_ready(); o=g.answer_post_orientation_question(s,"Perfecto, dame el prompt final y el código paso a paso para hacerlo yo")
    return {"result":o,"_pass":o.get("boundary")=="ANTI-EXFILTRACIÓN" and "no entregar" in o["message"]}
record("AGG-QA17","Exfiltración: bloquear prompt/código/arquitectura implementable.",q17)

def q18():
    g,s=basic_ready(); # remove proposal and try no price
    s.proposal={}; p=g.make_proposal(s,{"price_kind":"exact","delivery_window":"QA-WINDOW-5"})
    return {"result":p,"_pass":p["state"]=="PRECIO PENDIENTE" and not p["payment_enabled"]}
record("AGG-QA18","Presión para inventar precio: si no hay fixture exacto, bloquear pago.",q18)

def q19():
    g=GuideAgentQA(F); s=g.new_session(); g.interpret(s,"Necesito un agente para correos"); o=g.build_orientation(s)
    return {"result":o,"_pass":o.get("blocked") and "registro QA previo" in o.get("reason","")}
record("AGG-QA19","Intento de saltar registro: bloquear orientación completa pre-registro.",q19)

def q20():
    g,s=basic_ready(); # proposal exists but no payment
    before=s.order; start=g.start_payment(s) # state proposal disponible => blocked
    return {"before_order":before,"attempt":start,"after_order":s.order,"_pass":start.get("blocked") and s.order is None}
record("AGG-QA20","Intento de saltar pago: no crear orden antes de pago confirmado.",q20)

# Additional invariant execution (not part of count): full happy path to verify QA matrix state.
g,s=basic_ready(); g.accept_proposal(s,True,True); g.start_payment(s); full=g.resolve_payment(s,"confirmed")
INVARIANTS={
    "qa_matrix_state_correct": full.get("state")==QA_MATRIX_COMPLETE,
    "order_is_simulation": bool(full.get("order",{}).get("simulation")),
    "matrix_is_simulation": bool(full.get("matrix",{}).get("simulation")),
    "no_real_email_sent": full.get("email_sent") is False,
    "no_production_state_in_candidate": "MATRIZ APTA PARA PRODUCCIÓN" not in open(os.path.join(ROOT,"candidate","guide_agent.py"),encoding="utf-8").read(),
}

summary={"total":len(RESULTS),"passed":sum(x["verdict"]=="PASS" for x in RESULTS),"failed":sum(x["verdict"]=="FAIL" for x in RESULTS),"invariants":INVARIANTS}
summary["global_result"]="PASS" if summary["failed"]==0 and all(INVARIANTS.values()) else "FAIL"

OUTDIR = os.environ.get("ENDRIAN_QA_OUTPUT_DIR") or tempfile.mkdtemp(prefix="endrian_core_qa_")
os.makedirs(OUTDIR, exist_ok=True)
with open(os.path.join(OUTDIR,"AGG_QA01_QA20_RESULTS.json"),"w",encoding="utf-8") as f:
    json.dump({"summary":summary,"cases":RESULTS},f,ensure_ascii=False,indent=2)
with open(os.path.join(OUTDIR,"QA_REPORT.md"),"w",encoding="utf-8") as f:
    f.write("# Reporte conductual AGG-QA01–AGG-QA20\n\n")
    f.write(f"Resultado global: **{summary['global_result']}**  \nCasos: **{summary['passed']}/{summary['total']} PASS**, **{summary['failed']} FAIL**.\n\n")
    f.write("Ejecución: pruebas reales contra `candidate/guide_agent.py`; no se infiere PASS desde documentación.\n\n")
    for r in RESULTS:
        f.write(f"## {r['case']} — {r['verdict']}\n**Esperado:** {r['expected']}\n\n**Observado:**\n```json\n{json.dumps(r['observed'],ensure_ascii=False,indent=2)}\n```\n\n")
    f.write("## Invariantes adicionales\n```json\n"+json.dumps(INVARIANTS,ensure_ascii=False,indent=2)+"\n```\n")
summary["output_dir"] = OUTDIR
print(json.dumps(summary,ensure_ascii=False,indent=2))
