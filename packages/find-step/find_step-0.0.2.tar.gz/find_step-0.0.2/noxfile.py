# SPDX-FileCopyrightText: 2025 Alex Willmer <alex@moreati.org.uk>
# SPDX-License-Identifier: MIT

import nox

# Try `uv venv` first, fallback to `python -m virtualenv`
nox.options.default_venv_backend = 'uv|virtualenv'

# Nox doesn't natively handle PEP 735 dependency groups yet
# https://nox.thea.codes/en/stable/tutorial.html#loading-dependencies-from-pyproject-toml-or-scripts
# https://github.com/wntrblm/nox/issues/845
PYPROJECT = nox.project.load_toml('pyproject.toml')

PYTHONS = [
    '3.10',
    '3.11',
    '3.12',
    '3.13',
    '3.14',
    'pypy3',
]


@nox.session(tags=['clean'])
def cov_clean(session: nox.Session):
    session.install(*nox.project.dependency_groups(PYPROJECT, 'coverage'))
    session.run('coverage', 'erase')


@nox.session(requires=['cov_clean'], tags=['test'])
@nox.parametrize('python', PYTHONS, ids=PYTHONS)
def test(session: nox.Session):
    session.install('-e.', *nox.project.dependency_groups(PYPROJECT, 'test'))
    session.run('coverage', 'run', '-m', 'pytest')


@nox.session(tags=['test'])
def test_readme(session: nox.Session):
    session.install('-e.')
    session.run('python', '-mdoctest', 'README.rst')


@nox.session(requires=['test'], tags=['report'])
def cov_report(session: nox.Session):
    session.install(*nox.project.dependency_groups(PYPROJECT, 'coverage'))
    session.run('coverage', 'combine')
    session.run('coverage', 'report')
    session.run('coverage', 'html')
