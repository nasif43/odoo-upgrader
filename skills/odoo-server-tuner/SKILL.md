---
name: odoo-server-tuner
description: Specialized for tuning Odoo on single-server, low-spec hardware (e.g., 4GB RAM). It prioritizes deadlock prevention (minimum worker count) and aggressive memory recycling to keep the server responsive during PDF generation.
---

# Odoo Server Tuner (Anti-Deadlock Edition)

## 1. The Anti-Deadlock Worker Rule
To prevent `wkhtmltopdf` from hanging, you MUST have enough HTTP workers to handle the primary request PLUS the nested asset requests.

- **Production Minimum:** 4 to 5 workers (even on 1-2 cores).
- **Formula:** `workers = max(4, (CPU_CORES * 2) + 1)`
- **Cron:** `max_cron_threads = 1`

## 2. Low-Spec RAM Management
When RAM is limited (e.g., 4GB), you must squeeze these workers by lowering their recycle threshold.

- **Available RAM (Odoo):** `Total_RAM - (System_1GB + Postgres_1GB)`
- **Soft Limit (Bytes):** `(Available_RAM / workers) * 0.7` (Aggressive recycling)
- **Hard Limit (Bytes):** `(Available_RAM / workers)`

**Example for 4GB RAM, 5 Workers:**
- Available: 2GB
- `limit_memory_soft = 293601280` (~280MB)
- `limit_memory_hard = 419430400` (~400MB)

## 3. Critical Network Tuning
- **report.url:** Ensure this is set in System Parameters to `http://127.0.0.1:8069` to bypass external proxies/firewalls.
- **Timeouts:**
  - `limit_time_cpu = 600`
  - `limit_time_real = 1200`

## 4. Optimization Stack
- **Redis:** Mandatory for session offloading to save RAM and I/O.
- **Postgres:** `shared_buffers = 25% of RAM`.
