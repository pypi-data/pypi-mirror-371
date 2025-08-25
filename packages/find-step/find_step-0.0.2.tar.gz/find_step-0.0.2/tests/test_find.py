# SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
# SPDX-License-Identifier: MIT

import hypothesis as h
import hypothesis.strategies as st
import pytest

import find_step


def bounds(min_value: int | None = None, max_value: int | None = None):
    return st.one_of(st.none(), st.integers(min_value, max_value))


def bounds_invalid_type():
    return st.one_of(
        st.floats(),
        st.complex_numbers(),
        st.decimals(),
        st.fractions(),
        st.text(),
    )


def steps(max_value=None):
    return st.one_of(st.none(), st.integers(min_value=1, max_value=max_value))


def steps_invalid_type():
    return bounds_invalid_type()


def steps_invalid_value():
    return st.integers(max_value=-1)


def steps_passthrough():
    return st.one_of(st.none(), st.just(1))


def text():
    return st.text(alphabet=st.characters())


@h.given(text(), text(), bounds_invalid_type(), bounds(), steps())
def test_invalid_start_type(s, sub, start, end, step):
    with pytest.raises(TypeError):
        find_step.find(s, sub, start)
    with pytest.raises(TypeError):
        find_step.find(s, sub, start, end)
    with pytest.raises(TypeError):
        find_step.find(s, sub, start, end, step)


@h.given(text(), text(), bounds(), bounds_invalid_type(), steps())
def test_invalid_end_type(s, sub, start, end, step):
    with pytest.raises(TypeError):
        find_step.find(s, sub, start, end)
    with pytest.raises(TypeError):
        find_step.find(s, sub, start, end, step)


@h.given(text(), text(), bounds(), bounds(), steps_invalid_type())
def test_invalid_step_type(s, sub, start, end, step):
    with pytest.raises(TypeError):
        find_step.find(s, sub, start, end, step)


@h.given(text(), text(), bounds(), bounds(), steps_invalid_value())
def test_invalid_step_value(s, sub, start, end, step):
    with pytest.raises(ValueError):
        find_step.find(s, sub, start, end, step)


@h.given(text(), text())
def test_passthrough(s, sub):
    assert s.find(sub) == find_step.find(s, sub)


@h.given(text(), text(), bounds())
def test_passthrough_start(s, sub, start):
    assert s.find(sub, start) == find_step.find(s, sub, start)


@h.given(text(), text(), bounds(), bounds())
def test_passthrough_start_end(s, sub, start, end):
    assert s.find(sub, start, end) == find_step.find(s, sub, start, end)


@h.given(text(), text(), bounds(), bounds(), steps_passthrough())
def test_passthrough_start_end_step(s, sub, start, end, step):
    assert s.find(sub, start, end) == find_step.find(s, sub, start, end)
    assert s.find(sub, start, end) == find_step.find(s, sub, start, end, step)


@h.given(s=text(), sub=text(), start=st.integers(min_value=0), end=bounds(), step=steps())
def test_start_gt_len_s(s, sub, start, end, step):
    h.assume(start > len(s))
    assert s.find(sub, start, end) == find_step.find(s, sub, start, end, step)

@h.example('abab', 'a', 2, 1, 2)
@h.given(s=text(), sub=text(), start=st.integers(min_value=1), end=st.integers(min_value=0), step=steps())
def test_start_gt_end(s, sub, start, end, step):
    h.assume(start > end)
    assert -1 == s.find(sub, start, end) == find_step.find(s, sub, start, end, step)


@h.given(s=text(), sub=text(), start=bounds(), step=steps())
def test_end_zero(s, sub, start, step):
    assert s.find(sub, start, 0) == find_step.find(s, sub, start, 0, step)


@h.given(text(), text(), bounds(), bounds(), steps())
def test_returns_int(s, sub, start, end, step):
    assert type(find_step.find(s, sub, start, end, step)) is int


@h.given(text(), text(), bounds(), bounds(), st.integers(min_value=2))
def test_when_step_find_hits_always_on_valid_offset(s, sub, start, end, step):
    find_step_idx = find_step.find(s, sub, start, end, step)
    h.assume(find_step_idx != -1)
    find_idx = s.find(sub, start, end)
    assert find_idx != -1
    assert find_step_idx >= find_idx
    if start is None:
        assert find_step_idx % step == 0
    elif start >= 0:
        assert (find_step_idx - start) % step == 0

@pytest.mark.parametrize(
    ['expected', 's', 'sub', 'start', 'end', 'step'],
    [
        (0,  'abc', 'ab', None, None, 2),
        (3,  'abcabc', 'ab', 1, None, None),
        (3,  'abcabc', 'ab', 1, None, 2),
        (-1, 'abcabc', 'ab', 1, None, 3),
        (5,  'abcabc', 'c', 1, None, 2),
        (-1, 'abcabc', 'c', 1, 4, 2),
    ],
)
def test_selected_examples(expected, s, sub, start, end, step):
    assert expected == find_step.find(s, sub, start, end, step)
