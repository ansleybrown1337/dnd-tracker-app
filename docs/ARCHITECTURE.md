# Architecture

This document records the architectural direction and the Phase 1 vertical
slice now implemented under `src/aj_character_manager/`. The Flet UI,
application services, domain records and validation, catalog boundary, and
SQLite adapter exist. A broader rules engine, content packs, and import/export
remain planned work.

## Design goals

- Keep character and campaign data local and durable.
- Keep Flet and SQLite details out of core rules and use-case code.
- Treat rules/reference content differently from mutable play state.
- Let bundled and custom content flow through the same application boundaries.
- Add automation only where the application can behave predictably and explain
  the result.
- Prove each boundary with a small vertical slice before generalizing it.

## Intended layers

### Flet UI — implemented for Phase 1

The UI will render screens, collect input, and present validation and errors.
Event handlers will call application use cases rather than issue SQL or contain
rules calculations. Flet-specific state should remain presentation state; it
must not become the authoritative character record.

### Application and use cases — implemented for Phase 1

This layer will coordinate actions such as creating a campaign, updating HP,
searching catalog definitions, and adding an item to inventory. It will define
transaction boundaries and work through repository interfaces.

### Domain and rules — domain implemented, rules planned

The domain layer will represent gameplay concepts and enforce invariants that
do not depend on a UI or database. Phase 1 needs only a small domain surface.
The rules layer should grow in Phase 2 as real calculations and choices are
implemented. Unsupported or ambiguous mechanics should remain visible as text
or assisted/manual actions rather than receive invented automation.

### Catalog and content system — catalog boundary implemented

The catalog will expose searchable reference definitions independently of
their source. A small reviewed equipment fixture will exercise this interface
in Phase 1. A larger normalized SRD catalog, provenance pipeline, and generic
content packs are Phase 2 concerns.

### SQLite persistence — implemented for Phase 1

SQLite will store mutable campaign and character state and the identities of
the definitions that state references. Persistence adapters will implement
interfaces used by the application layer. Schema migrations, backups, and
upgrade behavior begin with Phase 1 and must be tested against real packaged
applications.

### Import and export — planned

Import/export will operate through validated application services rather than
copying arbitrary database files. The eventual formats must preserve content
identity, provenance, and licensing metadata. Their detailed schemas are
intentionally deferred until Phase 2.

## Definitions and instances

A reference definition describes a reusable kind of thing. An instance records
how one campaign or character owns and uses it.

For example, the catalog's **Trident definition** contains the shared name,
category, damage, properties, cost, weight, source, and provenance. A
**character's Trident instance** refers to that definition and stores mutable
facts such as quantity, inventory notes, and equipped state.

Definitions should not be copied into every character record, and changing a
character's quantity must not mutate the shared definition. This distinction
allows the Phase 1 fixture to be replaced by a normalized catalog without
redesigning inventory ownership.

## Content and state boundaries

The intended data categories are:

| Category | Purpose | Mutation policy |
| --- | --- | --- |
| Bundled redistributable content | Reviewed rules and reference definitions shipped with the application | Versioned application content, not edited as character state |
| Installed custom packs | Imported definitions with their own identity, provenance, and license | Installed or removed through content workflows; releases treated as stable |
| User-created local content | Definitions authored by the user through the GUI | Editable locally; export/share only when rights permit |
| Campaign and character state | HP, notes, inventory ownership, choices, and other play state | Mutable and persisted immediately through application use cases |

Editing an installed or bundled definition should eventually create a local
derivative rather than silently rewriting the source. Campaigns will need
stable references so a content update does not unexpectedly change an existing
character. The detailed versioning and upgrade UX are Phase 2 or later work.

## Current package shape

The small prototype keeps each concern in a focused module rather than adding
empty subpackages: `ui.py`, `service.py`, `domain.py`, `catalog.py`,
`database.py`, and `paths.py`. This is enough separation to test the catalog
and persistence boundaries without committing Phase 2 to a deep package tree.
