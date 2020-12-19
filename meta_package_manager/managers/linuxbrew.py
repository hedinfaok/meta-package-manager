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
import os
from shutil import which
from pathlib import Path

import simplejson as json
from boltons.cacheutils import cachedproperty

# from ..base import PackageManager
from .homebrew import Brew
from ..platform import LINUX
# from ..version import parse_version
from . import logger

class Linuxbrew(Brew):

    """Virutal package manager used by brew on Linux

    Homebrew was formerly referred to as Linuxbrew when running on Linux or WSL.
    """

    platforms = frozenset([LINUX])
    name = "Linuxbrew Formulae"

    @cachedproperty
    def cli_path(self):
        """Fully qualified path to the package manager CLI.

        Automatically search the location of the CLI in the system. Only checks
        if the file exists. Its executability will be assessed later. See the
        ``self.executable`` method below.

        Returns `None` if CLI is not found or is not a file.
        """
        # Check if the path exist in any of the environment locations.
        env_path = ":".join(self.cli_search_path + [os.getenv("PATH")])
        cli_path = which(self.cli_name, mode=os.F_OK, path=env_path)
        if not cli_path:
            logger.debug(f"{self.cli_name} CLI not found.")
            return

        # Normalize CLI path and check it is a file. Do not follow symlinks.
        # Homebrew on linux uses the symlink path to set environment variables.
        cli_path = Path.cwd() / Path(cli_path)
        logger.debug(f"CLI found at {cli_path}")

        if not cli_path.is_file():
            logger.warning(f"{cli_path} is not a file.")
            return

        return cli_path
