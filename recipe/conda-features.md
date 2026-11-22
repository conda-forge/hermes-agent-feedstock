# Bundled integrations in the Conda package

`browser-harness==0.1.13` and `firecrawl-anydoc==0.2.4` are core runtime
requirements. Browser automation and extended document extraction are enabled
when the Conda environment is installed. Python noarch packaging is retained;
platform-specific dependencies are selected by the environment solver.

Document reads import the installed converter without invoking pip or uv.
A missing or broken converter reports a Conda repair command. The four Windows
Store/App Installer WinRT projections remain omitted because Conda owns updates.

`test_integrations.py` checks installed metadata and the bundled lock, actual
RTF conversion, missing-converter handling, and browser discovery without
launching a browser, plus screenshot resizing with Pillow 13. Browser execution
still requires a configured browser.

## Dependency prerequisites

The browser-harness, fetch-use and firecrawl-anydoc packages must be published
to conda-forge before this build can pass CI. Browser-harness must also allow
Pillow 13 in both its Python metadata and Conda requirements: its upstream
12.3.0 pin conflicts with Hermes. Hermes retains Pillow 13.0.0, as required by
its upstream security override in pyproject.toml. Do not downgrade Pillow to
resolve this conflict.
