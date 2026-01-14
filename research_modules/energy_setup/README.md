# Stage 2: Energy Setup

> **Pipeline Stage:** 2 of 6  
> **Purpose:** Detect stored potential energy via compression and balance

## Philosophy

**Energy ≠ Direction.** Quiet stocks are often most interesting.

## Energy Behaviors

| Behavior | Question |
|:---------|:---------|
| Volatility Compression | Is volatility contracting? |
| Range Balance | Is price respecting a bounded range? |
| Mean Adherence | Is price staying close to reference values? |
| Energy Duration | Has compression persisted long enough? |

## Energy States

- **mature** (≥60): Ready for potential expansion
- **forming** (30-60): Building compression
- **none** (<30): No significant energy storage

## Usage

```powershell
python -m research_modules.energy_setup.runner --evaluate --symbols AAPL,GOOGL,MSFT
```

## Output

`data/energy/us/{YYYY-MM-DD}/{SYMBOL}_energy.parquet`
