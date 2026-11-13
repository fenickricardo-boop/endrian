# ENDRIAN LAB FULL FLOW QA — delta v0.2.1

## Estado
`CORRECCIÓN VISUAL LOCALIZADA / MOBILE HEADER / QA LOCAL / NO PRODUCCIÓN / SIN DEPLOY`

## Fuente exacta
- Fuente: `ENDRIAN_LAB_FULL_FLOW_QA_v0.2.zip`
- SHA-256 verificado: `1928dedc633339747fea66511c368470b6d72d99ff6170bc4635db4c457c57dc`
- El ZIP fuente permaneció inmutable.

## Única corrección funcional/visual
Se modificó únicamente `frontend/styles.css` para que, en Mobile (`max-width:900px`), el header sticky tenga una superficie completamente opaca y un stacking context propio. La corrección evita que el contenido desplazado quede visible, cortado o visualmente confundido por debajo del header.

Propiedades añadidas al header Mobile:
- `background:#000e19` opaco;
- `background-image:none`;
- `isolation:isolate`;
- separación visual mediante `box-shadow`;
- pseudo-superficie `::before` opaca, contenida dentro del header.

No se modificaron `frontend/index.html`, `frontend/app.js`, `app/**`, `PaymentGate`, rutas S0–S8/SH, agentes, identificadores, copy UI, selección ni persistencia.

## QA
- `pytest -q`: **60/60 PASS**.
- QA Chromium Mobile 390×844 posterior a scroll de 620 px: **PASS**.
  - header top = 0 px;
  - header bottom = 68 px;
  - `position: sticky`;
  - background computado = `rgb(0, 14, 25)` (opaco);
  - punto central del header resuelve a `HEADER_OR_DESCENDANT`;
  - `scrollWidth = innerWidth = 390`;
  - overflow horizontal = `false`.
- Evidencia: `evidence/full_flow/MOBILE_HEADER_SCROLL_OCCLUSION_390x844.png`.
- Resultado estructurado: `qa_results/full_flow/MOBILE_HEADER_QA_v0.2.1.json`.

## Lanzador local
`START_LAB_QA.bat` y `start_lab_qa.py` permanecen byte-identical a v0.2. Se verificó el lanzador Python subyacente: servidor listo, `/health` 200, cierre por Ctrl+C con return code 0 y puerto 8000 liberado. Evidencia: `qa_results/full_flow/LOCAL_LAUNCHER_QA_v0.2.1.json`.

## Entornos externos
GitHub, Railway, staging y producción no fueron accedidos ni modificados.
