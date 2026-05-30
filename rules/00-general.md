# Rule 00 — General Agent Behavior

These rules apply to every agent, every session, every task in this repo.

## Mindset
- Optimize for **leverage, throughput, and maintainability**. Prefer pragmatic-that-ships over perfect-that-stalls.
- For every non-trivial recommendation, answer the four questions: **why does this scale? what's the operational burden? what breaks at scale? what's the hidden tradeoff?**
- Challenge weak assumptions and surface better alternatives. Do not blindly agree. Intellectual friction is expected and wanted.
- Be direct and concise. No filler, no motivational language, no over-hedging.

## Source of truth
- The JSON in `.ai/state/` outranks your context window. When context is compacted or you're unsure, re-read state.
- Keep state current **as you work** — small frequent updates, not one big update at the end.
- If it isn't written to the relevant `.ai/state/*.json`, it didn't happen.

## Parallel agents (encouraged)
- You may and should **spin off subagents to run independent work in parallel**: research, scaffolding, test generation, audits, SEO/competitive research, multi-file edits.
- Launch independent subagents in a single message (multiple tool calls) so they run concurrently.
- Use a **dedicated verification subagent** for high-stakes work (security, data migrations, money flows, release gates).
- Constraint: **one writer per file** to avoid conflicts. Partition work by file or directory.
- Always reconcile subagent outputs back into the state files yourself before reporting done.

## Automation bias
- Anything done manually more than twice is a candidate for automation. Log it in `tech-debt.json` as `automation-opportunity` until automated.
- Prefer deterministic, observable, logged systems. If it can't be measured or logged, it can't be operated.

## Communication
- When you make a decision, state all three horizons (short/mid/long term).
- When you defer a gate or incur debt, say so explicitly and log it.
- Cite which state files you read and wrote in your summary.
