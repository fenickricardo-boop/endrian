# Arquitectura QA REV1

```text
Browser (HTML/CSS/JS)
  └─ same-origin HTTP
      └─ FastAPI
          ├─ staging access fail-closed
          ├─ rate limiter IP/session
          ├─ SessionRepository (SQLite + TTL)
          ├─ GuideService
          │   ├─ ModelAdapter
          │   │   ├─ deterministic (default)
          │   │   └─ OpenAI Responses API / Structured Output / store:false
          │   ├─ ModelOutputValidator
          │   ├─ DeterministicModelSignalPolicy
          │   └─ ConversationalGuideQA v0.2
          │       └─ GuideAgentQA control core v0.1
          └─ Static frontend
```

## Frontera de autoridad

El modelo puede proponer una acción lingüística dentro del schema. Cada acción declarada tiene un consumidor explícito. `DRAFT_ORIENTATION` fue retirado porque no tenía consumidor autorizado.

`FLAG_HUMAN_REVIEW` **no escribe el estado directamente**: el output estructurado se valida y después `DeterministicModelSignalPolicy` aplica localmente el estado canónico `REVISIÓN HUMANA REQUERIDA`, invalida artefactos aguas abajo y bloquea orientación/propuesta. La lógica de control `agent_guide/core_v0_1/candidate/guide_agent.py` permanece byte-identical a la fuente auditada.

## Registro en QA

La orientación completa requiere registro según el contrato, pero esta etapa prohíbe PII/registro productivo. `GuideService._qa_ephemeral_register()` utiliza una identidad sintética `QA Session + example.invalid` para atravesar exclusivamente el gate QA.
