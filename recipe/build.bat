@echo on
setlocal

@REM Preserve upstream workspace overrides and the reviewed dependency lock.
call pnpm --filter web... --filter hermes-tui... install --frozen-lockfile --ignore-scripts || exit /b 1

call pnpm --dir web build || exit /b 1
call pnpm --dir ui-tui build || exit /b 1

@REM Generate notices from the exact production dependencies used for the bundled assets.
call pnpm --filter web --filter hermes-tui licenses list --json --prod > pnpm-licenses.json || exit /b 1
call pnpm-licenses generate-disclaimer --json-input-file pnpm-licenses.json -o "%SRC_DIR%\third-party-licenses.txt" || exit /b 1
del /Q pnpm-licenses.json

if not exist "hermes_cli\tui_dist" mkdir "hermes_cli\tui_dist" || exit /b 1
xcopy /E /H /I /Y "ui-tui\dist" "hermes_cli\tui_dist" || exit /b 1

@REM Discard the generated skill index.
if exist "skills\index-cache" rmdir /S /Q "skills\index-cache"

set HERMES_CONDA_BUILD=1
"%PYTHON%" scripts\write_install_stamp.py --output install-stamp.json --base-version 0.23.2 --distance 0 --commit ae2a81ccc00e9b7c06301523e5bb09608397149c --source build --update-mechanism external || exit /b 1
"%PYTHON%" -m pip install . -vv --no-deps --no-build-isolation || exit /b 1

@REM Stage the resource trees omitted by the upstream wheel.
"%PYTHON%" "%RECIPE_DIR%\install_resources.py" || exit /b 1
