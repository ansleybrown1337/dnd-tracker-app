# Development

AJ's Character Manager targets Python 3.12 and uses uv for environments and
dependency locking. The application stack also includes Flet, SQLite, pytest,
and Ruff.

## Current Phase 1 setup

The repository contains a runnable Flet entry point, an application and domain
layer, a versioned SQLite schema, a small catalog, and automated tests. Flet
1.0.0 and its development tools are pinned so that local and CI behavior use
the same release.

Install Python 3.12 and [uv](https://docs.astral.sh/uv/) once on the development
computer. On macOS, uv can be installed with `brew install uv` or its official
standalone installer. Open a new terminal and verify `uv --version`, then
prepare the locked environment with:

```shell
uv sync --locked --group dev
```

This creates or reuses the repository's `.venv`. Run it after cloning and when
`pyproject.toml` or `uv.lock` changes; it is not required for every shell
session.

Launch the desktop application with:

```shell
uv run flet run src/main.py
```

For an already-synced checkout, the environment can also be invoked directly:

```shell
./.venv/bin/flet run src/main.py
```

Run the repository checks with:

```shell
uv run ruff check src tests
uv run ruff format --check src tests
uv run pytest -q
```

The app creates its database on first launch. `AJCM_DATA_DIR` can override the
data directory for development and testing. Otherwise the app uses Flet's data
directory when supplied, then a platform-specific user data directory. Local
databases and Flet build output are ignored by Git.

## Desktop builds

Flet packaging metadata lives in `pyproject.toml`. A manual GitHub Actions
workflow builds unsigned prototype archives for macOS and Windows. It does not
publish a release, sign binaries, or notarize the macOS app.

To attempt a local platform build with the required native toolchain installed:

```shell
uv run flet build macos --python-version 3.12
uv run flet build windows --python-version 3.12
```

Run only the command for the host platform. Phase 1 acceptance still requires
running the defining persistence workflow against both packaged artifacts.

SQLite is part of Python's standard library. Application databases and Flet
build output must remain outside version control, as configured in
`.gitignore`.

## Contribution discipline

Keep work within the current phase in the [roadmap](ROADMAP.md). Add only the
package structure needed by implemented behavior. Rules or catalog changes
must follow [Source of Truth](SOURCE_OF_TRUTH.md) and record provenance.
