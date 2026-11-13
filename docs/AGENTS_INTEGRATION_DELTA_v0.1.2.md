# ENDRIAN LAB AGENTES — DELTA v0.1.2

## Estado
`QA VISUAL MOBILE CORREGIDO / NO PRODUCCIÓN / SIN DEPLOY / MAIN SIN MODIFICAR`

## Base
- Candidato anterior: `ENDRIAN_LAB_AGENTES_QA_v0.1.1`
- Repositorio base congelado: `72548d8e8a0b58d521a8ec5fc4b02c7cecdbbcd2`
- La corrección se realizó localmente; `main` no fue modificado.

## Único cambio fuente autorizado
Se modificó exclusivamente `frontend/styles.css` para el responsive Mobile:
1. franja QA con wrapping explícito y ancho seguro;
2. `Explorar agentes` en flujo normal, separado del saludo inicial;
3. tarjeta `Agente seleccionado` con crecimiento vertical y acción `Cambiar` en fila propia;
4. acciones de ruta apiladas verticalmente;
5. tarjetas del selector con altura automática y copy sin truncamiento;
6. reglas de wrap adicionales para la ficha Mobile.

No se modificaron copy, JavaScript, lógica de selección, backend, esquema, estados, arquitectura ni identificadores.

## Verificación de byte-identidad frente a v0.1.1
Todos los archivos funcionales listados a continuación permanecen byte-identical: frontend JS/HTML, backend `app/`, catálogos/copy y los cuatro SVG de identificadores.

```json
{
  "frontend/app.js": {
    "v0.1.1": "096a2ea4c33b4f7a9f713eb24baff8edd9b303658741929c7eaf30c98439d1d4",
    "v0.1.2": "096a2ea4c33b4f7a9f713eb24baff8edd9b303658741929c7eaf30c98439d1d4",
    "byte_identical": true
  },
  "frontend/index.html": {
    "v0.1.1": "540cfc6c07287a01aa45abbeeea58ece903479ae79a700570b403b7e8d125ffe",
    "v0.1.2": "540cfc6c07287a01aa45abbeeea58ece903479ae79a700570b403b7e8d125ffe",
    "byte_identical": true
  },
  "app/main.py": {
    "v0.1.1": "87f16a0079670c8fd2d2d95ea65707c15fa1b50c3e9d0619b2624f56d146ab3b",
    "v0.1.2": "87f16a0079670c8fd2d2d95ea65707c15fa1b50c3e9d0619b2624f56d146ab3b",
    "byte_identical": true
  },
  "app/config.py": {
    "v0.1.1": "fad9e2be88e10313a2f88e4f2910bd9c2a167b5533a0248f36299b575071a9f7",
    "v0.1.2": "fad9e2be88e10313a2f88e4f2910bd9c2a167b5533a0248f36299b575071a9f7",
    "byte_identical": true
  },
  "app/service.py": {
    "v0.1.1": "a1367c9a8ddfb3952a131a243669dbb14430be04f79222b5bdcaca883861d2ca",
    "v0.1.2": "a1367c9a8ddfb3952a131a243669dbb14430be04f79222b5bdcaca883861d2ca",
    "byte_identical": true
  },
  "app/model_adapter.py": {
    "v0.1.1": "4f6c57b9606d684f11771dbf7c41e62d80a3b8adc13e75c17f58a139af22a60d",
    "v0.1.2": "4f6c57b9606d684f11771dbf7c41e62d80a3b8adc13e75c17f58a139af22a60d",
    "byte_identical": true
  },
  "app/model_schema.py": {
    "v0.1.1": "f9a0bdf589d36c0c6448081fc4a9bed9bb836b23133f8bb19a2008dd27638e67",
    "v0.1.2": "f9a0bdf589d36c0c6448081fc4a9bed9bb836b23133f8bb19a2008dd27638e67",
    "byte_identical": true
  },
  "app/model_signal_policy.py": {
    "v0.1.1": "68d5a9ab1a309982361791be73a4f51e084144bf125c4c82d3d61cb62f989c73",
    "v0.1.2": "68d5a9ab1a309982361791be73a4f51e084144bf125c4c82d3d61cb62f989c73",
    "byte_identical": true
  },
  "app/model_validator.py": {
    "v0.1.1": "88ad3c3b37942653b47f29b39f671ab051fb6e7df965ed453b68dd4c248b3507",
    "v0.1.2": "88ad3c3b37942653b47f29b39f671ab051fb6e7df965ed453b68dd4c248b3507",
    "byte_identical": true
  },
  "app/rate_limit.py": {
    "v0.1.1": "65f0afdd3d9217aefa50250e403ef43f334cd7a353f8adc72080ee5287a8f736",
    "v0.1.2": "65f0afdd3d9217aefa50250e403ef43f334cd7a353f8adc72080ee5287a8f736",
    "byte_identical": true
  },
  "app/safety.py": {
    "v0.1.1": "7a44a145ea59a474e331b37639fb0e41674a2ee72ab699b6b97997b24863e819",
    "v0.1.2": "7a44a145ea59a474e331b37639fb0e41674a2ee72ab699b6b97997b24863e819",
    "byte_identical": true
  },
  "app/security.py": {
    "v0.1.1": "1beda4d9af52b2136d4928b15d7e844a784f4a2166f54513635b9029f89f3cf7",
    "v0.1.2": "1beda4d9af52b2136d4928b15d7e844a784f4a2166f54513635b9029f89f3cf7",
    "byte_identical": true
  },
  "app/session_repository.py": {
    "v0.1.1": "1fd93f8c9463b29f75e591965333b195f2dd3dae806a8981e5dca7ef86b66197",
    "v0.1.2": "1fd93f8c9463b29f75e591965333b195f2dd3dae806a8981e5dca7ef86b66197",
    "byte_identical": true
  },
  "config/agents_catalog.json": {
    "v0.1.1": "bcfd7f14aa55a8b06450f0739c4b5b19a0a281de5e89412602c708082cf48aeb",
    "v0.1.2": "bcfd7f14aa55a8b06450f0739c4b5b19a0a281de5e89412602c708082cf48aeb",
    "byte_identical": true
  },
  "config/ui_copy.json": {
    "v0.1.1": "0855606233061237c457730d2ddcac83d6aa2117a28d4c6094fdcef6c72585b2",
    "v0.1.2": "0855606233061237c457730d2ddcac83d6aa2117a28d4c6094fdcef6c72585b2",
    "byte_identical": true
  },
  "frontend/assets/agents/ENDRIAN_AGENT_ID_AVANZADO.svg": {
    "v0.1.1": "3c4dde3b9c7093065791b6c3394cecac186071934571d799741ccdfd5042b6cb",
    "v0.1.2": "3c4dde3b9c7093065791b6c3394cecac186071934571d799741ccdfd5042b6cb",
    "byte_identical": true
  },
  "frontend/assets/agents/ENDRIAN_AGENT_ID_INTEGRAL.svg": {
    "v0.1.1": "b14372f6e8711f0b39b9c1534433ce137b0b421464efdfec8a21522b006d40f3",
    "v0.1.2": "b14372f6e8711f0b39b9c1534433ce137b0b421464efdfec8a21522b006d40f3",
    "byte_identical": true
  },
  "frontend/assets/agents/ENDRIAN_AGENT_ID_PROFESIONAL.svg": {
    "v0.1.1": "8e7904584a4f55fb1457e27d020bac574f709f3f856d5f41206232124fc5065f",
    "v0.1.2": "8e7904584a4f55fb1457e27d020bac574f709f3f856d5f41206232124fc5065f",
    "byte_identical": true
  },
  "frontend/assets/agents/ENDRIAN_AGENT_ID_PREMIUM.svg": {
    "v0.1.1": "1edf6af1656ec4e40a82e35917beebd42ae17d0a2aefe1bd774d152e8b89110b",
    "v0.1.2": "1edf6af1656ec4e40a82e35917beebd42ae17d0a2aefe1bd774d152e8b89110b",
    "byte_identical": true
  }
}
```

## QA
- `pytest -q` con `PYTHONDONTWRITEBYTECODE=1`: **36/36 PASS**.
- Nuevos tests específicos: `tests/test_agents_mobile_visual_contract_v012.py`.
- Verificación específica de colisión/recorte: `qa_results/mobile_visual_collision_checks_v0.1.2.json`.
- No se detectó una duplicación real del wordmark en el HTML: el header contiene una sola referencia al SVG de ENDRIAN; `LABORATORIO` es una etiqueta separada de la base vigente.

## Evidencia Mobile 390×844
- `MOBILE_SELECTOR_COMPLETE_390x844.png`
- `MOBILE_DETAIL_AVANZADO_390x844_v012.png`
- `MOBILE_AFTER_TALK_WITH_ENDRIAN_390x844.png`
- `MOBILE_ROUTE_STACKED_ACTIONS_390x844.png`
- `MOBILE_IDENTIFIERS_ALL_390x844.png`

## Evidencia Desktop de encabezado
- `DESKTOP_HEADER_WORDMARK_SINGLE_1440x900.png`
- `DESKTOP_IDENTIFIERS_ALL_1440x900.png`
