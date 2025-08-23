from __future__ import annotations

from typing import Any, Dict, List, Optional

from .cli_runner import CLIRunner
from .debug_logger import DebugLogger


class JobsService:
	"""Service to fetch and normalize job data via the CLI."""

	def __init__(self, runner: CLIRunner, logger: DebugLogger | None = None) -> None:
		self.runner = runner
		self._logger = logger or DebugLogger(False, prefix="JOBS")

	def list_jobs(self, project_id: Optional[str], limit: int, offset: int) -> List[Dict[str, Any]]:
		# Always request deterministic paging and include project filter when present
		args: List[str] = [
			"jobs", "list", "--format", "json",
			"--limit", str(limit),
			"--offset", str(offset),
		]
		if project_id:
			args += ["--project-id", str(project_id)]
		self._logger.debug(f"list_jobs: project_id={project_id} limit={limit} offset={offset}")
		jobs = self.runner.run_cli_json(args) or []
		if not isinstance(jobs, list):
			return []
		return jobs

	@staticmethod
	def format_row(job: Dict[str, Any]) -> List[str]:
		job_id = str(job.get("job_id") or job.get("id") or "")
		# Truncate job ID to first 8 chars
		if len(job_id) > 8:
			job_id = job_id[:8]
		
		# Format completed_at or created_at
		completed_at = str(job.get("completed_at") or "")
		if not completed_at:
			completed_at = str(job.get("created_at") or "")
		# Truncate timestamp to just the date part if it's an ISO format
		if len(completed_at) > 10 and "-" in completed_at:
			completed_at = completed_at.split("T")[0]
		
		return [
			job_id,
			str(job.get("tool_name") or job.get("job_type") or ""),
			str(job.get("status", "")),
			completed_at,
		]


