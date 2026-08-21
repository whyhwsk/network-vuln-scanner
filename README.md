# NetworkVulnScanner Crew

A two-agent [crewAI](https://crewai.com) pipeline for authorized network device
vulnerability assessment. Built for scanning embedded Linux network devices
(switches, OLTs, routers) running stacks like FRR or ZebOS, but works against
any authorized target.

**Only scan devices you are explicitly authorized to test.**

## What it does

1. **Network Security Scanner** agent runs:
   - `nmap` full TCP port sweep (`-p-`) with service/version detection, default
     scripts, and `vulners` CVE matching
   - SNMP enumeration (UDP 161) — brute-forces common default community
     strings and enumerates MIB info if one works
   - `ssh-audit` against any open SSH port — flags weak/deprecated ciphers,
     key exchange, MACs, and host key types
2. **Vulnerability Report Analyst** agent takes the raw findings and produces
   a severity-ranked report (Critical/High/Medium/Low/Info) with a concrete
   fix suggested for every finding, written to `report.md`.

A manual, low-thread default-credential check (e.g. via `hydra`, against an
authorized lab device only) is intentionally **not** automated, since
unattended brute-forcing risks account lockout or a denial-of-service
condition on the target device.

## Prerequisites

- Python >=3.10 <3.14
- [uv](https://docs.astral.sh/uv/) for dependency management:
  ```bash
  pip install uv
  ```
- [nmap](https://nmap.org/download.html) installed and on your `PATH`
- A [DeepSeek API key](https://platform.deepseek.com/api_keys)

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```
2. Copy the example env file and add your key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and set:
   ```
   DEEPSEEK_API_KEY=your_deepseek_api_key_here
   ```

## Running the Project

Run the crew against a target IP or hostname:

```bash
uv run run_crew <target-ip-or-hostname>
```

For example:

```bash
uv run run_crew 192.168.1.1
```

This scans the target, then writes a severity-ranked vulnerability report to
`report.md` in the project root.

> If you use a VPN/proxy client (e.g. Clash), the crew automatically bypasses
> it for this run's traffic — even when it's up and reachable, it can still
> stall specific outbound calls (LLM, telemetry) for minutes. Background
> telemetry is also disabled outright for the same reason.

See [`docs/process-trace.html`](docs/process-trace.html) for a diagram of
every hop `run_crew` makes between your machine, the target device, and the
DeepSeek API — open it in a browser after cloning.

## Project Structure

- `src/network_vuln_scanner/config/agents.yaml` — agent role/goal/backstory definitions
- `src/network_vuln_scanner/config/tasks.yaml` — scan and report task definitions
- `src/network_vuln_scanner/crew.py` — wires agents, tools, and LLMs together
- `src/network_vuln_scanner/tools/custom_tool.py` — the Nmap/SNMP/SSH-Audit tool implementations
- `src/network_vuln_scanner/main.py` — CLI entry point, unconditional proxy bypass, and telemetry disable

## Support

For support, questions, or feedback regarding crewAI itself:
- Visit the [documentation](https://docs.crewai.com)
- Reach out through the [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join the Discord](https://discord.com/invite/X4JWnZnxPb)
