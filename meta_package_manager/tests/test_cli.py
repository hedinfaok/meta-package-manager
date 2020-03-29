# -*- coding: utf-8 -*-
#
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

import textwrap
import unittest

import simplejson as json

from .. import __version__
from .case import CLITestCase, skip_destructive, unless_macos


class TestCLI(CLITestCase):

    def test_bare_call(self):
        result = self.invoke()
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--help", result.output)

    def test_main_help(self):
        result = self.invoke('--help')
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--help", result.output)

    def test_version(self):
        result = self.invoke('--version')
        self.assertEqual(result.exit_code, 0)
        self.assertIn(__version__, result.output)


class TestCLISubcommand(CLITestCase):

    """ Base class to define tests common to each subcommands. """

    subcommand_args = []

    @classmethod
    def setUpClass(klass):
        if not klass.subcommand_args:
            raise unittest.SkipTest('Skip generic test class.')

    def test_main_help(self):
        result = self.invoke(*(self.subcommand_args + ['--help']))
        self.assertEqual(result.exit_code, 0)
        self.assertIn("--help", result.output)

    def test_verbosity(self):
        result = self.invoke('--verbosity', 'DEBUG', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("debug:", result.output)

        result = self.invoke('--verbosity', 'INFO', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("debug:", result.output)

    def test_simple_call(self):
        result = self.invoke(*self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        return result

    def test_manager_selection(self):
        result = self.invoke('--manager', 'apm', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn(" apm", result.output)
        self.assertNotIn(" npm", result.output)
        self.assertNotIn(" apt", result.output)
        self.assertNotIn(" brew", result.output)
        self.assertNotIn(" composer", result.output)
        self.assertNotIn(" pip2", result.output)
        self.assertNotIn(" pip3", result.output)
        self.assertNotIn(" gem", result.output)
        self.assertNotIn(" flatpak", result.output)
        self.assertNotIn(" opkg", result.output)
        self.assertNotIn(" yarn", result.output)

    def test_manager_duplicate_selection(self):
        result = self.invoke(
            '--manager', 'apm', '--manager', 'apm', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn(" apm", result.output)
        self.assertNotIn(" npm", result.output)
        self.assertNotIn(" apt", result.output)
        self.assertNotIn(" brew", result.output)
        self.assertNotIn(" composer", result.output)
        self.assertNotIn(" pip2", result.output)
        self.assertNotIn(" pip3", result.output)
        self.assertNotIn(" gem", result.output)
        self.assertNotIn(" flatpak", result.output)
        self.assertNotIn(" opkg", result.output)
        self.assertNotIn(" yarn", result.output)

    def test_manager_multiple_selection(self):
        result = self.invoke(
            '--manager', 'apm', '--manager', 'gem', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn(" apm", result.output)
        self.assertIn(" gem", result.output)
        self.assertNotIn(" npm", result.output)
        self.assertNotIn(" apt", result.output)
        self.assertNotIn(" brew", result.output)
        self.assertNotIn(" composer", result.output)
        self.assertNotIn(" pip2", result.output)
        self.assertNotIn(" pip3", result.output)
        self.assertNotIn(" flatpak", result.output)
        self.assertNotIn(" opkg", result.output)
        self.assertNotIn(" yarn", result.output)

    def test_manager_exclusion(self):
        result = self.invoke('--exclude', 'apm', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn(" apm", result.output)
        self.assertIn(" gem", result.output)
        self.assertIn(" npm", result.output)
        self.assertIn(" apt", result.output)
        self.assertIn(" brew", result.output)
        self.assertIn(" composer", result.output)
        self.assertIn(" pip2", result.output)
        self.assertIn(" pip3", result.output)
        self.assertIn(" flatpak", result.output)
        self.assertIn(" opkg", result.output)
        self.assertIn(" yarn", result.output)

    def test_manager_duplicate_exclusion(self):
        result = self.invoke(
            '--exclude', 'apm', '--exclude', 'apm', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn(" apm", result.output)
        self.assertIn(" gem", result.output)
        self.assertIn(" npm", result.output)
        self.assertIn(" apt", result.output)
        self.assertIn(" brew", result.output)
        self.assertIn(" composer", result.output)
        self.assertIn(" pip2", result.output)
        self.assertIn(" pip3", result.output)
        self.assertIn(" flatpak", result.output)
        self.assertIn(" opkg", result.output)
        self.assertIn(" yarn", result.output)

    def test_manager_multiple_exclusion(self):
        result = self.invoke(
            '--exclude', 'apm', '--exclude', 'gem', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn(" apm", result.output)
        self.assertNotIn(" gem", result.output)
        self.assertIn(" npm", result.output)
        self.assertIn(" apt", result.output)
        self.assertIn(" brew", result.output)
        self.assertIn(" composer", result.output)
        self.assertIn(" pip2", result.output)
        self.assertIn(" pip3", result.output)
        self.assertIn(" flatpak", result.output)
        self.assertIn(" opkg", result.output)
        self.assertIn(" yarn", result.output)

    def test_manager_selection_priority(self):
        result = self.invoke(
            '--manager', 'apm', '--exclude', 'gem', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn(" apm", result.output)
        self.assertNotIn(" gem", result.output)
        self.assertNotIn(" npm", result.output)
        self.assertNotIn(" apt", result.output)
        self.assertNotIn(" brew", result.output)
        self.assertNotIn(" composer", result.output)
        self.assertNotIn(" pip2", result.output)
        self.assertNotIn(" pip3", result.output)
        self.assertNotIn(" flatpak", result.output)
        self.assertNotIn(" opkg", result.output)
        self.assertNotIn(" yarn", result.output)

    def test_manager_selection_exclusion_override(self):
        result = self.invoke(
            '--manager', 'apm', '--exclude', 'apm', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn(" apm", result.output)
        self.assertNotIn(" gem", result.output)
        self.assertNotIn(" npm", result.output)
        self.assertNotIn(" apt", result.output)
        self.assertNotIn(" brew", result.output)
        self.assertNotIn(" composer", result.output)
        self.assertNotIn(" pip2", result.output)
        self.assertNotIn(" pip3", result.output)
        self.assertNotIn(" flatpak", result.output)
        self.assertNotIn(" opkg", result.output)
        self.assertNotIn(" yarn", result.output)


class TestCLITableRendering(TestCLISubcommand):

    """ Test subcommands whose output is a configurable table.

    A table output is also allowed to be rendered as JSON.
    """

    def test_simple_call(self):
        result = super(TestCLITableRendering, self).test_simple_call()
        self.assertIn("═════", result.output)

    def test_simple_table_rendering(self):
        result = self.invoke(
            '--output-format', 'simple', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("-----", result.output)

    def test_plain_table_rendering(self):
        result = self.invoke('--output-format', 'plain', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("═════", result.output)
        self.assertNotIn("-----", result.output)

    def test_json_output(self):
        result = self.invoke('--output-format', 'json', *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        return json.loads(result.output)

    def test_json_debug_output(self):
        """ Debug output is expected to be unparseable.

        Because of interleaved debug messages and JSON output.
        """
        result = self.invoke(
            '--output-format', 'json', '--verbosity', 'DEBUG',
            *self.subcommand_args)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("debug:", result.output)
        with self.assertRaises(json.decoder.JSONDecodeError):
            json.loads(result.output)


class TestCLIManagers(TestCLITableRendering):

    subcommand_args = ['managers']

    def test_json_output(self):
        result = super(TestCLIManagers, self).test_json_output()

        self.assertSetEqual(set(result), set([
            'apm', 'apt', 'brew', 'cask', 'composer', 'gem', 'mas', 'npm',
            'pip2', 'pip3', 'flatpak', 'opkg', 'yarn']))

        for manager_id, info in result.items():
            self.assertIsInstance(manager_id, str)
            self.assertIsInstance(info, dict)

            self.assertSetEqual(set(info), set([
                'available', 'cli_path', 'errors', 'executable', 'fresh', 'id',
                'name', 'supported', 'version']))

            self.assertIsInstance(info['available'], bool)
            if info['cli_path'] is not None:
                self.assertIsInstance(info['cli_path'], str)
            self.assertIsInstance(info['errors'], list)
            self.assertIsInstance(info['executable'], bool)
            self.assertIsInstance(info['fresh'], bool)
            self.assertIsInstance(info['id'], str)
            self.assertIsInstance(info['name'], str)
            self.assertIsInstance(info['supported'], bool)
            if info['version'] is not None:
                self.assertIsInstance(info['version'], str)

            self.assertEqual(info['id'], manager_id)


class TestCLISync(TestCLISubcommand):

    subcommand_args = ['sync']


class TestCLIInstalled(TestCLITableRendering):

    subcommand_args = ['installed']

    def test_json_output(self):
        result = super(TestCLIInstalled, self).test_json_output()

        self.assertTrue(set(result).issubset([
            'apm', 'apt', 'brew', 'cask', 'composer', 'gem', 'mas', 'npm',
            'pip2', 'pip3', 'flatpak', 'opkg', 'yarn']))

        for manager_id, info in result.items():
            self.assertIsInstance(manager_id, str)
            self.assertIsInstance(info, dict)

            self.assertSetEqual(set(info), set([
                'errors', 'id', 'name', 'packages']))

            self.assertIsInstance(info['errors'], list)
            self.assertIsInstance(info['id'], str)
            self.assertIsInstance(info['name'], str)
            self.assertIsInstance(info['packages'], list)

            self.assertEqual(info['id'], manager_id)

            for pkg in info['packages']:
                self.assertIsInstance(pkg, dict)

                self.assertSetEqual(set(pkg), set([
                    'id', 'installed_version', 'name']))

                self.assertIsInstance(pkg['id'], str)
                self.assertIsInstance(pkg['installed_version'], str)
                self.assertIsInstance(pkg['name'], str)


class TestCLISearch(TestCLITableRendering):

    subcommand_args = ['search', 'abc']

    def test_json_output(self):
        result = super(TestCLISearch, self).test_json_output()

        self.assertTrue(set(result).issubset([
            'apm', 'apt', 'brew', 'cask', 'composer', 'gem', 'mas', 'npm',
            'pip2', 'pip3', 'flatpak', 'opkg', 'yarn']))

        for manager_id, info in result.items():
            self.assertIsInstance(manager_id, str)
            self.assertIsInstance(info, dict)

            self.assertSetEqual(set(info), set([
                'errors', 'id', 'name', 'packages']))

            self.assertIsInstance(info['errors'], list)
            self.assertIsInstance(info['id'], str)
            self.assertIsInstance(info['name'], str)
            self.assertIsInstance(info['packages'], list)

            self.assertEqual(info['id'], manager_id)

            for pkg in info['packages']:
                self.assertIsInstance(pkg, dict)

                self.assertSetEqual(set(pkg), set([
                    'exact', 'id', 'latest_version', 'name']))

                self.assertIsInstance(pkg['exact'], bool)
                self.assertIsInstance(pkg['id'], str)
                if pkg['latest_version'] is not None:
                    self.assertIsInstance(pkg['latest_version'], str)
                self.assertIsInstance(pkg['name'], str)

    @unless_macos()
    def test_unicode_search(self):
        """ See #16. """
        result = self.invoke('--manager', 'cask', 'search', 'ubersicht')
        self.assertEqual(result.exit_code, 0)
        self.assertIn("ubersicht", result.output)
        # XXX search command is not fetching details package infos like names
        # for now.
        # self.assertIn("Übersicht", result.output)

        result = self.invoke('--manager', 'cask', 'search', 'Übersicht')
        self.assertEqual(result.exit_code, 0)
        self.assertIn("ubersicht", result.output)
        # self.assertIn("Übersicht", result.output)


class TestCLIOutdated(TestCLITableRendering):

    subcommand_args = ['outdated']

    def test_json_output(self):
        result = super(TestCLIOutdated, self).test_json_output()

        self.assertTrue(set(result).issubset([
            'apm', 'apt', 'brew', 'cask', 'composer', 'gem', 'mas', 'npm',
            'pip2', 'pip3', 'flatpak', 'opkg', 'yarn']))

        for manager_id, info in result.items():
            self.assertIsInstance(manager_id, str)
            self.assertIsInstance(info, dict)

            self.assertIsInstance(info['errors'], list)
            self.assertIsInstance(info['id'], str)
            self.assertIsInstance(info['name'], str)
            self.assertIsInstance(info['packages'], list)

            keys = set(['errors', 'id', 'name', 'packages'])
            if 'upgrade_all_cli' in info:
                self.assertIsInstance(info['upgrade_all_cli'], str)
                self.assertGreater(len(info['packages']), 0)
                keys.add('upgrade_all_cli')
            else:
                self.assertEqual(len(info['packages']), 0)

            self.assertSetEqual(set(info), keys)

            self.assertEqual(info['id'], manager_id)

            for pkg in info['packages']:
                self.assertIsInstance(pkg, dict)

                self.assertSetEqual(set(pkg), set([
                    'id', 'installed_version', 'latest_version', 'name',
                    'upgrade_cli']))

                self.assertIsInstance(pkg['id'], str)
                self.assertIsInstance(pkg['installed_version'], str)
                self.assertIsInstance(pkg['latest_version'], str)
                self.assertIsInstance(pkg['name'], str)
                self.assertIsInstance(pkg['upgrade_cli'], str)

    def test_cli_format_plain(self):
        result = self.invoke(
            '--output-format', 'json', 'outdated', '--cli-format', 'plain')
        for outdated in json.loads(result.output).values():
            for infos in outdated['packages']:
                self.assertIsInstance(infos['upgrade_cli'], str)

    def test_cli_format_fragments(self):
        result = self.invoke(
            '--output-format', 'json', 'outdated', '--cli-format', 'fragments')
        for outdated in json.loads(result.output).values():
            for infos in outdated['packages']:
                self.assertIsInstance(infos['upgrade_cli'], list)

    def test_cli_format_bitbar(self):
        result = self.invoke(
            '--output-format', 'json', 'outdated', '--cli-format', 'bitbar')
        for outdated in json.loads(result.output).values():
            for infos in outdated['packages']:
                self.assertIsInstance(infos['upgrade_cli'], str)
                self.assertIn('param1=', infos['upgrade_cli'])

    @skip_destructive()
    def test_unicode_name(self):
        """ See #16. """
        # Install an old version of a package with a unicode name.
        # Old Cask formula for ubersicht 1.0.44.
        formula_url = (
            "https://raw.githubusercontent.com/caskroom/homebrew-cask"
            "/51add049f53225ac2c98f59bbeee5e19c29e6557/Casks/ubersicht.rb")
        code, output, error = self.run_cmd(
            'brew', 'cask', 'install', formula_url)
        self.assertEqual(code, 0)
        self.assertIn('Uebersicht-1.0.44.app', output)
        self.assertFalse(error)

        # Look for reported available upgrade.
        result = self.invoke('--manager', 'cask', 'outdated')
        self.assertEqual(result.exit_code, 0)
        self.assertIn("ubersicht", result.output)
        self.assertIn("Übersicht", result.output)

    @skip_destructive()
    def test_multiple_names(self):
        """ See #26. """
        # Install an old version of a package with multiple names.
        # Old Cask formula for xld 2016.09.20.
        formula_url = (
            "https://raw.githubusercontent.com/caskroom/homebrew-cask"
            "/9e6ca52ab7846c82471df586a930fb60231d63ee/Casks/xld.rb")
        code, output, error = self.run_cmd(
            'brew', 'cask', 'install', formula_url)
        self.assertEqual(code, 0)
        self.assertIn('xld-20160920.dmg', output)
        self.assertFalse(error)

        # Look for reported available upgrade.
        result = self.invoke('--manager', 'cask', 'outdated')
        self.assertEqual(result.exit_code, 0)
        self.assertIn("xld", result.output)
        self.assertIn("X Lossless Decoder", result.output)


class TestCLIUpgrade(TestCLISubcommand):

    subcommand_args = ['upgrade', '--dry-run']

    @skip_destructive()
    def test_full_upgrade(self):
        result = self.invoke('upgrade')
        self.assertEqual(result.exit_code, 0)


class TestCLIBackup(TestCLISubcommand):

    subcommand_args = ['backup', 'mpm-packages.toml']

    def test_export_all_packages_to_file(self):
        result = self.invoke('backup', 'mpm-packages.toml')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('mpm-packages.toml', result.output)

    def test_backup_single_manager(self):
        result = self.invoke('--manager', 'npm', 'backup', 'npm-packages.toml')
        self.assertEqual(result.exit_code, 0)
        with open('npm-packages.toml', 'r') as doc:
            # Check only [npm] section appears in TOML file.
            self.assertSetEqual(
                {l for l in doc.read().split() if l.startswith('[')},
                set(['[npm]']))


class TestCLIRestore(TestCLISubcommand):

    subcommand_args = ['restore', 'dummy.toml']

    def setUp(self, *args, **kwargs):
        """ Create a custom TOML file to feed the CLI with.

        Our dummy file should result in no action as whole sections of
        unrecognized managers are simply ignored.
        """
        toml_content = textwrap.dedent("""\
            [dummy_manager]
            fancy_package = "0.0.1"
            """)

        with open('dummy.toml', 'w') as doc:
            doc.write(toml_content)

        super(TestCLIRestore, self).setUp(*args, **kwargs)

    def test_ignore_dummy_manager(self):
        result = self.invoke('restore', 'dummy.toml')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('dummy.toml', result.output)
        self.assertNotIn('dummy_manager', result.output)

    def test_restore_single_manager(self):
        toml_content = textwrap.dedent("""\
            [pip3]
            fancy_package = "0.0.1"

            [npm]
            dummy_package = "2.2.2"
            """)

        with open('packages.toml', 'w') as doc:
            doc.write(toml_content)

        result = self.invoke('--manager', 'npm', 'restore', 'packages.toml')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('packages.toml', result.output)
        self.assertNotIn('Restore pip3', result.output)
        self.assertIn('Restore npm', result.output)

    def test_restore_excluded_manager(self):
        toml_content = textwrap.dedent("""\
            [pip3]
            fancy_package = "0.0.1"

            [npm]
            dummy_package = "2.2.2"
            """)

        with open('packages.toml', 'w') as doc:
            doc.write(toml_content)

        result = self.invoke('--exclude', 'npm', 'restore', 'packages.toml')
        self.assertEqual(result.exit_code, 0)
        self.assertIn('packages.toml', result.output)
        self.assertIn('Restore pip3', result.output)
        self.assertNotIn('Restore npm', result.output)
