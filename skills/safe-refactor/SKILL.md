---
name: safe-refactor
description: Restructure code while preserving behavior. Use for extraction, consolidation, ownership moves, or cleanup where verification must bracket structural edits.
---

# Safe refactor

Define behavior-preservation boundary and establish verification before structural edits.

- Keep feature changes outside refactor.
- Move one ownership boundary at a time.
- Preserve public interfaces, failure behavior, ordering, and compatibility unless explicitly scoped.
- Keep intermediate states buildable and testable.
- Avoid dependency or configuration growth without correctness need.

Untested area: write characterization tests first (snapshot/approval on current outputs, quick and coarse is fine). Run them on unmodified code and confirm they pass. Break something small on purpose and confirm a test fails. If a net test fails during refactor, the refactor is wrong, not the test. Once seams exist, replace coarse tests with focused ones and delete the rest. Say which phase you are in (Protect, Prepare, Produce).

Run same proof after change. Stop when behavior matches and requested structure is achieved.
