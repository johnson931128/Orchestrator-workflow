# Next Plan

## Milestone

Implement the first complete path-execution foundation for CtrlKine-AMR:

1. Preserve and expose the latest successful planned path.
2. Visualize that path in the simulator.
3. Allow the AMR to follow the planned path through its waypoints.
4. Integrate the behavior without moving path-planning logic into Simulator or rendering code.
5. Add focused tests and preserve the existing 43/43 regression baseline.

This is an intentionally authorized multi-phase milestone.

Use multiple subagents for parallel investigation and verification where useful.

The main agent owns architecture decisions, production-code integration, final verification, and STATUS update.

Do not stop after completing only one phase unless a genuine architectural ambiguity or repository problem blocks safe progress.

---

## Current Baseline

The repository currently has:

- Approved first-version A* PathPlanner behavior.
- `PathPlannerTests.exe`: 7 PASS, 0 FAIL.
- All current tests: 43 PASS, 0 FAIL.
- CoordinateMapper / MapData / persistence specification conformance complete.
- `PathPlanner` returns a complete start-to-goal path as `std::vector<GridCoord>`.
- Grid/world conversion is provided by `CoordinateMapper`.

Preserve this baseline.

Do not change existing PathPlanner semantics unless a defect is directly demonstrated.

---

## Functional Goal

After this milestone, the application should support this flow:

```text
Start / Goal configured
        ↓
Simulator requests planning
        ↓
PathPlanner returns PathResult
        ↓
Successful path is retained
        ↓
Path is visible in the simulator
        ↓
AMR follows path waypoints
        ↓
AMR reaches final waypoint
        ↓
Following stops cleanly
```

A planning failure must not begin path following.

---

## Required Behavior

### Planning Result Ownership

The application must retain the latest planning result or equivalent path-execution state at an appropriate integration layer.

Requirements:

- A successful plan makes its path available for visualization and following.
- A failed plan must not leave a newly executable invalid path.
- Replanning may replace the previously stored path.
- PathPlanner remains responsible only for planning.
- Rendering code must not invoke A* directly.
- AMR must not own PathPlanner.

Prefer the existing architecture and avoid introducing unnecessary global state.

### Path Visualization

A successful planned path must be visible in the existing SFML simulator.

Visualization requirements:

- Render the full path from start cell through goal cell.
- Convert `GridCoord` through `CoordinateMapper`.
- Draw using the existing SFML rendering pipeline.
- The rendered path must correspond to the actual `PathResult.path`.
- Visualization must not modify map state.
- Visualization must not contain planning logic.
- Visualization must disappear or be replaced when the current executable path is cleared or replaced.

Choose the smallest representation that clearly communicates the path.

A polyline, connected cell-center segments, or another simple existing-style representation is acceptable.

Do not build a new rendering subsystem.

### Path Following

Implement first-version waypoint following.

The AMR should follow the successful path in order.

Required semantics:

- Follow path cells from start to goal.
- Convert path cells to world-space waypoint positions using `CoordinateMapper`.
- Use cell centers as waypoint targets unless existing project semantics clearly require another position.
- Preserve the existing AMR movement model where practical.
- Move toward one waypoint at a time.
- Advance to the next waypoint only after the current waypoint is considered reached.
- Stop after the final waypoint is reached.
- Do not skip waypoint order.
- Do not invoke PathPlanner during movement.
- Do not automatically replan.

The implementation must tolerate an empty path safely.

A single-cell path must complete without attempting invalid movement.

### Execution State

Use the smallest amount of state required to safely control path following.

The implementation must be able to distinguish at least:

```text
not following
following
completed
```

This does not require a large general-purpose FSM.

If the existing AMR or Simulator design already has suitable state, extend it rather than introducing a parallel state framework.

Do not create an extensible FSM architecture unless the existing code clearly requires it.

---

## Explicit First-Version Limits

This milestone does NOT include:

- dynamic obstacle avoidance
- automatic replanning
- path smoothing
- spline trajectories
- acceleration profiles
- velocity planning
- costmaps
- robot footprint inflation
- collision prediction
- heading-aware A*
- reverse-motion planning
- multi-robot coordination
- work-zone traversal cost
- localization uncertainty
- ROS integration
- navigation stack redesign

Implement only simple path visualization and waypoint following.

---

## Required Initial Reading

The main agent must inspect the current repository before making architecture decisions.

Read:

- `AGENTS.md`
- `docs/agent/STATUS.md`
- `docs/specs/SystemOverview.md`
- `docs/specs/PathPlannerSpec.md`
- `docs/specs/MapCoordinateSpec.md`

Then inspect the relevant current implementation, including the actual files responsible for:

- Simulator lifecycle
- input handling
- update loop
- render loop
- planning requests
- PathPlanner
- PathResult
- AMR position and movement
- Environment rendering
- CoordinateMapper
- current tests
- Makefile

Use repository search to find exact files and symbols when needed.

Do not read unrelated documentation.

Do not update:

- `README.md`
- `Document.md`
- `docs/specs/README.md`
- `AGENTS.md`

---

## Phase 1 — Baseline Verification

Before production changes:

1. Run a clean build.
2. Run the current test suite.
3. Confirm the expected baseline:
   - 43 PASS
   - 0 FAIL
4. Inspect the current runtime ownership of:
   - current AMR pose
   - planning request
   - PathResult
   - update loop
   - rendering

If the baseline differs from the current `STATUS.md`, investigate before proceeding.

Do not modify production code during baseline verification.

---

## Phase 2 — Parallel Investigation

Use subagents for focused investigation.

Subagents should primarily inspect and report.

Avoid concurrent edits to overlapping production files.

The main agent remains the single integration writer.

### Subagent A — Planning and Simulator Integration

Investigate the current planning flow.

Determine:

- where `PathPlanner` is instantiated or called
- where `PathResult` currently exists
- whether the result is discarded after planning
- which object should own the current executable path
- how planning success/failure is currently surfaced
- how replanning should replace path state
- which existing Simulator methods are natural integration points

Return:

- relevant files and symbols
- current call flow
- recommended ownership of active path state
- smallest integration change
- risks of coupling PathPlanner to Simulator or rendering

Do not edit production code.

### Subagent B — AMR Movement

Investigate the current AMR implementation.

Determine:

- how AMR world position is stored
- how heading is stored
- how movement currently occurs
- whether movement is frame-time based
- existing movement speed semantics
- current update API
- current keyboard/manual movement behavior
- whether path following can reuse existing movement primitives
- potential conflicts between manual control and autonomous following

Return:

- relevant files and symbols
- current movement model
- recommended waypoint-following integration
- minimum new state required
- edge cases
- regression risks

Do not edit production code.

### Subagent C — Rendering and Coordinate Conversion

Investigate current rendering and coordinate conventions.

Determine:

- where map and AMR rendering occur
- the best existing render layer for path visualization
- how `CoordinateMapper::gridToWorldCenter()` or equivalent should be used
- whether rendering should live in Simulator, Environment, or an existing rendering helper
- how to draw the path without modifying persistent map state

Return:

- relevant files and symbols
- recommended rendering ownership
- proposed minimal rendering implementation
- coordinate assumptions
- regression risks

Do not edit production code.

### Subagent D — Test Strategy

Inspect existing tests and identify the smallest useful test coverage for this milestone.

Determine how to verify:

- successful path retention
- failed plan does not begin execution
- waypoint ordering
- single-cell path behavior
- empty path safety
- completion at final waypoint
- replanning/path replacement
- any separable path-execution state logic

Prefer deterministic unit tests over UI/render screenshot tests.

Return:

- existing test infrastructure that can be reused
- recommended test boundaries
- production seams needed for testability, if any
- cases that should remain integration-only

Do not edit production code.

---

## Phase 3 — Main-Agent Architecture Decision

After receiving the subagent findings:

1. Consolidate findings.
2. Inspect all proposed integration locations directly.
3. Choose the smallest architecture consistent with existing repository ownership.
4. Avoid duplicate state ownership.
5. Avoid introducing abstractions only for future possibilities.

Preserve these architectural rules:

```text
PathPlanner
    owns planning algorithm

MapData
    owns persistent map state

CoordinateMapper
    owns grid/world conversion

Simulator
    coordinates application flow

AMR
    owns robot movement/state that naturally belongs to the robot

Rendering
    displays state but does not decide routes
```

If the existing code strongly supports a slightly different ownership boundary, follow the existing architecture and explain the decision in STATUS.

Do not move A* logic into Simulator.

Do not move rendering logic into PathPlanner.

---

## Phase 4 — Implement Active Path Integration

Implement the smallest path-state integration required.

The application must be able to represent the current planned path and its execution progress.

Prefer a compact structure such as:

```text
active path
current waypoint index
following state
```

Do not create a large navigation framework.

Required behavior:

- successful plan installs/replaces active path
- failed plan does not start following
- active path can be cleared
- waypoint index is reset when a new path is installed
- invalid indexing is impossible
- single-cell and empty paths are handled safely

After this phase:

- build
- run directly relevant tests

Do not proceed with unresolved regressions.

---

## Phase 5 — Implement Path Visualization

Render the active successful path.

Requirements:

- use actual active path data
- convert path cells through CoordinateMapper
- render in the normal frame render path
- do not mutate MapData
- do not call PathPlanner from rendering
- keep rendering implementation simple
- avoid unnecessary allocations every frame when easily avoidable

The visualization must accurately update when the active path changes.

After this phase:

- build
- verify no compile/runtime integration problems
- run relevant automated tests

Do not add image-based UI tests unless existing infrastructure already supports them.

---

## Phase 6 — Implement Waypoint Following

Implement first-version automatic path following.

For each update:

1. If not following, do nothing.
2. Resolve the current waypoint.
3. Convert it to its world-space target.
4. Move the AMR toward the target using the existing movement model or the smallest compatible extension.
5. Detect waypoint arrival using a stable tolerance appropriate to existing movement units.
6. Advance the waypoint index.
7. Stop cleanly after the final waypoint.

Important constraints:

- movement must remain frame-rate independent if the existing AMR movement is frame-time based
- do not teleport between normal waypoints
- do not overshoot indefinitely
- avoid oscillation around waypoint centers
- never access a waypoint beyond the path bounds
- preserve manual movement behavior unless the task requires an explicit interaction rule

If manual and automatic movement conflict, implement the smallest deterministic rule.

Prefer:

```text
active path following owns movement while following
manual controls remain unchanged while not following
```

Do not redesign the input system.

---

## Phase 7 — Automated Tests

Add focused tests where the architecture allows deterministic testing.

At minimum, cover the separable logic for:

- empty path safety
- single-cell path completion
- waypoint progression
- final completion state
- path replacement resets progress
- failed/invalid execution input does not begin following

If movement logic is testable without SFML window creation, test it directly.

If rendering itself cannot be meaningfully unit-tested with current infrastructure, verify rendering through build/integration and keep rendering logic minimal.

Do not add brittle screenshot tests.

Do not weaken any existing tests.

---

## Phase 8 — Regression Verification

Perform a clean verification.

Run:

```text
mingw32-make clean
mingw32-make all
mingw32-make test
```

Also run relevant new test executables directly if added.

Verify the existing suites still pass:

```text
CoordinateMapperTests.exe
MapDataTests.exe
MapDataFileTests.exe
PathPlannerTests.exe
```

Existing baseline must remain:

```text
43 PASS
0 FAIL
```

plus any newly added passing tests.

PathPlanner must retain its approved first-version behavior.

---

## Phase 9 — Runtime Sanity Check

If the repository can be safely run in the current environment without requiring unavailable external services:

Perform a minimal manual/runtime sanity check.

Verify:

```text
plan succeeds
→ path becomes visible
→ following begins
→ AMR progresses through path
→ AMR reaches final waypoint
→ following stops
```

Also verify a planning failure does not begin following.

Do not spend excessive time automating GUI validation.

If runtime execution is unavailable or inappropriate, report that clearly and rely on build/tests.

---

## Completion Gate

The milestone is complete only when:

- successful planning creates a usable active path
- the active path is visible
- AMR can follow it in waypoint order
- final waypoint completion stops execution cleanly
- empty/single-cell paths are safe
- failed planning does not trigger following
- existing A* behavior is unchanged
- build passes
- all previous tests pass
- new relevant tests pass
- no unrelated architecture was modified

If any item cannot be completed safely, identify the exact blocker.

Do not silently omit a milestone requirement.

---

## Change Discipline

Modify only files necessary for this milestone.

Production changes may include the existing classes responsible for:

- Simulator coordination
- AMR movement
- path execution state
- rendering integration

and narrowly scoped new source/header files if they materially improve ownership or testability.

Do not create a new abstraction merely to distribute code across more files.

Prefer extending an appropriate existing class when responsibility already belongs there.

---

## Test Discipline

Do not:

- remove existing tests
- skip tests
- weaken assertions
- change approved specification behavior
- alter test expectations merely to make implementation pass

Add tests only for behavior introduced by this milestone.

---

## Explicit Out of Scope

Do not modify:

- `AGENTS.md`
- `README.md`
- `Document.md`
- `docs/specs/README.md`

Do not implement:

- automatic replanning
- dynamic obstacle response
- costmaps
- path smoothing
- advanced trajectory control
- generalized navigation FSM
- multi-AMR coordination
- new map-file format
- new PathPlanner algorithm
- unrelated UI features
- unrelated refactors
- build-system improvements such as Makefile dependency tracking

The known Makefile header-dependency limitation belongs to a separate milestone.

---

## Multi-Agent Rules

Use subagents where parallel investigation provides real value.

Recommended initial delegation:

```text
Main Sol Agent
├── Explorer A: planning / Simulator integration
├── Explorer B: AMR movement
├── Explorer C: rendering / coordinates
└── Explorer D: test strategy
```

Subagents are investigators unless the main agent explicitly delegates an isolated non-overlapping test task.

Do not allow multiple agents to concurrently edit the same production area.

The main agent is responsible for:

```text
architecture synthesis
production implementation
integration decisions
regression handling
final verification
STATUS update
```

Subagent findings are advisory.

The main agent must verify important findings against actual repository code before implementation.

---

## Long-Running Task Rules

This plan intentionally authorizes multiple sequential implementation phases.

Do not stop after:

- investigation
- visualization only
- state creation only
- one passing targeted test

Continue until the Completion Gate is satisfied or a genuine blocker is found.

After each implementation phase:

```text
change
→ build/test
→ verify
→ continue
```

If a proposed design causes increasing complexity, stop that direction and choose the smallest implementation satisfying the explicit requirements.

Do not expand scope to consume remaining token budget.

Correctness and integration quality take priority over maximum code volume.

---

## STATUS Update

Update only:

`docs/agent/STATUS.md`

Replace stale milestone information with the current repository state.

Record concisely:

- current milestone
- implemented path-execution behavior
- ownership decisions
- verification performed
- total test result
- known limitations
- next smallest meaningful milestone

Do not turn STATUS into a development log.

Do not update unrelated documentation.

---

## Git Ownership

For this orchestrated run:

- Do NOT run `git add`
- Do NOT run `git commit`
- Do NOT run `git push`

This task-specific rule overrides any repository instruction assigning Git finalization to Codex.

The external orchestrator owns Git finalization after Codex exits successfully.

Before returning control to the orchestrator, ensure all intended repository modifications are present in the working tree.

---

## Final Report

Before STOP, report:

1. Production files modified or added
2. Tests modified or added
3. Path execution architecture implemented
4. Visualization behavior implemented
5. Path-following behavior implemented
6. Verification commands and results
7. Total PASS / FAIL count
8. Remaining limitations or blockers

Do not produce a tutorial.

After the final report, STOP.
