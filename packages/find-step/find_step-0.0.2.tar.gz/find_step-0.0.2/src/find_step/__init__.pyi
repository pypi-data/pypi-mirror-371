# SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
# SPDX-License-Identifier: MIT

import typing

class SupportsFind(typing.Protocol):
    def find(
        self,
        sub,
        start: typing.SupportsIndex | None = None,
        stop: typing.SupportsIndex | None = None,
        /,
    ) -> int: ...

T = typing.TypeVar('T', bound=SupportsFind)

def find(
    s: T,
    sub: T,
    start: typing.SupportsIndex | None = None,
    end: typing.SupportsIndex | None = None,
    step: typing.SupportsIndex | None = None,
    /,
) -> int: ...
