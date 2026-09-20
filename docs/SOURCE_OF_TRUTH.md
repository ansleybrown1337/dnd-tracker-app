# Rules Sources and Source of Truth

AJ's Character Manager has two different source-of-truth questions. A source
that reflects how the owner's table plays does not automatically grant the
project permission to redistribute its contents.

## Gameplay and operational reference

[dnd2024.wikidot.com](http://dnd2024.wikidot.com/) is the project owner's
operational reference for current 2024 character statistics, equipment,
spells, classes, and related mechanics. The application should aim to produce
gameplay behavior that agrees with the expectations established there.

The site must not be scraped wholesale, copied into the repository, or treated
as permission to publish its text or data. Facts learned through comparison
still need a redistributable source before their expression can be bundled.

## Redistribution authority

The [official SRD 5.2.1](https://www.dndbeyond.com/srd) is the project's
authority for bundled open 2024-rules content. It is made available under the
Creative Commons Attribution 4.0 International license and supplies the
required attribution language.

Only material with appropriate redistribution rights may be included in the
public repository or application releases. Content appearing in a rulebook,
on a public website, or in a third-party dataset is not automatically part of
SRD 5.2.1.

## Normalized runtime catalog

The eventual AJ's Character Manager catalog will be a reviewed runtime
representation, not an independent authority. Each imported definition should
record enough provenance to identify its source document and revision, the
transformation that produced it, and any project correction or interpretation.
Third-party transcriptions may help produce structured data but must be checked
for license compatibility and fidelity to the official SRD.

## Handling discrepancies

When the gameplay reference, official SRD, and a structured source disagree:

1. Record the discrepancy with exact source and revision information.
2. Determine which behavior the owner's table expects.
3. Determine which text or data the project has the right to redistribute.
4. Encode only supportable data and document any project-authored correction or
   interpretation.
5. Preserve human-readable notes where the application cannot safely automate
   the result.

Discrepancies must not be silently resolved by copying text from the gameplay
reference or assuming that a dataset labeled “2024” is correct.
