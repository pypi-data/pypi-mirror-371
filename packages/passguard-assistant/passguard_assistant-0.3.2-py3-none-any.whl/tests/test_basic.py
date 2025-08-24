
from passguard_assistant import PassGuard, check_strength, suggest_password

def test_strength_and_suggest():
    info = check_strength("password")
    assert isinstance(info, dict)
    pg = PassGuard()
    pw = pg.suggest_password(length=16)
    assert len(pw) >= 16
