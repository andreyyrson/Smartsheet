from app.people import person_roles, resolve_person


def test_resolve_person_by_email():
    assert resolve_person("tovani@dextro.com.br") == "Tovani"


def test_resolve_person_by_name():
    assert resolve_person("Erika Miranda") == "Erika Miranda"
    assert resolve_person("erika") == "Erika Miranda"


def test_resolve_person_unknown():
    assert resolve_person("ovidios@uol.com.br") is None
    assert resolve_person(None) is None
    assert resolve_person("") is None


def test_person_roles_multiple():
    roles = person_roles("Anna Laura")
    assert "estrategista" in roles
    assert "analista" in roles


def test_person_roles_single():
    assert person_roles("Tovani") == ["analista"]
    assert person_roles("Gerson") == ["estrategista"]
