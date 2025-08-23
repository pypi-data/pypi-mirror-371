import pandas as pd
from statsmodels.imputation import mice
import matplotlib.pyplot as plt
from typing import List, Union, Dict
from joblib import Parallel, delayed

from pathlib import Path


def _impute_single_dataset(
    data: pd.DataFrame, columns_to_impute: List[str], num_iterations: int
):
    """Impute missing values in a single dataset using MICE.

    Args:
        data (pd.DataFrame): The input data with missing values.
        columns_to_impute (List[str]): The columns to impute.
        num_iterations (int): The number of MICE iterations to perform.

    Returns:
        pd.DataFrame: The imputed dataset.
    """
    # 记录每个目标列需要插补的行的索引
    missing_indices = {col: data.index[data[col].isnull()] for col in columns_to_impute}

    # 初始化MICEData
    imp_data = mice.MICEData(data)

    # 初始化用于存储本次运行历史的字典
    run_means_history = {col: [] for col in columns_to_impute}
    run_stds_history = {col: [] for col in columns_to_impute}

    # 迭代过程
    for _ in range(num_iterations):
        imp_data.update_all()
        for col in columns_to_impute:
            imputed_values = imp_data.data.loc[missing_indices[col], col]
            run_means_history[col].append(imputed_values.mean())
            run_stds_history[col].append(imputed_values.std())

    # --- 选择性地合并结果 ---
    fully_imputed_df = imp_data.next_sample()
    final_df = data.copy()
    final_df[columns_to_impute] = fully_imputed_df[columns_to_impute]

    # 返回本次运行的所有结果
    return final_df, run_means_history, run_stds_history


def impute_with_mice(
    data: pd.DataFrame,
    columns_to_impute: Union[str, List[str]],
    num_datasets: int = 20,
    num_iterations: int = 100,
    n_jobs: int = -1,
):
    """Perform multiple imputation using MICE (Multivariate Imputation by Chained Equations).

    Args:
        data (pd.DataFrame): The input data with missing values.
        columns_to_impute (Union[str, List[str]]): The columns to impute.
        num_datasets (int, optional): The number of complete datasets to generate. Defaults to 20.
        num_iterations (int, optional): The number of MICE iterations to perform. Defaults to 100.
        n_jobs (int, optional): The number of CPU cores to use. Defaults to -1.

    Returns:
        tuple: A tuple containing:
            - imputed_datasets (list): A list of DataFrames with imputed values.
            - all_means_history (dict): A dictionary with mean values history for each column.
            - all_stds_history (dict): A dictionary with standard deviation history for each column.
    """
    # 确保 columns_to_impute 是一个列表
    if isinstance(columns_to_impute, str):
        columns_to_impute = [columns_to_impute]

    print(
        f"Start imputation, {n_jobs if n_jobs!=-1 else 'all available'} cores will be used to generate {num_datasets} datasets..."
    )

    # 使用 joblib.Parallel 来并行执行工作函数
    # verbose=10 会打印进度条，非常有用
    results = Parallel(n_jobs=n_jobs, verbose=10)(
        delayed(_impute_single_dataset)(
            data=data.copy(),
            columns_to_impute=columns_to_impute,
            num_iterations=num_iterations,
        )
        for _ in range(num_datasets)
    )

    # --- 3. 聚合并行计算的结果 ---
    # `results` 是一个列表，每个元素是 (_impute_single_dataset的返回值)
    # 例如: [(df1, means1, stds1), (df2, means2, stds2), ...]

    imputed_datasets = [res[0] for res in results]

    # 初始化用于存储所有结果的字典
    all_means_history = {col: [] for col in columns_to_impute}
    all_stds_history = {col: [] for col in columns_to_impute}

    # 解包并重组历史记录
    for res in results:
        run_means = res[1]
        run_stds = res[2]
        for col in columns_to_impute:
            all_means_history[col].append(run_means[col])
            all_stds_history[col].append(run_stds[col])

    print("\nParallel imputation process completed.")
    return imputed_datasets, all_means_history, all_stds_history


# Convergence Plotting
def plot_imputation_convergence(
    means_history: Dict[str, List[List[float]]],
    stds_history: Dict[str, List[List[float]]],
    columns_to_plot: List[str] = None,
    max_runs_to_plot: int = 5,
    save_path: str = None,
):
    """Plot the convergence of MICE imputation.

    Args:
        means_history (Dict[str, List[List[float]]]): Mean values history for each column.
        stds_history (Dict[str, List[List[float]]]): Standard deviation history for each column.
        columns_to_plot (List[str], optional): Columns to plot. Defaults to None.
        max_runs_to_plot (int, optional): Maximum number of runs to plot for each column. Defaults to 5.
        save_path (str, optional): Path to save the plot. Defaults to None.
    """
    if columns_to_plot is None:
        columns_to_plot = list(means_history.keys())

    if not columns_to_plot:
        print("No columns to plot.")
        return

    num_cols = len(columns_to_plot)
    fig, axes = plt.subplots(num_cols, 2, figsize=(14, 5 * num_cols), squeeze=False)

    print(f"Generating convergence plots for {columns_to_plot}...")

    for i, col in enumerate(columns_to_plot):
        if col not in means_history:
            print(f"Warning: Column '{col}' not found in history, skipping.")
            continue

        # --- 绘制均值变化 ---
        ax_mean = axes[i, 0]
        num_lines = min(max_runs_to_plot, len(means_history[col]))
        for j in range(num_lines):
            means = means_history[col][j]
            ax_mean.plot(range(1, len(means) + 1), means, label=f"Imputation {j+1}")

        ax_mean.set_title(f"'{col}' - Mean Convergence")
        ax_mean.set_xlabel("Iteration")
        ax_mean.set_ylabel("Mean")
        ax_mean.legend()
        ax_mean.grid(True)

        # --- 绘制标准差变化 ---
        ax_std = axes[i, 1]
        num_lines = min(max_runs_to_plot, len(stds_history[col]))
        for j in range(num_lines):
            stds = stds_history[col][j]
            ax_std.plot(range(1, len(stds) + 1), stds, label=f"Imputation {j+1}")

        ax_std.set_title(f"'{col}' - Standard Deviation Convergence")
        ax_std.set_xlabel("Iteration")
        ax_std.set_ylabel("Standard Deviation")
        ax_std.legend()
        ax_std.grid(True)

    fig.tight_layout()

    # Save or show the plot
    if save_path:
        # If a save path is provided
        output_path = Path(save_path)
        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # Save the figure
        fig.savefig(output_path)
        # Close the figure to prevent it from being displayed on the screen
        plt.close(fig)
        print(f"\nFigure saved successfully to: {output_path.resolve()}")
    else:
        # If no path is provided, show the plot as before
        plt.show()


# Save data
def save_imputed_datasets(
    imputed_datasets: List[pd.DataFrame], folder_path: str, file_format: str = "csv"
):
    """Save imputed datasets to a specified folder.

    Args:
        imputed_datasets (List[pd.DataFrame]): A list of imputed DataFrames to save.
        folder_path (str): The folder path to save the files.
        file_format (str, optional): The file format to save the files. Defaults to "csv".

    Raises:
        ValueError: If the file format is not supported.
    """
    print(f"Saving {len(imputed_datasets)} imputed datasets to folder '{folder_path}'...")

    # 1. 使用 pathlib 创建文件夹，如果不存在
    # exist_ok=True 确保如果文件夹已存在，不会报错
    path = Path(folder_path)
    path.mkdir(parents=True, exist_ok=True)

    # 2. 检查支持的文件格式
    supported_formats = ["csv", "parquet", "pickle"]
    if file_format not in supported_formats:
        raise ValueError(
            f"Unsupported file format '{file_format}'. Please choose from: {supported_formats}"
        )

    # 3. Loop through and save each dataset
    for i, df in enumerate(imputed_datasets):
        # Create file name, e.g., imputation_1.csv
        file_name = f"imputation_{i+1}.{file_format}"
        full_path = path / file_name

        # Save the DataFrame according to the selected format
        if file_format == "csv":
            # index=False is a common option to avoid writing the DataFrame's index to the file
            df.to_csv(full_path, index=False)
        elif file_format == "parquet":
            df.to_parquet(full_path, index=False)
        elif file_format == "pickle":
            df.to_pickle(full_path)

    print(f"\nAll datasets have been successfully saved.")
    print(f"You can find them at the following path: {path.resolve()}")


# Save convergence history
def save_convergence_history(
    means_history: Dict[str, List[List[float]]],
    stds_history: Dict[str, List[List[float]]],
    file_path: str,
):
    """Save the convergence history of imputed datasets.

    Args:
        means_history (Dict[str, List[List[float]]]): A dictionary containing the mean history for each imputed column.
        stds_history (Dict[str, List[List[float]]]): A dictionary containing the standard deviation history for each imputed column.
        file_path (str): The file path to save the convergence history.

    Raises:
        ValueError: If the file format is not supported.
    """
    print(f"Saving convergence history to '{file_path}'...")

    # Convert the history data into a long-format DataFrame
    records = []
    # Iterate over each imputed column
    for col_name, all_runs_means in means_history.items():
        # Iterate over each imputation run for this column (e.g., 20 runs for 20 datasets)
        for run_idx, run_means_list in enumerate(all_runs_means):
            # Iterate over each iteration within a single run
            for iter_idx, mean_value in enumerate(run_means_list):
                # Get the corresponding standard deviation value
                std_value = stds_history[col_name][run_idx][iter_idx]

                records.append(
                    {
                        "column_name": col_name,
                        "imputation_run": run_idx + 1,  # Start counting from 1 for better readability
                        "iteration": iter_idx + 1,  # Start counting from 1
                        "mean": mean_value,
                        "std": std_value,
                    }
                )

    # Convert the record list into a DataFrame
    history_df = pd.DataFrame(records)

    # Save the DataFrame to a file
    output_path = Path(file_path)
    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    file_format = output_path.suffix

    if file_format == ".csv":
        history_df.to_csv(output_path, index=False)
    elif file_format == ".parquet":
        history_df.to_parquet(output_path, index=False)
    elif file_format == ".pickle":
        history_df.to_pickle(output_path)
    else:
        raise ValueError(
            f"Unsupported file format '{file_format}'. Please choose from: .csv, .parquet, or .pickle"
        )

    print(f"\nConvergence history has been successfully saved.")
