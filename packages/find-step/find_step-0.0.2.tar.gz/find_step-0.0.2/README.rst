find-step
=========

find-step supplements Python ``str.find()`` and ``bytes.find()`` methods
with an extra *step* argument - just like slicing has ``s[start:end:step]``.


Usage
-----

If *step* is ``None``, ``1``, or omitted then behaviour is unchanged
from ``str.find()`` or ``bytes.find()``.

.. code:: pycon

   >>> import find_step
   >>> find_step.find('.a.a.a.a', 'a')  # Same as '.a.a.a.a'.find('a')
   1

If *step* is 2 or higher then only indexes satisfying
``start + n * step`` are tried, where ``n >= 0``.

.. code:: pycon

   >>> find_step.find('.a.a.a.a', 'a', None, None, 3)  # Tries index 0, then index 3
   3
   >>> find_step.find('hello', 'l', 1, None, 2)  # Tries index 1, then index 1 + 2 = 3
   3
   >>> find_step.find('abcde', 'c', 1, None, 2)  # Tries index 1, then 3, then 5
   -1

If *step* is ``O`` then ``ValueError`` is raised, as in slice notation.

.. code:: pycon

   >>> find_step.find('abc', 'a', None, None, 0)
   Traceback (most recent call last):
       ...
   ValueError: slice step cannot be zero


Install
-------

.. code:: shell

   python3 -m pip install find-step`

or

.. code:: shell

   uv pip install find-step


License
-------

..
   SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
   SPDX-License-Identifier: MIT

MIT
