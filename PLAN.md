## GOAL
ORCHESTRATOR
↓
讀另一個 repo 的 NEXT_TASK.md
↓
呼叫 Codex CLI
↓
Codex 在目標 repo 工作
↓
build / commit / push
↓
結束

Python → Codex CLI → CtrlKine-AMR

Orchestrator
      ↓
Sol High Main Agent
      ↓
┌────────────┬────────────┬────────────┐
│ Explorer A │ Explorer B │ Explorer C │
│ Coordinate │ MapData    │ File I/O   │
│ failures   │ failures   │ failures   │
└────────────┴────────────┴────────────┘
      ↓
Main Agent 收斂 findings
      ↓
分批修改 production code
      ↓
targeted tests
      ↓
full test
      ↓
STATUS
      ↓
Orchestrator commit + push
----
Ground Truth AMR
        │
        ├──────────────┐
        │              │
        ↓              ↓
 Odometry Model    Simulated LiDAR
   + noise          + ray casting
        │              │
        ↓              ↓
   Motion Update   Sensor Update
        └──────┬───────┘
               ↓
        Particle Filter
               ↓
      Weight Normalization
               ↓
      Adaptive Resampling
               ↓
        Pose Estimation
               ↓
   Estimated (x, y, θ, covariance)
               ↓
 Particle Cloud + Estimated Pose UI
 ---
 1. Localization data model
   Particle
   Pose estimate
   Covariance
   AMCL config/result

2. Ground Truth / Estimated Pose separation
   AMR 真實位置 ≠ Localization estimate

3. Odometry simulator
   wheel motion
   noisy odometry
   accumulated odom pose

4. 2D LiDAR simulator
   configurable beams
   FOV
   min/max range
   ray casting against MapData
   optional measurement noise

5. Occupancy / likelihood representation
   obstacles → occupancy
   distance-to-nearest-obstacle field

6. AMCL particle initialization
   local Gaussian initialization
   global uniform initialization

7. Differential-drive motion model
   odom delta
   noisy particle propagation
   alpha parameters

8. Laser likelihood-field sensor model
   predicted endpoint
   obstacle distance
   likelihood
   particle weight update

9. Weight normalization

10. Pose estimation
    weighted x/y
    circular mean for θ
    covariance

11. Resampling
    systematic / low-variance base
    adaptive KLD particle count

12. Recovery behavior
    w_slow / w_fast
    random particle injection

13. Simulator integration

14. Rendering
    particle cloud
    estimated pose
    ground-truth pose
    optional LiDAR rays

15. Inspector statistics
    particle count
    localization estimate
    position error
    heading error
    ESS / convergence state

16. Tests
    ray casting
    motion noise
    likelihood field
    sensor likelihood
    normalization
    resampling
    KLD
    pose estimate
    deterministic seeded runs
    convergence scenario
    kidnapped-robot recovery