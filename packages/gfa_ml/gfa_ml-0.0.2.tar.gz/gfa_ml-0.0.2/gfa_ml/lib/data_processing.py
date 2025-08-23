import pandas as pd
import os
import logging
import traceback
from typing import Dict, Union
import yaml
from ..data_model.common import Metric, MetricReport
from ..data_model.data_type import TimeUnit, TimeNormalizationType, ChartType
from .constant import DEFAULT_GRAPH_ATTRIBUTES, SRC_PATH, LIB_PATH, DOCS_PATH, IMG_PATH
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def smooth_data_frame(df: pd.DataFrame, metric_dict: Dict[str, Metric]) -> pd.DataFrame:
    """
    Apply smoothing to the DataFrame based on the metric definitions.
    """
    try:
        new_df = df.copy()
        for metric_name, metric in metric_dict.items():
            column_name = metric.display_name
            if column_name not in new_df.columns:
                logging.warning(
                    f"Column '{column_name}' not found in DataFrame. Skipping smoothing for this metric."
                )
                continue
            if metric.smoothing_function:
                logging.info(
                    f"Smoothing column: {column_name} with {metric.smoothing_function.function_name}"
                )
                if metric.smoothing_function.function_name == "moving_average":
                    window_size = metric.smoothing_function.smoothing_param.window_size
                    min_periods = metric.smoothing_function.smoothing_param.min_periods
                    new_df[column_name] = (
                        new_df[column_name]
                        .rolling(window=window_size, min_periods=min_periods)
                        .mean()
                    )
        return new_df
    except Exception as e:
        logging.error(f"Error occurred while smoothing data frame: {e}")
        logging.error(traceback.format_exc())
        return df


def extract_dataframe(
    df: pd.DataFrame,
    remove_zeros: bool = False,
    remove_inf: bool = False,
    remove_negatives: bool = False,
    remove_nans: bool = False,
    start_row: int = 0,
    end_row: int = -1,
    n_rows: int = None,
    n_percent: float = None,
    start_percent: float = None,
) -> pd.DataFrame:
    try:
        if start_row < 0 or start_row >= len(df):
            start_row = 0
            logging.warning("start_row is less than 0, setting to 0.")
        if start_percent is not None:
            start_row = int(len(df) * (start_percent / 100))
        if n_rows is not None:
            end_row = start_row + n_rows
        if n_percent is not None:
            end_row = start_row + int(len(df) * (n_percent / 100))
        if end_row > len(df):
            end_row = len(df)
            logging.warning(
                "end_row is greater than DataFrame length, setting to DataFrame length."
            )
        if end_row < 0:
            end_row = len(df) + end_row
            logging.warning("end_row is negative, setting to relative index.")

        process_df = df.iloc[start_row:end_row].copy()
        if remove_zeros:
            process_df = process_df[(process_df != 0).all(axis=1)]
        if remove_inf:
            process_df = process_df[
                (process_df != float("inf")).all(axis=1)
                & (process_df != float("-inf")).all(axis=1)
            ]
        if remove_negatives:
            process_df = process_df[(process_df >= 0).all(axis=1)]
        if remove_nans:
            process_df = process_df.dropna()
        logging.info(
            f"Extracted DataFrame from rows {start_row} to {end_row} with shape {process_df.shape}."
        )
        return process_df
    except Exception as e:
        logging.error(f"Error extracting DataFrame: {e}")
        logging.debug(traceback.format_exc())
        return pd.DataFrame()
