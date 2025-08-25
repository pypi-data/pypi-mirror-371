# SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
# SPDX-License-Identifier: MIT

from ._slow_and_simple import _find


def find(s, sub, start=None, end=None, step=None, /):
    """
    Return the lowest index in *s* where *sub* is found within the slice
    ``s[start:end]`` and the index satisfies ``start + n * step``.
    Return ``-1`` if *sub* is not found.

    Optional arguments *start*, *end*, and *step* are interpreted as in
    slice notation.

    If *step* is ``None``, ``1``, or omitted then behaviour is unchanged from
    ``s.find()`` or ``bytes.find()``.

    >>> find('.a.a.a.a', 'a')  # Same as '.a.a.a.a'.find('a')
    1

    If *step* is 2 or higher then only indexes satisfying ``start + n * step``
    are tried, where ``n >= 0``.

    >>> find('.a.a.a.a', 'a', None, None, 3)  # Tries index 0, then index 3
    3
    >>> find('hello', 'l', 1, None, 2)  # Tries index 1, then index 1 + 2 = 3
    3
    >>> find('abcde', 'c', 1, None, 2)  # Tries index 1, then 3, then 5
    -1

    If *step* is ``O`` then ``ValueError`` is raised, as in slice notation.

    >>> find('abc', 'a', None, None, 0)
    Traceback (most recent call last):
        ...
    ValueError: slice step cannot be zero
    """
    return _find(s, sub, start, end, step)
