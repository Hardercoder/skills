# Observability Plan — <system>

- **Date**: YYYY-MM-DD
- **Owner**: <name>

## 1. Logs (structured)
- Format: <JSON / key=value>; required fields: <trace_id, user_id, ...>
- Where they go: <log platform>

## 2. Metrics (RED)
| Metric | Type | Alert threshold |
|---|---|---|
| Rate (req/s) | counter | |
| Errors (%) | gauge | > <x>% for <y>m |
| Duration (p95/p99) | histogram | > <ms> |

## 3. Traces
- Sampling: <always / <x>%>; propagated across: <services>

## 4. Dashboards & alert routing
- Dashboard: <link>; pages: <team / on-call>

## 5. Ownership
- Responder runbook: <link to un-doc-gen runbook>
