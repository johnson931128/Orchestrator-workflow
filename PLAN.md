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