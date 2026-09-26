"""Plain-text QueryWatch report formatting."""

from __future__ import annotations

from ..models import AnalysisReport, Finding


_DIVIDER = "─" * 32


def format_console_report(report: AnalysisReport) -> str:
    """Format an analysis report for terminal output without extra packages."""
    summary = report.summary
    lines = [
        "QueryWatch",
        _DIVIDER,
        f"Queries: {summary.query_count}",
        f"Total DB time: {summary.total_duration_ms:.1f}ms",
        f"Slow queries: {summary.slow_query_count}",
        f"Duplicate groups: {summary.duplicate_group_count}",
        "",
        "Findings",
        _DIVIDER,
    ]

    if not report.findings:
        lines.append("No findings.")
    else:
        for index, finding in enumerate(report.findings):
            if index:
                lines.append("")
            lines.extend(_format_finding(finding))

    return "\n".join(lines)


def _format_finding(finding: Finding) -> list[str]:
    lines = [
        f"{finding.severity.upper()}  {finding.title}",
        finding.message,
    ]
    lines.extend(
        f"{key}: {value}" for key, value in sorted(finding.evidence.items())
    )
    if finding.suggestion:
        lines.append(f"Suggestion: {finding.suggestion}")
    return lines
