# ENDRIAN Agente Guía MVP QA v0.2

Estado: **NÚCLEO DE CONTROL + CAPA CONVERSACIONAL INTEGRABLE / PRUEBAS DE CAJA NEGRA / QA / NO PRODUCCIÓN**.

- `core_v0_1/`: v0.1 preservada íntegramente como núcleo determinista de control y reglas.
- `candidate/conversational_agent.py`: capa v0.2 con punto de entrada único `handle_message(session_id, user_message)`.
- `qa/run_blackbox_qa.py`: pruebas de caja negra que llaman únicamente al punto de entrada público.
- `docs/MODEL_INTEGRATION_CONTRACT.md`: contrato para integrar posteriormente un modelo real sin darle autoridad sobre estados/transacciones.
- `docs/VALERIA_TECHNICAL_INTEGRATION.md`: contrato técnico posterior para la interfaz.

No contiene credenciales, proveedor de IA configurado, red, registro real, correo real, pago real, órdenes productivas ni conexión productiva con Laboratorio.
