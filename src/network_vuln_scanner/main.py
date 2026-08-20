#!/usr/bin/env python
import os
import socket
import sys
import warnings
from urllib.parse import urlparse

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")


def _disable_unreachable_proxy():
    """
    HTTP_PROXY/HTTPS_PROXY may point at a local VPN client (e.g. Clash) that
    isn't always running. If it's down, outbound LLM API calls hang instead
    of failing fast. Probe the proxy port; if it doesn't accept a connection,
    clear the proxy vars for this process so requests go direct.
    """
    for var in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        proxy_url = os.environ.get(var)
        if not proxy_url:
            continue
        parsed = urlparse(proxy_url)
        if not parsed.hostname or not parsed.port:
            continue
        try:
            with socket.create_connection((parsed.hostname, parsed.port), timeout=1):
                pass  # proxy is up, leave it configured
        except OSError:
            for clear_var in ("HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"):
                os.environ.pop(clear_var, None)
        break  # only need to probe once (HTTP/HTTPS proxy is normally the same host:port)


_disable_unreachable_proxy()

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
