# Copyright Kevin Deldycke <kevin@deldycke.com> and contributors.
# All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import re
from operator import attrgetter, itemgetter
from pathlib import Path, PurePath
from string import ascii_letters, ascii_lowercase, digits
from types import MethodType

import pytest

from ..managers import pool
from ..platform import OS_DEFINITIONS
from ..version import TokenizedString
from .conftest import MANAGER_IDS

""" Test the structure, data and types returned by all package managers. """

# Parametrization decorators.
all_managers = pytest.mark.parametrize("manager", pool().values(), ids=attrgetter("id"))


def test_manager_count():
    """Check all implemented package managers are accounted for."""
    assert len(pool()) == 14
    assert len(pool()) == len(MANAGER_IDS)
    assert MANAGER_IDS == set(pool())


def test_cached_pool():
    assert pool() == pool()
    assert pool() is pool()


def test_sorted_pool():
    assert list(pool()) == sorted([m.id for m in pool().values()])


@pytest.mark.parametrize("manager_id,manager", pool().items())
def test_ascii_id(manager_id, manager):
    """All package manager IDs should be short ASCII strings."""
    assert manager_id
    assert isinstance(manager_id, str)
    assert manager_id.isascii()
    assert set(manager_id).issubset(ascii_lowercase + digits + "-")
    assert manager_id == manager.id


@all_managers
def test_name(manager):
    """Check all managers have a name."""
    assert manager.name
    assert isinstance(manager.name, str)
    assert set(manager.name).issubset(ascii_letters + digits + "' ")


def test_unique_names():
    assert len({m.name for m in pool().values()}) == len(MANAGER_IDS)


@all_managers
def test_platforms(manager):
    """Check that definitions returns supported platforms as a frozenset."""
    assert manager.platforms
    assert isinstance(manager.platforms, frozenset)
    assert manager.platforms.issubset(OS_DEFINITIONS)


@all_managers
def test_cli_names_type(manager):
    """Check the pointed CLI name and path are file-system compatible."""
    assert manager.cli_names
    assert isinstance(manager.cli_names, list)
    for name in manager.cli_names:
        assert isinstance(name, str)
        assert name.isalnum()
        assert PurePath(name).name == name


@all_managers
def test_virtual(manager):
    """Check the manager as a defined virtual property."""
    assert isinstance(manager.virtual, bool)


@all_managers
def test_cli_search_path(manager):
    assert isinstance(manager.cli_search_path, list)
    assert len(set(manager.cli_search_path)) == len(manager.cli_search_path)
    for search_path in manager.cli_search_path:
        assert isinstance(search_path, str)
        path_obj = Path(search_path).resolve()
        assert path_obj.is_absolute()
        assert not path_obj.is_reserved()
        if path_obj.exists():
            assert path_obj.is_file() or path_obj.is_dir()


@all_managers
def test_cli_path(manager):
    if manager.cli_path is not None:
        assert isinstance(manager.cli_path, Path)
        assert manager.cli_path.is_absolute()
        assert not manager.cli_path.is_reserved()
        assert manager.cli_path.is_file()


@all_managers
def test_global_args_type(manager):
    """Check that definitions returns CLI args as a list of strings."""
    assert isinstance(manager.global_args, list)
    for arg in manager.global_args:
        assert arg
        assert isinstance(arg, str)
        assert set(arg).issubset(ascii_letters + digits + "-=")


@all_managers
def test_requirement(manager):
    """Each manager is required to specify a minimal version."""
    assert isinstance(manager.requirement, str)
    assert set(manager.requirement).issubset(digits + ".")
    # Check provided string is lossless once passed via TokenizedString.
    assert str(TokenizedString(manager.requirement)) == manager.requirement


def test_get_version():
    """Check that method parsing the CLI version returns a string."""
    for manager in pool().values():
        assert isinstance(manager.get_version, MethodType)
        if manager.executable:
            if manager.get_version() is not None:
                assert isinstance(manager.get_version(), str)




@all_managers
def test_version(manager):
    if manager.version is not None:
        assert isinstance(manager.version, TokenizedString)


@all_managers
def test_supported(manager):
    assert isinstance(manager.supported, bool)


@all_managers
def test_executable(manager):
    assert isinstance(manager.executable, bool)


@all_managers
def test_fresh(manager):
    assert isinstance(manager.fresh, bool)


@all_managers
def test_available(manager):
    assert isinstance(manager.available, bool)


@all_managers
def test_cli_type(manager):
    """Check that all methods returning a CLI is either not implemented or returns a list."""
    try:
        result = manager.upgrade_cli("dummy_package_id")
    except Exception as excpt:
        assert isinstance(excpt, NotImplementedError)
    else:
        assert isinstance(result, list)

    try:
        result = manager.upgrade_all_cli()
    except Exception as excpt:
        assert isinstance(excpt, NotImplementedError)
    else:
        assert isinstance(result, list)


@all_managers
def test_installed_type(manager):
    """Check that all installed operations returns a dict of dicts."""
    if manager.available:
        assert isinstance(manager.installed, dict)
        for pkg in manager.installed.values():
            assert isinstance(pkg, dict)
            assert set(pkg) == {"id", "name", "installed_version"}
            assert isinstance(pkg["id"], str)
            assert isinstance(pkg["name"], str)
            if pkg["installed_version"] is not None:
                assert isinstance(pkg["installed_version"], TokenizedString)


@all_managers
def test_search_type(manager):
    """Check that all search operations returns a dict of dicts."""
    if manager.available:
        matches = manager.search("python", extended=True, exact=False)
        assert isinstance(matches, dict)
        for pkg in matches.values():
            assert isinstance(pkg, dict)
            assert set(pkg) == {"id", "name", "latest_version"}
            assert isinstance(pkg["id"], str)
            assert isinstance(pkg["name"], str)
            if pkg["latest_version"] is not None:
                assert isinstance(pkg["latest_version"], TokenizedString)


@all_managers
def test_outdated_type(manager):
    """Check that all outdated operations returns a dict of dicts."""
    if manager.available:
        try:
            result = manager.outdated
        except Exception as excpt:
            assert isinstance(excpt, NotImplementedError)
        else:
            assert isinstance(result, dict)
            for pkg in manager.outdated.values():
                assert isinstance(pkg, dict)
                assert set(pkg) == {"id", "name", "installed_version", "latest_version"}
                assert isinstance(pkg["id"], str)
                assert isinstance(pkg["name"], str)
                if pkg["installed_version"] is not None:
                    assert isinstance(pkg["installed_version"], TokenizedString)
                assert isinstance(pkg["latest_version"], TokenizedString)


@all_managers
def test_sync_type(manager):
    """Check that sync operation return nothing."""
    if manager.available:
        assert isinstance(manager.sync, MethodType)
        assert manager.sync() is None


@all_managers
def test_cleanup_type(manager):
    """Check that cleanup operation return nothing."""
    if manager.available:
        assert isinstance(manager.cleanup, MethodType)
        assert manager.cleanup() is None
