"""
Enhanced CSS Documentation Generator
Extract CSS classes, selectors, and other constructs with detailed information
"""

import re
from pathlib import Path
from collections import Counter, defaultdict


def generate_css_documentation(css_dir: Path):
    """
    Generate CSS documentation by extracting constructs with details
    """

    # Find all CSS files and extract constructs with details
    all_constructs = Counter()
    file_constructs = defaultdict(list)

    for css_file in Path(css_dir).rglob("*.css"):
        content = css_file.read_text(encoding='utf-8')

        # Extract detailed CSS constructs
        constructs = extract_css_constructs(content)

        # Track constructs per file and globally
        file_constructs[css_file] = constructs
        construct_names = [c['name'] for c in constructs]
        all_constructs.update(construct_names)

    # Generate markdown documentation
    doc = [
        "# CSS Documentation",
        f"*Auto-generated from `{css_dir}/`*\n",
        "## Constructs by Usage Frequency",
        ""
    ]

    # Most used constructs first
    for construct_name, count in all_constructs.most_common():
        doc.append(f"- `{construct_name}` ({count} files)")

    doc.extend(["\n## Constructs by File", ""])

    # Group by directory for organization
    for css_file in sorted(file_constructs.keys()):
        relative_path = css_file.relative_to(css_dir)
        doc.append(f"### {relative_path}")

        constructs = file_constructs[css_file]
        if constructs:
            for construct in constructs:
                doc.append(format_css_construct(construct))
        else:
            doc.append("- *No CSS constructs found*")
        doc.append("")

    # Write documentation
    file = css_dir.parent / "css_documentation.md"
    file.touch(exist_ok=True)
    file.unlink()
    file.touch()
    file.write_text('\n'.join(doc), encoding='utf-8')
    return f"Documentation written to {file}"


def extract_css_constructs(content: str) -> list:
    """
    Extract CSS constructs with detailed information
    """
    constructs = []

    # Split content into lines for line tracking
    lines = content.split('\n')

    for i, line in enumerate(lines):
        original_line = line
        stripped = line.strip()

        if not stripped or stripped.startswith('/*'):
            continue

        # Extract same-line comment if present
        comment = extract_css_comment(stripped)

        # CSS Custom Properties (Variables): --variable-name
        var_matches = re.findall(r'(--[\w-]+)\s*:', stripped)
        for var_name in var_matches:
            constructs.append({
                'type': 'css-variable',
                'name': var_name,
                'line': i + 1,
                'comment': comment
            })

        # CSS Classes: .class-name
        class_matches = re.findall(r'\.([a-zA-Z][\w-]*(?:--[\w-]+)?)', stripped)
        for class_name in class_matches:
            # Skip if it's inside a property value (after :)
            if ':' in stripped and stripped.find(f'.{class_name}') > stripped.find(':'):
                continue
            constructs.append({
                'type': 'class',
                'name': class_name,
                'line': i + 1,
                'comment': comment
            })

        # CSS IDs: #id-name
        id_matches = re.findall(r'#([a-zA-Z][\w-]+)', stripped)
        for id_name in id_matches:
            # Skip if it's inside a property value (after :)
            if ':' in stripped and stripped.find(f'#{id_name}') > stripped.find(':'):
                continue
            constructs.append({
                'type': 'id',
                'name': id_name,
                'line': i + 1,
                'comment': comment
            })

        # CSS Animations: @keyframes animation-name
        keyframe_matches = re.findall(r'@keyframes\s+([a-zA-Z][\w-]*)', stripped)
        for animation_name in keyframe_matches:
            constructs.append({
                'type': 'animation',
                'name': animation_name,
                'line': i + 1,
                'comment': comment
            })

        # CSS Media Queries: @media
        if stripped.startswith('@media'):
            media_query = stripped[6:].strip().rstrip('{')
            constructs.append({
                'type': 'media-query',
                'name': media_query or 'media query',
                'line': i + 1,
                'comment': comment
            })

        # Other At-Rules: @import, @font-face, etc.
        at_rule_match = re.match(r'@([a-zA-Z-]+)', stripped)
        if at_rule_match and not stripped.startswith(('@keyframes', '@media')):
            rule_name = at_rule_match.group(1)
            constructs.append({
                'type': 'at-rule',
                'name': f'@{rule_name}',
                'line': i + 1,
                'comment': comment
            })

    # Remove duplicates (same construct on same line)
    seen = set()
    unique_constructs = []
    for construct in constructs:
        key = (construct['type'], construct['name'], construct['line'])
        if key not in seen:
            seen.add(key)
            unique_constructs.append(construct)

    return unique_constructs


def extract_css_comment(line: str) -> str:
    """Extract same-line comment from CSS"""
    # Look for /* comment */
    comment_match = re.search(r'/\*\s*(.+?)\s*\*/', line)
    if comment_match:
        return comment_match.group(1).strip()

    return ''


def format_css_construct(construct: dict) -> str:
    """Format a CSS construct for display in documentation"""
    type_icon = {
        'class': '🎨',
        'id': '🆔',
        'css-variable': '🔧',
        'animation': '🎬',
        'media-query': '📱',
        'at-rule': '📋'
    }

    icon = type_icon.get(construct['type'], '•')
    name = construct['name']
    line = construct['line']
    comment = construct.get('comment', '')

    # Format the name based on type
    if construct['type'] == 'class':
        formatted_name = f'.{name}'
    elif construct['type'] == 'id':
        formatted_name = f'#{name}'
    else:
        formatted_name = name

    # Build the base construct display
    base = f"- {icon} **{construct['type']}** `{formatted_name}` *(line {line})*"

    # Add comment if present
    if comment:
        base += f" - *{comment}*"

    return base