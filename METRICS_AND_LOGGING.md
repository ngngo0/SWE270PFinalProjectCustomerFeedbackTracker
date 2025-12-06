# Quick Reference: Logging & Metrics Implementation

## Summary of Changes

### New Files Added

1. **`core/metrics_utils.py`** - Reusable metrics tracking module
2. **`test_metrics.py`** - Testing and demonstration script
3. **`QUICK_REFERENCE.md`** - This file

### Modified Files

1. **`core/system_runner2.py`** - Enhanced with logging and metrics
2. **`ui/app.py`** - Updated to display metrics in UI

### Generated Files (During Runtime)

1. **`agent_communication.log`** - Detailed execution logs
2. **`metrics/metrics_*.json`** - Structured metrics data

---

## Quick Start

### 1. Run the System

```bash
# Activate environment
conda activate feedback
# OR if using venv:
# .\feedback_env\Scripts\Activate.ps1

# Run UI
python -m ui.app
```

### 2. Test Metrics System

```bash
# Run automated tests
python test_metrics.py

# Run interactive demo
python test_metrics.py --demo
```

### 3. View Logs and Metrics

```bash
# View logs in real-time (Linux/Mac)
tail -f agent_communication.log

# View logs (Windows PowerShell)
Get-Content agent_communication.log -Wait

# View saved metrics
cat metrics/metrics_*.json
```

---

## Features

### 1. Comprehensive Metrics Tracking

The system now tracks:
- **API Calls**: Number of calls made by each agent
- **Token Usage**: Input, output, and total tokens per agent
- **Tool Calls**: Number of tool invocations
- **Iterations**: Agent execution loop iterations
- **Errors**: Error count per agent
- **Execution Time**: Total system runtime

**Access Methods:**
```python
# Use global tracker
from core.metrics_utils import get_global_tracker
tracker = get_global_tracker()

# Create custom tracker
tracker = MetricsTracker(['agent1', 'agent2'])
```

### 2. Enhanced Logging

All agent communications are logged with:
- Timestamps for all operations
- Agent identification
- Log levels (INFO, DEBUG, WARNING, ERROR)
- Tool call details with arguments
- API call summaries
- Input/output data previews

**Log Locations:**
- Console output (real-time)
- `agent_communication.log` (file)

### 3. Agent Communication Visibility

Enhanced visibility includes:
- Phase transitions clearly marked (Planning, Development, Testing)
- Data passed between agents logged
- Tool execution details
- Iteration counts
- Success/failure status
- Performance metrics per agent

### 4. Persistent Storage

Metrics and logs are saved to:
- `agent_communication.log` - Detailed execution logs
- `metrics/metrics_[timestamp].json` - Structured metrics data

---

## Common Use Cases

### Use Case 1: Monitor Real-time Execution

```bash
# In terminal 1: Run the system
python -m ui.app

# In terminal 2: Watch logs (Linux/Mac)
tail -f agent_communication.log

# In terminal 2: Watch logs (Windows PowerShell)
Get-Content agent_communication.log -Wait -Tail 50
```

### Use Case 2: Track Token Usage

```python
from core.metrics_utils import get_global_tracker

tracker = get_global_tracker()
# ... after execution ...
summary = tracker.get_summary()
total_tokens = summary['metrics']['total']['total_tokens']
print(f"Total tokens used: {total_tokens}")
```

### Use Case 3: Analyze Performance

```python
tracker = get_global_tracker()
tracker.print_summary(detailed=True)
tracker.save_to_file()  # Save for later analysis
```

### Use Case 4: Debug Agent Issues

```bash
# Check logs for errors (Linux/Mac)
grep "ERROR" agent_communication.log

# Check logs for errors (Windows PowerShell)
Select-String -Path agent_communication.log -Pattern "ERROR"

# Check specific agent (Linux/Mac)
grep "\[DEVELOPER\]" agent_communication.log

# Check specific agent (Windows PowerShell)
Select-String -Path agent_communication.log -Pattern "\[DEVELOPER\]"
```



