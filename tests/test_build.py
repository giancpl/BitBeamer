"""Portable launcher contract tests; no TeX distribution or Docker is needed."""

import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import asset_library
import build


class LauncherTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='bitbeamer project ')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        (self.root / 'assets').mkdir()
        asset_library.prepare(self.root)
        (self.root / 'main.tex').write_text('test document', encoding='utf-8')
        self.stdout, self.stderr = io.StringIO(), io.StringIO()
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(sys, 'stdout', self.stdout).start()
        mock.patch.object(sys, 'stderr', self.stderr).start()

    def test_missing_native_tools_never_invoke_docker(self):
        with mock.patch.object(build.shutil, 'which', return_value=None), mock.patch.object(build.subprocess, 'run') as run:
            self.assertEqual(build.main(['--backend', 'native'], root=self.root), 1)
            run.assert_not_called()
        self.assertIn('Missing native tools', self.stderr.getvalue())

    def test_native_absolute_paths_with_spaces_and_force(self):
        document = self.root / 'slides with spaces.tex'
        document.write_text('test', encoding='utf-8')
        with mock.patch.object(build.shutil, 'which', side_effect=lambda name: name), mock.patch.object(build.subprocess, 'run') as run:
            self.assertEqual(build.main([str(document), 'output with spaces', '--force', '--backend', 'native'], root=self.root), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[0], 'latexmk')
        self.assertIn('-g', command)
        self.assertIn('-outdir=' + (self.root / 'output with spaces').as_posix(), command)
        self.assertEqual(command[-1], './slides with spaces.tex')
        self.assertEqual(run.call_args.kwargs['cwd'], self.root)
        self.assertNotIn('shell', run.call_args.kwargs)

    def test_failed_rebuild_restores_previous_pdf_after_compiler_truncates_it(self):
        output = self.root / 'build'
        output.mkdir()
        pdf = output / 'main.pdf'
        previous = b'%PDF-1.7 last successful presentation'
        pdf.write_bytes(previous)

        def fail(command, **kwargs):
            pdf.write_bytes(b'%PDF-1.7 incomplete replacement')
            raise subprocess.CalledProcessError(1, command)

        with mock.patch.object(build, 'native_tools', return_value='latexmk'), \
                mock.patch.object(build.subprocess, 'run', side_effect=fail):
            self.assertEqual(build.main(['--backend', 'native'], root=self.root), 1)
        self.assertEqual(pdf.read_bytes(), previous)
        self.assertFalse(list(output.glob('.bitbeamer-pdf-*')))

    def test_failed_first_build_does_not_leave_a_partial_pdf(self):
        pdf = self.root / 'build/main.pdf'

        def fail(command, **kwargs):
            pdf.write_bytes(b'%PDF-1.7 incomplete first build')
            raise subprocess.CalledProcessError(1, command)

        with mock.patch.object(build, 'native_tools', return_value='latexmk'), \
                mock.patch.object(build.subprocess, 'run', side_effect=fail):
            self.assertEqual(build.main(['--backend', 'native'], root=self.root), 1)
        self.assertFalse(pdf.exists())

    def test_nested_personal_documents_get_unique_default_outputs(self):
        source = self.root / 'presentations/my-talk/main.tex'
        source.parent.mkdir(parents=True)
        source.write_text('test', encoding='utf-8')
        with mock.patch.object(build.shutil, 'which', side_effect=lambda name: name), mock.patch.object(build.subprocess, 'run') as run:
            self.assertEqual(build.main([str(source), '--backend', 'native'], root=self.root), 0)
        self.assertIn('-outdir=' + (self.root / 'build/presentations/my-talk').as_posix(), run.call_args.args[0])

    def test_included_file_build_targets_its_root_and_isolated_pdf(self):
        source = self.root / 'presentations/my-talk/main.tex'
        fragment = source.parent / 'layouts/box with spaces.tex'
        fragment.parent.mkdir(parents=True)
        source.write_text('test document', encoding='utf-8')
        fragment.write_text('% !TEX root = ../main.tex\nFragment', encoding='utf-8')
        with mock.patch.object(build, 'native_tools', return_value='latexmk'), \
                mock.patch.object(build.subprocess, 'run') as run:
            self.assertEqual(build.main([str(fragment), '--backend', 'native'], root=self.root), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[-1], './presentations/my-talk/main.tex')
        self.assertIn('-outdir=' + (self.root / 'build/presentations/my-talk').as_posix(), command)

    def test_root_comment_cycle_stops_before_running_compiler(self):
        (self.root / 'main.tex').write_text('% !TEX root = other.tex', encoding='utf-8')
        (self.root / 'other.tex').write_text('% !TEX root = main.tex', encoding='utf-8')
        with mock.patch.object(build.subprocess, 'run') as run:
            self.assertEqual(build.main(['--backend', 'native'], root=self.root), 1)
        run.assert_not_called()
        self.assertIn('Cyclic TeX root', self.stderr.getvalue())

    def test_root_comment_cannot_escape_the_checkout(self):
        (self.root / 'main.tex').write_text('% !TEX root = ../outside.tex', encoding='utf-8')
        with mock.patch.object(build.subprocess, 'run') as run:
            self.assertEqual(build.main(['--backend', 'native'], root=self.root), 1)
        run.assert_not_called()
        self.assertIn('inside the project', self.stderr.getvalue())

    def test_editor_pdf_opening_reuses_canonical_path_without_waiting(self):
        pdf = self.root / 'build/folder with spaces/main.pdf'
        with mock.patch.dict(build.os.environ, {'VSCODE_PID': '123'}, clear=True), \
                mock.patch.object(build.sys, 'platform', 'linux'), \
                mock.patch.object(build.shutil, 'which', return_value='/usr/bin/code'), \
                mock.patch.object(build.subprocess, 'run') as run:
            build.open_pdf(pdf)
            build.open_pdf(pdf)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[0], run.call_args_list[1])
        self.assertEqual(run.call_args.args[0], ['/usr/bin/code', '--reuse-window', str(pdf.resolve())])
        self.assertNotIn('shell', run.call_args.kwargs)
        self.assertNotIn('--wait', run.call_args.args[0])

    def test_windows_editor_pdf_opening_avoids_batch_shell_for_special_paths(self):
        install = self.root / 'VS Code'
        (install / 'bin').mkdir(parents=True)
        (install / 'resources/app/out').mkdir(parents=True)
        (install / 'Code.exe').write_bytes(b'cli executable')
        (install / 'resources/app/out/cli.js').write_text('// CLI', encoding='utf-8')
        cmd = install / 'bin/code.cmd'
        cmd.write_text('@echo off', encoding='utf-8')
        pdf = self.root / 'talk&notes/main.pdf'
        with mock.patch.dict(build.os.environ, {'VSCODE_PID': '123'}, clear=True), \
                mock.patch.object(build.sys, 'platform', 'win32'), \
                mock.patch.object(build.shutil, 'which', return_value=str(cmd)), \
                mock.patch.object(build.subprocess, 'run') as run:
            build.open_pdf(pdf)
        self.assertEqual(run.call_args.args[0], [str(install / 'Code.exe'),
                         str(install / 'resources/app/out/cli.js'), '--reuse-window', str(pdf.resolve())])
        self.assertEqual(run.call_args.kwargs['env']['ELECTRON_RUN_AS_NODE'], '1')
        self.assertNotIn('shell', run.call_args.kwargs)

    def test_native_setup_does_not_compile_or_create_output(self):
        with mock.patch.object(build.shutil, 'which', side_effect=lambda name: name), mock.patch.object(build.subprocess, 'run') as run:
            self.assertEqual(build.main(['--backend', 'native', '--setup'], root=self.root), 0)
            run.assert_not_called()
        self.assertFalse((self.root / 'build').exists())

    def test_stale_artwork_stops_before_any_compiler_invocation(self):
        (self.root / 'assets/new.svg').write_text('<svg/>', encoding='utf-8')
        with mock.patch.object(build.subprocess, 'run') as run:
            self.assertEqual(build.main([], root=self.root), 1)
            run.assert_not_called()
        self.assertIn('prepare-assets.py', self.stderr.getvalue())

    def test_default_wrapper_checks_studio_before_compiling(self):
        (self.root/'main.tex').write_text(r'\input{main-studio.tex}', encoding="utf-8")
        (self.root/'main-studio.tex').write_text(r'\usetheme{bitpolito-studio}', encoding="utf-8")
        with mock.patch.object(build,'prepare_studio',side_effect=RuntimeError('Stale Studio artwork')) as prepare, \
                mock.patch.object(build.subprocess,'run') as run:
            self.assertEqual(build.main([],root=self.root),1)
            prepare.assert_called_once_with(self.root,check=True)
            run.assert_not_called()
        self.assertIn('Stale Studio artwork',self.stderr.getvalue())

    def test_external_document_is_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            doc = Path(outside) / 'outside.tex'
            doc.write_text('test', encoding='utf-8')
            with mock.patch.object(build.subprocess, 'run') as run:
                self.assertEqual(build.main([str(doc)], root=self.root), 1)
                run.assert_not_called()

    def test_default_docker_builds_image_only_when_missing(self):
        responses = [subprocess.CompletedProcess([], 0), subprocess.CompletedProcess([], 1),
                     subprocess.CompletedProcess([], 0), subprocess.CompletedProcess([], 0)]
        with mock.patch.object(build.shutil, 'which', return_value='docker'), mock.patch.object(build.subprocess, 'run', side_effect=responses) as run:
            self.assertEqual(build.main([], root=self.root), 0)
        commands = [call.args[0] for call in run.call_args_list]
        self.assertEqual(commands[0], ['docker', 'info'])
        self.assertEqual(commands[2][:2], ['docker', 'build'])
        self.assertEqual(commands[3][:3], ['docker', 'run', '--rm'])
        self.assertIn('none', commands[3])
        self.assertIn(f'type=bind,source={self.root},target=/source,readonly', commands[3])

    def test_missing_default_docker_reports_native_option_without_falling_back(self):
        with mock.patch.object(build.shutil, 'which', return_value=None), \
                mock.patch.object(build, 'native_tools') as native, \
                mock.patch.object(build.subprocess, 'run') as run:
            self.assertEqual(build.main([], root=self.root), 1)
            native.assert_not_called()
            run.assert_not_called()
        self.assertIn('--backend native', self.stderr.getvalue())

    def test_docker_setup_prepares_image_without_compiling(self):
        responses = [subprocess.CompletedProcess([], 0), subprocess.CompletedProcess([], 1),
                     subprocess.CompletedProcess([], 0)]
        with mock.patch.object(build.shutil, 'which', return_value='docker'), \
                mock.patch.object(build.subprocess, 'run', side_effect=responses) as run:
            self.assertEqual(build.main(['--setup'], root=self.root), 0)
        self.assertEqual(run.call_args.args[0][:2], ['docker', 'build'])
        self.assertFalse((self.root / 'build').exists())

    def test_windows_docker_command_omits_unix_user_and_normalizes_document(self):
        with mock.patch.object(build.sys, 'platform', 'win32'):
            command = build.docker_command('docker', self.root, self.root / 'build', Path('nested/slides.tex'), 'image')
        self.assertNotIn('--user', command)
        self.assertEqual(command[-1], './nested/slides.tex')

    def test_platform_installation_instructions(self):
        self.assertIn('Windows', build.install_help('win32'))
        self.assertIn('MacTeX', build.install_help('darwin'))
        self.assertIn('apt-get', build.install_help('linux'))

    def test_editor_tasks_use_launcher_with_docker_default(self):
        data = json.loads((ROOT / '.vscode/tasks.json').read_text(encoding='utf-8'))
        default = next(task for task in data['tasks'] if task.get('group', {}).get('isDefault'))
        self.assertIn('Studio',default['label'])
        self.assertIn('${file}', default['args'])
        self.assertIn('--open', default['args'])
        self.assertIn(r'\input{main-studio.tex}',(ROOT/'main.tex').read_text(encoding="utf-8"))
        self.assertIn('${workspaceFolder}/scripts/build.py', default['args'])
        self.assertNotIn('--backend', default['args'])
        self.assertNotIn('--backend', default['windows']['args'])
        self.assertEqual(default['windows']['command'], 'py')
        recipes = json.loads((ROOT / '.vscode/settings.json').read_text(encoding='utf-8'))
        self.assertIn('Docker', recipes['latex-workshop.latex.recipes'][0]['name'])
        self.assertIn('%RELATIVE_DIR%', recipes['latex-workshop.latex.outDir'])
        for tool in recipes['latex-workshop.latex.tools']:
            self.assertIn('%DOC_EXT%', tool['args'])
            self.assertIn('--open', tool['args'])
            if tool['name'].startswith('bitbeamer-native'):
                self.assertEqual(tool['args'][-2:], ['--backend', 'native'])


if __name__ == '__main__':
    unittest.main()
