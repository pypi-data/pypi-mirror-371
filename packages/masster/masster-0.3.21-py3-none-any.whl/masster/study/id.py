"""study/id.py

Identification helpers for Study: load a Lib and identify consensus features
by matching m/z (and optionally RT).
"""
from __future__ import annotations

from typing import Optional

import polars as pl


def lib_load(study, lib_source, polarity: Optional[str] = None, adducts: Optional[list] = None):
    """Load a compound library into the study.

    Args:
        study: Study instance
        lib_source: either a CSV file path (str) or a Lib instance
        polarity: ionization polarity ("positive" or "negative") - used when lib_source is a CSV path
        adducts: specific adducts to generate - used when lib_source is a CSV path

    Side effects:
        sets study.lib_df to a Polars DataFrame and stores the lib object on
        study._lib for later reference.
    """
    # Lazy import to avoid circular imports at module import time
    try:
        from masster.lib.lib import Lib
    except Exception:
        Lib = None

    if lib_source is None:
        raise ValueError("lib_source must be a CSV file path (str) or a Lib instance")

    # Use study polarity if not explicitly provided
    if polarity is None:
        study_polarity = getattr(study, 'polarity', 'positive')
        # Normalize polarity names
        if study_polarity in ['pos', 'positive']:
            polarity = 'positive'
        elif study_polarity in ['neg', 'negative']:
            polarity = 'negative'
        else:
            polarity = 'positive'  # Default fallback

    # Handle string input (CSV file path)
    if isinstance(lib_source, str):
        if Lib is None:
            raise ImportError("Could not import masster.lib.lib.Lib - required for CSV loading")
        
        lib_obj = Lib()
        lib_obj.import_csv(lib_source, polarity=polarity, adducts=adducts)
        
    # Handle Lib instance
    elif Lib is not None and isinstance(lib_source, Lib):
        lib_obj = lib_source
        
    # Handle other objects with lib_df attribute
    elif hasattr(lib_source, "lib_df"):
        lib_obj = lib_source
        
    else:
        raise TypeError("lib_source must be a CSV file path (str), a masster.lib.Lib instance, or have a 'lib_df' attribute")

    # Ensure lib_df is populated
    lf = getattr(lib_obj, "lib_df", None)
    if lf is None or (hasattr(lf, 'is_empty') and lf.is_empty()):
        raise ValueError("Library has no data populated in lib_df")

    # Filter by polarity to match study
    # Map polarity to charge signs
    if polarity == 'positive':
        target_charges = [1, 2]  # positive charges
    elif polarity == 'negative':
        target_charges = [-1, -2]  # negative charges
    else:
        target_charges = [-2, -1, 1, 2]  # all charges

    # Filter library entries by charge sign (which corresponds to polarity)
    filtered_lf = lf.filter(pl.col("z").is_in(target_charges))
    
    if filtered_lf.is_empty():
        print(f"Warning: No library entries found for polarity '{polarity}'. Using all entries.")
        filtered_lf = lf

    # Store pointer and DataFrame on study
    study._lib = lib_obj
    
    # Add to existing lib_df instead of replacing
    if hasattr(study, 'lib_df') and study.lib_df is not None and not study.lib_df.is_empty():
        # Concatenate with existing data
        study.lib_df = pl.concat([study.lib_df, filtered_lf])
    else:
        # First time loading - create new
        try:
            study.lib_df = filtered_lf.clone() if hasattr(filtered_lf, "clone") else pl.DataFrame(filtered_lf)
        except Exception:
            study.lib_df = pl.from_pandas(filtered_lf) if hasattr(filtered_lf, "to_pandas") else pl.DataFrame(filtered_lf)


def identify(study, mz_tolerance: float = 0.01, rt_tolerance: Optional[float] = None) -> pl.DataFrame:
    """Identify consensus features against the loaded library.

    Matches consensus_df.mz against lib_df.mz within mz_tolerance. If rt_tolerance
    is provided and both consensus and library entries have rt values, RT is
    used as an additional filter.

    The resulting DataFrame is stored as study.id_df and returned. Columns:
        - consensus_uid
        - lib_uid
        - delta_mz
        - delta_rt (nullable)
    """
    # Validate inputs
    if getattr(study, "consensus_df", None) is None or study.consensus_df.is_empty():
        study.id_df = pl.DataFrame()
        return study.id_df

    if getattr(study, "lib_df", None) is None or study.lib_df.is_empty():
        raise ValueError("Library (study.lib_df) is empty; call lib_load() first")

    results = []

    # Iterate consensus rows and find matching lib rows by m/z +/- tolerance
    for cons in study.consensus_df.iter_rows(named=True):
        cons_mz = cons.get("mz")
        cons_rt = cons.get("rt")
        if cons_mz is None:
            continue

        # Filter lib by mz window
        matches = study.lib_df.filter(
            (pl.col("mz") >= cons_mz - mz_tolerance) & (pl.col("mz") <= cons_mz + mz_tolerance)
        )

        # If rt_tolerance provided and consensus RT present, prefer rt-filtered hits
        if rt_tolerance is not None and cons_rt is not None:
            rt_matches = matches.filter(
                pl.col("rt").is_not_null() & (pl.col("rt") >= cons_rt - rt_tolerance) & (pl.col("rt") <= cons_rt + rt_tolerance)
            )
            if not rt_matches.is_empty():
                matches = rt_matches

        for m in matches.iter_rows(named=True):
            delta_mz = abs(cons_mz - m.get("mz")) if m.get("mz") is not None else None
            lib_rt = m.get("rt")
            delta_rt = abs(cons_rt - lib_rt) if (cons_rt is not None and lib_rt is not None) else None
            results.append(
                {
                    "consensus_uid": cons.get("consensus_uid"),
                    "lib_uid": m.get("lib_uid"),
                    "delta_mz": delta_mz,
                    "delta_rt": delta_rt,
                }
            )

    study.id_df = pl.DataFrame(results) if results else pl.DataFrame()
    return study.id_df
