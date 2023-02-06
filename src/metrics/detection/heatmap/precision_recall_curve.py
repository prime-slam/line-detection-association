# Copyright (c) 2022, Kirill Ivanov, Anastasiia Kornilova and Dmitrii Iarosh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import os

from joblib import Parallel, delayed
from tqdm.contrib import tzip
from typing import List, Tuple

from src.metrics.detection.heatmap.basic_metrics import BasicMetrics
from src.metrics.detection.heatmap.tp_indicator import (
    HeatmapTPIndicator,
)
from src.metrics.detection.heatmap.utils import equally_sized, rasterize
from src.typing import ArrayNx4, ArrayN

__all__ = ["heatmap_precision_recall_curve"]


class PrecisionRecallCurve:
    """
    Class that calculates precision-recall pairs for different score thresholds
    over batches of predicted and ground truth lines
    """

    def __init__(self):
        self.tp_indicator = HeatmapTPIndicator()

    def calculate(
        self,
        pred_lines_batch: List[ArrayNx4[float]],
        gt_lines_batch: List[ArrayNx4[float]],
        line_scores_batch: List[ArrayNx4[float]],
        heights_batch: ArrayN[int],
        widths_batch: ArrayN[int],
        thresholds: ArrayN[float],
    ) -> Tuple[ArrayN[float], ArrayN[float]]:
        """
        Calculates the Precision-Recall Curve
        :param pred_lines_batch: list of predicted lines for each image
        :param gt_lines_batch: list of ground truth lines for each image
        :param line_scores_batch: list of predicted lines scores for each image
        :param heights_batch: array of heights of each image
        :param widths_batch: array of widths of each image
        :param thresholds: array of line scores thresholds to filter predicted lines
        :return: lists of x (recall) and y (precision) coordinates
        """
        if not equally_sized(
            [
                pred_lines_batch,
                gt_lines_batch,
                line_scores_batch,
                heights_batch,
                widths_batch,
            ]
        ):
            raise ValueError("All batches must be the same size")

        thresholds_number = len(thresholds)
        if thresholds_number == 0:
            raise ValueError("The list of threshold cannot be empty")

        def calculate_statistics(pred_lines, gt_lines, scores, height, width):
            gt_map = rasterize(gt_lines, height, width)
            gt_size = gt_map.nnz
            tp = np.zeros(thresholds_number)
            fp = np.zeros(thresholds_number)
            for i, threshold in enumerate(thresholds):
                pred_map = rasterize(pred_lines[scores > threshold], height, width)
                tp_indicators_map = self.tp_indicator.indicate(gt_map, pred_map)
                tp[i] += tp_indicators_map.nnz
                fp[i] += pred_map.nnz - tp_indicators_map.nnz
            return BasicMetrics(tp, fp, gt_size)

        stats = sum(
            Parallel(n_jobs=os.cpu_count())(
                delayed(calculate_statistics)(
                    pred_lines, gt_lines, scores, height, width
                )
                for pred_lines, gt_lines, scores, height, width in tzip(
                    pred_lines_batch,
                    gt_lines_batch,
                    line_scores_batch,
                    heights_batch,
                    widths_batch,
                )
            )
        )

        tp = stats.tp
        fp = stats.fp
        gt = stats.gt

        recall = tp / gt
        precision = np.zeros(np.size(tp), dtype=float)
        nonzero_mask = stats.tp + stats.fp != 0
        precision[nonzero_mask] = tp[nonzero_mask] / (
            tp[nonzero_mask] + fp[nonzero_mask]
        )

        threshold_decreasing_order = np.argsort(-thresholds)
        return precision[threshold_decreasing_order], recall[threshold_decreasing_order]


def heatmap_precision_recall_curve(
    pred_lines_batch: List[ArrayNx4[float]],
    gt_lines_batch: List[ArrayNx4[float]],
    line_scores_batch: List[ArrayNx4[float]],
    heights_batch: ArrayN[int],
    widths_batch: ArrayN[int],
    thresholds: ArrayN[float],
) -> Tuple[ArrayN[float], ArrayN[float]]:
    """
    Calculates the Precision-Recall Curve
    :param pred_lines_batch: list of predicted lines for each image
    :param gt_lines_batch: list of ground truth lines for each image
    :param line_scores_batch: list of predicted lines scores for each image
    :param heights_batch: array of heights of each image
    :param widths_batch: array of widths of each image
    :param thresholds: array of line scores thresholds to filter predicted lines
    :return: lists of x (recall) and y (precision) coordinates
    """

    return PrecisionRecallCurve().calculate(
        pred_lines_batch,
        gt_lines_batch,
        line_scores_batch,
        heights_batch,
        widths_batch,
        thresholds,
    )
