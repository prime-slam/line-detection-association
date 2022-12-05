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

from src.metrics.detection.structural.distance.distance import Distance
from src.typing import ArrayNx2x2, ArrayNxM


class StructuralDistance(Distance):
    def calculate(
        self, first_lines: ArrayNx2x2[np.float], second_lines: ArrayNx2x2[np.float]
    ) -> ArrayNxM[np.float]:
        endpoint_distances = (
            (first_lines[:, np.newaxis, :, np.newaxis] - second_lines[:, np.newaxis])
            ** 2
        ).sum(-1)

        structural_distances = np.minimum(
            endpoint_distances[..., 0, 0] + endpoint_distances[..., 1, 1],
            endpoint_distances[..., 0, 1] + endpoint_distances[..., 1, 0],
        )

        return structural_distances
