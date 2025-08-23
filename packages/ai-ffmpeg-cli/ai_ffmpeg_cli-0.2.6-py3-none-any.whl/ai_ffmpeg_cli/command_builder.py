"""Command builder for ai-ffmpeg-cli.

This module converts command plans into executable ffmpeg command lists,
applying appropriate defaults and ensuring proper argument ordering.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .intent_models import CommandPlan

logger = logging.getLogger(__name__)


def build_commands(plan: CommandPlan, assume_yes: bool = False) -> list[list[str]]:
    """Build executable ffmpeg commands from a command plan.

    Converts a CommandPlan into a list of executable ffmpeg command lists,
    applying appropriate defaults and ensuring proper argument ordering
    for optimal performance and compatibility.

    Args:
        plan: Command plan containing entries to convert
        assume_yes: Whether to add -y flag to overwrite output files

    Returns:
        List of ffmpeg command argument lists ready for execution
    """
    commands: list[list[str]] = []
    for entry in plan.entries:
        cmd: list[str] = ["ffmpeg"]
        if assume_yes:
            cmd.append("-y")

        # Some actions prefer -ss before -i for copy, but we construct here based on args
        # We assume args already contain any pre-input flags such as -ss when copying
        pre_input_flags: list[str] = []
        post_input_flags: list[str] = []

        # Split args into pre/post by presence of -ss/-t/-to which are often pre-input
        # Keep order stable otherwise for predictable command generation
        for i in range(0, len(entry.args), 2):
            flag = entry.args[i]
            val = entry.args[i + 1] if i + 1 < len(entry.args) else None
            bucket = pre_input_flags if flag in {"-ss", "-t", "-to"} else post_input_flags
            bucket.append(flag)
            if val is not None:
                bucket.append(val)

        # Build command with proper flag ordering
        cmd.extend(pre_input_flags)
        cmd.extend(["-i", str(entry.input)])
        for extra in entry.extra_inputs:
            cmd.extend(["-i", str(extra)])

        # Defaults and action-specific handling
        if plan.entries and plan.entries[0].args is entry.args:
            pass

        # Action-specific default codecs/filters
        # We infer action by plan summary keywords; better would be to carry action per entry.
        # Rely on presence of typical flags and file extensions.
        # Safer approach: detect based on output extension and flags included by router.
        # Apply broad defaults below.

        if "-vframes" in entry.args:
            # thumbnail action detected
            pass

        # If overlay is intended, builder must add filter_complex
        if "overlay=" in " ".join(entry.args):
            pass

        # For compression, ensure codec flag precedes CRF (from args)
        summary = plan.summary.lower()
        existing_args_str = " ".join(entry.args)
        if "compress" in summary and "-c:v" not in existing_args_str:
            cmd.extend(["-c:v", "libx265"])

        # Add post-input flags from the plan entry
        cmd.extend(post_input_flags)

        # Apply defaults based on summary heuristics, avoiding duplicates

        if "convert" in summary:
            if "-c:v" not in existing_args_str:
                cmd.extend(["-c:v", "libx264"])
            if "-c:a" not in existing_args_str:
                cmd.extend(["-c:a", "aac"])
        if "compress" in summary and "-crf" not in existing_args_str:
            cmd.extend(["-crf", "28"])
        if "frames" in summary and "fps=" not in existing_args_str:
            # default fps = 1/5 for frame extraction
            cmd.extend(["-vf", "fps=1/5"])
        if "overlay" in summary and "-filter_complex" not in entry.args:
            # default top-right overlay with 10px margins
            cmd.extend(["-filter_complex", "overlay=W-w-10:10"])
        if "thumbnail" in summary and "-vframes" not in entry.args:
            cmd.extend(["-vframes", "1"])

        # Trim/segment: if only timing flags and no explicit codecs/filters, use copy
        if ("trim" in summary or "segment" in summary) and not any(
            token in existing_args_str for token in ["-c:v", "-c:a", "-filter", "-vf", "-af"]
        ):
            cmd.extend(["-c", "copy"])

        cmd.append(str(entry.output))

        # Validate the command before adding it for security
        from .file_operations import validate_ffmpeg_command

        if not validate_ffmpeg_command(cmd):
            logger.warning(f"Generated command failed validation: {' '.join(cmd[:5])}...")

        commands.append(cmd)

    return commands
