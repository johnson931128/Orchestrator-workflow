# Next Task

## Goal

Fix only the `COORD-005` grid-resolution validity behavior defined by
`docs/specs/MapCoordinateSpec.md`.

Do not address any other existing specification failures in this task.

## Required Reading

Read only the files needed for this task:

- `AGENTS.md`
- `docs/agent/STATUS.md`
- `docs/specs/MapCoordinateSpec.md`, specifically `COORD-005`
- `include/CoordinateTypes.hpp`
- `src/MapData.cpp`
- `tests/CoordinateMapperTests.cpp`
- `tests/MapDataTests.cpp`

## Required Behavior

According to `COORD-005`:

- Grid resolution must always remain positive.
- `CoordinateMapper::setGridResolution()` must reject zero and negative values.
- An invalid setter value must not replace the current valid resolution.
- Constructing `CoordinateMapper` with zero or a negative value must still produce a positive resolution.
- Constructing `MapData` with zero or a negative resolution must also result in a positive resolution.

Use the existing valid default resolution when an invalid constructor value must be replaced.

## Scope

Make the smallest production-code change needed to satisfy `COORD-005`.

Prefer fixing the invariant at the `CoordinateMapper` level so that users of
`CoordinateMapper`, including `MapData`, inherit the valid-resolution guarantee.

Do not modify `MapData` unless it is actually necessary after fixing
`CoordinateMapper`.

## Tests

Use the existing `COORD-005` tests as the primary acceptance tests.

Verify that these cases pass:

### CoordinateMapper

- setting resolution to `0`
- setting resolution to a negative value
- constructing with resolution `0`
- constructing with a negative resolution

### MapData

- setting resolution to `0`
- setting resolution to a negative value
- constructing with resolution `0`
- constructing with a negative resolution

Do not weaken or remove existing tests.

Do not change approved specification behavior to make tests pass.

## Verification

Run:

- `mingw32-make all`
- `build/tests/CoordinateMapperTests.exe`
- `build/tests/MapDataTests.exe`

If `MapDataTests.exe` still exits non-zero because of unrelated pre-existing
specification failures, confirm specifically whether its `COORD-005` cases pass.

Do not fix unrelated failures in this task.

## STATUS Update

Update `docs/agent/STATUS.md` briefly with:

- `COORD-005` implementation status
- verification performed
- remaining specification failures
- next smallest unresolved implementation issue

Keep the update concise.

## Out of Scope

Do not modify:

- `README.md`
- `Document.md`
- `docs/specs/README.md`
- `PathPlanner`
- PathPlanner tests
- unrelated CoordinateMapper behavior
- unrelated MapData behavior
- unrelated specification failures

Do not add dependencies.
Do not perform unrelated refactoring.
Do not add documentation beyond the required `STATUS.md` update.

## Completion

When the implementation and verification are complete:

- Do NOT run `git add`
- Do NOT run `git commit`
- Do NOT run `git push`
- STOP and report:
  - modified production files
  - relevant test results
  - remaining unrelated failures

The external orchestrator handles Git finalization.