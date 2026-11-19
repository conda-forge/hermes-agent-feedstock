#!/usr/bin/env bash
set -exo pipefail

# Preserve upstream workspace overrides and the reviewed dependency lock.
pnpm --filter web... --filter hermes-tui... install --frozen-lockfile --ignore-scripts

pnpm --dir web build
pnpm --dir ui-tui build

# Generate notices from the exact production dependencies used for the bundled assets.
pnpm --filter web --filter hermes-tui licenses list --json --prod | pnpm-licenses generate-disclaimer --json-input -o third-party-licenses.txt

mkdir -p hermes_cli/tui_dist
cp -R ui-tui/dist/. hermes_cli/tui_dist/

# Discard the generated skill index.
rm -rf skills/index-cache

export HERMES_CONDA_BUILD=1
${PYTHON} scripts/write_install_stamp.py --output install-stamp.json --base-version 0.23.2 --distance 0 --commit ae2a81ccc00e9b7c06301523e5bb09608397149c --source build --update-mechanism external

${PYTHON} -m pip install . -vv --no-deps --no-build-isolation

# Stage the resource trees omitted by the upstream wheel.
${PYTHON} "$RECIPE_DIR/install_resources.py"
