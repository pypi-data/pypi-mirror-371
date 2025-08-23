import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess
import warnings


#  Single
def draw_calibration_plot(
    df,
    outcome_col,
    prob_col,
    bin_num=10,
    max_scale=1.0,
    smooth_frac=1.0,
    font_size=14,
    plot_title="Calibration Plot",
    fig_size=(8, 6),
):
    """Draws a calibration plot from a DataFrame to compare predicted probabilities with observed frequencies.

    Args:
        df (pd.DataFrame): The input DataFrame containing predicted probabilities and observed outcomes.
        outcome_col (str): The name of the column containing the observed outcomes.
        prob_col (str): The name of the column containing the predicted probabilities.
        bin_num (int, optional): The number of bins to use for the calibration plot. Defaults to 10.
        max_scale (float, optional): The maximum scale for the plot axes. Defaults to 1.0.
        smooth_frac (float, optional): The smoothing fraction for the LOWESS curve. Defaults to 1.0.
        font_size (int, optional): The font size for the plot labels. Defaults to 14.
        plot_title (str, optional): The title of the plot. Defaults to "Calibration Plot".
        fig_size (tuple, optional): The size of the figure. Defaults to (8, 6).

    Raises:
        ValueError: If the required columns are not found in the DataFrame.

    Returns:
        plt.Figure: The calibration plot figure.
    """
    if not all(col in df.columns for col in [outcome_col, prob_col]):
        raise ValueError(
            f"Columns '{outcome_col}' and/or '{prob_col}' not found in the DataFrame."
        )

    internal_df = df[[prob_col, outcome_col]].copy()
    internal_df.rename(
        columns={prob_col: "predictions", outcome_col: "outcomes"}, inplace=True
    )
    internal_df.dropna(inplace=True)

    if len(internal_df) == 0:
        warnings.warn("After removing NA values, no data is left for plotting.")
        return plt.figure()

    try:
        internal_df["bin"] = pd.qcut(
            internal_df["predictions"], q=bin_num, labels=False, duplicates="drop"
        )
        actual_bin_num = internal_df["bin"].nunique()
        if actual_bin_num < bin_num:
            warnings.warn(
                f"Due to duplicate prediction values, the number of bins was reduced to {actual_bin_num}."
            )
    except ValueError:
        warnings.warn("Could not create bins. The data might not be varied enough.")
        internal_df["bin"] = 1

    plot_data = (
        internal_df.groupby("bin")
        .agg(
            mean_pred=("predictions", "mean"),
            mean_obs=("outcomes", "mean"),
            n=("outcomes", "count"),
        )
        .reset_index()
    )

    plt.style.use("seaborn-v0_8-ticks")
    fig, ax = plt.subplots(figsize=fig_size)
    plt.rcParams["font.family"] = "serif"

    ax.scatter(
        plot_data["mean_pred"],
        plot_data["mean_obs"],
        s=25,  # Size of points
        facecolor="dodgerblue",
        edgecolor="black",
        alpha=0.8,
        label="Binned Observations",
    )

    sorted_data = plot_data.sort_values("mean_pred")
    if len(sorted_data) > 2:
        smoothed = lowess(
            sorted_data["mean_obs"],
            sorted_data["mean_pred"],
            frac=min(smooth_frac, 1.0),
        )
        ax.plot(
            smoothed[:, 0],
            smoothed[:, 1],
            color="black",
            linewidth=1.2,
            label="LOWESS Smoother",
        )

    ax.plot(
        [0, max_scale],
        [0, max_scale],
        linestyle="--",
        color="grey",
        label="Perfect Calibration",
    )

    ax.set_xlabel("Predicted Probability", fontsize=font_size)
    ax.set_ylabel("Observed Frequency", fontsize=font_size)
    ax.set_title(plot_title, fontsize=font_size + 2, weight="bold", pad=20)
    ax.set_xlim(0, max_scale)
    ax.set_ylim(0, max_scale)
    ax.set_aspect("equal", adjustable="box")

    ax.tick_params(axis="both", which="major", labelsize=font_size - 2)
    sns.despine(trim=True, offset=5)
    ax.legend(fontsize=font_size - 2)
    plt.tight_layout()

    return fig


#  Merge Multiple
def draw_calibration_plot_merge(
    list_of_dfs, outcome_col="outcome", prob_col="probabilities", **kwargs
):
    """Merge multiple DataFrames and draw a calibration plot.

    Args:
        list_of_dfs (list): A list of pandas DataFrames.
        outcome_col (str, optional): The name of the common outcome column. Defaults to "outcome".
        prob_col (str, optional): The name of the probability column in each DataFrame. Defaults to "probabilities".

    Raises:
        ValueError: If the required columns are not found in the DataFrames.
        ValueError: If the outcome columns in the DataFrames do not match.
        ValueError: If the probability columns in the DataFrames do not match.
        ValueError: If the DataFrames are not all the same length.

    Returns:
        matplotlib.figure.Figure: The figure object containing the merged calibration plot.
    """
    # Validate input
    if not isinstance(list_of_dfs, list) or not list_of_dfs:
        raise ValueError("`list_of_dfs` must be a non-empty list of DataFrames.")

    # Validate the columns of the first DataFrame
    first_df = list_of_dfs[0]
    if not all(col in first_df.columns for col in [outcome_col, prob_col]):
        raise ValueError(
            f"Columns '{outcome_col}' and/or '{prob_col}' not found in the first DataFrame."
        )

    # Extract the common outcome column and verify all outcome columns are identical
    common_outcomes = first_df[outcome_col]
    for i, df in enumerate(list_of_dfs[1:], 1):
        if not common_outcomes.equals(df[outcome_col]):
            raise ValueError(
                f"The outcome column '{outcome_col}' in DataFrame at index {i} is not identical to the first one."
            )

    # Extract all probability columns and compute the mean
    # Efficiently extract all probability Series using a list comprehension
    prob_series_list = [df[prob_col] for df in list_of_dfs]
    # Concatenate them into a DataFrame and compute the mean across rows
    averaged_probs = pd.concat(prob_series_list, axis=1).mean(axis=1)

    # Create the merged DataFrame
    merged_df = pd.DataFrame(
        {"merged_outcomes": common_outcomes, "merged_probs": averaged_probs}
    )

    # Call the base plotting function
    # Use kwargs to pass all optional plotting parameters
    # If the user did not provide plot_title, we give a default one
    if "plot_title" not in kwargs:
        kwargs["plot_title"] = "Merged Calibration Plot"

    fig = draw_calibration_plot(
        df=merged_df,
        outcome_col="merged_outcomes",
        prob_col="merged_probs",
        **kwargs,  # Pass all other parameters
    )

    return fig
