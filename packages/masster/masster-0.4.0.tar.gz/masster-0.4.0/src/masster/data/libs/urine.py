#!/usr/bin/env python3
"""
Simple XML -> CSV parser for urine metabolites.

Produces `masster/data/libs/urine_metabolites.csv` with columns:
  name,smiles,inchikey,formula

Usage:
  uv run python masster/data/libs/urine.py [path/to/urine_metabolites.xml]

If no argument is given the script uses masster/data/libs/urine_metabolites.xml
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    from rdkit import Chem
except Exception:
    Chem = None


# Determine repo root (three levels up: .../masster/data/libs -> repo root)
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_XML = WORKSPACE_ROOT / "master" / "data" / "libs" / "urine_metabolites.xml"
OUT_CSV = WORKSPACE_ROOT / "master" / "data" / "libs" / "urine_metabolites.csv"


def local(tag: str) -> str:
    return tag.split("}")[-1] if tag else ""


NAME_KEYS = {
    "name",
    "approved_name",
    "primary_name",
    "common_name",
    "metabolite_name",
    "accession",
}
FORMULA_KEYS = {"formula", "chemical_formula", "molecular_formula"}
SMILES_KEYS = {"smiles", "canonical_smiles", "isomeric_smiles"}
INCHIKEY_KEYS = {"inchikey", "inchi_key", "standard_inchikey"}
INCHI_KEYS = {"inchi", "standard_inchi"}


def find_first_text(elem, candidates):
    for child in elem.iter():
        t = child.text
        if not t:
            continue
        if local(child.tag).lower() in candidates:
            s = t.strip()
            if s:
                return s
    return ""


def find_name(elem):
    """Find the primary name for a record, ignoring synonym lists.

    Priority: name, approved_name, primary_name, common_name, metabolite_name, accession
    """
    priority = [
        "name",
        "approved_name",
        "primary_name",
        "common_name",
        "metabolite_name",
        "accession",
    ]
    for key in priority:
        for child in elem.iter():
            if local(child.tag).lower() == key:
                t = child.text
                if t:
                    s = t.strip()
                    if s:
                        return s
    return ""


def inchi_to_smiles(inchi_text: str) -> str:
    if not inchi_text or Chem is None:
        return ""
    try:
        mol = Chem.MolFromInchi(inchi_text, sanitize=False)
        if mol is None:
            mol = Chem.MolFromInchi(inchi_text)
        if mol is None:
            return ""
        try:
            Chem.SanitizeMol(mol)
        except Exception:
            pass
        return Chem.MolToSmiles(mol, isomericSmiles=True)
    except Exception:
        return ""


def parse_and_write(xml_path: Path, out_csv: Path) -> tuple[int, int, int]:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with_smiles = 0
    with_inchikey = 0

    with out_csv.open("w", encoding="utf-8", newline="") as outf:
        writer = csv.DictWriter(
            outf,
            fieldnames=["name", "smiles", "inchikey", "formula"],
        )
        writer.writeheader()

        context = ET.iterparse(str(xml_path), events=("end",))
        for event, elem in context:
            tag = local(elem.tag).lower()
            has_candidate = any(
                local(ch.tag).lower()
                in NAME_KEYS | FORMULA_KEYS | SMILES_KEYS | INCHIKEY_KEYS
                for ch in elem
            )
            if tag in {"metabolite", "compound", "entry", "record"} or has_candidate:
                name = find_name(elem)
                formula = find_first_text(elem, FORMULA_KEYS)
                smiles = find_first_text(elem, SMILES_KEYS)
                inchikey = find_first_text(elem, INCHIKEY_KEYS)
                inchi = find_first_text(elem, INCHI_KEYS)

                if not smiles:
                    for ch in elem.iter():
                        if ch.text and "smiles" in local(ch.tag).lower():
                            s = ch.text.strip()
                            if s:
                                smiles = s
                                break

                if not inchikey:
                    for ch in elem.iter():
                        if ch.text and "inchikey" in local(ch.tag).lower():
                            s = ch.text.strip()
                            if s:
                                inchikey = s
                                break

                if not smiles and inchi:
                    smi = inchi_to_smiles(inchi)
                    if smi:
                        smiles = smi

                if name or formula or smiles or inchikey:
                    writer.writerow(
                        {
                            "name": name,
                            "smiles": smiles,
                            "inchikey": inchikey,
                            "formula": formula,
                        },
                    )
                    total += 1
                    if smiles:
                        with_smiles += 1
                    if inchikey:
                        with_inchikey += 1

                elem.clear()

    return total, with_smiles, with_inchikey


def main(args):
    xml_path = Path(args[0]) if args else DEFAULT_XML
    if not xml_path.exists():
        print(f"XML not found: {xml_path}")
        return 2
    total, with_smiles, with_inchikey = parse_and_write(xml_path, OUT_CSV)
    print(f"Wrote {total} rows to {OUT_CSV}")
    print(f"with_smiles={with_smiles} with_inchikey={with_inchikey}")

    # optional quick import check
    try:
        sys.path.insert(0, str(WORKSPACE_ROOT))
        from master.lib import Lib  # type: ignore

        try:
            lib = Lib(str(OUT_CSV))
            print(f"Successfully imported {len(lib)} library entries from {OUT_CSV}")
        except Exception:
            pass
    except Exception:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
