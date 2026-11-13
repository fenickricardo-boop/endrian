# Guía breve de prueba v0.5.8

1. Extrae el ZIP en una carpeta nueva; no lo ejecutes sobre una versión anterior.
2. En Windows, abre `START_LAB_QA.bat`. En otro sistema, crea el entorno indicado en `README_LOCAL_QA.md` y ejecuta `start_lab_qa.py`.
3. Abre la URL local informada por el launcher.
4. Comprueba el menú: `Volver a ENDRIAN · Servicios · Precios · Contacto · Nueva conversación`.
5. Abre Servicios y revisa las tres fichas completas y el scroll interno.
6. Usa `Volver a la conversación`; verifica que el chat y los datos permanezcan y que el campo del chat reciba el foco.
7. Abre Precios y verifica USD 39, USD 89 y USD 149, sus alcances breves y la nota final.
8. Cambia entre Servicios, Precios y Contacto; solo un panel debe permanecer abierto.
9. Comprueba cierre por X, Escape y backdrop. El foco debe volver al control que abrió el panel.
10. En Contacto, revisa alineación de Correo/País y Prefijo/Número, teléfono vacío/parcial, conservación de datos y Mensaje más alto.
11. Repite en pantalla estrecha mediante herramientas responsive del navegador.

La revisión visual desktop/móvil debe completarse manualmente porque el entorno de construcción no dispuso de un navegador gráfico ejecutable.
