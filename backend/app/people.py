"""Registro de pessoas (estrategistas e analistas) e resolução a partir do
campo `Responsável` (owner), que pode vir como email ou nome.
"""

from __future__ import annotations

import unicodedata

ESTRATEGISTAS: list[str] = [
    "Erika Miranda",
    "Gerson",
    "Anna Laura",
    "Eline",
    "Thadeu",
    "Diogo",
]

ANALISTAS: list[str] = [
    "Anna Laura",
    "Tovani",
    "Joao",
    "Leandro",
]

# Apelidos explícitos: chave normalizada (email completo, prefixo de email ou
# nome) -> nome canônico da pessoa. Estenda conforme novos responsáveis aparecem.
ALIASES: dict[str, str] = {
    "tovani@dextro.com.br": "Tovani",
    "tovani": "Tovani",
    "erika": "Erika Miranda",
    "erika miranda": "Erika Miranda",
    "joao": "Joao",
    "joão": "Joao",
    "anna laura marques": "Anna Laura",
    "annacarvalho@hotmail.com": "Anna Laura",
    "laura@cardosogestao.com.br": "Anna Laura",
    "laura@dextro.com.br": "Anna Laura",
}


def normalize(text: str | None) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8")
    return text.lower().strip()


def _canonical_lookup() -> dict[str, str]:
    """Mapa normalizado -> nome canônico, cobrindo nomes completos, primeiro
    nome e apelidos."""
    lookup: dict[str, str] = {}
    for name in set(ESTRATEGISTAS) | set(ANALISTAS):
        norm = normalize(name)
        lookup[norm] = name
        first = norm.split(" ")[0]
        lookup.setdefault(first, name)
    for alias, canonical in ALIASES.items():
        lookup[normalize(alias)] = canonical
    return lookup


_LOOKUP = _canonical_lookup()


def resolve_person(owner: str | None) -> str | None:
    """Resolve um valor de `owner` (email ou nome) para o nome canônico de uma
    pessoa conhecida, ou None se não for classificável."""
    norm = normalize(owner)
    if not norm:
        return None
    if norm in _LOOKUP:
        return _LOOKUP[norm]
    # tenta o prefixo do email
    if "@" in norm:
        prefix = norm.split("@")[0]
        if prefix in _LOOKUP:
            return _LOOKUP[prefix]
        first = prefix.split(".")[0]
        if first in _LOOKUP:
            return _LOOKUP[first]
    # tenta o primeiro nome
    first = norm.split(" ")[0]
    if first in _LOOKUP:
        return _LOOKUP[first]
    return None


def person_roles(name: str | None) -> list[str]:
    """Papéis de uma pessoa canônica."""
    roles: list[str] = []
    if name is None:
        return roles
    if name in ESTRATEGISTAS:
        roles.append("estrategista")
    if name in ANALISTAS:
        roles.append("analista")
    return roles


def owners_for_person(name: str) -> list[str]:
    """Retorna os apelidos/aliases normalizados que resolvem para a pessoa.
    Útil para construir filtros sobre o campo owner."""
    result: set[str] = set()
    target = normalize(name)
    for key, canonical in _LOOKUP.items():
        if normalize(canonical) == target:
            result.add(key)
    return sorted(result)


def list_estrategistas() -> list[str]:
    return list(ESTRATEGISTAS)


def list_analistas() -> list[str]:
    return list(ANALISTAS)
