from __future__ import annotations
from typing import Any, Dict

HUMAN_REVIEW_STATE = "REVISIÓN HUMANA REQUERIDA"


class DeterministicModelSignalPolicy:
    """Consumes validated model signals without granting the model state authority.

    The model may *request* review. This deterministic policy decides the canonical
    transition and applies the fail-safe effects. The preserved v0.1 control core is
    not modified.
    """

    @staticmethod
    def apply_human_review(session: Any, proposal: Dict[str, Any]) -> Dict[str, Any]:
        reason = str(proposal.get("human_review_reason") or "").strip()
        if not reason:
            raise ValueError("validated FLAG_HUMAN_REVIEW missing reason")
        session.human_review_reason = f"SEÑAL VALIDADA DEL MODELO: {reason}"
        session.state = HUMAN_REVIEW_STATE
        # Any previously prepared downstream artifacts are invalidated.
        session.orientation = {}
        session.classification = None
        session.proposal = {}
        session.payment = {"status": "NO INICIADO", "simulation": True}
        session.order = None
        session.matrix = None
        session.trace.append({
            "event": "HUMAN_REVIEW_REQUIRED",
            "reference": "ENDRIAN_AGENTE_GUIA_CONTRATO_FUNCIONAL_MVP_v1.1.docx · §12 Revisión humana y reunión como excepción",
            "source": "MODEL_SIGNAL_VALIDATED_DETERMINISTIC_POLICY",
        })
        return {
            "event": "HUMAN_REVIEW_REQUIRED",
            "state": session.state,
            "simulation": True,
            "message": "Tu caso necesita una revisión más específica. Conservaremos lo conversado sin cerrar precio, pago ni producción.",
            "data": {"reason": session.human_review_reason},
        }
