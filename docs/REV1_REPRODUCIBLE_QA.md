# QA reproducible REV1

Ejecutar desde la raíz del paquete con Python y dependencias de `requirements.txt` ya instaladas.

```bash
pytest -q
python agent_guide/core_v0_1/qa/run_qa.py
python agent_guide/qa/run_blackbox_qa.py
```

Los dos runners del Agente Guía escriben por defecto en un directorio temporal externo y **no modifican** el paquete. Si se desea conservar resultados en una ubicación concreta:

```bash
ENDRIAN_QA_OUTPUT_DIR=/ruta/temporal python agent_guide/core_v0_1/qa/run_qa.py
ENDRIAN_QA_OUTPUT_DIR=/ruta/temporal python agent_guide/qa/run_blackbox_qa.py
```

Resultados de la ejecución usada para cerrar REV1 se incluyen en `qa_results/`.
