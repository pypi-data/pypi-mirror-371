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


"""Provide an abstract repository for rate limiters."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

import httpx

from .async_limiter import AsyncLimiter, PyRateLimiterKeywordArguments
from .rate import Rate


class AbstractRateLimiterRepository(ABC):
    """
    Define the abstract repository for rate limiters.

    This abstract base class provides a framework for managing rate limiters
    based on HTTP requests. It maintains a cache of rate limiters and provides
    methods to retrieve request-specific identifiers, rates, and limiters.

    Subclasses must implement methods to determine how requests are identified
    and what rate limits should be applied to them.

    Methods:
        get_identifier: Return a request-specific identifier.
        get_rates: Return one or more request-specific rates.
        get: Return a request-specific rate limiter.

    """

    def __init__(self, **kwargs: dict[str, object]) -> None:
        super().__init__(**kwargs)
        self._limiters: dict[str, AsyncLimiter] = {}

    @abstractmethod
    def get_identifier(self, request: httpx.Request) -> str:
        """Return a request-specific identifier."""

    @abstractmethod
    def get_rates(self, request: httpx.Request) -> Sequence[Rate]:
        """Return one or more request-specific rates."""

    def _get_limiter_kwargs(
        self,
        request: httpx.Request,  # noqa: ARG002
    ) -> PyRateLimiterKeywordArguments:
        """Return the keyword arguments for creating a rate limiter."""
        return {}

    def get(self, request: httpx.Request) -> AsyncLimiter:
        """Return a request-specific rate limiter."""
        identifier = self.get_identifier(request)

        if identifier not in self._limiters:
            self._limiters[identifier] = AsyncLimiter.create(
                *self.get_rates(request),
                **self._get_limiter_kwargs(request),
            )

        return self._limiters[identifier]
