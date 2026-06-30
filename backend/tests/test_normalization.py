from app.api._normalization import (
    CANONICAL_PROJECTS,
    aggregate_by_canonical,
    normalize_project_name,
)


def test_normalize_accent_and_case_insensitive():
    assert normalize_project_name("Plano de Ação PREMAZON 2025") == "PREMAZON"
    assert normalize_project_name("plano de ação milano") == "MILANO"


def test_normalize_with_parentheses():
    assert normalize_project_name("Plano K SUSHI BPO 2025") == "K SUSHI(BPO)"


def test_normalize_returns_outros():
    assert normalize_project_name("01. Plano de Ação MX 01") == "Outros"
    assert normalize_project_name(None) == "Outros"


def test_aggregate_by_canonical():
    items = [
        ("Plano PREMAZON 2025", 10),
        ("PREMAZON Vendas", 5),
        ("Plano de Ação MX", 3),
    ]
    result = aggregate_by_canonical(items)
    assert result["PREMAZON"] == 15
    assert result["Outros"] == 3


def test_all_canonicals_present():
    assert len(CANONICAL_PROJECTS) == 36
