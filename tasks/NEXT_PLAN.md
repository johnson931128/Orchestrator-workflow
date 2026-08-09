# Next Plan

## Milestone

Implement a complete first-version native AMCL localization subsystem for CtrlKine-AMR.

The goal is not to add a decorative particle cloud. The goal is to establish a real localization pipeline with explicit separation between ground truth, odometry, sensor observations, particle belief, estimated pose, uncertainty, adaptive resampling, and recovery.

This is an intentionally large, long-running, multi-phase milestone.

The main agent must continue through architecture, implementation, integration, deterministic tests, convergence tests, kidnapped-robot recovery tests, full regression, and STATUS update unless a genuine blocker makes safe completion impossible.

Do not stop after implementing only one AMCL component.

---

## Current Baseline

The repository currently has:

- C++ / SFML 2D AMR simulator and map editor.
- `MapData` as authoritative persistent map state.
- `CoordinateMapper` for grid/world conversion.
- `AMR` as runtime ground-truth robot pose and geometry.
- Start Pose synchronized with runtime AMR pose.
- Grid-based A* path planning.
- Clearance-aware runtime planning.
- Path execution and visualization.
- Collinear waypoint compression.
- Progressive stop-turn-go motion.
- Runtime collision checking.
- Current automated baseline: 79 PASS, 0 FAIL.

Existing suites:

```text
CoordinateMapperTests.exe   6 PASS
MapDataTests.exe           16 PASS
MapDataFileTests.exe       15 PASS
PathPlannerTests.exe       14 PASS
PathExecutionTests.exe     19 PASS
SimulatorRuntimeTests.exe   9 PASS
```

Preserve all existing behavior unless this milestone explicitly extends it.

---

# Primary Goal

After this milestone, the simulator must support this localization flow:

```text
AMR ground-truth pose
        │
        ├─────────────────────┐
        │                     │
        ↓                     ↓
Noisy odometry          Simulated 2D LiDAR
        │                     │
        ↓                     ↓
Differential motion     Likelihood-field
model update            sensor update
        │                     │
        └──────────┬──────────┘
                   ↓
             Particle filter
                   ↓
        weight normalization
                   ↓
         ESS / resample gate
                   ↓
       adaptive KLD resampling
                   ↓
          recovery injection
                   ↓
      estimated pose + covariance
                   ↓
 particle cloud / estimated pose / inspector
```

The localization estimate must not read the AMR ground-truth pose as its answer.

Ground truth may only be used by:

- sensor simulation,
- odometry simulation,
- test truth/error measurement,
- visualization/debugging.

AMCL itself must consume simulated odometry and simulated laser measurements.

---

# Required Architectural Separation

The implementation must explicitly distinguish:

```text
Ground Truth Pose
    actual AMR runtime pose

Odometry Pose / Increment
    noisy dead-reckoning information

Laser Scan
    noisy range measurements from simulated sensor

Particle Belief
    set of weighted pose hypotheses

Estimated Pose
    localization result derived from particle belief

Estimated Covariance
    uncertainty derived from particle belief
```

Do not collapse these concepts into one pose field.

Do not allow AMCL to simply copy `AMR::getPosition()` or `AMR::getHeading()`.

---

# AMCL Scope

This milestone includes all of the following first-version components:

1. Localization data model
2. Deterministic random-number ownership
3. 2D LiDAR simulator
4. Map distance / likelihood representation
5. Noisy odometry simulator
6. Differential-drive particle motion model
7. Local Gaussian particle initialization
8. Global free-space particle initialization
9. Likelihood-field laser sensor model
10. Particle weight normalization
11. Effective sample size
12. Low-variance/systematic resampling
13. Adaptive KLD particle-count control
14. Fast/slow recovery statistics
15. Random-particle recovery injection
16. Weighted pose estimation
17. Circular heading mean
18. Pose covariance
19. Convergence/error metrics
20. Simulator runtime integration
21. Particle-cloud rendering
22. Estimated-pose rendering
23. Optional LiDAR rendering if inexpensive
24. Inspector localization statistics
25. Deterministic unit tests
26. End-to-end convergence test
27. Moving-localization tracking test
28. Kidnapped-robot recovery test
29. Full existing regression

This is intentionally a full vertical slice.

---

# First-Version Non-Goals

Do not implement:

- ROS
- ROS 2
- TF tree
- nav_msgs / sensor_msgs
- pluginlib
- external AMCL dependency
- SLAM
- map building
- dynamic obstacle tracking
- multi-LiDAR fusion
- IMU fusion
- EKF / UKF
- 3D localization
- 3D LiDAR
- scan matching
- ICP
- graph SLAM
- localization persistence across application restart
- production-grade real-time optimization
- GPU acceleration
- path-planner redesign
- 8-neighbor A*
- Theta*
- path smoothing
- controller redesign
- dynamic replanning

AMCL must be implemented natively in this repository using the existing map and simulator.

Do not copy ROS/Nav2 implementation wholesale.

Use standard AMCL concepts, but keep the code appropriate for this project's scale and architecture.

---

# Reference Behavior

Use standard AMCL concepts:

```text
Known static 2D map
+ differential odometry
+ 2D laser observations
+ particle filter
+ likelihood-field sensor model
+ adaptive particle count
+ recovery sampling
→ estimated robot pose
```

Recommended parameter vocabulary:

```text
alpha1
alpha2
alpha3
alpha4
alpha5

minParticles
maxParticles

pfErr
pfZ

recoveryAlphaSlow
recoveryAlphaFast

sigmaHit
zHit
zRand
likelihoodMaxDistance

maxBeams

updateMinTranslation
updateMinRotation

resampleInterval
```

Names may follow the project's existing C++ style.

Do not introduce parameters that have no first-version behavior.

---

# Required Initial Reading

The main agent must first read:

- `AGENTS.md`
- `docs/agent/STATUS.md`
- `docs/specs/SystemOverview.md`
- `docs/specs/MapCoordinateSpec.md`
- `docs/specs/PathPlannerSpec.md`

Then inspect current files responsible for:

- `Simulator`
- `AMR`
- `Environment`
- `MapData`
- `CoordinateMapper`
- `MapValidator`
- `PathPlanner`
- `PathExecution`
- collision geometry
- rendering
- Inspector UI
- tests
- Makefile

Search the repository for:

```text
AMCL
localization
particle
laser
lidar
odometry
sensor
range
ray
```

Confirm whether any reusable localization code already exists before adding new components.

Do not read unrelated documentation.

Do not update:

- `README.md`
- `Document.md`
- `docs/specs/README.md`
- `AGENTS.md`

---

# Phase 1 — Clean Baseline

Before production edits:

```text
mingw32-make clean
mingw32-make all
mingw32-make test
```

Confirm:

```text
79 PASS
0 FAIL
```

Also run the six existing test executables directly.

Record the current:

- AMR pose representation
- AMR update flow
- automatic motion flow
- manual motion flow
- collision acceptance flow
- MapData obstacle representation
- world boundary representation
- grid resolution
- Simulator update order
- Simulator render order
- Inspector layout

Do not edit production code during baseline collection.

---

# Phase 2 — Multi-Agent Investigation Batch

Use no more than 3 live investigation subagents concurrently.

If `agent thread limit reached` occurs:

- do not repeatedly retry,
- continue remaining investigation serially,
- do not block the milestone solely because another subagent cannot be created.

Subagents are primarily read-only investigators.

The main agent is the production integration owner.

## Explorer A — Localization Architecture and Particle Filter

Investigate how a native AMCL subsystem should fit the existing repository.

Focus on:

- particle data structure
- AMCL configuration
- RNG ownership
- initialization
- motion update
- weight update
- normalization
- ESS
- resampling
- KLD sampling
- recovery injection
- pose estimate
- covariance
- deterministic testing

Return:

- recommended classes/files
- responsibility boundaries
- state lifecycle
- update API
- initialization API
- reset/reinitialize behavior
- deterministic RNG strategy
- edge cases
- test strategy
- integration risks

Do not edit production code.

## Explorer B — LiDAR and Map Likelihood Model

Investigate the existing map geometry and design the simulated range sensor and likelihood representation.

Focus on:

- ray casting against obstacle cell AABBs
- ray termination at world boundary
- beam angles
- min/max range
- range noise
- beam subsampling
- obstacle-distance queries
- likelihood field
- map-change invalidation
- computational cost for current map scale

Return:

- recommended classes/files
- ray intersection algorithm
- map-distance representation
- update/rebuild policy
- numerical tolerances
- test cases
- performance risks

Do not edit production code.

## Explorer C — Odometry and Simulator Integration

Investigate runtime motion and where localization updates should occur.

Focus on:

- ground-truth pose capture
- previous/current pose delta
- manual motion
- autonomous following
- reset/start synchronization
- map editing
- planning
- rendering
- Inspector
- collision rollback
- localization initialization/reinitialization

Return:

- exact integration points
- recommended noisy odometry model
- update ordering
- reset semantics
- visualization ownership
- Inspector fields
- test seams
- regression risks

Do not edit production code.

---

# Phase 3 — Main-Agent Architecture Synthesis

After investigation:

1. Verify subagent findings directly against repository code.
2. Consolidate class responsibilities.
3. Prevent circular dependencies.
4. Prefer plain C++ value types and narrowly scoped classes.
5. Keep SFML dependency out of pure probabilistic logic where practical.
6. Keep AMCL independent of rendering.
7. Keep sensor simulation separate from particle-filter inference.
8. Keep MapData authoritative for map geometry.
9. Keep AMR authoritative for ground truth only.

Recommended conceptual dependency direction:

```text
MapData
   ↓
DistanceField / LidarSimulator

AMR ground truth
   ↓
OdometrySimulator
   ↓
AmclLocalizer
       ↑
LaserScan

AmclLocalizer
   ↓
LocalizationEstimate

Simulator
   coordinates all of the above
```

Do not create a single giant `AMCL.cpp` containing every responsibility.

Do not over-fragment the implementation into unnecessary abstractions either.

---

# Phase 4 — Localization Data Model

Introduce the minimum clear value types required.

Recommended concepts:

```text
Particle
    Pose2D pose
    double weight

LaserScan
    vector<float> ranges
    angleMin
    angleIncrement
    minRange
    maxRange

OdometryDelta
    translation / rotation decomposition
    or equivalent differential motion delta

LocalizationEstimate
    Pose2D pose
    covariance
    valid/converged flags
    particleCount
    effectiveSampleSize

AmclConfig
    particle counts
    noise parameters
    likelihood parameters
    thresholds
    recovery parameters
    deterministic seed
```

Use `double` for probability/statistical calculations unless current code conventions strongly justify otherwise.

Pose/world values may interoperate with existing `Pose2D`.

Avoid ROS-like message wrappers.

---

# Phase 5 — Deterministic Random Number Ownership

AMCL behavior must be testable.

Implement one explicit RNG ownership path.

Requirements:

- deterministic seed can be configured for tests,
- production/default seed behavior is explicit,
- subcomponents do not each create independent hidden random engines,
- Gaussian and uniform sampling use the owned RNG,
- tests do not depend on wall-clock seeding.

Do not use `rand()`.

---

# Phase 6 — 2D LiDAR Simulator

Implement a native simulated 2D range sensor.

## Inputs

```text
ground-truth pose
MapData
LiDAR configuration
RNG
```

## Outputs

```text
LaserScan
```

## Required Behavior

Support:

- configurable field of view
- configurable beam count
- minimum range
- maximum range
- sensor heading relative to AMR heading
- optional Gaussian range noise
- deterministic noise with configured RNG
- world-boundary termination
- obstacle-cell intersection

First version may assume LiDAR origin is AMR center.

Do not model sensor height or 3D geometry.

## Ray Casting

Each beam must determine the nearest valid hit against:

- occupied obstacle cell rectangles
- world boundary termination

Use a deterministic geometric method.

For current map size, correctness is more important than advanced spatial acceleration.

Avoid stepping by an arbitrarily large increment that can skip thin geometry.

A grid traversal or exact ray/AABB intersection approach is preferred.

## Edge Cases

Test:

- no obstacle before max range
- obstacle directly ahead
- nearest of multiple obstacles
- boundary hit
- diagonal beam
- origin near obstacle
- max-range clamp
- deterministic noise
- invalid configuration rejection

---

# Phase 7 — Likelihood / Distance Field

Build a reusable known-map likelihood representation.

## Purpose

The likelihood-field sensor model requires:

```text
query world point
→ distance to nearest occupied map surface
```

## Requirements

- derived from physical MapData
- not persisted into map files
- rebuilt when relevant map geometry changes
- deterministic
- bounded by configurable `likelihoodMaxDistance`
- handles world boundary consistently with LiDAR simulation
- efficient enough for max particle count × selected beams

For current grid scale, a precomputed grid-based distance field is acceptable.

If using a grid distance field:

- document cell-center vs surface-distance semantics,
- preserve CoordinateMapper usage,
- do not mutate MapData.

If exact obstacle-surface distance is simple enough, that is also acceptable.

Add unit tests around known obstacle configurations.

---

# Phase 8 — Noisy Odometry Simulator

Introduce odometry distinct from ground truth.

## Required Flow

```text
previous ground-truth AMR pose
        ↓
current ground-truth AMR pose
        ↓
compute true incremental motion
        ↓
inject configurable odometry noise
        ↓
produce noisy odometry increment / odom pose
```

The localizer must receive the noisy result, not the true pose.

## Required Behavior

- supports forward motion
- supports in-place rotation
- supports combined translation/rotation
- normalizes angles
- zero motion remains stable
- deterministic with fixed seed
- integrates during both manual and autonomous movement

Do not modify AMR physics solely to create odometry.

Odometry simulation observes executed AMR motion.

Collision rollback must not generate fake odometry motion for a motion that was rejected.

---

# Phase 9 — Particle Initialization

Support both first-version initialization modes.

## Local Gaussian Initialization

Input:

```text
initial mean pose
initial x/y/yaw standard deviations or covariance
```

Generate particles around the configured initial pose.

Use valid finite poses.

Particles outside the world or inside occupied space must be rejected/resampled or handled by a documented deterministic policy.

## Global Initialization

Generate particles across valid free map space.

Requirements:

- position uniformly distributed over valid free area/cells
- heading uniformly distributed over [-pi, pi)
- particle weights initially normalized
- obey `minParticles` / configured initialization count

Global initialization must not use the true AMR pose.

---

# Phase 10 — Differential Motion Model

Implement the AMCL particle motion update using noisy differential-drive odometry.

Use a standard odometry decomposition such as:

```text
rot1
trans
rot2
```

with configurable noise parameters analogous to:

```text
alpha1
alpha2
alpha3
alpha4
alpha5
```

Requirements:

- particle propagation depends on measured odometry increment
- noise magnitude scales with motion
- heading is normalized
- zero/near-zero translation handles rotation without numerical instability
- deterministic with fixed seed
- no ground-truth pose access

Do not directly move every particle by the same exact ground-truth delta.

Add statistical but deterministic-seed tests.

---

# Phase 11 — Likelihood-Field Laser Sensor Model

Implement the first-version AMCL observation model.

Use selected beams from the simulated scan.

For each particle:

1. transform each selected beam endpoint into map/world space from the particle pose,
2. query nearest-obstacle distance from the likelihood representation,
3. compute hit likelihood,
4. include random-measurement probability,
5. combine beam contributions into a stable particle weight update.

Recommended first-version terms:

```text
zHit
zRand
sigmaHit
likelihoodMaxDistance
maxBeams
```

Do not implement the full beam short/max mixture unless actually required by the selected likelihood-field formulation.

## Numerical Stability

Avoid multiplying many tiny floating-point values directly if it causes underflow.

Log-likelihood accumulation is acceptable and preferred if it simplifies stability.

After weight update:

- all weights must be finite,
- weights must be non-negative,
- the normalized sum must be approximately 1.

If all particle likelihoods collapse to zero/non-finite:

- recover using a documented safe fallback,
- do not propagate NaNs.

---

# Phase 12 — Weight Normalization and ESS

Implement reusable normalization.

Requirements:

```text
sum(weights) ≈ 1
```

Handle:

- normal weights
- extremely small weights
- zero total
- non-finite values

Calculate effective sample size:

```text
ESS = 1 / sum(w_i^2)
```

Use ESS as a diagnostic.

It may be used as a resampling trigger in addition to the configured resample interval if the architecture supports it cleanly.

Do not introduce an arbitrary opaque threshold without exposing/documenting it.

---

# Phase 13 — Low-Variance / Systematic Resampling

Implement deterministic-seed low-variance or systematic resampling.

Requirements:

- samples according to normalized weights,
- avoids O(N²) roulette-wheel behavior,
- resets resampled weights consistently,
- preserves configured minimum/maximum count constraints,
- handles degenerate inputs safely.

Add tests with highly skewed distributions.

---

# Phase 14 — Adaptive KLD Particle Count

Implement first-version KLD-sampling or equivalent standard AMCL adaptive particle-count control.

Requirements:

- particle count adapts between `minParticles` and `maxParticles`,
- occupied particle bins are defined in x/y/theta,
- bin resolution is explicit/configurable or clearly named constants,
- `pfErr` controls approximation error,
- `pfZ` controls confidence,
- output particle count is deterministic for fixed RNG and input belief,
- low-diversity/concentrated belief may use fewer particles,
- broad/multimodal belief may require more particles,
- never produce fewer than minimum or more than maximum.

Do not fake adaptive sampling by choosing a random count.

If implementing the standard KLD required-sample formula, isolate it into a testable helper.

Add direct unit tests for required-sample behavior.

---

# Phase 15 — Recovery Statistics and Random Injection

Implement first-version AMCL recovery behavior.

Track slow and fast running averages of observation quality using parameters analogous to:

```text
recoveryAlphaSlow
recoveryAlphaFast
```

During resampling, derive a random-particle injection probability from the fast/slow relationship.

Requirements:

- healthy tracking produces little/no unnecessary random injection,
- sudden severe mismatch can increase random-particle injection,
- random particles are sampled only from valid free map space,
- recovery behavior is disabled or inert when recovery alpha values are configured to zero,
- values remain numerically stable.

Do not teleport the estimate directly to ground truth.

Recovery must emerge from particles.

---

# Phase 16 — Pose Estimation

Compute the localization estimate from particle belief.

## Position

Use weighted mean x/y.

## Heading

Use circular mean:

```text
sum(w * cos(theta))
sum(w * sin(theta))
atan2(...)
```

Do not use arithmetic mean of wrapped angles.

## Covariance

At minimum compute a 3x3 covariance over:

```text
x
y
yaw
```

with wrapped angular residuals.

Requirements:

- finite values
- non-negative diagonal within numerical tolerance
- covariance decreases as belief converges in deterministic test scenarios
- estimate invalid state is explicit if belief is unavailable

---

# Phase 17 — AMCL Coordinator / Localizer

Create one clear high-level AMCL component that owns filter state and coordinates:

```text
initialize
motion update
sensor update
normalize
estimate
resample
recovery
```

Recommended external API shape conceptually:

```text
initializeLocal(...)
initializeGlobal(...)

update(odometryDelta, laserScan, mapLikelihood)

getParticles()
getEstimate()
getStatistics()

reset()
```

Exact names may follow existing style.

Do not expose every internal helper through Simulator.

---

# Phase 18 — Runtime Update Thresholds

Avoid unnecessarily updating AMCL on every tiny motion if a clean threshold mechanism can be added.

Support first-version thresholds analogous to:

```text
updateMinTranslation
updateMinRotation
resampleInterval
```

Requirements:

- accumulated odometry motion is not lost,
- sensor updates occur after sufficient movement or explicit initialization,
- first valid scan after initialization may update immediately,
- thresholds are deterministic and testable.

Do not make localization depend on wall-clock timing.

---

# Phase 19 — Simulator Integration

Integrate localization into the existing runtime without breaking navigation.

## Ground Truth

`AMR` remains ground truth.

## Localization State

Simulator owns or coordinates a dedicated localization subsystem.

## Initialization

When Start Pose is configured:

- AMR still synchronizes to Start as current behavior requires,
- localization may initialize around Start with configurable uncertainty,
- do not initialize every particle exactly on ground truth.

Map load / Start replacement must rebuild or reset localization state as appropriate.

## Runtime Ordering

Choose and document a consistent order similar to:

```text
1. process input
2. execute AMR motion
3. collision acceptance / rollback
4. derive accepted ground-truth pose change
5. update noisy odometry
6. generate laser scan
7. update AMCL when thresholds permit
8. update estimated pose/statistics
9. render
```

Do not generate odometry from rejected collision motion.

## Planning

PathPlanner must continue using configured MapData Start/Goal semantics.

Do not silently switch navigation to use AMCL estimate in this milestone.

Localization is observational for now.

---

# Phase 20 — Localization Reset Semantics

Define consistent behavior for:

- new Start Pose
- Start heading change
- Ctrl+R
- map clear
- map load
- obstacle edit
- world-boundary change if supported
- global localization request if exposed

Minimum rules:

```text
map geometry changes
→ likelihood representation invalidated/rebuilt

Start reset
→ ground truth follows existing behavior
→ odometry state reset
→ AMCL locally reinitialized with uncertainty

global initialization
→ particle belief spread across free map
→ ground truth unchanged
```

Do not allow stale distance fields after map editing.

---

# Phase 21 — Visualization

Render localization state clearly without contaminating inference code.

## Particle Cloud

Draw particles using lightweight primitives.

Visual representation should communicate:

- x/y position
- optionally heading with tiny direction mark if inexpensive
- optionally weight via opacity/size only if simple

Rendering thousands of particles must remain responsive.

Avoid creating a separate SFML shape object for every particle every frame if a vertex-based representation is simpler.

## Estimated Pose

Draw a distinct estimated-pose marker and heading.

It must be visually distinguishable from:

- ground-truth AMR
- Start marker
- Goal marker
- particle cloud

## LiDAR

If straightforward and performance-safe:

- draw a subset of current scan rays or endpoints,
- make visualization optional or lightweight.

LiDAR drawing is secondary to AMCL correctness.

---

# Phase 22 — Inspector Localization Statistics

Add a concise localization section.

Display at least:

```text
Localization

State:
Particles:
ESS:

Estimated X:
Estimated Y:
Estimated Heading:

Ground Truth X:
Ground Truth Y:
Ground Truth Heading:

Position Error:
Heading Error:

Odom X:
Odom Y:
Odom Heading:
```

If covariance is available compactly, show:

```text
Sigma X
Sigma Y
Sigma Heading
```

Use ground truth only for simulation diagnostics.

Do not feed displayed error back into AMCL.

---

# Phase 23 — Convergence State

Provide a first-version convergence diagnostic.

Define explicit thresholds/config for:

- position uncertainty
- heading uncertainty
- minimum effective particle behavior if used

Possible states:

```text
Uninitialized
Tracking
Converged
Recovering
```

Do not build a generalized FSM framework.

These states are diagnostics derived from localization belief/recovery condition.

Do not use actual ground-truth error as the primary convergence criterion.

Ground truth may be reported separately for validation.

---

# Phase 24 — Unit Test Expansion

Add dedicated tests for each pure subsystem.

Recommended new test executables or grouped suites:

```text
LidarSimulatorTests
DistanceFieldTests
OdometrySimulatorTests
AmclMotionModelTests
AmclSensorModelTests
ParticleFilterTests
AmclLocalizerTests
LocalizationIntegrationTests
```

Combine suites when that keeps the Makefile simpler.

Do not create needless one-test executables.

## Minimum Unit Coverage

### LiDAR

- straight hit
- diagonal hit
- nearest hit
- world-boundary hit
- max range
- deterministic noise

### Distance Field

- obstacle cell distance
- neighboring cell distance
- empty area
- clamped max distance
- map rebuild

### Odometry

- zero motion
- translation
- rotation
- mixed motion
- deterministic noise
- collision-rejected motion integration path if testable

### Motion Model

- no motion
- forward propagation
- turn propagation
- normalized heading
- seeded noise spread

### Sensor Model

- correct-pose scan scores better than clearly wrong pose in deterministic map
- finite weights
- range handling
- beam subsampling

### Weighting

- normalization
- zero-weight fallback
- ESS
- no NaNs

### Resampling

- skewed weights replicate high-weight hypotheses
- systematic sampling bounds
- normalized output

### KLD

- min bound
- max bound
- concentrated bins
- broad bins
- deterministic required count

### Recovery

- no mismatch injection near zero
- severe mismatch increases injection
- zero recovery alphas disable behavior

### Estimate

- weighted x/y
- circular heading around +pi/-pi
- covariance
- finite output

---

# Phase 25 — Deterministic End-to-End Convergence Test

This is a hard Completion Gate requirement.

Build a deterministic map scenario with asymmetric geometry sufficient to localize uniquely.

Example characteristics:

```text
known world boundary
multiple non-symmetric obstacle walls/blocks
known ground-truth pose
simulated scan
initial particle uncertainty
deterministic RNG
```

Run repeated AMCL updates with realistic odometry + scans.

Required assertions:

- estimate becomes valid,
- particle distribution contracts,
- position estimate approaches ground truth within a documented tolerance,
- heading estimate approaches ground truth within a documented tolerance,
- covariance decreases from initialization,
- all intermediate weights remain finite,
- particle count remains within configured bounds.

Do not make the test pass by initializing particles almost exactly at truth.

The initial uncertainty must be meaningful.

Use tolerances appropriate to the existing 50-world-unit grid resolution.

---

# Phase 26 — Motion + Localization Tracking Test

Create a deterministic scenario where the robot moves through several updates.

Required flow:

```text
initialize with uncertainty
→ robot translates
→ robot turns
→ robot translates
→ noisy odometry accumulates error
→ LiDAR updates correct the belief
```

Verify:

- odometry pose diverges measurably from ground truth under configured noise,
- AMCL estimate remains or returns closer to ground truth than raw odometry after sufficient observations,
- estimate does not directly equal ground truth at every step,
- no NaNs,
- no particle-count bound violation.

This demonstrates that the sensor model is doing actual localization work.

---

# Phase 27 — Kidnapped-Robot Recovery Test

This is also a hard Completion Gate requirement unless investigation proves recovery cannot be implemented safely in the current milestone.

Scenario:

```text
AMCL converged near Pose A
        ↓
ground-truth AMR is teleported to distant valid Pose B
        ↓
do NOT reset particle filter
        ↓
odometry alone cannot explain the jump
        ↓
new LiDAR scans strongly disagree
        ↓
recovery mechanism increases random hypotheses
        ↓
belief eventually finds Pose B
        ↓
AMCL reconverges near Pose B
```

Requirements:

- use deterministic seed,
- no direct ground-truth injection into the filter,
- test must detect a genuine recovery phase,
- final position and heading errors must fall below documented thresholds,
- complete within a bounded number of updates,
- no infinite loop.

If default recovery alpha values are zero, use explicit non-zero recovery config in this test.

Do not change production defaults solely to force the test.

---

# Phase 28 — Performance Sanity Check

Measure basic runtime cost without building a benchmark framework.

Test or manually inspect with:

```text
minParticles around several hundred
maxParticles around a few thousand
selected laser beams around several dozen
```

Confirm:

- interactive simulator remains usable,
- no obviously quadratic particle-resampling loop,
- no per-particle full-map rebuild,
- likelihood field is reused,
- particle rendering remains reasonable.

Optimize only demonstrated hotspots.

Do not perform speculative micro-optimization.

---

# Phase 29 — Full Regression

After all localization work:

```text
mingw32-make clean
mingw32-make all
mingw32-make test
```

Run all test executables directly.

Existing baseline must remain:

```text
79 existing tests PASS
0 existing tests FAIL
```

All new localization tests must also pass.

Do not weaken:

- map tests
- PathPlanner tests
- PathExecution tests
- SimulatorRuntime tests

Do not modify approved planning semantics to accommodate AMCL.

---

# Phase 30 — Desktop Runtime Sanity Check

If the SFML executable can be launched:

Perform a limited manual/automated sanity attempt.

Verify where observable:

```text
Start placed
→ particle cloud initializes around uncertain Start
→ estimated pose marker appears
→ robot moves
→ odometry differs slightly from truth
→ particles update with scans
→ estimate tracks robot
```

Also verify:

- map editing does not leave stale likelihood data,
- reset reinitializes localization,
- navigation still runs,
- particle rendering does not hide the robot/path excessively.

If Windows UI automation cannot attach to the SFML window, report this honestly.

Do not claim visual verification without observing it.

---

# Completion Gate

The milestone is complete only if ALL applicable items below are satisfied.

## Architecture

- Ground truth, odometry, scan, particle belief, and estimate are separate.
- AMCL does not read ground truth as its estimate.
- MapData remains authoritative map state.
- Simulator coordinates integration.
- Probabilistic logic is not embedded in rendering.

## Sensor Simulation

- LiDAR ray casting works.
- measurement noise is deterministic when seeded.
- map boundary and obstacles behave consistently.

## Map Model

- likelihood/distance representation works.
- map changes invalidate/rebuild derived localization map state.

## Motion

- noisy odometry exists separately from truth.
- particle differential motion model exists.
- motion noise is configurable.

## Particle Filter

- initialization works.
- normalization works.
- ESS works.
- resampling works.
- adaptive KLD count works.
- min/max count enforced.
- recovery statistics work.
- random recovery injection works.

## Estimation

- weighted pose estimate works.
- circular heading mean works.
- covariance works.
- convergence diagnostics work.

## Integration

- runtime AMCL updates during accepted robot motion.
- reset/start behavior is coherent.
- navigation behavior remains intact.
- particle and estimate visualization exist.
- Inspector statistics exist.

## Tests

- all previous 79 tests pass.
- all new unit tests pass.
- deterministic convergence test passes.
- deterministic moving-localization test passes.
- kidnapped-robot recovery test passes.
- 0 total test failures.

If some requirement is genuinely blocked:

- identify the exact requirement,
- state the blocker,
- preserve all completed safe work,
- do not silently declare the entire milestone complete.

---

# Implementation Discipline

Prefer simple, explicit C++.

Avoid:

- template-heavy generic frameworks,
- dependency injection frameworks,
- unnecessary inheritance,
- ROS-style plugin architecture,
- premature threading,
- hidden global RNG,
- singleton localization state,
- duplicated map representations with unclear ownership.

New dependencies are not allowed unless absolutely necessary.

Prefer the C++ standard library and existing SFML dependency.

---

# Numerical Discipline

All probabilistic code must defend against:

- NaN
- infinity
- zero total weight
- divide-by-zero
- invalid standard deviation
- invalid particle count
- angle wrap errors
- log(0)
- underflow from repeated likelihood multiplication

Use clearly named epsilon/floor constants where required.

Do not hide invalid state by silently producing arbitrary estimates.

---

# Multi-Agent Execution Rules

This is a long-running task.

Use up to 3 concurrent subagents.

Recommended initial batch:

```text
Main Sol Agent
├── Explorer A: particle filter / KLD / recovery architecture
├── Explorer B: LiDAR / likelihood-field architecture
└── Explorer C: odometry / Simulator integration
```

After the first batch completes:

- the main agent synthesizes architecture,
- production integration remains owned by the main agent,
- completed agents may be reused for review if the tool supports it,
- do not repeatedly spawn new agents if capacity is unavailable.

If capacity allows after major implementation:

```text
Reviewer A
→ mathematical/probabilistic correctness

Reviewer B
→ integration/regression risks

Reviewer C
→ deterministic test completeness
```

Reviewers should report findings.

The main agent owns final fixes.

If `agent thread limit reached` occurs:

- continue serially,
- do not repeatedly retry spawn,
- do not abandon the milestone.

---

# Long-Running Task Rules

This task explicitly authorizes substantial implementation.

Do not stop after:

- creating data types,
- implementing LiDAR only,
- implementing particles only,
- obtaining a compiling build,
- passing only unit tests,
- showing a particle cloud,
- obtaining one convergence demo.

Continue through:

```text
baseline
→ architecture
→ sensor simulation
→ odometry
→ particle filter
→ likelihood model
→ KLD
→ recovery
→ estimation
→ integration
→ visualization
→ deterministic unit tests
→ convergence test
→ moving localization test
→ kidnapped recovery test
→ full regression
→ STATUS
→ STOP
```

Do not expand into unrelated navigation features.

Do not optimize for consuming tokens.

Optimize for completing this full milestone correctly.

---

# STATUS Update

Update only:

`docs/agent/STATUS.md`

Replace stale milestone content with the actual repository state.

Record concisely:

- current AMCL milestone result
- new localization modules
- ground truth / odometry / estimate ownership
- LiDAR model
- likelihood model
- motion model
- particle initialization
- resampling/KLD behavior
- recovery behavior
- estimate/covariance behavior
- Simulator integration
- visualization
- test totals
- deterministic convergence result
- kidnapped recovery result
- runtime verification status
- known limitations
- next smallest meaningful milestone

Do not turn STATUS into a chronological development log.

Do not update unrelated documentation.

---

# Git Ownership

For this orchestrated run:

- Do NOT run `git add`
- Do NOT run `git commit`
- Do NOT run `git push`

The external orchestrator owns Git finalization after Codex exits successfully.

This task-specific rule overrides repository instructions that assign Git finalization to Codex.

Before returning control, ensure all intended production/test/STATUS changes remain in the working tree.

---

# Final Report

Before STOP, report:

1. Production files added/modified
2. Test files added/modified
3. AMCL architecture implemented
4. LiDAR simulation behavior
5. Odometry simulation behavior
6. Motion model behavior
7. Likelihood-field behavior
8. Particle initialization behavior
9. Resampling and KLD behavior
10. Recovery behavior
11. Pose estimate/covariance behavior
12. Simulator/rendering integration
13. Convergence test result
14. Moving-localization test result
15. Kidnapped-robot recovery test result
16. Full regression commands and result
17. Total PASS / FAIL count
18. Remaining limitations or blockers

Do not produce a tutorial.

After the final report, STOP.
