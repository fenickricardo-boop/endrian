import time
from app.session_repository import SessionRepository


def test_session_roundtrip_and_delete(tmp_path):
    repo = SessionRepository(str(tmp_path / "qa.db"), ttl_seconds=60)
    repo.save("S1", {"x":1}, turn_count=2)
    got = repo.get("S1")
    assert got["x"] == 1
    assert got["_repo"]["turn_count"] == 2
    assert repo.increment_turn("S1") == 3
    repo.delete("S1")
    assert repo.get("S1") is None
