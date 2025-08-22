"""Figure processing for markdown to LaTeX conversion.

This module handles conversion of markdown figures to LaTeX figure environments,
including figure attributes, captions, and references.
"""

import os
import re
from pathlib import Path

from .types import (
    FigureAttributes,
    FigureCaption,
    FigureId,
    FigurePath,
    FigurePosition,
    FigureWidth,
    LatexContent,
    MarkdownContent,
)


def convert_figures_to_latex(text: MarkdownContent, is_supplementary: bool = False) -> LatexContent:
    r"""Convert markdown figures to LaTeX figure environments.

    Args:
        text: The text containing markdown figures
        is_supplementary: If True, enables supplementary content processing

    Returns:
        Text with figures converted to LaTeX format
    """
    # First protect code blocks from figure processing
    protected_blocks: list[str] = []

    # Protect fenced code blocks FIRST (before inline code)
    def protect_fenced_code(match: re.Match[str]) -> str:
        protected_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(protected_blocks) - 1}__"

    text = re.sub(r"```.*?```", protect_fenced_code, text, flags=re.DOTALL)

    # Protect inline code (backticks) AFTER fenced code blocks
    def protect_inline_code(match: re.Match[str]) -> str:
        protected_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(protected_blocks) - 1}__"

    text = re.sub(r"`[^`]+`", protect_inline_code, text)

    # Process different figure formats
    text = _process_new_figure_format(text)
    text = _process_figure_with_attributes(text)
    text = _process_figure_without_attributes(text)

    # Restore protected code blocks
    for i, block in enumerate(protected_blocks):
        text = text.replace(f"__CODE_BLOCK_{i}__", block)

    return text


def convert_figure_references_to_latex(text: MarkdownContent) -> LatexContent:
    r"""Convert figure references from @fig:id and @sfig:id to LaTeX.

    Converts @fig:id to Fig. \\ref{fig:id} and @sfig:id to Fig. \\ref{sfig:id}.
    Handles panel references like @fig:Figure1 A to produce Fig. \\ref{fig:Figure1}A (no space).

    Args:
        text: Text containing figure references

    Returns:
        Text with figure references converted to LaTeX format with "Figure" prefix
    """
    # Convert @fig:id followed by space and panel letter to Figure \ref{fig:id}PanelLetter (no space)
    # Use empty group {} to prevent LaTeX from inserting unwanted spaces after \ref{}
    text = re.sub(r"@fig:([a-zA-Z0-9_-]+)\s+([A-Z])", r"Fig. \\ref{fig:\1}{}\2", text)

    # Convert @fig:id to Figure \ref{fig:id} (remaining basic references)
    text = re.sub(r"@fig:([a-zA-Z0-9_-]+)", r"Fig. \\ref{fig:\1}", text)

    # Convert @sfig:id followed by space and panel letter to Figure \ref{sfig:id}PanelLetter (no space)
    # Use empty group {} to prevent LaTeX from inserting unwanted spaces after \ref{}
    text = re.sub(r"@sfig:([a-zA-Z0-9_-]+)\s+([A-Z])", r"Fig. \\ref{sfig:\1}{}\2", text)

    # Convert @sfig:id to Figure \ref{sfig:id} (supplementary figures)
    text = re.sub(r"@sfig:([a-zA-Z0-9_-]+)", r"Fig. \\ref{sfig:\1}", text)

    return text


def convert_equation_references_to_latex(text: MarkdownContent) -> LatexContent:
    r"""Convert equation references from @eq:id to LaTeX.

    Converts @eq:id to \\eqref{eq:id} for proper equation referencing.

    Args:
        text: Text containing equation references

    Returns:
        Text with equation references converted to LaTeX format
    """
    # Convert @eq:id to \eqref{eq:id} for numbered equations
    text = re.sub(r"@eq:([a-zA-Z0-9_-]+)", r"\\eqref{eq:\1}", text)

    return text


def parse_figure_attributes(attr_string: str) -> FigureAttributes:
    r"""Parse figure attributes like {#fig:1 tex_position="!ht" width="0.8"}.

    Args:
        attr_string: String containing figure attributes

    Returns:
        Dictionary of parsed attributes
    """
    attributes: FigureAttributes = {}

    # Extract ID (starts with #)
    id_match = re.search(r"#([a-zA-Z0-9_:-]+)", attr_string)
    if id_match:
        attributes["id"] = id_match.group(1)

    # Extract other attributes (key="value" or key=value)
    attr_matches = re.findall(r'(\w+)=(["\'])([^"\']*)\2', attr_string)
    for match in attr_matches:
        key, _, value = match
        attributes[key] = value

    return attributes


def create_latex_figure_environment(
    path: FigurePath,
    caption: FigureCaption,
    attributes: FigureAttributes | None = None,
    is_supplementary: bool = False,
) -> LatexContent:
    """Create a complete LaTeX figure environment.

    Args:
        path: Path to the figure file
        caption: Figure caption text
        attributes: Optional figure attributes (position, width, id)
        is_supplementary: Whether this is a supplementary figure

    Returns:
        Complete LaTeX figure environment
    """
    if attributes is None:
        attributes = {}

    # Convert path from FIGURES/ to Figures/ for LaTeX and handle new
    # subdirectory structure
    latex_path = path.replace("FIGURES/", "Figures/")

    # Handle new subdirectory structure: Figure__name.svg -> Figure__name/Figure__name.png
    if "/" not in latex_path.split("Figures/")[-1]:  # Only if not already in subdirectory
        # Extract figure name from path like "Figures/Figure__name.svg"
        figure_name = os.path.splitext(os.path.basename(latex_path))[0]
        figure_ext = os.path.splitext(latex_path)[1]

        # Check if figure already exists as ready file (direct in FIGURES/ directory)
        # Resolve against manuscript path when available to avoid false negatives
        manuscript_root = os.getenv("MANUSCRIPT_PATH")
        if manuscript_root:
            # Use the original path to check for ready files (preserves spaces and special chars)
            original_figure_name = os.path.basename(path.replace("FIGURES/", ""))
            ready_figure_fullpath = Path(manuscript_root) / "FIGURES" / original_figure_name
        else:
            original_figure_name = os.path.basename(path.replace("FIGURES/", ""))
            ready_figure_fullpath = Path("FIGURES") / original_figure_name

        if ready_figure_fullpath.exists():
            # Ready figure exists, use it directly without subdirectory conversion
            # latex_path already contains the correct ready file path (with Figures/ prefix)
            # Ensure we preserve the original filename exactly as it appears in FIGURES/
            latex_path = f"Figures/{original_figure_name}"
        else:
            # Convert to subdirectory format: Figures/Figure__name/Figure__name.ext
            # Note: Keep original figure name with spaces for subdirectory
            latex_path = f"Figures/{figure_name}/{figure_name}{figure_ext}"

    # Convert SVG to PNG for LaTeX compatibility
    if latex_path.endswith(".svg"):
        latex_path = latex_path.replace(".svg", ".png")

    # Get positioning first to inform 2-column decision
    position: FigurePosition = attributes.get("tex_position", "ht")

    # Get width (default to '\linewidth' if not specified)
    width: FigureWidth = attributes.get("width", "\\linewidth")
    if not width.startswith("\\"):
        # Handle percentage values by converting to decimal
        if width.endswith("%"):
            # Convert percentage to decimal (e.g., "80%" -> "0.8")
            percentage_value = float(width[:-1]) / 100
            width = f"{percentage_value}\\linewidth"
        else:
            # Assume fraction of linewidth if no backslash
            width = f"{width}\\linewidth"

    # Check if this should be a 2-column spanning figure
    is_twocolumn = (
        attributes.get("span") == "2col" or attributes.get("twocolumn") == "true" or attributes.get("twocolumn") is True
    )

    # Store original position before modifications
    original_position = position

    # Auto-detect 2-column for full-width figures (but not for originally dedicated pages)
    if not is_twocolumn and width == "\\textwidth" and original_position != "p":
        is_twocolumn = True

    # Handle dedicated page positioning - use [p] for dedicated pages
    if original_position == "p":
        # Keep position as 'p' for safer dedicated page placement
        position = "p"
        is_twocolumn = True

    # Only adjust positioning for two-column spanning figures that don't have explicit positioning
    if is_twocolumn and position == "ht":
        # For two-column spanning figures with default positioning, use 'tp' for better placement
        position = "tp"

    # Process caption text to remove markdown formatting
    processed_caption = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", caption)
    processed_caption = re.sub(r"\*([^*]+)\*", r"\\textit{\1}", processed_caption)

    # Process caption formatting - handle dedicated page figures FIRST to prevent text cutting
    if original_position == "p":
        # For dedicated page figures, use proper single-page caption formatting
        # Use \linewidth to span the full available width within the figure environment
        # This ensures the caption matches the figure width on dedicated pages
        processed_caption = f"\\captionsetup{{width=\\linewidth,justification=justified,format=plain,singlelinecheck=false}}\n{processed_caption}"
    elif is_twocolumn:
        # For 2-column spanning figures (figure*), ensure caption spans full width
        # This ensures both figure and caption use the full text width
        if len(processed_caption) > 150:
            # For longer captions, add justified text formatting
            processed_caption = f"\\captionsetup{{width=\\textwidth,justification=justified}}\n{processed_caption}"
        else:
            # For shorter captions, just ensure full width
            processed_caption = f"\\captionsetup{{width=\\textwidth}}\n{processed_caption}"
    elif width == "\\textwidth":
        # For full-width figures that are NOT dedicated page, use captionsetup for proper formatting
        # Two-column figures need \textwidth to span columns, but dedicated page figures don't
        if len(processed_caption) > 150:
            # For longer captions, add justified text formatting
            processed_caption = f"\\captionsetup{{width=\\textwidth,justification=justified}}\n{processed_caption}"
        else:
            # For shorter captions, just ensure full width
            processed_caption = f"\\captionsetup{{width=\\textwidth}}\n{processed_caption}"

    # Create LaTeX figure environment - use figure* for 2-column spanning
    figure_env = "figure*" if is_twocolumn else "figure"

    # For figures with captionsetup, extract and place it before \caption
    if "\\captionsetup" in processed_caption:
        # Extract the captionsetup command and the actual caption text
        if processed_caption.startswith("\\captionsetup"):
            lines = processed_caption.split("\n", 1)
            captionsetup_cmd = lines[0]
            actual_caption = lines[1] if len(lines) > 1 else ""

            latex_figure = f"""\\begin{{{figure_env}}}[{position}]
\\centering
\\includegraphics[width={width}]{{{latex_path}}}
{captionsetup_cmd}
\\caption{{{actual_caption}}}"""
        else:
            latex_figure = f"""\\begin{{{figure_env}}}[{position}]
\\centering
\\includegraphics[width={width}]{{{latex_path}}}
\\caption{{{processed_caption}}}"""
    else:
        latex_figure = f"""\\begin{{{figure_env}}}[{position}]
\\centering
\\includegraphics[width={width}]{{{latex_path}}}
\\caption{{{processed_caption}}}"""

    # Add label if ID is present
    if "id" in attributes:
        latex_figure += f"\n\\label{{{attributes['id']}}}"

    latex_figure += f"\n\\end{{{figure_env}}}"

    # For dedicated page figures, ensure proper page placement without double clearpage
    if original_position == "p":
        # Use FloatBarrier for safer page control, avoiding potential blank page issues
        latex_figure = f"\\FloatBarrier\n{latex_figure}"

    return latex_figure


def _process_new_figure_format(text: MarkdownContent) -> LatexContent:
    r"""Process new figure format: ![](path)\n{attributes} **Caption text**."""

    def process_new_figure_format_full(match: re.Match[str]) -> str:
        path = match.group(1)
        attr_string = match.group(2)
        caption_text = match.group(3).strip()

        # Parse attributes
        attributes = parse_figure_attributes(attr_string)
        return create_latex_figure_environment(path, caption_text, attributes)

    # Handle new format: ![](path)\n{attributes} **Caption text**
    return re.sub(
        r"!\[\]\(([^)]+)\)\s*\n\{([^}]+)\}\s*(.+?)(?=\n\n|\n$|$)",
        process_new_figure_format_full,
        text,
        flags=re.MULTILINE | re.DOTALL,
    )


def _process_figure_with_attributes(text: MarkdownContent) -> LatexContent:
    """Process figures with attributes: ![caption](path){attributes}."""

    def process_figure_with_attributes(match: re.Match[str]) -> str:
        caption = match.group(1)
        path = match.group(2)
        attr_string = match.group(3)

        # Parse attributes
        attributes = parse_figure_attributes(attr_string)
        return create_latex_figure_environment(path, caption, attributes)

    # Handle figures with attributes (old format)
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)\{([^}]+)\}", process_figure_with_attributes, text)


def _process_figure_without_attributes(text: MarkdownContent) -> LatexContent:
    """Process figures without attributes: ![caption](path)."""

    def process_figure_without_attributes(match: re.Match[str]) -> str:
        caption = match.group(1)
        path = match.group(2)
        return create_latex_figure_environment(path, caption)

    # Handle figures without attributes (remaining ones)
    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", process_figure_without_attributes, text)


def validate_figure_path(path: FigurePath) -> bool:
    """Validate that a figure path is properly formatted.

    Args:
        path: Figure file path

    Returns:
        True if path is valid, False otherwise
    """
    # Check for valid image extensions
    valid_extensions = [".png", ".jpg", ".jpeg", ".pdf", ".svg", ".eps"]
    return any(path.lower().endswith(ext) for ext in valid_extensions)


def extract_figure_ids_from_text(text: MarkdownContent) -> list[FigureId]:
    """Extract all figure IDs from markdown text.

    Args:
        text: Text to extract figure IDs from

    Returns:
        List of unique figure IDs found in the text
    """
    figure_ids: list[FigureId] = []

    # Find figure attribute blocks
    attr_matches = re.findall(r"\{#([a-zA-Z0-9_:-]+)[^}]*\}", text)
    for match in attr_matches:
        if (match.startswith("fig:") or match.startswith("sfig:")) and match not in figure_ids:
            figure_ids.append(match)

    return figure_ids
