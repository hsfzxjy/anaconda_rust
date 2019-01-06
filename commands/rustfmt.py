
# Copyright (C) 2016 - Oscar Campos <oscar.campos@member.fsf.org>
# This program is Free Software see LICENSE file for details

import os
import logging
import tempfile
import traceback
from functools import partial

import sublime
import sublime_plugin

from anaconda_rust.anaconda_lib.anaconda_plugin import is_code
from anaconda_rust.anaconda_lib.anaconda_plugin import ProgressBar
from anaconda_rust.anaconda_lib.anaconda_plugin import Worker, Callback
from anaconda_rust.anaconda_lib.helpers import get_settings, get_window_view
from anaconda_rust.anaconda_lib.helpers import file_directory

import subprocess


class AnacondaRustFmt(sublime_plugin.TextCommand):
    """Execute rustfmt command in a file
    """

    def is_enabled(self, *args):
        return 'rust' in self.view.settings().get('syntax').lower()

    def run(self, edit):

        rustfmt = get_settings(
            self.view, 'rustfmt_binary_path', 'rustfmt'
        )
        if rustfmt == '':
            rustfmt = 'rustfmt'

        region = sublime.Region(0, self.view.size())

        self.code = self.view.substr(
            region
        )

        config_path = get_settings(self.view, 'rust_rustfmt_config_path', '')

        timeout = get_settings(self.view, 'rust_rustfmt_timeout', 1)

        if config_path:
            config_params = ['--config-path', config_path]
        else:
            config_params = []

        fd, path = tempfile.mkstemp(text=False)
        with os.fdopen(fd, 'w') as f:
            f.write(self.code)

        p = subprocess.Popen(
            [
                rustfmt, path,
                # '--emit', 'stdout',
            ] + config_params,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        try:
            stdout, stderr = p.communicate(self.code.encode())
            if p.returncode != 0:
                return

            with open(path, 'r') as f:
                output = f.read()

            self.view.replace(edit, region, output)
        finally:
            try:
                os.remove(path)
            except:
                pass

