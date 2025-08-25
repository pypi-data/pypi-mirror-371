# SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
# SPDX-License-Identifier: MIT


def _find(s, sub, start, end, step, /):
    # Check start, end and step have correct types (int|None|SupportsIndex).
    # Check stop has allowed value (step != 0).
    # Raises TypeError or ValueError as appropriate.
    ()[start:end:step]

    if step is None:
        step = 1

    # Artificial limitation to simplify proof of concept & initial testing.
    if step < 0:
        raise ValueError('step cannot be negative (yet)')

    # Start is beyond length of s, there is nothing to search.
    # Matches behaviour of s.find().
    if start is not None and start > len(s):
        return -1

    # Incrementally check indexes that satisfy idx == start + n * step.
    # Repeat until  a hit is found, or the index goes out of bounds.
    start_idx, end_idx, step_idx = slice(start, end, step).indices(len(s))
    while start_idx + len(sub) <= end_idx:
        if s[start_idx:start_idx+len(sub)] == sub:
            return start_idx
        start_idx += step_idx
    else:
        return -1
