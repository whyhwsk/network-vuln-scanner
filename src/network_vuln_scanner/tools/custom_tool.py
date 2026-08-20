import shutil
import subprocess
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Known Windows install locations to fall back to if the binary isn't on PATH.
_KNOWN_LOCATIONS = {
    "nmap": [r"C:\Program Files (x86)\Nmap\nmap.exe", r"C:\Program Files\Nmap\nmap.exe"],
}


class TargetInput(BaseModel):
    """Common input schema for all scan tools."""
    target: str = Field(..., description="IP address or hostname of the authorized target device to scan.")


def _resolve_binary(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    import os
    for candidate in _KNOWN_LOCATIONS.get(name, []):
        if os.path.isfile(candidate):
            return candidate
    return name


def _run_subprocess(cmd: list[str], timeout: int) -> str:
    cmd = [_resolve_binary(cmd[0]), *cmd[1:]]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout or result.stderr
    except FileNotFoundError:
        return f"Error: '{cmd[0]}' is not installed or not on PATH. Install it and retry."
    except subprocess.TimeoutExpired:
        return f"Error: '{cmd[0]}' scan timed out after {timeout} seconds."


class NmapFullScanTool(BaseTool):
    name: str = "Nmap Full Scan"
    description: str = (
        "Runs a full TCP port sweep (all 65535 ports) with service/version "
        "detection, default NSE scripts, vulners CVE matching, and banner/crypto "
        "checks on SSH and Telnet (ssh2-enum-algos, telnet-encryption, banner) "
        "against a single target IP or hostname. This is the primary discovery "
        "and fingerprinting scan — run it first. Only scan devices you are "
        "explicitly authorized to test."
    )
    args_schema: Type[BaseModel] = TargetInput

    def _run(self, target: str) -> str:
        return _run_subprocess(
            [
                "nmap", "-sV", "-sC", "-p-",
                "--script", "vulners,banner,ssh2-enum-algos,telnet-encryption",
                target,
            ],
            timeout=1800,
        )


class SnmpEnumTool(BaseTool):
    name: str = "SNMP Enumerator"
    description: str = (
        "Checks UDP port 161 for SNMP, brute-forces common default community "
        "strings (public/private/etc.), and if one works, enumerates system "
        "info, interfaces, and sysdescr via that community string. Network "
        "devices very commonly leave default SNMP community strings enabled. "
        "Only scan devices you are explicitly authorized to test."
    )
    args_schema: Type[BaseModel] = TargetInput

    def _run(self, target: str) -> str:
        return _run_subprocess(
            [
                "nmap", "-sU", "-p", "161", "-T4",
                "--max-retries", "1", "--host-timeout", "90s",
                "--script", "snmp-brute,snmp-info,snmp-sysdescr,snmp-interfaces",
                target,
            ],
            timeout=150,
        )


class SshAuditTool(BaseTool):
    name: str = "SSH Audit"
    description: str = (
        "Runs ssh-audit against a target's SSH service (default port 22) to "
        "flag weak/deprecated key exchange algorithms, ciphers, MACs, and host "
        "key types, and to identify the exact SSH server version/banner. Only "
        "run this if the Nmap Full Scan found an open SSH port. Only scan "
        "devices you are explicitly authorized to test."
    )
    args_schema: Type[BaseModel] = TargetInput

    def _run(self, target: str) -> str:
        return _run_subprocess(["ssh-audit", "--skip-rate-test", target], timeout=120)
