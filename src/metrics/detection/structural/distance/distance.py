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

from abc import ABC, abstractmethod

from src.typing import ArrayNx2x2, ArrayNxM


class Distance(ABC):
    @abstractmethod
    def calculate(
        self, ffirst_lines: ArrayNx2x2[np.float], second_lines: ArrayNx2x2[np.float]
    ) -> ArrayNxM[np.float]:
        pass
