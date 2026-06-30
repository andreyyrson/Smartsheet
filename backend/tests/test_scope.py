from app.sync_service import is_action_sheet, is_in_scope


def test_is_action_sheet():
    assert is_action_sheet("01. Plano de Ação")
    assert is_action_sheet("Plano de ação comercial")
    assert not is_action_sheet("Orçamento 2025")


def test_in_scope_keeps_no_year_and_recent():
    assert is_in_scope("01. Plano de Ação")
    assert is_in_scope("Plano de Ação Vendas 2025")
    assert is_in_scope("Plano de Ação Kick Off 2026")


def test_in_scope_excludes_inativo():
    assert not is_in_scope("(Inativo) Plano de Ação - Posto OK")


def test_in_scope_excludes_old_years():
    assert not is_in_scope("Plano de Ação Vendas e Marketing 2024 RSAL")
    assert not is_in_scope("Plano de Ação 2023")
