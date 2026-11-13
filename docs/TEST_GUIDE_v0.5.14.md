# Guía de prueba — v0.5.14

## Crear una orden QA nueva

1. Inicia el paquete con `START_LAB_QA.bat` o `python start_lab_qa.py`.
2. Usa el mensaje inicial del fixture indicado en la interfaz y responde la pregunta material con el texto de prueba sugerido.
3. Pulsa **Sí, preparar mi resumen**.
4. Revisa el resumen y pulsa **Continuar con mi solicitud**.
5. Completa datos ficticios, país, las dos aceptaciones y avanza al checkout simulado.
6. Regresa al Laboratorio: debe mostrarse **Estamos verificando tu pago** y no debe existir orden.
7. Abre `http://127.0.0.1:8000/qa-control/payment` y confirma privadamente el intento pendiente.
8. Recarga el Laboratorio. Anota la orden `END-AAAAMMDD-NNNN`.

## Abrir salidas privadas

Sustituye `ORDEN` por el número real:

- Correo al cliente: `http://127.0.0.1:8000/qa-control/orders/ORDEN/confirmation`.
- PDF: `http://127.0.0.1:8000/api/qa-control/orders/ORDEN/contract-copy.pdf`.
- Ficha interna: `http://127.0.0.1:8000/qa-control/orders/ORDEN/internal`.
- Aviso interno: `http://127.0.0.1:8000/qa-control/orders/ORDEN/internal-notice`.
- JSON archivado: `http://127.0.0.1:8000/api/qa-control/orders/ORDEN`.

Las rutas privadas solo responden desde localhost con `APP_ENV=QA_CONTROLLED_TEST_ONLY`. Finalizar la conversación no elimina la orden ni estas representaciones.
