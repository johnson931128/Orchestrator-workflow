# Next Plan

## Milestone

Implement the next navigation-quality milestone for CtrlKine-AMR:

1. Diagnose and fix the observed Start/Goal placement-range problem without weakening approved map-boundary semantics.
2. Make path planning aware of AMR body clearance so planned routes are physically traversable by the current robot footprint.
3. Reduce unnecessary grid-by-grid waypoint corners where it is safe to do so.
4. Improve automatic path-following motion so heading changes are progressive rather than instantaneous.
5. Preserve all existing approved behavior and the current 54 PASS / 0 FAIL baseline.

This is an intentionally authorized long-running multi-phase milestone.

Use subagents for parallel investigation and verification.

The main agent owns architecture decisions, production-code integration, final regression verification, and `docs/agent/STATUS.md`.

Do not stop after completing only one subtask unless a genuine specification ambiguity, repository inconsistency, or unsafe design dependency blocks further work.

---

## Observed Runtime Problems

The current interactive desktop run exposed three concrete problems:

### Problem A — Start/Goal Placement Range

When placing a Goal, positions that visually appear to be part of the usable editor area can become impossible to place beyond a certain region.

This may be:

- correct `MapData` world-boundary enforcement with unclear visualization,
- a mismatch between displayed grid extent and editable map extent,
- a coordinate/viewport conversion problem,
- or an actual placement-validation defect.

Do not assume which explanation is correct.

Investigate first.

Do not weaken approved `MapCoordinateSpec.md` boundary behavior merely to allow placement farther away.

### Problem B — Rigid Path Following

Current automatic motion follows discrete cell-center waypoints and can change heading abruptly at grid corners.

Observed behavior feels mechanically rigid.

Improve motion quality while preserving deterministic, safe waypoint execution.

Do not build a full trajectory-planning stack.

### Problem C — Planner Ignores Robot Footprint

The current A* planner reasons about cell-center occupancy.

A route may therefore be valid for a point but invalid for the physical AMR body.

Observed result:

```text
PathPlanner: route is free
Runtime AMR collision: body hits obstacle
```

This is the highest-priority correctness issue in this milestone.

---

## Current Baseline

The repository currently has:

- First-version A* planning complete.
- `PathExecution` retaining successful paths and waypoint state.
- Path visualization integrated in Simulator.
- Automatic waypoint following integrated.
- Runtime collision checks.
- `CoordinateMapper`, `MapData`, and persistence specification conformance complete.
- Existing full test suite: 54 PASS, 0 FAIL.

Current suites:

```text
CoordinateMapperTests.exe   6 PASS
MapDataTests.exe           15 PASS
MapDataFileTests.exe       15 PASS
PathPlannerTests.exe        7 PASS
PathExecutionTests.exe     11 PASS
```

Preserve this baseline.

---

## Priority Order

Implement in this order unless investigation proves a dependency requires a different safe order:

```text
1. Footprint-aware planning correctness
2. Start/Goal placement-range diagnosis and fix
3. Safe path simplification
4. Progressive motion / turning quality
5. Full regression and desktop sanity verification
```

Correctness takes priority over visual smoothness.

---

## Architectural Constraints

Preserve the current responsibility boundaries:

```text
PathPlanner
    owns path-search behavior

MapData
    owns persistent map state

CoordinateMapper
    owns grid/world conversion

Simulator
    coordinates planning, execution, rendering, and input flow

PathExecution
    owns active transient path and execution progress

AMR
    owns robot pose and movement primitives

Environment
    owns editor interaction and map visualization
```

Do not:

- move A* logic into Simulator,
- make AMR depend on PathPlanner,
- put persistent navigation state into MapData,
- make rendering decide route validity,
- create global navigation state,
- redesign the project architecture.

Use the smallest extension consistent with existing ownership.

---

## Required Initial Reading

The main agent must first read:

- `AGENTS.md`
- `docs/agent/STATUS.md`
- `docs/specs/SystemOverview.md`
- `docs/specs/MapCoordinateSpec.md`
- `docs/specs/PathPlannerSpec.md`

Then inspect the current implementation responsible for:

- Simulator event handling and update loop
- Start/Goal placement
- viewport-to-world coordinate conversion
- world-boundary rendering
- MapData pose validation
- PathPlanner blocked-cell logic
- AMR geometry/configuration
- AMR collision checking
- PathExecution
- path visualization
- automatic path following
- existing tests
- Makefile

Use repository search to locate exact files and symbols.

Do not read unrelated documentation.

Do not modify:

- `AGENTS.md`
- `README.md`
- `Document.md`
- `docs/specs/README.md`

---

# Phase 1 — Clean Baseline

Before production edits:

1. Run:
   - `mingw32-make clean`
   - `mingw32-make all`
   - `mingw32-make test`
2. Confirm:
   - 54 PASS
   - 0 FAIL
3. Record the current relevant runtime flow:
   - editor click → world position
   - pose placement → MapData
   - PathPlanner → PathResult
   - PathExecution → current waypoint
   - AMR movement → collision acceptance/rollback

If baseline tests do not match `STATUS.md`, investigate before implementation.

---

# Phase 2 — Parallel Investigation

Use subagents as read-only investigators unless the main agent explicitly delegates an isolated non-overlapping test task.

Do not allow concurrent production edits.

---

## Subagent A — Start/Goal Placement and World Boundary

Investigate the observed placement-range problem.

Determine:

- how mouse pixel coordinates become simulation world coordinates,
- how the simulation viewport and camera affect that conversion,
- how the world boundary is defined,
- how the boundary is rendered,
- how Start and Goal setters validate positions,
- whether the displayed grid extends outside the editable world,
- whether Start and Goal have identical placement semantics,
- whether the observed restriction is correct behavior, misleading UX, or a defect.

Compare behavior against `MapCoordinateSpec.md`.

Return:

- exact files and symbols,
- root cause,
- whether approved spec behavior is currently violated,
- smallest correct fix,
- any required UI/boundary-visualization adjustment,
- tests that should be added or updated,
- regression risks.

Do not edit production code.

---

## Subagent B — Footprint-Aware Planning

Investigate how to make A* routes physically traversable for the current AMR.

Inspect:

- `AMRConfig`,
- body length/width,
- current collision geometry,
- grid resolution,
- PathPlanner blocked-cell logic,
- obstacle representation,
- world boundary semantics.

Evaluate a first-version configuration-space approach based on obstacle/boundary inflation.

Preferred design direction:

```text
physical obstacle / boundary
        ↓
inflate by robot clearance
        ↓
planner evaluates AMR-center positions
        ↓
existing A* remains largely unchanged
```

The first version should use a conservative clearance representation.

Do not implement orientation-dependent footprint search unless required by the current architecture.

Return:

- exact current body/collision dimensions,
- recommended clearance model,
- where inflation/traversability should be calculated,
- whether inflation should be precomputed or queried,
- boundary-clearance handling,
- expected behavior for narrow passages,
- smallest implementation change,
- required tests,
- regression risks.

Do not edit production code.

---

## Subagent C — Path Simplification

Investigate whether the raw grid path can be safely simplified before execution.

Goal:

Reduce unnecessary waypoint-by-waypoint turning while preserving collision safety.

Evaluate a minimal approach such as:

- removing collinear intermediate cells,
- or line-of-sight waypoint compression only if collision/clearance checks can prove the segment safe.

Do not blindly connect distant waypoints.

Any simplified segment must remain valid for the same footprint-aware traversability model used by planning.

Return:

- current raw path characteristics,
- recommended first-version simplification rule,
- exact safety predicate needed,
- ownership location,
- tests,
- cases where simplification must not occur,
- regression risks.

Do not edit production code.

---

## Subagent D — Motion Controller

Investigate current AMR automatic movement and differential-drive behavior.

Determine:

- how manual `AMR::update(dt, vL, vR)` works,
- how current automatic `moveToward()` changes heading,
- current speed units,
- current collision rollback semantics,
- current arrival tolerance,
- how to make turns progressive without introducing a full trajectory planner.

Preferred behavior:

```text
current heading
    ↓
compute target heading
    ↓
limit heading change by dt
    ↓
move forward only as appropriate
    ↓
approach waypoint
```

If the existing differential-drive model can be reused cleanly, prefer that over directly assigning heading.

Return:

- exact movement model,
- recommended first-version automatic controller,
- required new parameters/constants,
- behavior near sharp corners,
- behavior near final waypoint,
- interaction with collision rollback,
- deterministic test strategy,
- regression risks.

Do not edit production code.

---

# Phase 3 — Main-Agent Design Synthesis

After all subagents report:

1. Consolidate findings.
2. Verify important claims directly against repository code.
3. Resolve overlaps between footprint planning, simplification, and motion.
4. Choose the smallest architecture satisfying the milestone.
5. Preserve approved specification behavior.
6. Define one consistent traversability predicate for planning and any line-of-sight simplification.

Do not create separate inconsistent definitions of "safe cell" in multiple modules.

If a new narrowly scoped helper/class materially prevents duplicated safety logic, it is allowed.

Do not introduce a generalized navigation framework.

---

# Phase 4 — Footprint-Aware Traversability

Implement the highest-priority correctness fix first.

## Required Behavior

A planner-valid route must provide enough clearance for the current AMR body under the first-version conservative footprint model.

At minimum:

- obstacle-adjacent cells that cannot safely contain the AMR center must be blocked for planning,
- world-boundary clearance must also account for AMR body size,
- start and goal must fail planning if they are not footprint-valid,
- narrow passages smaller than required robot clearance must not be considered traversable,
- existing four-neighbor A* semantics remain otherwise unchanged.

Prefer configuration-space inflation or an equivalent conservative center-validity test.

Do not mutate persistent obstacles merely to create planner inflation.

Do not write inflated obstacles back to map files.

The physical map remains authoritative; inflated occupancy is derived planning data.

## Robot Footprint

Use the actual configured AMR geometry.

If an orientation-independent first-version approximation is required, use a conservative footprint radius/half-extent derived from current AMR dimensions and document that decision in STATUS.

Do not invent arbitrary clearance unless required as a small explicit safety margin.

If a safety margin is introduced, make it a clearly named constant or configuration value.

## Verification Gate

After implementation:

- build,
- run PathPlanner tests,
- add focused footprint tests,
- run PathExecution tests,
- confirm existing behavior has not regressed.

Do not proceed with a known correctness regression.

---

# Phase 5 — Start/Goal Placement Fix

Implement only the root-cause fix found by Subagent A.

Possible acceptable outcomes include:

### Case 1 — Existing boundary semantics are correct

If the editor visually shows space outside the editable world:

- keep MapData validation unchanged,
- improve the visual/editor behavior so the usable region is unambiguous.

### Case 2 — Coordinate conversion is wrong

Fix pixel/view/world conversion at the correct integration layer.

### Case 3 — Pose validation is inconsistent with approved spec

Fix the minimum validation defect required by `MapCoordinateSpec.md`.

Do not enlarge the world boundary implicitly as a workaround.

Do not make Start/Goal placement bypass MapData invariants.

Add targeted regression tests where practical.

---

# Phase 6 — Safe Path Simplification

Implement the smallest safe path simplification supported by investigation.

Minimum acceptable first version:

- remove redundant collinear intermediate waypoints.

If robust footprint-aware line-of-sight checking is simple and clearly safe, it may also compress multiple grid segments into longer straight segments.

Any line-of-sight compression must:

- use the same effective clearance model as planning,
- reject segments that cross or graze invalid clearance space,
- preserve start and goal,
- preserve path order,
- never create a less safe route than the raw A* path.

Do not implement splines or curve generation in this phase.

Keep the original `PathPlanner` result semantics clear.

If simplification is execution-only, do not silently redefine `PathResult.path` unless architecture strongly supports that choice.

Prefer retaining the raw planner result and deriving an execution waypoint sequence if needed.

---

# Phase 7 — Progressive Automatic Motion

Improve automatic path following so the robot does not instantaneously snap its heading to each new waypoint.

## Required Behavior

Automatic movement must:

- remain frame-time based,
- rotate progressively toward the target direction,
- use bounded angular change,
- avoid instant 90-degree heading jumps,
- move toward waypoints without indefinite overshoot,
- stop cleanly at the final waypoint,
- preserve waypoint order,
- preserve collision rollback/acceptance behavior,
- remain deterministic,
- leave manual controls unchanged when not following.

Use the existing differential-drive model when practical.

If a simpler heading-rate-limited controller is the smallest safe first version, it is acceptable.

Do not implement:

- PID tuning framework,
- acceleration planner,
- curvature-continuous trajectory generation,
- dynamic obstacle avoidance,
- automatic replanning.

## Corner Behavior

At sharp corners, it is acceptable for the robot to slow or rotate before advancing.

Safety takes priority over constant translational speed.

---

# Phase 8 — Automated Tests

Add focused tests for newly introduced behavior.

At minimum cover, where deterministic unit testing is practical:

## Footprint Safety

- obstacle clearance blocks an adjacent unsafe center cell,
- a sufficiently wide route remains traversable,
- a too-narrow corridor is rejected,
- start footprint collision fails planning,
- goal footprint collision fails planning,
- boundary clearance is enforced.

## Placement

- root-cause placement regression,
- Start and Goal remain consistent with approved world-boundary semantics.

## Simplification

- collinear waypoints simplify correctly,
- required corners are preserved,
- unsafe shortcut is rejected if line-of-sight compression is implemented,
- start and goal remain preserved.

## Motion

- heading change is bounded per update,
- robot progresses toward a waypoint,
- sharp turn does not instantaneously snap heading,
- final waypoint completes,
- non-positive/invalid update inputs remain safe if relevant,
- collision rejection does not consume waypoint progress.

Do not remove or weaken existing tests.

Do not add screenshot tests.

---

# Phase 9 — Full Regression

Perform a clean build and full test run:

```text
mingw32-make clean
mingw32-make all
mingw32-make test
```

Run all relevant executables directly as well.

Existing suites must still pass:

```text
CoordinateMapperTests.exe
MapDataTests.exe
MapDataFileTests.exe
PathPlannerTests.exe
PathExecutionTests.exe
```

Current baseline:

```text
54 PASS
0 FAIL
```

Completion requires:

```text
54 existing tests PASS
+ all new tests PASS
0 FAIL
```

Do not claim completion with regressions.

---

# Phase 10 — Runtime Sanity Check

If desktop execution is available, launch the simulator and perform a minimal runtime sanity check.

Verify:

### Placement

- Start and Goal can be placed throughout the intended valid world area.
- Invalid outside-boundary placement is clearly rejected.

### Footprint-Aware Planning

Create an obstacle wall/corner where the previous planner produced a wall-hugging path.

Confirm:

- new path keeps sufficient clearance,
- AMR no longer immediately collides on a planner-approved corner,
- an actually too-narrow route is rejected rather than planned.

### Motion

Confirm visually:

- heading turns progressively,
- AMR no longer instantly snaps orientation at every grid corner,
- movement remains stable,
- AMR completes a valid route.

### Replanning

Change the map and plan again.

Confirm:

- active route is replaced,
- safety behavior remains correct,
- execution restarts cleanly.

If GUI automation cannot verify these visually, report that limitation honestly.

Do not claim visual verification without observing it.

---

# Completion Gate

The milestone is complete only when all of the following are true:

- Start/Goal placement-range root cause is identified.
- Placement behavior is corrected without weakening approved map semantics.
- Path planning accounts for AMR body clearance.
- Planner does not intentionally return routes that the conservative footprint model says are physically invalid.
- Boundary clearance accounts for the robot footprint.
- Raw execution waypoints are simplified at least for redundant collinear points.
- Any more aggressive simplification is safety-checked.
- Automatic heading changes are progressive rather than instantaneous.
- Existing manual controls remain functional when not following.
- Existing A* ownership and MapData ownership remain intact.
- Clean build passes.
- All existing tests pass.
- All new tests pass.
- STATUS accurately describes the resulting implementation and remaining limitations.

If any requirement cannot be safely completed, report the exact blocker and do not silently omit it.

---

# Explicit Out of Scope

Do not implement:

- automatic replanning,
- dynamic obstacle detection,
- dynamic obstacle avoidance,
- D* / D* Lite,
- RRT / RRT*,
- costmaps as a generalized subsystem,
- orientation-expanded A* state,
- full nonholonomic search,
- spline/path-curvature optimization,
- PID framework,
- acceleration/deceleration profiles,
- localization uncertainty,
- multi-robot coordination,
- ROS integration,
- new map-file format,
- unrelated editor features,
- unrelated UI redesign,
- Makefile header-dependency work.

Do not modify:

- `AGENTS.md`
- `README.md`
- `Document.md`
- `docs/specs/README.md`

Do not perform unrelated refactoring.

---

# Multi-Agent Rules

Recommended initial structure:

```text
Main Sol Agent
├── Explorer A: Start/Goal placement + boundary/viewport
├── Explorer B: footprint-aware traversability
├── Explorer C: path simplification
└── Explorer D: AMR motion controller
```

Subagents investigate and report.

The main agent is the single production-code integration writer.

The main agent may delegate isolated test implementation only when:

- the file ownership is non-overlapping,
- the expected behavior is already decided,
- concurrent edits cannot collide.

Subagent findings are advisory.

The main agent must verify findings against actual code and approved specifications before changing behavior.

---

# Long-Running Task Rules

This plan intentionally authorizes several sequential engineering phases.

Do not stop after:

- footprint investigation only,
- one fixed bug,
- path simplification only,
- motion improvement only,
- one passing targeted test.

Continue through the Completion Gate unless blocked.

Use this cycle:

```text
investigate
→ decide
→ implement one coherent phase
→ targeted tests
→ verify
→ continue
```

If implementation complexity grows significantly beyond this plan, reduce scope to the smallest design satisfying the explicit first-version requirements.

Do not expand scope merely to consume token budget.

---

# STATUS Update

Update only:

`docs/agent/STATUS.md`

Keep it concise and current-state oriented.

Record:

- current milestone,
- placement-range root cause and resulting behavior,
- footprint/traversability model,
- path-simplification behavior,
- automatic motion behavior,
- ownership decisions,
- verification results,
- total PASS / FAIL count,
- runtime verification status,
- known limitations,
- next smallest meaningful milestone.

Do not turn STATUS into a chronological log.

---

# Git Ownership

For this orchestrated run:

- Do NOT run `git add`
- Do NOT run `git commit`
- Do NOT run `git push`

The external orchestrator owns Git finalization after Codex exits successfully.

This task-specific instruction overrides repository instructions that assign Git finalization to Codex.

---

# Final Report

Before STOP, report:

1. Production files modified or added
2. Tests modified or added
3. Start/Goal placement root cause and fix
4. Footprint-aware planning design and behavior
5. Path simplification behavior
6. Motion-controller improvement
7. Verification commands and results
8. Total PASS / FAIL count
9. Runtime sanity-check result
10. Remaining limitations or blockers

Do not produce a tutorial.

After the final report, STOP.
