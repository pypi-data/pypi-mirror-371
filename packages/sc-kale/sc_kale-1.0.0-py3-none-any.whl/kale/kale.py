import os
from typing import Any

from pandas import DataFrame
from tqdm.auto import tqdm
import math
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from scipy.sparse import issparse
from scipy.stats import zscore, norm

# CORES_USED = 1 # For debugging, use a single core
CORES_USED = max(1, int(os.cpu_count() * 0.8))  # Use 80% of available cores


def std_dev_mean_norm_rank(n_population: int, k_sample: int) -> float:
    """Return σₙ,ₖ – the analytic SD of the mean of *k* normalised ranks.
    Calculates sigma_m_k: the theoretical standard deviation of the mean of k
    normalized ranks (r_i = (R_i - 0.5)/n) sampled without replacement
    from a population of size n.
    """
    if not (isinstance(n_population, int) and n_population > 0):
        raise ValueError("n_population must be a positive integer.")
    if not (isinstance(k_sample, int) and k_sample > 0):
        raise ValueError("k_sample must be a positive integer.")
    if k_sample > n_population:
        raise ValueError(
            "Sample size k_sample cannot exceed population size n_population."
        )

    if k_sample == n_population or n_population == 1:
        return 0.0  # No variability – we sampled everything.

    var = ((n_population + 1) * (n_population - k_sample)) / (
            12 * n_population ** 2 * k_sample
    )
    return math.sqrt(max(var, 0.0))


def _process_single_cell(
        cell_name: str, expression_series: pd.Series, priors_df: pd.DataFrame
):
    # Drop genes with all‑nan expression, rank-remaining genes
    expr = expression_series.dropna().sort_values(ascending=False)
    n_genes = expr.size

    # Robustness: If no genes with valid expression, return empty scores for this cell.
    if n_genes == 0:
        return cell_name, {}

    ranks = (np.arange(1, n_genes + 1) - 0.5) / n_genes
    rank_df = pd.DataFrame({"target": expr.index, "Rank": ranks})

    # Merge ranks into a *copy* of priors_df (avoid in‑place edits)
    p = priors_df.merge(rank_df, on="target", how="left")
    p = p[p["Rank"].notna()]

    # Invert rank for repressors (RegulatoryEffect == 0)
    # max_rank_val = (n_genes - 0.5) / n_genes
    p["AdjustedRank"] = np.where(
        p["RegulatoryEffect"].eq(0),
        1 - p["Rank"],
        p["Rank"],
    )  # AdjustedRank is (max_rank_val - Rank) for repressors Note: (1 - Rank)

    # Summarise per TF
    tf_summary = (
        p.groupby("source", observed=True)
        .agg(
            AvailableTargets=("AdjustedRank", lambda x: x.notna().sum()),
            RankMean=("AdjustedRank", "mean"),
        )
        .reset_index()
    )
    tf_summary = tf_summary[tf_summary["AvailableTargets"] > 0]

    # If tf_summary is empty after filtering, no TFs to score for this cell
    if tf_summary.empty:
        return cell_name, {}

    # Create a new column, If RankMean is <0.5, 1 else -1
    tf_summary["ActivationDir"] = np.where(tf_summary["RankMean"] < 0.5, 1, -1)
    # Compute σₙ,ₖ, Z‑score, and p‑value
    tf_summary["Sigma_n_k"] = tf_summary["AvailableTargets"].apply(
        lambda k: std_dev_mean_norm_rank(n_genes, k)
    )
    tf_summary["Z"] = (tf_summary["RankMean"] - 0.5) / (tf_summary["Sigma_n_k"].replace(0, np.nan))
    tf_summary["P_two_tailed"] = np.where(
        tf_summary["RankMean"] < 0.5,
        2 * norm.cdf(tf_summary["Z"]),
        2 * (1 - norm.cdf(tf_summary["Z"])),
    )

    regulators = tf_summary["source"].tolist()
    p_values = tf_summary["P_two_tailed"].tolist()
    directions = tf_summary["ActivationDir"].tolist()

    return cell_name, regulators, p_values, directions


def _process_single_cell_stouffer(cell_name: str, expression_z_scores: pd.Series, priors_df: pd.DataFrame):
    priors_group = (
        priors_df.groupby("source", observed=True)
        .agg({
            "target": list,
            "RegulatoryEffect": list
        })
    )

    valid_z_scores = expression_z_scores.dropna()
    if valid_z_scores.empty:
        return cell_name, [], [], []

    # Create a fast lookup map from gene to Z-score for this cell
    z_score_map = valid_z_scores.to_dict()

    regulators = []
    p_values = []
    directions = []

    # Iterate through the pre-grouped priors (much faster than merging)
    for tf, data in priors_group.iterrows():
        target_genes = data['target']
        effects = data['RegulatoryEffect']

        evidence_z = []
        for i, gene in enumerate(target_genes):
            z = z_score_map.get(gene)
            if z is not None:
                # If repressor (effect=0), flip the sign.
                evidence_z.append(-z if effects[i] == 0 else z)

        k = len(evidence_z)
        # if k < min_targets:  # Enforce min_targets at the cell level (Pass as a function argument if needed)
        #     continue

        # Calculate Stouffer's Z
        z_sum = np.sum(evidence_z)
        stouffer_z = z_sum / np.sqrt(k) if k > 0 else 0

        # Use a two-tailed test for the p-value
        p_value = 2 * norm.sf(abs(stouffer_z))

        # Direction is the sign of the combined evidence
        direction = np.sign(stouffer_z)

        regulators.append(tf)
        p_values.append(p_value)
        directions.append(direction)

    return cell_name, regulators, p_values, directions


def run_tf_analysis(adata, adj, ignore_zeros, min_targets, analysis_method):
    try:
        # Validate input data
        if adata is None or adata.n_obs == 0:
            raise ValueError("Input data is empty or invalid")

        if adata.n_obs > 500_000:
            print(f"Large dataset detected: {adata.n_obs} cells. This may take a long time.")


        # ───── Load gene expression data ────────────────────────────────────────
        X = adata.X.toarray() if issparse(adata.X) else adata.X.copy()

        print("Calculating Z-scores...")
        if ignore_zeros:
            print("[Z-SCORE] Calculating Z-scores based only on non-zero expression values.")
            X[X == 0] = np.nan
            X[X == 0.0] = np.nan
            z_mat = zscore(X, axis=0, nan_policy="omit")  # across all cells for a single gene (axis=0)
        else:
            print("[Z-SCORE] Calculating standard Z-scores including zero values.")
            z_mat = zscore(X, axis=0)

        # z_mat = X.copy()
        z_df = pd.DataFrame(z_mat, index=adata.obs_names, columns=adata.var_names)
        z_df.to_csv("results/z_scores.tsv", index=True, header=True, sep="\t")


        # ───── Load TF‑target priors ──────────────────────────────────────────────
        # Restructure adj for this method
        print("Loading TF-target priors...")
        adj["weight"] = np.where(adj["weight"] > 0, 1, -1)
        adj.rename(columns={adj.columns[-1]: "RegulatoryEffect"}, inplace=True)
        priors = adj.copy()


        priors = priors.groupby("source").filter(lambda x: len(x) >= min_targets)
        priors = priors[priors["target"].isin(z_df.columns)]
        priors_group = priors.groupby("source", observed=True).agg({"RegulatoryEffect": list, "target": list})
        priors_group = priors_group[priors_group["RegulatoryEffect"].apply(len) >= min_targets]
        priors = priors[priors["source"].isin(priors_group.index)]


        # ───── Decide the analysis method ───────────────────────────────────────
        if analysis_method == 'ranks_from_zscore':
            print("Using Rank-Based method for inference.")
            process_func = _process_single_cell
            data_for_processing = z_df

        elif analysis_method == 'stouffers_zscore':
            print("Using Stouffer's Z-score method for inference.")
            process_func = _process_single_cell_stouffer
            data_for_processing = z_df

        elif analysis_method == 'ranks_from_gene_expression':
            print("Using method: Ranks from Gene Expression.")
            raw_df = pd.DataFrame(X, index=adata.obs_names, columns=adata.var_names)

            rank_input_df = raw_df.copy()
            rank_input_df[rank_input_df == 0] = np.nan

            ranked_across_cells = rank_input_df.rank(axis=0, na_option='keep')
            ranked_across_cells = (ranked_across_cells - 0.5) / ranked_across_cells.max(axis=0, skipna=True)

            process_func = _process_single_cell
            data_for_processing = ranked_across_cells

        else:
            raise ValueError(f"Unknown analysis method: {analysis_method}")

        # ───── Parallel processing of cells ───────────────────────────────────────
        print(f"Starting TF analysis for user")
        print(f"Starting TF activity using {CORES_USED if CORES_USED > 0 else 'all available'} cores.")
        tasks = [
            delayed(process_func)(
                cell_name,
                data_for_processing.loc[cell_name],
                priors,
            )
            for cell_name in data_for_processing.index
        ]

        if CORES_USED == 1:  # Useful for debugging
            print("Running sequentially (CORES_USED=1)...")
            cell_results_list = [
                process_func(cell_name, data_for_processing.loc[cell_name], priors)
                for cell_name in tqdm(data_for_processing.index, desc="Processing cells")
            ]
        else:
            print(f"Running in parallel with CORES_USED={CORES_USED}...")
            cell_results_list = Parallel(n_jobs=CORES_USED, backend="loky", verbose=2)(tqdm(tasks, desc="Processing cells"))


        # ───── Aggregate results into two separate DataFrames ───────────────────
        print("\nAggregating results...")
        p_value_records = []
        activation_records = []

        # 1. Unpack results into flat lists of records
        for cell_name, regulators, p_values, directions in tqdm(cell_results_list, desc="Unpacking results"):
            for i, regulator in enumerate(regulators):
                p_value_records.append({'cell': cell_name, 'regulator': regulator, 'p_value': p_values[i]})
                activation_records.append({'cell': cell_name, 'regulator': regulator, 'direction': directions[i]})

        # 2. Build temporary DataFrames from the lists of records (very fast)
        p_values_temp_df = pd.DataFrame.from_records(p_value_records)
        activation_temp_df = pd.DataFrame.from_records(activation_records)

        # 3. Pivot the temporary DataFrames into the desired final shape (cells x regulators)
        if not p_values_temp_df.empty:
            pvalue_df = p_values_temp_df.pivot(index='cell', columns='regulator', values='p_value')
            activation_df = activation_temp_df.pivot(index='cell', columns='regulator', values='direction')
        else:
            # Handle a case where no TFs were found for any cell
            all_regulators = priors["source"].unique()
            pvalue_df = pd.DataFrame(index=z_df.index, columns=all_regulators, dtype=float)
            activation_df = pd.DataFrame(index=z_df.index, columns=all_regulators, dtype=float)

        print("Reindexing result DataFrames to match AnnData object order.")
        pvalue_df = pvalue_df.reindex(adata.obs_names)
        activation_df = activation_df.reindex(adata.obs_names)


        # ───── Save p_value and activation results ─────────────────────────────────────
        pvalue_df.dropna(axis=1, how="all", inplace=True)
        scores = -np.log10(pvalue_df)
        scores = scores.multiply(activation_df, fill_value=0)

        print("TF analysis completed")
        return scores, pvalue_df

    except Exception as e:
        print(f"Error during TF analysis: {e}")
        raise e


def run_kale(
    mat,
    adj,
    method: str = "ranks_from_zscore",
    n_targets: int = 10,
    ignore_zeros: bool = True
) -> tuple[Any, DataFrame]:

    scores, pvalues = run_tf_analysis(mat, adj, ignore_zeros, min_targets=n_targets, analysis_method=method)

    return scores, pvalues

