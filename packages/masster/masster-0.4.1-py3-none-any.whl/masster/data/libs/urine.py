#!/usr/bin/env python3
"""
Simple XML -> CSV parser for urine metabolites.

Produces `masster/data/libs/urine_metabolites.csv` with columns:
  name,smiles,inchikey,formula,db_id,db

Usage:
  uv run python masster/data/libs/urine.py [path/to/urine_metabolites.xml]

If no argument is given the script uses masster/data/libs/urine_metabolites.xml
"""
from __future__ import annotations

import csv
import sys
import time
from pathlib import Path
import xml.etree.ElementTree as ET
import requests
from urllib.parse import quote

try:
    from rdkit import Chem
except Exception:
    Chem = None


# Determine repo root (three levels up: .../masster/data/libs -> repo root)
WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_XML = WORKSPACE_ROOT / 'masster' / 'data' / 'libs' / 'urine_metabolites.xml'
OUT_CSV = WORKSPACE_ROOT / 'masster' / 'data' / 'libs' / 'urine_metabolites.csv'


def local(tag: str) -> str:
    return tag.split('}')[-1] if tag else ''


NAME_KEYS = {'name', 'approved_name', 'primary_name', 'common_name', 'metabolite_name', 'accession'}
FORMULA_KEYS = {'formula', 'chemical_formula', 'molecular_formula'}
SMILES_KEYS = {'smiles', 'canonical_smiles', 'isomeric_smiles'}
INCHIKEY_KEYS = {'inchikey', 'inchi_key', 'standard_inchikey'}
INCHI_KEYS = {'inchi', 'standard_inchi'}
PUBCHEM_KEYS = {'pubchem_compound_id', 'pubchem_cid'}


def find_first_text(elem, candidates):
    for child in elem.iter():
        t = child.text
        if not t:
            continue
        if local(child.tag).lower() in candidates:
            s = t.strip()
            if s:
                return s
    return ''


def find_name(elem):
    """Find the primary name for a record, ignoring synonym lists.

    Priority: name, approved_name, primary_name, common_name, metabolite_name, accession
    """
    priority = ['name', 'approved_name', 'primary_name', 'common_name', 'metabolite_name', 'accession']
    for key in priority:
        for child in elem.iter():
            if local(child.tag).lower() == key:
                t = child.text
                if t:
                    s = t.strip()
                    if s:
                        return s
    return ''


def inchi_to_smiles(inchi_text: str) -> str:
    if not inchi_text or Chem is None:
        return ''
    try:
        mol = Chem.MolFromInchi(inchi_text, sanitize=False)
        if mol is None:
            mol = Chem.MolFromInchi(inchi_text)
        if mol is None:
            return ''
        try:
            Chem.SanitizeMol(mol)
        except Exception:
            pass
        return Chem.MolToSmiles(mol, isomericSmiles=True)
    except Exception:
        return ''


def canonicalize_smiles(smiles_str: str) -> str:
    """
    Canonicalize SMILES string using RDKit.
    
    Args:
        smiles_str: Input SMILES string
        
    Returns:
        Canonical SMILES string, or original string if canonicalization fails
    """
    if not smiles_str or not smiles_str.strip() or Chem is None:
        return smiles_str
    
    try:
        mol = Chem.MolFromSmiles(smiles_str, sanitize=True)
        if mol is None:
            return smiles_str
        
        # Generate canonical SMILES with isomeric information
        canonical_smiles = Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
        return canonical_smiles
        
    except Exception:
        # If canonicalization fails, return the original SMILES
        return smiles_str


def query_pubchem_by_inchikey(inchikey: str, max_retries: int = 3, delay: float = 0.2) -> str:
    """Query PubChem for compound ID using InChI key.
    
    Args:
        inchikey: The InChI key to search for
        max_retries: Maximum number of retry attempts
        delay: Delay between requests in seconds
        
    Returns:
        PubChem compound ID as string, or empty string if not found
    """
    if not inchikey or not inchikey.strip():
        return ''
    
    # Clean the InChI key
    inchikey = inchikey.strip()
    
    # PubChem REST API URL for searching by InChI key
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/{quote(inchikey)}/cids/JSON"
    
    for attempt in range(max_retries):
        try:
            time.sleep(delay)  # Rate limiting
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'IdentifierList' in data and 'CID' in data['IdentifierList']:
                    cids = data['IdentifierList']['CID']
                    if cids:
                        return str(cids[0])  # Return the first CID
            elif response.status_code == 404:
                # Not found in PubChem
                return ''
            else:
                # Other error, might retry
                if attempt < max_retries - 1:
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
                    continue
                    
        except requests.RequestException:
            if attempt < max_retries - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
                continue
        except Exception:
            # JSON parsing error or other unexpected error
            break
            
    return ''


def parse_and_write(xml_path: Path, out_csv: Path) -> tuple[int, int, int, int, int]:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with_smiles = 0
    with_inchikey = 0
    with_pubchem_id = 0
    existing_pubchem_ids = 0

    with out_csv.open('w', encoding='utf-8', newline='') as outf:
        writer = csv.DictWriter(outf, fieldnames=['name', 'smiles', 'inchikey', 'formula', 'db_id', 'db'])
        writer.writeheader()

        context = ET.iterparse(str(xml_path), events=('end',))
        for event, elem in context:
            tag = local(elem.tag).lower()
            
            # Only process actual metabolite entries (root level compounds)
            if tag == 'metabolite':
                name = find_name(elem)
                formula = find_first_text(elem, FORMULA_KEYS)
                
                # Only generate rows for entries that have a formula
                if not formula:
                    elem.clear()
                    continue
                    
                smiles = find_first_text(elem, SMILES_KEYS)
                inchikey = find_first_text(elem, INCHIKEY_KEYS)
                inchi = find_first_text(elem, INCHI_KEYS)
                existing_pubchem_id = find_first_text(elem, PUBCHEM_KEYS)

                if not smiles:
                    for ch in elem.iter():
                        if ch.text and 'smiles' in local(ch.tag).lower():
                            s = ch.text.strip()
                            if s:
                                smiles = s
                                break

                if not inchikey:
                    for ch in elem.iter():
                        if ch.text and 'inchikey' in local(ch.tag).lower():
                            s = ch.text.strip()
                            if s:
                                inchikey = s
                                break

                if not smiles and inchi:
                    smi = inchi_to_smiles(inchi)
                    if smi:
                        smiles = smi

                # Determine database ID - check XML first, then query PubChem if needed
                db_id = ''
                db = ''
                if existing_pubchem_id:
                    # Use existing PubChem ID from XML
                    db_id = f"CID:{existing_pubchem_id}"
                    db = 'pubchem'
                    with_pubchem_id += 1
                    existing_pubchem_ids += 1
                    print(f"Processing {total + 1}: Found existing PubChem CID for {name or 'Unknown'}: {existing_pubchem_id}")
                elif inchikey:
                    # Query PubChem only if no existing ID
                    print(f"Processing {total + 1}: Querying PubChem for {name or 'Unknown'} ({inchikey[:14]}...)...")
                    pubchem_id = query_pubchem_by_inchikey(inchikey)
                    if pubchem_id:
                        db_id = f"CID:{pubchem_id}"
                        db = 'pubchem'
                        with_pubchem_id += 1
                        print(f"  -> Found CID: {pubchem_id}")
                    else:
                        print(f"  -> No PubChem match found")

                # Canonicalize SMILES if present
                if smiles:
                    smiles = canonicalize_smiles(smiles)

                # Write the row for this metabolite
                writer.writerow({
                    'name': name, 
                    'smiles': smiles, 
                    'inchikey': inchikey, 
                    'formula': formula,
                    'db_id': db_id,
                    'db': db
                })
                total += 1
                if smiles:
                    with_smiles += 1
                if inchikey:
                    with_inchikey += 1

                elem.clear()

    return total, with_smiles, with_inchikey, with_pubchem_id, existing_pubchem_ids


def main(args):
    xml_path = Path(args[0]) if args else DEFAULT_XML
    if not xml_path.exists():
        print(f"XML not found: {xml_path}")
        return 2
    total, with_smiles, with_inchikey, with_pubchem_id, existing_pubchem_ids = parse_and_write(xml_path, OUT_CSV)
    print(f"Wrote {total} rows to {OUT_CSV}")
    print(f"with_smiles={with_smiles} with_inchikey={with_inchikey} with_pubchem_id={with_pubchem_id}")
    print(f"existing_pubchem_ids={existing_pubchem_ids} queried_pubchem_ids={with_pubchem_id - existing_pubchem_ids}")

    # optional quick import check
    try:
        sys.path.insert(0, str(WORKSPACE_ROOT))
        from masster.lib import Lib  # type: ignore
        try:
            lib = Lib(str(OUT_CSV))
            print(f"Successfully imported {len(lib)} library entries from {OUT_CSV}")
        except Exception:
            pass
    except Exception:
        pass

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
