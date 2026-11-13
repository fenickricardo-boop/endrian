# QA v0.5.8

## Resultado

- Base v0.5.6: tamaño, SHA-256, extracción general y cinco ZIP internos: PASS.
- Suite automatizada: 164 PASS / 0 FAIL.
- Sintaxis JavaScript: PASS.
- Compilación Python: PASS.
- Health HTTP: PASS.
- HTML y JavaScript servidos: PASS.
- Menú desktop y móvil con Servicios y Precios independientes: PASS automatizado.
- Tres fichas completas y tres precios autorizados: PASS automatizado.
- Oferta antigua, USD 79 y bloque empresarial ausentes de los paneles servidos: PASS.
- Cierre, Escape, exclusión mutua, retorno de foco y Volver a la conversación: PASS por contratos automatizados.
- Ausencia de creación de sesión o envío automático desde paneles: PASS por contrato automatizado.
- Contacto general, validaciones y recuperación: PASS por regresión automatizada.
- Normalización visual de controles de Contacto a 42 px, textarea mayor y responsive CSS: PASS por contrato automatizado.
- Ruta conversacional, PaymentGate, orden única, correo y PDF: PASS por regresión automatizada existente.
- Navegador gráfico desktop/móvil y capturas reales: PENDIENTE. El navegador de automatización no pudo instalar su ejecutable en este entorno; no se declara PASS visual.

## Diferencias registradas fuera del alcance

Persisten nombres y precios QA anteriores en `app/full_flow.py`, `app/service.py` y los catálogos internos. Se conservaron deliberadamente porque el encargo prohíbe ampliar la intervención a clasificación, solicitud, contratación, pago u orden. Requieren reconciliación separada antes de producción o venta.

## Fronteras

Sin IA, pagos, correo o SMS reales. Sin publicación. Sin cambios en One Page.
