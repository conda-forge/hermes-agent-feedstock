"""Install resources no longer included in upstream's Python wheel."""

from pathlib import Path
import shutil
import sysconfig


site_packages = Path(sysconfig.get_path("purelib"))
for directory in ("skills", "optional-skills", "optional-mcps", "locales"):
    shutil.copytree(directory, site_packages / directory, dirs_exist_ok=True)

for directory in ("web_dist", "tui_dist"):
    shutil.copytree(
        Path("hermes_cli") / directory,
        site_packages / "hermes_cli" / directory,
        dirs_exist_ok=True,
    )

# Bundled plugin dashboards are served as static assets at runtime.
for dashboard in Path("plugins").glob("*/dashboard"):
    shutil.copytree(dashboard, site_packages / dashboard, dirs_exist_ok=True)

# Runtime version reporting and the optional-dependency manager read these.
for filename in ("install-stamp.json", "pyproject.toml", "uv.lock"):
    shutil.copy2(filename, site_packages / filename)
