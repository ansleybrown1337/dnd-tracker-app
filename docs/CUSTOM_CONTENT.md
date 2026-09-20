# Custom Content Vision

Custom and homebrew content is a core product goal, not a Briarwood-specific
extension. Future users should be able to use their own definitions alongside
bundled SRD content without editing source code or JSON for common tasks.

## Intended experience

The application should eventually let users:

- create ordinary custom content through guided GUI editors;
- preview and validate content before using it;
- install content packs alongside bundled definitions;
- export and import packs for backup or sharing; and
- retain authorship, provenance, license, and attribution information.

Sharing is appropriate only when the author has the necessary rights. Local
content may refer to privately owned material without making that material
eligible for the public repository.

## Planned content categories

Phase 1 will prove the boundary with a simple custom-item creator. Phase 2 is
expected to support species, items, and backgrounds through the GUI, plus
pack-based definitions for spells and feats. Classes and subclasses are later
possibilities because their progression and choices require a broader rules
model.

Features should carry human-readable rules text even when they also have
structured behavior. Structured effects can support deterministic automation;
assisted behavior can ask a player to confirm context or a result; manual
behavior can provide rules text and tracking without claiming the engine can
adjudicate it.

## Briarwood as an example

Briarwood is planned as a Phase 2 example pack that exercises the same generic
content system offered to every user. Species such as Batfolk or Shrew will be
data in that pack, never special cases in application code. The example will
exclude the private source document, unlicensed artwork, and any text that the
project lacks permission to redistribute.

## Schema status

The pack archive format, JSON schema, dependency model, version constraints,
and upgrade workflow are intentionally not finalized in Phase 0. They will be
designed in Phase 2 after Phase 1 proves the definition-versus-instance model
and reveals what Flet and SQLite need in practice.
