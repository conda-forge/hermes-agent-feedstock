# Optional features in the Conda package

The Conda package keeps Python noarch builds and omits integrations whose
packages are not yet available on conda-forge:

- `browser-harness==0.1.13`: browser_exec is unavailable unless this optional
  engine is installed. Python metadata exposes the `browser-automation` extra.
- `firecrawl-anydoc==0.2.4`: extended document extraction (PDF, PowerPoint,
  legacy Office, OpenDocument, RTF and EPUB) requires this optional converter.
  The existing `doc-extract` extra is retained. Notebook, DOCX, XLSX and SQLite
  extraction remain available without it. Reading a document never installs
  the converter automatically.
- The four `winrt-windows-*` projections used by the Windows Store/App Installer
  updater are omitted. Conda owns package updates; the install stamp declares
  the external update mechanism.

The Python extras describe optional dependencies; they are not separate Conda
outputs. Installing them with another package manager is outside this recipe's
validation. In particular, upstream's uv lock overrides browser-harness's
Pillow pin with Pillow 13, so a plain pip extras install is not guaranteed to
resolve. This patch does not change Hermes's other version pins.

`test_optional_features.py` checks the installed metadata and bundled lock,
missing/present converter behavior, basic document extraction, and browser
availability without spawning a browser or installing dependencies.
