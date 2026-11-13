from copy import deepcopy

from test_postpayment_finalization_v050 import confirmed_order, service


EXPECTED_TITLE = "Solución para gestión de atención por correo"


def test_order_snapshot_carries_canonical_specific_title(tmp_path):
    svc, _ = service(tmp_path)
    _, order = confirmed_order(svc, "TITLE-V051")
    snapshot = order["construction_request_snapshot"]
    assert snapshot["solution_title"] == EXPECTED_TITLE
    assert snapshot["agent"] == "ENDRIAN Especializado"
    assert snapshot["solution_title"] != snapshot["agent"]
    assert snapshot["conversation_evidence_included"] is False


def test_replay_and_reload_keep_one_order_and_same_snapshot(tmp_path):
    svc, _ = service(tmp_path)
    ref, order = confirmed_order(svc, "REPLAY-V051")
    original_id = order["order_id"]
    original_snapshot = deepcopy(order["construction_request_snapshot"])
    replay = svc.order_replay("REPLAY-V051")
    assert replay["same_order"] is True
    assert replay["order"]["order_id"] == original_id
    assert replay["order"]["construction_request_snapshot"] == original_snapshot
    archived = svc.archived_order(original_id)
    assert archived["order"]["order_id"] == original_id
    assert archived["order"]["construction_request_snapshot"] == original_snapshot
    assert archived["email_preview"]["sent"] is False
    assert ref == original_snapshot["payment_reference"]


def test_finalize_rotates_public_session_but_keeps_private_order(tmp_path):
    svc, repo = service(tmp_path)
    _, order = confirmed_order(svc, "CLEAN-V051")
    order_id = order["order_id"]
    result = svc.finalize_conversation("CLEAN-V051")
    assert result["ok"] is True
    assert repo.get("CLEAN-V051") is None
    clean = svc.summary("CLEAN-V051")
    assert clean["full_flow"]["state"] == "S0"
    assert clean["history"] == []
    assert clean["full_flow"].get("qa_identity") is None
    assert clean["full_flow"].get("order_qa") is None
    assert svc.archived_order(order_id)["order"]["order_id"] == order_id
