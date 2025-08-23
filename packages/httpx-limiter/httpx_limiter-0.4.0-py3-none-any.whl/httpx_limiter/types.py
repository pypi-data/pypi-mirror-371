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


"""Provide additional type definitions."""

import ssl
import typing
from typing import TypedDict

import httpx


class HTTPXAsyncHTTPTransportKeywordArguments(TypedDict, total=False):
    """Keyword arguments for the httpx.AsyncHTTPTransport constructor."""

    verify: ssl.SSLContext | str | bool
    cert: httpx._types.CertTypes | None
    trust_env: bool
    http1: bool
    http2: bool
    limits: httpx._config.Limits
    proxy: httpx._types.ProxyTypes | None
    uds: str | None
    local_address: str | None
    retries: int
    socket_options: typing.Iterable[httpx._transports.default.SOCKET_OPTION] | None
