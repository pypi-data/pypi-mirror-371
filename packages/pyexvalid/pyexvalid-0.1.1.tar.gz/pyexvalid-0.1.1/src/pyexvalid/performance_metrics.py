import numpy as np
import statsmodels.api as sm
from scipy.stats import norm
import scipy.stats as stats
from typing import Tuple, Optional


def get_citl(result_df, outcome_col, LP_col, level=0.95):
    """    Calculate the Calibration in the Large (CITL) for a given result DataFrame.

    Args:
        result_df (pd.DataFrame): The result DataFrame containing the outcomes and linear predictors.
        outcome_col (str): The name of the outcome column in the DataFrame.
        LP_col (str): The name of the linear predictor column in the DataFrame.
        level (float, optional): The confidence level for the CITL calculation. Defaults to 0.95.

    Returns:
        dict: A dictionary containing the CITL estimate and its confidence interval.
    """
    # Set the confidence level and calculate the Z-score
    # scipy.stats.norm.ppf is the equivalent of qnorm in R
    z_val = norm.ppf(1 - (1 - level) / 2)

    # Build the model of calibration in the large (outcome ~ offset(linear predictor))
    citl_model = sm.GLM(
        result_df[outcome_col],
        np.ones(len(result_df)),
        family=sm.families.Binomial(),  # Binomial family with logit link
        offset=result_df[LP_col],
    )

    citl_result = citl_model.fit()

    # Calibration in the large (the intercept)
    citl = citl_result.params.iloc[0]
    # Standard error
    citl_se = citl_result.bse.iloc[0]
    # Calculate the lower and upper bounds of the confidence interval
    citl_lower = citl - z_val * citl_se
    citl_upper = citl + z_val * citl_se

    results = {
        "citl": citl,
        "citl_se": citl_se,
        "citl_lower": citl_lower,
        "citl_upper": citl_upper,
    }

    return results


def get_cal_slope(result, outcome_col, LP_col, level=0.95):
    """Calculate the Calibration Slope (CAL) for a given result DataFrame.

    Args:
        result (pd.DataFrame): The result DataFrame containing the outcomes and linear predictors.
        outcome_col (str): The name of the outcome column in the DataFrame.
        LP_col (str): The name of the linear predictor column in the DataFrame.
        level (float, optional): The confidence level for the CAL calculation. Defaults to 0.95.

    Returns:
        dict: A dictionary containing the CAL estimate and its confidence interval.
    """
    # Set the confidence level and calculate the Z-score
    # scipy.stats.norm.ppf is the equivalent of qnorm in R
    z_val = norm.ppf(1 - (1 - level) / 2)

    # Build the model of calibration slope (outcome ~ linear predictor)
    slope_model = sm.GLM(
        result[outcome_col],
        sm.add_constant(result[LP_col]),
        family=sm.families.Binomial(),
    )

    slope_result = slope_model.fit()

    # Calibration in the large (the intercept)
    slope = slope_result.params.iloc[1]
    # Standard error
    slope_se = slope_result.bse.iloc[1]
    # Calculate the lower and upper bounds of the confidence interval
    slope_lower = slope - z_val * slope_se
    slope_upper = slope + z_val * slope_se

    results = {
        "cal_slope": slope,
        "cal_slope_se": slope_se,
        "cal_slope_lower": slope_lower,
        "cal_slope_upper": slope_upper,
    }

    return results


# ---- DeLong implementation (binary classification) ----
def compute_midrank(x: np.ndarray) -> np.ndarray:
    """Computes midranks.
    Args:
       x - a 1D numpy array
    Returns:
       array of midranks
    """
    J = np.argsort(x)
    Z = x[J]
    N = len(x)
    T = np.zeros(N, dtype=float)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]:
            j += 1
        T[i:j] = 0.5 * (i + j - 1)
        i = j
    T2 = np.empty(N, dtype=float)
    # Note(kazeevn) +1 is due to Python using 0-based indexing
    # instead of 1-based in the AUC formula in the paper
    T2[J] = T + 1
    return T2


def compute_midrank_weight(x: np.ndarray, sample_weight: np.ndarray) -> np.ndarray:
    """Computes midranks.
    Args:
       x - a 1D numpy array
    Returns:
       array of midranks
    """
    J = np.argsort(x)
    Z = x[J]
    cumulative_weight = np.cumsum(sample_weight[J])
    N = len(x)
    T = np.zeros(N, dtype=float)
    i = 0
    while i < N:
        j = i
        while j < N and Z[j] == Z[i]:
            j += 1
        T[i:j] = cumulative_weight[i:j].mean()
        i = j
    T2 = np.empty(N, dtype=float)
    T2[J] = T
    return T2


def fastDeLong(
    predictions_sorted_transposed: np.ndarray, label_1_count: int
) -> Tuple[np.ndarray, np.ndarray]:
    """
    The fast version of DeLong's method for computing the covariance of
    unadjusted AUC.
    Args:
       predictions_sorted_transposed: a 2D numpy.array[n_classifiers, n_examples]
          sorted such as the examples with label "1" are first
    Returns:
       (AUC value, DeLong covariance)
    Reference:
     @article{sun2014fast,
       title={Fast Implementation of DeLong's Algorithm for
              Comparing the Areas Under Correlated Receiver Oerating Characteristic Curves},
       author={Xu Sun and Weichao Xu},
       journal={IEEE Signal Processing Letters},
       volume={21},
       number={11},
       pages={1389--1393},
       year={2014},
       publisher={IEEE}
     }
    """
    # Short variables are named as they are in the paper
    m = label_1_count
    n = predictions_sorted_transposed.shape[1] - m
    positive_examples = predictions_sorted_transposed[:, :m]
    negative_examples = predictions_sorted_transposed[:, m:]
    k = predictions_sorted_transposed.shape[0]

    tx = np.empty([k, m], dtype=float)
    ty = np.empty([k, n], dtype=float)
    tz = np.empty([k, m + n], dtype=float)
    for r in range(k):
        tx[r, :] = compute_midrank(positive_examples[r, :])
        ty[r, :] = compute_midrank(negative_examples[r, :])
        tz[r, :] = compute_midrank(predictions_sorted_transposed[r, :])
    aucs = tz[:, :m].sum(axis=1) / m / n - float(m + 1.0) / 2.0 / n
    v01 = (tz[:, :m] - tx[:, :]) / n
    v10 = 1.0 - (tz[:, m:] - ty[:, :]) / m
    sx = np.cov(v01)
    sy = np.cov(v10)
    delongcov = sx / m + sy / n
    return aucs, delongcov


def calc_pvalue(aucs: np.ndarray, sigma: np.ndarray) -> float:
    """Computes log(10) of p-values.
    Args:
       aucs: 1D array of AUCs
       sigma: AUC DeLong covariances
    Returns:
       log10(pvalue)
    """
    l = np.array([[1, -1]])
    z = np.abs(np.diff(aucs)) / np.sqrt(np.dot(np.dot(l, sigma), l.T))
    return float(np.log10(2) + stats.norm.logsf(z, loc=0, scale=1).item() / np.log(10))


def compute_ground_truth_statistics(
    ground_truth: np.ndarray, sample_weight: Optional[np.ndarray] = None
) -> Tuple[np.ndarray, int, Optional[np.ndarray]]:
    assert np.array_equal(np.unique(ground_truth), [0, 1])
    order = (-ground_truth).argsort()
    label_1_count = int(ground_truth.sum())
    if sample_weight is None:
        ordered_sample_weight = None
    else:
        ordered_sample_weight = sample_weight[order]

    return order, label_1_count, ordered_sample_weight


def delong_roc_variance(
    ground_truth: np.ndarray, predictions: np.ndarray
) -> Tuple[float, np.ndarray]:
    """
    Computes ROC AUC variance for a single set of predictions
    Args:
       ground_truth: np.array of 0 and 1
       predictions: np.array of floats of the probability of being class 1
    """
    sample_weight = None
    order, label_1_count, ordered_sample_weight = compute_ground_truth_statistics(
        ground_truth, sample_weight
    )
    predictions_sorted_transposed = predictions[np.newaxis, order]
    aucs, delongcov = fastDeLong(predictions_sorted_transposed, label_1_count)
    assert (
        len(aucs) == 1
    ), "There is a bug in the code, please forward this to the developers"
    return aucs[0], delongcov


def delong_roc_test(
    ground_truth: np.ndarray, predictions_one: np.ndarray, predictions_two: np.ndarray
) -> float:
    """
    Computes log(p-value) for hypothesis that two ROC AUCs are different
    Args:
       ground_truth: np.array of 0 and 1
       predictions_one: predictions of the first model,
          np.array of floats of the probability of being class 1
       predictions_two: predictions of the second model,
          np.array of floats of the probability of being class 1
    """
    sample_weight = None
    order, label_1_count, _ = compute_ground_truth_statistics(ground_truth)
    predictions_sorted_transposed = np.vstack((predictions_one, predictions_two))[
        :, order
    ]
    aucs, delongcov = fastDeLong(predictions_sorted_transposed, label_1_count)
    return calc_pvalue(aucs, delongcov)


def get_auc(data, outcome_col, prob_col, level=0.95):
    y_true = data[outcome_col].to_numpy()
    y_pred = data[prob_col].to_numpy()
    auc, auc_cov = delong_roc_variance(y_true, y_pred)
    auc_std = np.sqrt(auc_cov)

    # Handle edge cases when auc_std is zero or very small
    if auc_std < 1e-10:
        if auc == 1.0:
            ci = np.array([1.0, 1.0])
        elif auc == 0.0:
            ci = np.array([0.0, 0.0])
        else:
            # If std dev is extremely low but AUC is not exactly 0 or 1
            ci = np.array([auc, auc])
    else:
        lower_upper_q = np.abs(np.array([0, 1]) - (1 - level) / 2)
        ci = stats.norm.ppf(lower_upper_q, loc=auc, scale=auc_std)

        # Ensure confidence intervals within [0,1]
        ci[ci > 1] = 1
        ci[ci < 0] = 0

    result = {"auc": auc, "auc_se": auc_std, "auc_lower": ci[0], "auc_upper": ci[1]}

    return result


# Rubin's Rule
def rubins_rule_pooling(estimates, variances):
    """Apply Rubin's Rule for pooling multiple imputation results.

    Args:
        estimates (array-like): The estimated values from each imputed dataset.
        variances (array-like): The variances (SE^2) from each imputed dataset.

    Returns:
        dict: A dictionary containing the pooled estimate and its confidence interval.
    """
    estimates = np.array(estimates)
    variances = np.array(variances)

    m = len(estimates)  # number of imputed datasets

    # Step 1: Pooled estimate (mean)
    pooled_estimate = np.mean(estimates)

    # Step 2: Within-imputation variance (mean variance)
    within_var = np.mean(variances)

    # Step 3: Between-imputation variance (variance between estimates)
    between_var = np.var(estimates, ddof=1) if m > 1 else 0

    # Step 4: Total variance
    total_var = within_var + (1 + 1 / m) * between_var
    pooled_se = np.sqrt(total_var)

    # Step 5: Degrees of freedom
    if between_var > 0:
        lambda_val = (1 + 1 / m) * between_var / total_var
        df = (m - 1) * (1 + within_var / ((1 + 1 / m) * between_var)) ** 2
    else:
        df = np.inf

    # Step 6: 95% confidence interval (using t-distribution)
    from scipy import stats

    if df == np.inf:
        t_critical = stats.norm.ppf(0.975)
    else:
        t_critical = stats.t.ppf(0.975, df)

    ci_lower = pooled_estimate - t_critical * pooled_se
    ci_upper = pooled_estimate + t_critical * pooled_se

    return {
        "pooled_estimate": pooled_estimate,
        "pooled_se": pooled_se,
        "within_var": within_var,
        "between_var": between_var,
        "total_var": total_var,
        "df": df,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


# Apply Rubin's Rule to the data
def pool_metrics(validation_df, metrics=["citl", "cal_slope", "auc"]):
    """Calculate the pooled results for all metrics.

    Args:
        validation_df (pd.DataFrame): The validation DataFrame containing metric estimates and standard errors.
        metrics (list, optional): The list of metrics to pool. Defaults to ["citl", "cal_slope", "auc"].

    Returns:
        dict: A dictionary containing the pooled results for each metric.
    """

    # Remove rows with errors
    valid_df = validation_df.dropna()

    results = {}

    for metric in metrics:
        estimates = valid_df[f"{metric}"].values
        variances = (valid_df[f"{metric}_se"].values) ** 2
        results[metric] = rubins_rule_pooling(estimates, variances)

    return results
