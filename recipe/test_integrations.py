"""Regression checks for the Conda package's bundled integrations; no network."""
import base64
import importlib.metadata as metadata
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import tomllib
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch
import zipfile

from packaging.requirements import Requirement
from tools import read_extract


class BundledIntegrationsTest(unittest.TestCase):
    def test_base_metadata_includes_integrations(self):
        requirements = [Requirement(r) for r in metadata.requires('hermes-agent')]
        omitted = {'winrt-windows-applicationmodel', 'winrt-windows-foundation',
                   'winrt-windows-foundation-collections', 'winrt-windows-services-store'}
        for platform in ('linux', 'darwin', 'win32'):
            env = {'sys_platform': platform, 'python_version': '3.14',
                   'python_full_version': '3.14.0', 'extra': ''}
            active = {r.name for r in requirements if r.marker is None or r.marker.evaluate(env)}
            self.assertFalse(active & omitted, (platform, active & omitted))
            self.assertIn('openai', active)
            self.assertLessEqual({'browser-harness', 'firecrawl-anydoc'}, active)
        root = Path(read_extract.__file__).resolve().parent.parent
        project = tomllib.loads((root / 'pyproject.toml').read_text())['project']
        lock = tomllib.loads((root / 'uv.lock').read_text())
        package = next(p for p in lock['package'] if p['name'] == 'hermes-agent')
        self.assertFalse({r['name'] for r in package['dependencies']} & omitted)
        self.assertLessEqual(set(package['optional-dependencies']), set(project['optional-dependencies']))
        self.assertEqual(set(package['metadata']['provides-extras']), set(project['optional-dependencies']))
        self.assertLessEqual({'browser-harness', 'firecrawl-anydoc'},
                             {r['name'] for r in package['dependencies']})

    def test_documents_without_converter_do_not_install(self):
        installer = Mock(side_effect=AssertionError('Document reads must not install packages'))
        with patch.dict(sys.modules, {'pm': SimpleNamespace(ensure_import=installer)}), \
                patch.object(read_extract, '_anydoc_module', read_extract._ANYDOC_UNSET), \
                patch.object(read_extract, '_anydoc_failed_at', None), \
                patch.object(read_extract.importlib, 'import_module', side_effect=ModuleNotFoundError('anydoc')):
            self.assertTrue(read_extract.is_extractable_document('document.pdf'))
            with self.assertRaisesRegex(read_extract.ExtractionError, 'firecrawl-anydoc==0.2.4 is missing or broken'):
                read_extract.extract_document_bytes(b'%PDF-1.4', 'document.pdf')
            installer.assert_not_called()
            notebook = {'cells': [{'cell_type': 'markdown', 'source': ['notebook text']}],
                        'metadata': {}, 'nbformat': 4, 'nbformat_minor': 5}
            self.assertIn('notebook text', read_extract.extract_document_bytes(json.dumps(notebook).encode(), 'a.ipynb'))
            data = io.BytesIO()
            with zipfile.ZipFile(data, 'w') as archive:
                archive.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>document text</w:t></w:r></w:p></w:body></w:document>')
            self.assertIn('document text', read_extract.extract_document_bytes(data.getvalue(), 'a.docx'))

    def test_installed_converter_is_used(self):
        import anydoc
        with patch.object(read_extract, '_anydoc_module', read_extract._ANYDOC_UNSET), \
                patch.object(read_extract, '_anydoc_failed_at', None):
            self.assertIs(read_extract._anydoc(), anydoc)
            text = read_extract.extract_document_bytes(br'{\rtf1\ansi Bundled document converter.}', 'a.rtf')
            self.assertIn('Bundled document converter.', text)

    def test_browser_screenshot_resize_with_pillow13(self):
        from PIL import Image
        from browser_harness import helpers
        image = io.BytesIO()
        Image.new('RGB', (80, 40), 'red').save(image, format='PNG')
        response = {'data': base64.b64encode(image.getvalue()).decode()}
        with TemporaryDirectory() as directory, patch.object(helpers, 'cdp', return_value=response):
            output = helpers.capture_screenshot(str(Path(directory) / 'shot.png'), max_dim=20)
            with Image.open(output) as resized:
                self.assertEqual(resized.size, (20, 10))
        self.assertEqual(metadata.version('pillow'), '13.0.0')

    def test_browser_availability_without_spawning(self):
        from tools import browser_use_cli as browser
        with patch.object(browser.subprocess, 'Popen') as spawn:
            self.assertTrue(browser.browser_exec_available())
            self.assertEqual(browser._find_cli(), [sys.executable, '-m', 'browser_harness.run'])
            spawn.assert_not_called()
        with patch.object(browser.importlib.util, 'find_spec', return_value=None), \
                patch.object(browser.subprocess, 'Popen') as spawn:
            self.assertFalse(browser.browser_exec_available())
            self.assertIsNone(browser._find_cli())
            spawn.assert_not_called()
        with patch.object(browser.importlib.util, 'find_spec', return_value=SimpleNamespace(origin=__file__)):
            self.assertTrue(browser.browser_exec_available())
            self.assertEqual(browser._find_cli(), [sys.executable, '-m', 'browser_harness.run'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
