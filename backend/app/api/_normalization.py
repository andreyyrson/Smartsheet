"""Normalização de nomes de projeto (department) para labels canônicos."""

from __future__ import annotations

import unicodedata

CANONICAL_PROJECTS: list[str] = [
    "QUADRA",
    "MOVIX",
    "MDS",
    "DALLAS",
    "K SUSHI(BPO)",
    "AYLA",
    "MARELLI",
    "FORMA",
    "POSTO OK",
    "GO PARK",
    "OYAMOTA",
    "MINAFERRO",
    "AMAZÔNIA NA CUIA",
    "DEHON",
    "SOS PASSAGEM",
    "GRUPO MELK",
    "MILANO",
    "TUDO CONVENIÊNCIA",
    "GRUPO LONGO",
    "HPOLI",
    "GRUPO SÃO MIGUEL",
    "FIT4YOU",
    "PREMAZON",
    "DGS",
    "ON SAÚDE",
    "IONPA",
    "SOFINTECH",
    "IT PROTECT",
    "SEMAS",
    "CODEC",
    "BELÉM DIGITAL",
    "SEMEC",
    "JACK GARAGE",
    "OGMO",
    "TPL (ASSESSORIA)",
    "BEZERRA E PENA",
]


def _normalize(text: str | None) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    return text.lower()


def normalize_project_name(raw_name: str | None) -> str:
    """Mapeia um nome bruto de planilha/departamento para um label canônico.

    Faz correspondência ignorando acentos, caixa e parênteses. O primeiro
    canônico encontrado como substring é usado. Caso nenhum seja encontrado,
    retorna 'Outros'.
    """
    if not raw_name:
        return "Outros"
    norm = _normalize(raw_name)
    for canonical in CANONICAL_PROJECTS:
        key = _normalize(canonical)
        # Remove parênteses para busca genérica (ex.: K SUSHI(BPO) -> K SUSHI)
        key_plain = key.split("(")[0].strip()
        if key_plain in norm or key in norm:
            return canonical
    return "Outros"


def aggregate_by_canonical(items: list[tuple[str | None, int]]) -> dict[str, int]:
    """Recebe pares (raw_label, value) e agrega por label canônico."""
    result: dict[str, int] = {}
    for raw, value in items:
        canonical = normalize_project_name(raw)
        result[canonical] = result.get(canonical, 0) + value
    return result
