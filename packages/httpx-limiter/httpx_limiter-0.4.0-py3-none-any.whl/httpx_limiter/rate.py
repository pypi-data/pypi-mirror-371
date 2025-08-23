# Copyright (c) 2025 Moritz E. Beber
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.


"""Provide a definition of a rate."""

from __future__ import annotations

from datetime import timedelta
from typing import NamedTuple


Number = float | int


class Rate(NamedTuple):
    """Define the rate."""

    magnitude: int
    duration: timedelta

    @classmethod
    def create(cls, magnitude: int = 1, duration: timedelta | Number = 1) -> Rate:
        """Create a rate."""
        magnitude = int(magnitude)

        if not (magnitude > 0):
            msg = f"Magnitude must be strictly positive (provided {magnitude=})."
            raise ValueError(msg)

        if not isinstance(duration, timedelta):
            duration = timedelta(seconds=float(duration))

        if not (duration > timedelta(seconds=0)):
            msg = f"Duration must be strictly positive (provided {duration=})."
            raise ValueError(msg)

        return cls(magnitude=magnitude, duration=duration)

    def in_milliseconds(self) -> int:
        """Return the duration in unit milliseconds."""
        return int(self.duration.total_seconds() * 1_000)
