# Roadmap

AJ's Character Manager will be developed in three deliberate phases. The full
product vision includes a desktop UI, durable character state, rules-aware
features, homebrew authoring, portable content, and multi-platform packaging.
Building all of that before testing the basic desktop experience would create a
large amount of code around assumptions that have not been proven.

Each phase therefore has a distinct question to answer. Later phases may be
adjusted based on what is learned earlier; listed Phase 3 work is a direction,
not a promise.

## Phase 1: Prove the Application

### Objective

Prove that Flet, SQLite, and the proposed catalog boundary can support an
enjoyable, reliable desktop application worth developing further.

### Major deliverables

- A clean Flet desktop shell
- Durable local SQLite persistence
- Campaign creation and selection
- Multiple basic characters per campaign
- Basic character fields: name, level, class name, species name, current and
  maximum HP, and notes
- A campaign or party dashboard and a simple playable character screen
- A generic reference-catalog interface
- A manually reviewed fixture of roughly 10 to 20 SRD-compatible equipment
  definitions, including Trident
- Search, inspection, addition, removal, quantity, and notes for inventory
- Separate item definitions and character-owned inventory instances
- A simple GUI custom-item creator using the same catalog boundary
- Minimal tests and a development workflow on macOS
- Basic macOS and Windows build-workflow scaffolding when practical

The defining workflow is:

1. Open the application and create a campaign.
2. Create a character and set HP and notes.
3. Search the inventory catalog for “trident” and inspect its definition.
4. Add a Trident to the character.
5. Close and reopen the application.
6. Confirm that the character's HP, notes, and Trident remain intact.

### Explicit non-goals

Phase 1 will not include complete SRD ingestion, hundreds of items, full
character-creation rules, species or class mechanics, spellcasting, a complete
spell catalog, feats, detailed backgrounds, automated progression,
multiclassing, generalized homebrew species, the Briarwood pack, mature content
pack versioning, cloud services, accounts, networking, or web deployment.

The small equipment fixture is a test input, not a permanent hard-coded
catalog design.

### Completion criteria

Phase 1 is complete when the defining workflow passes against packaged macOS
Apple Silicon and Windows x64 builds; the UI has been evaluated in ordinary
use; data survives clean restarts; reference definitions remain separate from
inventory instances; and the project owner can make an informed decision about
whether to continue with Flet and the proposed architecture.

## Phase 2: Make It Useful for Real Play

### Objective

Make the application capable of replacing the project owner's paper or PDF
character sheet during ordinary 2024-rules play.

### Major deliverables

- A complete, reviewed SRD equipment catalog and a maintained normalization
  pipeline
- Guided 2024 character creation
- Ability scores and modifiers, saves, skills, AC, initiative, movement, hit
  dice, attacks, resources, and rests
- Class and species feature display with appropriate automation
- Searchable spells and practical spell/resource associations
- GUI editors for custom species, items, and backgrounds
- Generic content-pack import and export
- A Briarwood example pack using exactly the same content mechanisms available
  to other users
- Campaign export and import
- Stronger automated and packaged-application testing

Homebrew behavior will be classified as automated, assisted, or manual. The
application should calculate deterministic mechanics, help with mechanics that
require confirmation, and preserve rules text where human adjudication is
required.

### Explicit non-goals

Phase 2 will not require comprehensive multiclassing, complete custom
class/subclass creation, fully automated resolution of every spell or feature,
cloud synchronization, shared online campaigns, mobile clients, or a second
rules edition. Briarwood-specific application code is prohibited.

### Completion criteria

Phase 2 is complete when a typical 2024 SRD character can be created and used
during a session without a separate character sheet; supported homebrew can be
created through the GUI and moved through generic content packs; the Briarwood
example exercises that public mechanism; and catalog provenance, licensing,
and data integrity are covered by repeatable checks.

## Phase 3: Mature Open-Source Application

### Objective

Improve the proven application into a polished, sustainable public project and
selectively add advanced capabilities justified by real use.

### Potential deliverables

- More comprehensive level progression and multiclassing
- Custom class and subclass creation tools
- Richer spell and homebrew-feature automation
- Content-pack release and upgrade workflows
- Session history and a character-progression timeline
- Richer campaign portability and printable or PDF character sheets
- Additional platforms, potentially Intel macOS, Linux, web, or mobile
- Optional shared campaigns or cloud synchronization
- Polished installers, code signing, Apple notarization, and expanded release
  infrastructure
- Broader accessibility work
- Optional SRD 5.1 / 2014 rules support

### Explicit non-goals

This phase is not a commitment to implement every item above. Online services,
new platforms, and additional rulesets require separate product, maintenance,
privacy, security, and licensing decisions. They should not be added merely to
make the feature list larger.

### Completion criteria

Phase 3 has no single fixed finish line. Work should be accepted when it solves
a demonstrated user need, preserves offline and local-first behavior where
applicable, meets the project's quality and licensing standards, and has a
credible maintenance path.
