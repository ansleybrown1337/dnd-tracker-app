# Development

AJ's Character Manager targets Python 3.12 and will use uv for environments and
dependency locking. The approved application stack also includes Flet, SQLite,
pytest, and Ruff.

## Current Phase 0 setup

The repository currently contains documentation, `pyproject.toml`, a Python
version declaration, and a package marker. It does not contain a Flet entry
point, SQLite schema, application tests, or a runnable desktop application.

The project metadata currently has no runtime dependencies. Flet is deferred
until Phase 1, when its version can be selected and tested as part of the first
packaged vertical slice. The development dependency group contains pytest and
Ruff.

With Python 3.12 and [uv](https://docs.astral.sh/uv/) installed, the Phase 0
environment can be prepared with:

```shell
uv sync --group dev
```

Useful checks for the current repository are:

```shell
uv run ruff check src
uv run python -c "import aj_character_manager"
```

There are intentionally no executable tests yet. Running pytest before Phase 1
will report that no tests were collected.

## Expected Phase 1 workflow

After Phase 1 begins, its first changes should add a pinned Flet runtime
dependency, real tests, and an application entry point. The expected daily
commands will then be documented from the behavior that actually exists,
likely including:

```shell
uv sync --group dev
uv run ruff check .
uv run pytest
```

Development launch and platform build commands will be added only after the
corresponding entry point and packaging configuration exist. Developers should
not infer support from this document before those changes land.

SQLite is part of Python's standard library. Application databases and Flet
build output must remain outside version control, as configured in
`.gitignore`.

## Contribution discipline

Keep work within the current phase in the [roadmap](ROADMAP.md). Add only the
package structure needed by implemented behavior. Rules or catalog changes
must follow [Source of Truth](SOURCE_OF_TRUTH.md) and record provenance.
