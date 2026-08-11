from django.test import SimpleTestCase

from .apps import CommandsConfig


class CommandsConfigTests(SimpleTestCase):
    def test_app_name_is_commands(self):
        self.assertEqual(CommandsConfig.name, "commands")
