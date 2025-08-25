from __future__ import annotations

from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import subprocess
import sys
import threading
import re


class TestGate:
    """Runs pytest for the repository and returns a concise summary.

    Designed to be used from the TUI to gate project selection until tests pass.
    """

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        python_executable: Optional[str] = None,
        pytest_args: Optional[List[str]] = None,
    ) -> None:
        try:
            self.repo_root: Path = repo_root or Path(__file__).resolve().parents[2]
        except Exception:
            # Fallback to CWD if resolution fails
            self.repo_root = Path.cwd()
        self.python_executable: str = python_executable or sys.executable
        # Keep output informative (summary + warnings) without being overly verbose
        self.pytest_args: List[str] = pytest_args or ["-ra", "-W", "default"]
        self._running: bool = False

    def is_running(self) -> bool:
        return self._running

    def run_async(self, on_finished: Callable[[Dict[str, Any]], None]) -> None:
        if self._running:
            return
        self._running = True
        thread = threading.Thread(target=self._run_and_callback, args=(on_finished,), daemon=True)
        thread.start()

    def _run_and_callback(self, on_finished: Callable[[Dict[str, Any]], None]) -> None:
        try:
            result = self._run_sync()
        finally:
            self._running = False
        try:
            on_finished(result)
        except Exception:
            # Swallow callback errors
            pass

    def _run_sync(self) -> Dict[str, Any]:
        cmd = [self.python_executable, "-m", "pytest", *self.pytest_args]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            output = proc.stdout or ""
            ok = proc.returncode == 0
        except Exception as e:
            output = f"Error running tests: {e}"
            ok = False

        summary_line, warnings_count = self._extract_summary(output)
        return {
            "ok": ok,
            "output": output,
            "summary_line": summary_line,
            "warnings": warnings_count,
        }

    # Public sync API for non-UI (CLI) use
    def run_sync(self) -> Dict[str, Any]:
        return self._run_sync()

    @staticmethod
    def _extract_summary(output: str) -> tuple[str, int]:
        summary_line = ""
        warnings_count = 0
        # Find the last line that looks like a pytest summary
        lines = output.splitlines()
        for line in reversed(lines):
            if re.match(r"=+ .* =+", line.strip()):
                summary_line = line.strip()
                break
        # Extract warnings count if present
        if summary_line:
            m = re.search(r"(\d+)\s+warnings?", summary_line)
            if m:
                try:
                    warnings_count = int(m.group(1))
                except Exception:
                    warnings_count = 0
        return summary_line, warnings_count


