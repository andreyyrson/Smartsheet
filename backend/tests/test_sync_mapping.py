from app.sync_service import build_column_mapping, normalize


def test_normalize_removes_accents_and_lowercases():
    assert normalize("Responsável") == "responsavel"
    assert normalize("Plano de Ação") == "plano de acao"
    assert normalize("  Status  ") == "status"


def test_build_column_mapping_maps_known_columns():
    columns = [
        {"id": 1, "title": "Atividade", "type": "TEXT_NUMBER"},
        {"id": 2, "title": "Status", "type": "PICKLIST"},
        {"id": 3, "title": "Responsável", "type": "CONTACT_LIST"},
        {"id": 4, "title": "Prazo", "type": "DATE"},
        {"id": 5, "title": "Concluído", "type": "CHECKBOX"},
        {"id": 6, "title": "Luz", "type": "PICKLIST"},
    ]
    mapping = build_column_mapping(columns)
    assert mapping["title"] == 1
    assert mapping["status"] == 2
    assert mapping["owner"] == 3
    assert mapping["due_date"] == 4
    assert mapping["is_completed"] == 5
    assert mapping["priority"] == 6


def test_build_column_mapping_ignores_unknown_columns():
    columns = [
        {"id": 10, "title": "Custo", "type": "TEXT_NUMBER"},
    ]
    mapping = build_column_mapping(columns)
    assert mapping == {}
