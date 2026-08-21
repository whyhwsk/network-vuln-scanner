#!/usr/bin/env python
import os
import sys
import warnings

# CrewAI's background telemetry (PostHog analytics) has no bounded timeout
# on its own network call, independent of the LLM's timeout/max_retries.
# Disable it — must be set before crewai is imported.
os.environ.setdefault("CREWAI_DISABLE_TELEMETRY", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def _force_bypass_proxy():
    """
    HTTP_PROXY/HTTPS_PROXY typically point at a local VPN client (e.g.
    Clash). Even when it's up and reachable, it has caused multi-minute
    hangs on some outbound call this crew makes (LLM and/or telemetry) —
    not worth chasing down per-destination. This crew's actual traffic
    (DeepSeek's API, nmap/ssh-audit against the target, etc.) works fine
    without it, so unconditionally bypass it for this process whenever a
    VPN/proxy is configured, running direct. If nothing is configured, this
    is a no-op and the run proceeds as-is.
    """
    had_proxy = any(
        os.environ.get(var) for var in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy")
    )
    for var in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
        os.environ.pop(var, None)
    if had_proxy:
        print("[STARTUP] VPN/proxy detected — bypassing it for this run (direct connection).")


_force_bypass_proxy()

from network_vuln_scanner.crew import NetworkVulnScanner


def run():
    """
    Run the crew.
    """
    if len(sys.argv) < 2:
        raise Exception("Usage: run <target-ip-or-hostname>")

    inputs = {
        'target': sys.argv[1],
    }

    try:
        NetworkVulnScanner().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'target': sys.argv[3] if len(sys.argv) > 3 else '127.0.0.1',
    }
    try:
        NetworkVulnScanner().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        NetworkVulnScanner().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'target': sys.argv[3] if len(sys.argv) > 3 else '127.0.0.1',
    }

    try:
        NetworkVulnScanner().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "target": trigger_payload.get("target", ""),
    }

    try:
        result = NetworkVulnScanner().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
