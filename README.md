# AJ's Character Manager

An open source character manager for D&D players, with offline rules support
and homebrew content creation.

> **Project status:** Early development. The repository currently contains the
> project foundation and design documentation; there is no runnable application
> or downloadable release yet.

AJ's Character Manager is planned as a desktop-first application that keeps
campaign and character data on the user's computer. The initial targets are
Windows x64 and macOS on Apple Silicon.

## Intended features

- Campaigns with multiple characters
- Playable character sheets with durable local persistence
- Searchable, legally redistributable 2024 rules reference content
- Inventory built from reusable reference definitions and character-owned items
- GUI tools for common custom and homebrew content
- Importable and exportable content packs and campaigns

Development is deliberately incremental. Phase 1 will test the desktop UI,
SQLite persistence, packaging, and a small inventory workflow before the
project invests in a full rules engine or catalog. Phase 2 aims to make the app
useful during ordinary play. Phase 3 covers project maturation and possible
advanced features. See the [roadmap](docs/ROADMAP.md) for the boundaries and
completion criteria.

## Rules and custom content

The initial rules target is the current 2024 revision of fifth edition. SRD
5.2.1 is the redistribution foundation for bundled rules content. The project's
gameplay reference and redistribution authority have different roles; see
[Source of Truth](docs/SOURCE_OF_TRUTH.md).

Homebrew content is a first-class goal. Users should eventually be able to
create ordinary custom content in the GUI and share content packs when they
have the rights to do so. Briarwood is planned as a Phase 2 example pack using
the same generic tools available to everyone. It is not application logic.

## Technology and platforms

The approved stack is Python 3.12, Flet, SQLite, uv, pytest, and Ruff. Windows
x64 and macOS Apple Silicon are the first packaging targets. Other platforms
remain possible future work.

## Development

Phase 0 establishes documentation and tooling only. The expected development
workflow is described in [Development](docs/DEVELOPMENT.md). Contributions are
welcome; read [Contributing](CONTRIBUTING.md) before opening an issue or pull
request.

Additional documentation:

- [Architecture](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Custom content](docs/CUSTOM_CONTENT.md)
- [Content and licensing](docs/CONTENT_AND_LICENSING.md)
- [Security policy](SECURITY.md)

## Licensing and attribution

Original application code is licensed under the [MIT License](LICENSE). Rules,
structured data, example packs, and user content may have separate licenses;
see [Third-Party Notices](THIRD_PARTY_NOTICES.md) and
[Content and Licensing](docs/CONTENT_AND_LICENSING.md).

AJ's Character Manager is an independent, unofficial project and is not
affiliated with or endorsed by Wizards of the Coast.
