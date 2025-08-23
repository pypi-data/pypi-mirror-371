import os
import subprocess

def run_command(cmd, cwd=None):
    """Run a shell command and stream output."""
    process = subprocess.Popen(
        cmd, shell=True, cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for line in iter(process.stdout.readline, b""):
        print(line.decode(), end="")
    process.wait()
    return process.returncode
