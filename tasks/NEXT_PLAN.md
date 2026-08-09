# Next Plan

## Milestone

Resolve the remaining approved `MapCoordinateSpec.md` implementation failures
for the CoordinateMapper / MapData / map persistence layer.

This is an intentionally authorized multi-phase milestone.

Use subagents to divide investigation and verification work, but the main agent
must continue through all phases of this plan before stopping unless a genuine
specification ambiguity or unsafe repository state blocks progress.

Do not stop after completing only the first subtask.

---

## Primary Goal

Bring the implementation covered by the approved
`docs/specs/MapCoordinateSpec.md` into conformance with its existing
specification tests.

The approved specification is authoritative.

Do not weaken the specification or change tests merely to match existing
implementation behavior.

---

## Required Initial Reading

The main agent must first read:

- `AGENTS.md`
- `docs/agent/STATUS.md`
- `docs/specs/MapCoordinateSpec.md`
- `include/CoordinateTypes.hpp`
- `include/MapData.hpp`
- `src/MapData.cpp`
- `tests/CoordinateMapperTests.cpp`
- `tests/MapDataTests.cpp`
- `tests/MapDataFileTests.cpp`
- `tests/TestSupport.hpp`
- `Makefile`

Do not spend time reading unrelated documentation.

Do not read or update:

- `README.md`
- `Document.md`
- `docs/specs/README.md`

unless required to understand a compiler error caused by this task.

---

# Phase 1 — Baseline

Before modifying production code:

1. Run the relevant existing test executables or `mingw32-make test`.
2. Capture the currently failing specification cases.
3. Group failures by specification requirement.
4. Distinguish failures belonging to:
   - CoordinateMapper
   - MapData runtime behavior
   - MapData save/load behavior

Do not modify code during baseline collection.

The purpose is to establish the exact failure set before implementation changes.

---

# Phase 2 — Parallel Investigation

Use subagents for investigation.

Subagents are primarily read-only investigators. They must not independently
make overlapping production-code changes.

The main agent owns final implementation decisions and production-code edits.

## Subagent A — CoordinateMapper

Investigate all failing CoordinateMapper-related cases.

Focus on:

- grid-resolution invariants
- world-to-grid conversion
- grid-to-world conversion
- snapping behavior
- any other failing `COORD-*` requirement

Compare:

- approved specification
- tests
- current implementation

Return to the main agent:

- failing spec IDs
- root cause for each failure
- exact production location responsible
- smallest correct fix
- regression risks

Do not edit production code.

---

## Subagent B — MapData Runtime

Investigate failing MapData runtime behavior excluding file persistence.

Focus on:

- world-boundary containment
- obstacle insertion/removal
- GridCoord/world-position behavior
- work zones
- start/goal pose state
- clear/reset behavior
- grid-resolution interaction
- any other failing runtime `MAP-*` requirement

Return:

- failing spec IDs
- root cause
- production location
- smallest correct fix
- interactions with PathPlanner or editor behavior that must remain unchanged

Do not edit production code.

---

## Subagent C — Map Persistence

Investigate failing `MapData` save/load specification behavior.

Focus on:

- serialization
- deserialization
- malformed input
- required records
- invalid values
- atomic load behavior
- preservation of existing state on failed load
- any failing persistence-related `MAP-*` requirement

Return:

- failing spec IDs
- root cause
- production location
- smallest correct fix
- edge cases that require targeted verification

Do not edit production code.

---

# Phase 3 — Main-Agent Triage

After all investigation subagents report:

1. Consolidate findings.
2. Remove duplicates.
3. Confirm every proposed change against `MapCoordinateSpec.md`.
4. Identify dependencies between fixes.
5. Apply fixes in the smallest safe order.

Do not fix behavior that already conforms to the approved specification.

Do not rewrite working code for style.

Do not introduce new abstractions unless required for correctness.

Prefer local invariant fixes over duplicated caller-side validation.

Example:

If `CoordinateMapper` itself can guarantee a resolution invariant, prefer fixing
the invariant there instead of adding the same validation to every caller.

---

# Phase 4 — Implementation

The main agent performs production-code edits.

For each independent failure group:

1. Make the smallest implementation change.
2. Build if necessary.
3. Run the directly relevant tests.
4. Confirm the targeted specification failures are resolved.
5. Continue to the next confirmed failure group.

Do not batch unrelated speculative changes.

Production changes are allowed only when supported by:

1. Approved specification
2. Existing specification tests
3. Verified root cause

---

# Phase 5 — Test Discipline

Existing specification tests are authoritative evidence.

Do not:

- delete failing tests
- skip failing tests
- weaken assertions
- change expected values to fit current implementation
- relabel a failure as intentional without specification evidence

Tests may only be modified if the test itself is demonstrably inconsistent
with the approved specification.

If such a case is discovered:

- do not silently change the test
- report the conflict clearly
- leave it unresolved unless the specification makes the correct behavior
  unambiguous

Add new tests only when needed to prevent regression for a production fix that
is not adequately covered by existing tests.

Do not create redundant test cases simply to increase coverage count.

---

# Phase 6 — Regression Verification

After all justified fixes:

Run:

- `mingw32-make all`
- `mingw32-make test`

Also confirm specifically:

- `CoordinateMapperTests.exe`
- `MapDataTests.exe`
- `MapDataFileTests.exe`
- `PathPlannerTests.exe`

PathPlanner must remain:

- 7 PASS
- 0 FAIL

unless the repository now contains additional valid PathPlanner tests.

Any new regression caused by this milestone must be fixed before completion.

---

# Phase 7 — Completion Gate

The milestone is complete only if:

- all resolvable `MapCoordinateSpec.md` failures have been addressed
- relevant production code matches the approved specification
- targeted tests pass
- no previously passing relevant test regressed
- PathPlanner tests still pass
- the project builds successfully

If some specification failures remain:

Do not guess.

For every remaining failure, report one of:

- specification ambiguity
- test/spec conflict
- blocked by an out-of-scope architectural issue
- unresolved implementation defect

Include the exact spec ID.

---

# STATUS Update

Update only:

`docs/agent/STATUS.md`

Keep it concise.

Record:

- milestone result
- specification behaviors fixed
- verification results
- remaining failures, if any
- next smallest engineering milestone
- important implementation decisions only when needed

Do not turn STATUS into a chronological log.

---

# Explicit Out of Scope

Do not modify:

- `README.md`
- `Document.md`
- `docs/specs/README.md`
- `AGENTS.md`
- UI behavior
- rendering
- Simulator architecture
- PathPlanner algorithm behavior
- AMR movement behavior

Do not:

- add dependencies
- perform broad refactors
- redesign the project architecture
- implement the next navigation milestone
- add path visualization
- add robot path following

---

# Multi-Agent Rules

Use subagents for parallel investigation where useful.

Recommended structure:

- Explorer A: CoordinateMapper
- Explorer B: MapData runtime
- Explorer C: persistence / file loading

Subagents must not concurrently edit overlapping production files.

The main agent is the single writer for production-code integration.

Subagent findings are advisory.

The main agent must independently verify findings against the approved
specification before changing code.

---

# Git Ownership

For this orchestrated run:

- Do NOT run `git add`
- Do NOT run `git commit`
- Do NOT run `git push`

This task-specific rule overrides repository handoff instructions that assign
Git finalization to Codex.

The external orchestrator owns Git finalization after Codex exits successfully.

---

# Final Report

Before STOP, report only:

1. Production files modified
2. Tests modified or added
3. Specification failures fixed
4. Verification results
5. Remaining failures and their spec IDs
6. Any blocking ambiguity

Do not produce a long tutorial or documentation summary.

After the final report, STOP.