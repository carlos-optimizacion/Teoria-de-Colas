#!/usr/bin/env python3
"""Valida el paquete de skill con Python stdlib."""
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/"SKILL.md"
FILES=("references/architecture.md","references/acceptance-matrix.md",
       "references/github-render.md","assets/hito-template.md","scripts/validate_skill.py")


def validate():
    errors=[]
    if not SKILL.is_file():
        return ["SKILL.md no existe"]
    content=SKILL.read_text(encoding="utf-8")
    front=re.match(r"\A---\s*\n(.*?)\n---\s*\n",content,re.S)
    if not front:
        return ["El bloque YAML inicial falta o es inválido"]
    meta=dict(line.split(": ",1) for line in front.group(1).splitlines() if ": " in line)
    if meta.get("name")!="astalanka-opt-dev":errors.append("name incorrecto")
    if len(meta.get("description",""))<50:errors.append("description insuficiente")
    for rel in FILES:
        p=ROOT/rel
        if not p.is_file() or p.stat().st_size<10:errors.append(f"Recurso faltante: {rel}")
        if rel not in content:errors.append(f"Recurso no citado: {rel}")
    if len(content)>20000:errors.append("SKILL.md demasiado extenso")
    for token in ("-----BEGIN PRIVATE KEY-----","ghp_","github_pat_","sk-proj-"):
        if token in content:errors.append("Posible secreto en SKILL.md")
    return errors


if __name__=="__main__":
    errors=validate()
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("OK: ASTALANKA skill validada (manifest + referencias)")
