# ENDRIAN Laboratorio — Full Flow QA v0.5.15

**QA SIMULADO / NO PRODUCCIÓN.** No uses datos personales reales.

## Abrir en Windows
1. Cierra cualquier ventana anterior del lanzador y comprueba que no quede otro servidor usando el puerto 8000.
2. Extrae este ZIP en una carpeta nueva; no lo ejecutes dentro de una carpeta de una versión anterior.
3. Asegura Python 3.11+ y las dependencias de `requirements.txt`.
4. Haz doble clic en `START_LAB_QA.bat`; FastAPI inicia en `http://127.0.0.1:8000/` y el navegador se abre automáticamente.
5. Abre una ventana privada del navegador o realiza una recarga completa para evitar archivos estáticos en caché.
6. Para cerrar, vuelve a la ventana del lanzador y presiona **Ctrl+C**; Uvicorn se termina explícitamente y el puerto queda liberado.

## Revisión UX vigente
- Menú visible: `Volver a ENDRIAN · Servicios · Precios · Contacto · Nueva conversación`.
- `Servicios` abre tres tarjetas compactas: `ENDRIAN Esencial`, `ENDRIAN Especializado` y `ENDRIAN Integral`.
- `Ver ficha` sustituye las tarjetas por una única ficha dentro del mismo panel; `Volver a Servicios` regresa al selector restaurando desplazamiento y foco, y `×` cierra el panel sin reiniciar la conversación.
- `Precios` utiliza la `×` circular superior como único control visible de cierre; restaura el foco en el control que abrió el panel y no inicia ni envía mensajes.
- `Precios` permanece independiente y muestra los valores comerciales vigentes del candidato.
- `Privacidad` queda como enlace secundario en el footer y dentro del formulario de contacto.
- `Contacto` es solo interfaz local: no envía ni almacena el formulario. Usa datos ficticios para revisar la pantalla.
- El comportamiento conversacional, S0–S8/SH, PaymentGate y backend permanecen fuera de esta corrección.

## Volver a ENDRIAN en local
La Home v2.3 no está incluida dentro de este ZIP. El acceso `Volver a ENDRIAN` usa primero una ruta local relativa recibida en `?home=/ruta-local` y, si no existe, el `document.referrer` desde el que se abrió el Laboratorio. Si se lanza directamente sin referencia, muestra un aviso integrado en lugar de inventar una URL pública.

## Confirmar privadamente un pago QA

1. Completa el recorrido público hasta volver del checkout y ver `Estamos verificando tu pago`.
2. Sin cerrar el navegador, abre otra pestaña en `http://127.0.0.1:8000/qa-control/payment`.
3. La consola privada carga automáticamente la referencia `PAY-QA-...` de la sesión pendiente.
4. Pulsa `Confirmado`. Esta consola solo responde desde localhost y `QA_CONTROLLED_TEST_ONLY`; no está enlazada desde la navegación pública.
5. Pulsa `Volver al Laboratorio` o regresa a la primera pestaña y actualízala. Debe aparecer `Pago confirmado` y una única orden con estado `Pedido recibido`.
6. Si repites la confirmación, el backend la bloquea y conserva la misma orden. La comprobación de replay permanece en la capa privada y en la regresión automatizada; no se expone como botón público.
7. Anota el número `END-AAAAMMDD-NNNN`. Tras `Finalizar conversación`, la orden sigue consultable de forma privada en `http://127.0.0.1:8000/api/qa-control/orders/NUMERO-DE-ORDEN`.

`Finalizar conversación` elimina la sesión conversacional activa, limpia chat/datos/fichas y rota la cookie a una sesión nueva. No elimina la orden archivada. Cerrar el navegador sin pulsar este botón no equivale a finalizar: la sesión QA puede recuperarse mientras su cookie y TTL sigan vigentes.

Las salidas posteriores a la orden están separadas de la experiencia pública y se generan desde la orden archivada y su snapshot inmutable:

- Correo breve al cliente: `http://127.0.0.1:8000/qa-control/orders/NUMERO-DE-ORDEN/confirmation`.
- Único PDF: botón de la vista anterior o `http://127.0.0.1:8000/api/qa-control/orders/NUMERO-DE-ORDEN/contract-copy.pdf`.
- Ficha interna de preparación: `http://127.0.0.1:8000/qa-control/orders/NUMERO-DE-ORDEN/internal`.
- Aviso interno no enviado: `http://127.0.0.1:8000/qa-control/orders/NUMERO-DE-ORDEN/internal-notice`.

Las vistas privadas solo responden desde localhost y `QA_CONTROLLED_TEST_ONLY`. Correo y aviso permanecen `sent=false`, sin proveedor ni destinatario corporativo inventado. La ficha interna muestra como pendientes los criterios, materiales o asignaciones que la orden no registra.

La tarjeta pública obtiene el título específico desde `construction_request_snapshot.solution_title`, ofrece solo `Finalizar conversación` y muestra los cuatro pasos de `Tu recorrido` como completados tras la confirmación. Esto no significa que el agente esté construido o entregado.

## Condiciones del candidato
- `MODEL_MODE=deterministic`.
- SQLite local: `data/full_flow_qa.db`.
- Sin `OPENAI_API_KEY`.
- Sin proveedor de pago, correo o servicios externos.
- Utiliza únicamente datos ficticios. La aplicación valida formato, pero no verifica la existencia del correo o teléfono.
- Monto y plazo del flujo funcional son valores QA simulados, no oferta comercial.

## Recuperación
Usa el enlace secundario **Recuperar solicitud** del footer e ingresa únicamente el `qa_identity_ref` sintético mostrado por la aplicación.

## Rollback
La carpeta `rollback/` conserva la copia fuente heredada del flujo funcional y su SHA-256.
