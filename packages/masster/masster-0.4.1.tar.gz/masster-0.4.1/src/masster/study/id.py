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


def identify(study, mz_tol: float = 0.01, rt_tol: Optional[float] = None):
    """Identify consensus features against the loaded library.

    Matches consensus_df.mz against lib_df.mz within mz_tolerance. If rt_tolerance
    is provided and both consensus and library entries have rt values, RT is
    used as an additional filter.

    The resulting DataFrame is stored as study.id_df. Columns:
        - consensus_uid
        - lib_uid
        - mz_delta
        - rt_delta (nullable)
    """
    # Get logger from study if available
    logger = getattr(study, 'logger', None)
    
    if logger:
        logger.debug(f"Starting identification with mz_tolerance={mz_tol}, rt_tolerance={rt_tol}")

    # Validate inputs
    if getattr(study, "consensus_df", None) is None or study.consensus_df.is_empty():
        if logger:
            logger.warning("No consensus features found for identification")
        study.id_df = pl.DataFrame()
        return

    if getattr(study, "lib_df", None) is None or study.lib_df.is_empty():
        if logger:
            logger.error("Library (study.lib_df) is empty; call lib_load() first")
        raise ValueError("Library (study.lib_df) is empty; call lib_load() first")

    consensus_count = len(study.consensus_df)
    lib_count = len(study.lib_df)
    
    if logger:
        logger.debug(f"Identifying {consensus_count} consensus features against {lib_count} library entries")

    results = []
    features_with_matches = 0
    total_matches = 0
    rt_filtered_compounds = 0
    multiply_charged_filtered = 0

    # Iterate consensus rows and find matching lib rows by m/z +/- tolerance
    for cons in study.consensus_df.iter_rows(named=True):
        cons_mz = cons.get("mz")
        cons_rt = cons.get("rt")
        cons_uid = cons.get("consensus_uid")
        
        if cons_mz is None:
            if logger:
                logger.debug(f"Skipping consensus feature {cons_uid} - no m/z value")
            continue

        # Filter lib by mz window
        matches = study.lib_df.filter(
            (pl.col("mz") >= cons_mz - mz_tol) & (pl.col("mz") <= cons_mz + mz_tol)
        )

        initial_matches = len(matches)

        # If rt_tol provided and consensus RT present, prefer rt-filtered hits
        if rt_tol is not None and cons_rt is not None:
            rt_matches = matches.filter(
                pl.col("rt").is_not_null() & (pl.col("rt") >= cons_rt - rt_tol) & (pl.col("rt") <= cons_rt + rt_tol)
            )
            if not rt_matches.is_empty():
                matches = rt_matches
                if logger:
                    logger.debug(f"Consensus {cons_uid}: {initial_matches} m/z matches, {len(matches)} after RT filter")
            else:
                if logger:
                    logger.debug(f"Consensus {cons_uid}: {initial_matches} m/z matches, 0 after RT filter - using m/z matches only")

        # Apply scoring-based filtering system
        if not matches.is_empty():
            filtered_matches = matches.clone()
        else:
            filtered_matches = pl.DataFrame()

        if not filtered_matches.is_empty():
            features_with_matches += 1
            feature_match_count = len(filtered_matches)
            total_matches += feature_match_count
            
            if logger:
                logger.debug(f"Consensus {cons_uid} (mz={cons_mz:.5f}): {feature_match_count} library matches")

        for m in filtered_matches.iter_rows(named=True):
            mz_delta = abs(cons_mz - m.get("mz")) if m.get("mz") is not None else None
            lib_rt = m.get("rt")
            rt_delta = abs(cons_rt - lib_rt) if (cons_rt is not None and lib_rt is not None) else None
            results.append(
                {
                    "consensus_uid": cons.get("consensus_uid"),
                    "lib_uid": m.get("lib_uid"),
                    "mz_delta": mz_delta,
                    "rt_delta": rt_delta,
                    "matcher": "ms1",
                    "score": 1.0,
                }
            )

    study.id_df = pl.DataFrame(results) if results else pl.DataFrame()
    
    if logger:
        if rt_filtered_compounds > 0:
            logger.debug(f"RT consistency filtering applied to {rt_filtered_compounds} compound groups")
        
        if multiply_charged_filtered > 0:
            logger.debug(f"Excluded {multiply_charged_filtered} multiply charged adducts (no [M+H]+ or [M-H]- coeluting)")
        
        logger.info(f"Identification completed: {features_with_matches}/{consensus_count} features matched, {total_matches} total identifications")
        
        
        if total_matches > 0:
            # Calculate some statistics
            mz_deltas = [r["mz_delta"] for r in results if r["mz_delta"] is not None]
            rt_deltas = [r["rt_delta"] for r in results if r["rt_delta"] is not None]
            
            if mz_deltas:
                avg_mz_delta = sum(mz_deltas) / len(mz_deltas)
                max_mz_delta = max(mz_deltas)
                logger.debug(f"m/z accuracy: average Δ={avg_mz_delta:.5f} Da, max Δ={max_mz_delta:.5f} Da")
            
            if rt_deltas:
                avg_rt_delta = sum(rt_deltas) / len(rt_deltas)
                max_rt_delta = max(rt_deltas)
                logger.debug(f"RT accuracy: average Δ={avg_rt_delta:.2f} min, max Δ={max_rt_delta:.2f} min")
    


def get_id(study, features=None) -> pl.DataFrame:
    """Get identification results with comprehensive annotation data.

    Combines identification results (study.id_df) with library information to provide
    comprehensive identification data including names, adducts, formulas, etc.

    Args:
        study: Study instance with id_df and lib_df populated
        features: Optional DataFrame or list of consensus_uids to filter results.
                 If None, returns all identification results.

    Returns:
        Polars DataFrame with columns:
        - consensus_uid
        - lib_uid  
        - mz (consensus feature m/z)
        - rt (consensus feature RT)
        - name (compound name from library)
        - formula (molecular formula from library)
        - adduct (adduct type from library)
        - smiles (SMILES notation from library)
        - mz_delta (absolute m/z difference)
        - rt_delta (absolute RT difference, nullable)
        - Additional library columns if available (inchi, inchikey, etc.)

    Raises:
        ValueError: If study.id_df or study.lib_df are empty
    """
    # Validate inputs
    if getattr(study, "id_df", None) is None or study.id_df.is_empty():
        raise ValueError("Identification results (study.id_df) are empty; call identify() first")

    if getattr(study, "lib_df", None) is None or study.lib_df.is_empty():
        raise ValueError("Library (study.lib_df) is empty; call lib_load() first")

    if getattr(study, "consensus_df", None) is None or study.consensus_df.is_empty():
        raise ValueError("Consensus features (study.consensus_df) are empty")

    # Start with identification results
    result_df = study.id_df.clone()

    # Filter by features if provided
    if features is not None:
        if hasattr(features, 'columns'):  # DataFrame-like
            if 'consensus_uid' in features.columns:
                uids = features['consensus_uid'].unique().to_list()
            else:
                raise ValueError("features DataFrame must contain 'consensus_uid' column")
        elif hasattr(features, '__iter__') and not isinstance(features, str):  # List-like
            uids = list(features)
        else:
            raise ValueError("features must be a DataFrame with 'consensus_uid' column or a list of UIDs")
        
        result_df = result_df.filter(pl.col("consensus_uid").is_in(uids))
        
        if result_df.is_empty():
            return pl.DataFrame()

    # Join with consensus_df to get consensus feature m/z and RT
    consensus_cols = ["consensus_uid", "mz", "rt"]
    # Only select columns that exist in consensus_df
    available_consensus_cols = [col for col in consensus_cols if col in study.consensus_df.columns]
    
    result_df = result_df.join(
        study.consensus_df.select(available_consensus_cols),
        on="consensus_uid",
        how="left",
        suffix="_consensus"
    )

    # Join with lib_df to get library information
    lib_cols = ["lib_uid", "name", "formula", "adduct", "smiles", "cmpd_uid", "inchikey"]
    # Add optional columns if they exist
    optional_lib_cols = ["inchi"]
    for col in optional_lib_cols:
        if col in study.lib_df.columns:
            lib_cols.append(col)

    # Only select columns that exist in lib_df
    available_lib_cols = [col for col in lib_cols if col in study.lib_df.columns]
    
    result_df = result_df.join(
        study.lib_df.select(available_lib_cols),
        on="lib_uid", 
        how="left",
        suffix="_lib"
    )

    # Reorder columns for better readability
    column_order = [
        "consensus_uid",
        "cmpd_uid" if "cmpd_uid" in result_df.columns else None,
        "lib_uid", 
        "name" if "name" in result_df.columns else None,
        "formula" if "formula" in result_df.columns else None,
        "adduct" if "adduct" in result_df.columns else None,
        "mz" if "mz" in result_df.columns else None,
        "mz_delta",
        "rt" if "rt" in result_df.columns else None,
        "rt_delta",
        "matcher" if "matcher" in result_df.columns else None,
        "score" if "score" in result_df.columns else None,
        "smiles" if "smiles" in result_df.columns else None,
        "inchikey" if "inchikey" in result_df.columns else None
    ]
    
    # Add any remaining columns
    remaining_cols = [col for col in result_df.columns if col not in column_order]
    column_order.extend(remaining_cols)
    
    # Filter out None values and select existing columns
    final_column_order = [col for col in column_order if col is not None and col in result_df.columns]
    
    result_df = result_df.select(final_column_order)
    
    # Add compound and formula count columns
    if "consensus_uid" in result_df.columns:
        # Calculate counts per consensus_uid
        count_stats = result_df.group_by("consensus_uid").agg([
            pl.col("cmpd_uid").n_unique().alias("num_cmpds") if "cmpd_uid" in result_df.columns else pl.lit(None).alias("num_cmpds"),
            pl.col("formula").n_unique().alias("num_formulas") if "formula" in result_df.columns else pl.lit(None).alias("num_formulas")
        ])
        
        # Join the counts back to the main dataframe
        result_df = result_df.join(count_stats, on="consensus_uid", how="left")
        
        # Reorder columns to put count columns in the right position
        final_columns = []
        for col in result_df.columns:
            if col in ["consensus_uid", "cmpd_uid", "lib_uid", "name", "formula", "adduct", 
                      "mz", "mz_delta", "rt", "rt_delta", "matcher", "score"]:
                final_columns.append(col)
        # Add count columns
        if "num_cmpds" in result_df.columns:
            final_columns.append("num_cmpds")
        if "num_formulas" in result_df.columns:
            final_columns.append("num_formulas")
        # Add remaining columns
        for col in result_df.columns:
            if col not in final_columns:
                final_columns.append(col)
        
        result_df = result_df.select(final_columns)
        
        # Apply scoring-based filtering system
        if "consensus_uid" in result_df.columns and len(result_df) > 0:
            # (i) Start with score 1.0 for all
            result_df = result_df.with_columns(pl.lit(1.0).alias("score"))
            
            # (ii) If not [M+H]+ or [M-H]-, score *= 0.7
            if "adduct" in result_df.columns:
                preferred_adducts = ["[M+H]+", "[M-H]-"]
                result_df = result_df.with_columns(
                    pl.when(pl.col("adduct").is_in(preferred_adducts))
                    .then(pl.col("score"))
                    .otherwise(pl.col("score") * 0.7)
                    .alias("score")
                )
            
            # (iii) If num_formulas > 1, score *= 0.7
            if "num_formulas" in result_df.columns:
                result_df = result_df.with_columns(
                    pl.when(pl.col("num_formulas") > 1)
                    .then(pl.col("score") * 0.7)
                    .otherwise(pl.col("score"))
                    .alias("score")
                )
            
            # (iv) If num_cmpds > 1, score *= 0.7
            if "num_cmpds" in result_df.columns:
                result_df = result_df.with_columns(
                    pl.when(pl.col("num_cmpds") > 1)
                    .then(pl.col("score") * 0.7)
                    .otherwise(pl.col("score"))
                    .alias("score")
                )
            
            # (v) Rank by score, assume that highest score has the correct rt
            # (vi) Remove all lower-scoring ids with a different rt (group by cmpd_uid)
            # (vii) Remove multiply charged ids if not in line with [M+H]+ or [M-H]- (group by cmpd_uid)
            
            # Group by cmpd_uid and apply filtering logic
            if "cmpd_uid" in result_df.columns:
                filtered_dfs = []
                for cmpd_uid, group_df in result_df.group_by("cmpd_uid"):
                    # Sort by score descending to get highest score first
                    group_df = group_df.sort("score", descending=True)
                    
                    if len(group_df) == 0:
                        continue
                        
                    # Get the highest scoring entry's RT as reference
                    reference_rt = group_df["rt"][0] if "rt" in group_df.columns and group_df["rt"][0] is not None else None
                    
                    # Filter entries: keep those with same RT as highest scoring entry
                    if reference_rt is not None and "rt" in group_df.columns:
                        # Keep entries with the same RT or null RT
                        rt_filtered = group_df.filter(
                            (pl.col("rt") == reference_rt) | pl.col("rt").is_null()
                        )
                    else:
                        # No reference RT, keep all
                        rt_filtered = group_df
                    
                    # Check multiply charged constraint
                    if "z" in rt_filtered.columns and "adduct" in rt_filtered.columns and len(rt_filtered) > 0:
                        # Check if there are multiply charged adducts
                        multiply_charged = rt_filtered.filter((pl.col("z") > 1) | (pl.col("z") < -1))
                        singly_charged = rt_filtered.filter((pl.col("z") == 1) | (pl.col("z") == -1))
                        
                        if not multiply_charged.is_empty():
                            # Check if [M+H]+ or [M-H]- are present
                            reference_adducts = ["[M+H]+", "[M-H]-"]
                            has_reference = any(singly_charged.filter(pl.col("adduct").is_in(reference_adducts)).height > 0)
                            
                            if not has_reference:
                                # Remove multiply charged adducts
                                rt_filtered = singly_charged
                    
                    if len(rt_filtered) > 0:
                        filtered_dfs.append(rt_filtered)
                
                if filtered_dfs:
                    result_df = pl.concat(filtered_dfs)
                else:
                    result_df = pl.DataFrame()
    
    # Sort by cmpd_uid if available
    if "cmpd_uid" in result_df.columns:
        result_df = result_df.sort("cmpd_uid")
    
    return result_df
