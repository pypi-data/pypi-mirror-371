"""Generate a cleaned CSV of central-carbon metabolism compounds.

Workflow:
- Use a curated list of central-carbon/metabolism-relevant names (glycolysis, TCA, PPP,
    amino acids, common organic acids, nucleotides, fatty acids, cofactors, sugars).
- Query PubChem's PUG-REST for MolecularFormula, CanonicalSMILES and InChIKey for each name
    with retries and basic name normalization to improve matching.
- Save results to `masster/data/examples/ccm.csv`.
- Test loading with `masster.lib.Lib.import_csv`.

This is a best-effort programmatic lookup; ambiguous names may not resolve (those rows will
have empty Formula/SMILES/InChIKey). For authoritative lists, prefer curated databases
(e.g., HMDB, KEGG) and bulk downloads.
"""

from __future__ import annotations

import csv
import sys
import time
import os
import re
from urllib.parse import quote

try:
    import requests
except Exception:
    requests = None

try:
    from rdkit import Chem
except Exception:
    Chem = None

try:
    from rdkit import Chem
except Exception:
    Chem = None


CCM_METABOLITES = [
    # Central carbon metabolism core (glycolysis, TCA, PPP, gluconeogenesis, pyruvate metabolism)
    "Glucose",
    "Glucose-6-phosphate",
    "Fructose-6-phosphate",
    "Fructose-1,6-bisphosphate",
    "Glyceraldehyde-3-phosphate",
    "Dihydroxyacetone phosphate",
    "3-Phosphoglycerate",
    "2-Phosphoglycerate",
    "Phosphoenolpyruvate",
    "Pyruvate",
    "Lactate",
    "Acetyl-CoA",
    "Citric acid",
    "Isocitrate",
    "Alpha-ketoglutaric acid",
    "Succinyl-CoA",
    "Succinic acid",
    "Fumaric acid",
    "Malic acid",
    "Oxaloacetic acid",
    "Ribose-5-phosphate",
    "Ribulose-5-phosphate",
    "Sedoheptulose-7-phosphate",
    "Erythrose-4-phosphate",
    "Sedoheptulose-1,7-bisphosphate",
    "Glycerol-3-phosphate",
    "Glycerate",
    "Pentose",
    "Acetaldehyde",
    "Acetic acid",

    # Proteinogenic amino acids (20 standard)
    "Alanine",
    "Arginine",
    "Asparagine",
    "Aspartic acid",
    "Cysteine",
    "Glutamic acid",
    "Glutamine",
    "Glycine",
    "Histidine",
    "Isoleucine",
    "Leucine",
    "Lysine",
    "Methionine",
    "Phenylalanine",
    "Proline",
    "Serine",
    "Threonine",
    "Tryptophan",
    "Tyrosine",
    "Valine",
    # Additional amino acid related metabolites
    "Ornithine",
    "Citrulline",
    "Homocysteine",
    "S-adenosylmethionine",
    "S-adenosylhomocysteine",

    # Common organic acids / intermediates & related small metabolites
    "Formic acid",
    "Propionic acid",
    "Butyric acid",
    "Malonic acid",
    "2-Hydroxyglutarate",
    "3-Hydroxybutyrate",
    "Acetoacetate",
    "Beta-hydroxybutyrate",
    "Pyruvic acid",
    "Lactic acid",

    # Fatty acids (common)
    "Myristic acid",
    "Palmitic acid",
    "Stearic acid",
    "Palmitoleic acid",
    "Oleic acid",
    "Linoleic acid",
    "Alpha-linolenic acid",
    "Arachidonic acid",

    # Nucleobases and nucleosides
    "Adenine",
    "Guanine",
    "Cytosine",
    "Thymine",
    "Uracil",
    "Adenosine",
    "Guanosine",
    "Cytidine",
    "Uridine",

    # Nucleotides (mono/di/tri)
    "AMP",
    "ADP",
    "ATP",
    "GMP",
    "GDP",
    "GTP",
    "CMP",
    "CDP",
    "CTP",
    "UMP",
    "UDP",
    "UTP",

    # Cofactors / common metabolites
    "NAD+",
    "NADH",
    "NADP+",
    "NADPH",
    "FAD",
    "FMN",
    "Coenzyme A",
    "Pantothenic acid",
    "Riboflavin",
    "Niacin",

    # Sugar and sugar derivatives
    "Fructose",
    "Mannose",
    "Mannose-6-phosphate",
    "Ribose",
    "Glucosamine",
    "N-acetylglucosamine",

    # Other common metabolites
    "Choline",
    "Betaine",
    "Carnitine",
    "Phosphocholine",
    "Glycerol",
    "Sorbitol",
    "Inositol",
    "Cholesterol",
    "Pantothenate",
]


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


def fetch_from_pubchem(name: str):
    """Fetch formula, smiles, inchikey, and CID from PubChem by compound name.

    Uses basic normalization and retries with exponential backoff. Returns
    (formula, smiles, inchikey, cid) or (None, None, None, None) on failure.
    """
    props = (None, None, None, None)

    def normalize_name(n: str) -> str:
        if not n:
            return n
        s = n
        s = re.sub(r"\(.*?\)", "", s)  # remove parentheses
        s = s.replace("+", "+")
        s = s.replace("–", "-")
        s = re.sub(r"\s+", " ", s).strip()
        # common abbreviation mapping
        mapping = {
            "AMP": "Adenosine monophosphate",
            "ADP": "Adenosine diphosphate",
            "ATP": "Adenosine triphosphate",
            "GMP": "Guanosine monophosphate",
            "GDP": "Guanosine diphosphate",
            "GTP": "Guanosine triphosphate",
            "NAD+": "Nicotinamide adenine dinucleotide",
            "NADH": "Nicotinamide adenine dinucleotide (reduced)",
            "CoA": "Coenzyme A",
        }
        up = s.upper()
        if up in mapping:
            return mapping[up]
        return s

    query = normalize_name(name)

    def try_query(q: str):
        url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{quote(q)}/property/"
            + "MolecularFormula,CanonicalSMILES,InChI,InChIKey/JSON"
        )
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.json()
        except Exception:
            return None
        return None

    def try_query_with_cid(q: str):
        """Query compound by name and get CID along with properties."""
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{quote(q)}/cids/JSON"
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                j = r.json()
                if 'IdentifierList' in j and 'CID' in j['IdentifierList']:
                    cids = j['IdentifierList']['CID']
                    if cids:
                        return cids[0]  # Return the first CID
        except Exception:
            return None
        return None

    def try_query_inchikey(ik: str):
        url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/{quote(ik)}/property/"
            + "MolecularFormula,CanonicalSMILES,InChI,InChIKey/JSON"
        )
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.json()
        except Exception:
            return None
        return None

    def try_query_cid(cid: int):
        url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/property/"
            + "MolecularFormula,CanonicalSMILES,InChI,InChIKey/JSON"
        )
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                return r.json()
        except Exception:
            return None
        return None

    def try_get_cids_from_inchikey(ik: str):
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/{quote(ik)}/cids/JSON"
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                j = r.json()
                if 'IdentifierList' in j and 'CID' in j['IdentifierList']:
                    return j['IdentifierList']['CID']
        except Exception:
            return []
        return []

    if requests is None:
        return props

    # exponential backoff attempts
    attempts = 3
    cid = None
    
    for i in range(attempts):
        # First try to get the CID
        if not cid:
            cid = try_query_with_cid(query)
            
        j = try_query(query)
        if j:
            try:
                if "PropertyTable" in j and "Properties" in j["PropertyTable"]:
                    p = j["PropertyTable"]["Properties"][0]
                    mf = p.get("MolecularFormula")
                    sm = p.get("CanonicalSMILES")
                    inchi = p.get("InChI")
                    ik = p.get("InChIKey")
                    # if SMILES missing, try a lookup by InChIKey (dedicated endpoint)
                    if not sm and ik:
                        j2 = try_query_inchikey(ik)
                        if j2 and "PropertyTable" in j2 and "Properties" in j2["PropertyTable"]:
                            p2 = j2["PropertyTable"]["Properties"][0]
                            sm = p2.get("CanonicalSMILES") or sm
                            inchi = inchi or p2.get("InChI")

                    # if still no SMILES but InChI present and RDKit available, try InChI -> SMILES conversion
                    if not sm and inchi and Chem is not None:
                        try:
                            m = Chem.MolFromInchi(inchi)
                            if m is not None:
                                sm = Chem.MolToSmiles(m, isomericSmiles=True)
                        except Exception:
                            pass

                    # if still no SMILES, try fetching CIDs from InChIKey and query a CID record
                    if not sm and ik:
                        cids = try_get_cids_from_inchikey(ik)
                        for cid_from_ik in (cids or [])[:5]:
                            if not cid:  # Only set CID if we don't have one yet
                                cid = cid_from_ik
                            j3 = try_query_cid(cid_from_ik)
                            if j3 and "PropertyTable" in j3 and "Properties" in j3["PropertyTable"]:
                                p3 = j3["PropertyTable"]["Properties"][0]
                                sm = p3.get("CanonicalSMILES") or sm
                                if sm:
                                    break

                    return (mf, sm, ik, cid)
            except Exception:
                pass
        time.sleep(1 + 2 ** i)

    # final fallback: try raw name without normalization
    if not cid:
        cid = try_query_with_cid(name)
        
    j = try_query(name)
    if j and "PropertyTable" in j and "Properties" in j["PropertyTable"]:
        p = j["PropertyTable"]["Properties"][0]
        return (p.get("MolecularFormula"), p.get("CanonicalSMILES"), p.get("InChIKey"), cid)

    return props


def generate_csv(out_path: str = "ccm.csv"):
    rows = []
    for name in CCM_METABOLITES:
        formula, smiles, inchikey, cid = (None, None, None, None)
        if requests is not None:
            formula, smiles, inchikey, cid = fetch_from_pubchem(name)

        # Neutralize charged molecular formulas (e.g., trailing +, -, 2+, 3-)
        # by adjusting the hydrogen count accordingly and removing the explicit charge.
        def neutralize_formula(fmt: str) -> str:
            if not fmt:
                return fmt
            s = fmt.strip()
            # normalize common unicode superscripts (²³¹⁺⁻) to ascii
            sup_map = str.maketrans({
                "²": "2",
                "³": "3",
                "¹": "1",
                "⁺": "+",
                "⁻": "-",
            })
            s = s.translate(sup_map)
            # Remove enclosing brackets if present, e.g. [C6H5O7]2-
            if s.startswith("[") and s.endswith("]"):
                s = s[1:-1]
            # strip trailing punctuation or separators (commas, periods, parentheses)
            s = s.rstrip(" \t\n\r,.;)")
            # detect trailing charge formats e.g. '2-', '-','3+','+','-2','+2' optionally with whitespace
            m = re.search(r"([+-]?\d+[+-]?|[+-])\s*$", s)
            if not m:
                return fmt

            charge_str = m.group(1)
            base = s[: m.start(1)].strip()
            # determine magnitude and sign for patterns like '2-' or '-2' or '+2' or '3+'
            sign = 1
            mag = 1
            if charge_str[0] in '+-':
                # formats like '-2' or '+2' or '-' or '+'
                sign = -1 if charge_str[0] == '-' else 1
                mag = int(charge_str[1:]) if len(charge_str) > 1 and charge_str[1:].isdigit() else 1
            elif charge_str[-1] in '+-':
                # formats like '2-' or '3+'
                sign = -1 if charge_str[-1] == '-' else 1
                mag = int(charge_str[:-1]) if charge_str[:-1].isdigit() else 1

            # parse element counts from base formula
            tokens = re.findall(r"([A-Z][a-z]?)(\d*)", base)
            if not tokens:
                # if parsing failed, return base without charge marker
                return base

            elems = []
            counts: dict[str, int] = {}
            for el, num in tokens:
                counts[el] = counts.get(el, 0) + (int(num) if num else 1)
                if el not in elems:
                    elems.append(el)

            # adjust hydrogens: negative charge -> add H (protonation),
            # positive charge -> remove H (deprotonation)
            if sign == -1:
                counts["H"] = counts.get("H", 0) + mag
                if "H" not in elems:
                    # place H after C if present, else at beginning
                    if "C" in elems:
                        idx = elems.index("C") + 1
                        elems.insert(idx, "H")
                    else:
                        elems.insert(0, "H")
            else:
                if "H" in counts:
                    counts["H"] = counts.get("H", 0) - mag
                    if counts["H"] <= 0:
                        counts.pop("H", None)
                        if "H" in elems:
                            elems.remove("H")
                else:
                    # can't remove hydrogens we don't have; leave base unchanged
                    pass

            # rebuild formula preserving original element order
            parts = []
            for el in elems:
                if el in counts:
                    n = counts[el]
                    parts.append(f"{el}{n if n!=1 else ''}")
            new_formula = "".join(parts)
            return new_formula

        try:
            formula_neutral = neutralize_formula(formula) if formula else formula
            if formula and formula_neutral != formula:
                # prefer the neutralized formula in the output
                formula = formula_neutral
        except Exception:
            # if anything goes wrong, keep original formula
            pass

        # neutralize SMILES using RDKit when available
        def neutralize_smiles(smiles_str: str) -> str:
            if not smiles_str or Chem is None:
                return smiles_str
            try:
                m = Chem.MolFromSmiles(smiles_str, sanitize=True)
                if m is None:
                    return smiles_str
                # Work on a read-write mol to adjust hydrogens and formal charges
                rw = Chem.RWMol(Chem.AddHs(m))
                to_remove = []
                for a in list(rw.GetAtoms()):
                    idx = a.GetIdx()
                    q = a.GetFormalCharge()
                    if q > 0:
                        # remove up to q hydrogen neighbors (by index)
                        h_neighbors = [nbr.GetIdx() for nbr in a.GetNeighbors() if nbr.GetSymbol() == "H"]
                        remove = h_neighbors[: min(len(h_neighbors), q)]
                        to_remove.extend(remove)
                    elif q < 0:
                        # add -q hydrogens bonded to this atom
                        for _ in range(-q):
                            h = Chem.Atom("H")
                            new_idx = rw.AddAtom(h)
                            rw.AddBond(idx, new_idx, Chem.BondType.SINGLE)
                    # reset formal charge on this atom
                    rw.GetAtomWithIdx(idx).SetFormalCharge(0)

                # remove hydrogen atoms collected, in reverse order so indices stay valid
                for ridx in sorted(set(to_remove), reverse=True):
                    try:
                        rw.RemoveAtom(ridx)
                    except Exception:
                        pass

                newm = rw.GetMol()
                try:
                    Chem.SanitizeMol(newm)
                except Exception:
                    # best effort: continue
                    pass
                # remove explicit Hs to produce a clean canonical SMILES
                try:
                    no_h = Chem.RemoveHs(newm)
                except Exception:
                    no_h = newm
                sm = Chem.MolToSmiles(no_h, isomericSmiles=True)
                return sm
            except Exception:
                return smiles_str

        try:
            smiles = neutralize_smiles(smiles) if smiles else smiles
        except Exception:
            pass
        
        # Canonicalize SMILES after neutralization
        try:
            smiles = canonicalize_smiles(smiles) if smiles else smiles
        except Exception:
            pass
            
        # Format the database ID and database name
        db_id = f"CID:{cid}" if cid else ""
        db = "pubchem" if cid else ""
        
        rows.append({
            "Name": name,
            "Formula": formula or "",
            "SMILES": smiles or "",
            "InChIKey": inchikey or "",
            "db_id": db_id,
            "db": db,
        })

    # Ensure output directory exists (data/libs)
    out_dir = os.path.join('masster', 'data', 'libs')
    os.makedirs(out_dir, exist_ok=True)
    out_path_full = os.path.join(out_dir, os.path.basename(out_path))

    fieldnames = ["Name", "Formula", "SMILES", "InChIKey", "db_id", "db"]
    with open(out_path_full, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} entries to {out_path_full}")
    return out_path_full


def test_load_with_lib(csv_path: str):
    """Try to load the generated CSV using masster.lib.Lib.import_csv."""
    try:
        from masster.lib import Lib
    except Exception as e:
        print(f"Cannot import masster.lib.Lib: {e}")
        return False

    try:
        lib = Lib()
        # import_csv expects a path and optional polarity; use polarity=None to import both
        lib.import_csv(csv_path, polarity=None)
        print(f"Lib loaded: {len(lib)} entries")
        # print a few entries (polars DataFrame -> head)
        try:
            print(lib.lib_df.select(["name", "formula", "adduct", "mz"]).head(8))
        except Exception:
            # older implementations might not have the same columns; just show length
            pass
        return True
    except Exception as e:
        print(f"Failed to load CSV with Lib.import_csv: {e}")
        return False


if __name__ == "__main__":
    csv_file = generate_csv()
    ok = test_load_with_lib(csv_file)
    if not ok:
        print("Test failed; please inspect messages above.")
        sys.exit(2)
    print("Done.")
