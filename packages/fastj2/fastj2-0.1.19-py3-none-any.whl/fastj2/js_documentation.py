"""
Simple JavaScript Documentation Generator
Extract top-level functions, classes, and constants with detailed information
"""

import re
from pathlib import Path
from collections import Counter, defaultdict


def generate_js_documentation(js_dir: Path):
    """
    Generate JavaScript documentation by extracting top-level constructs with details
    """

    # Find all JS files and extract constructs with details
    all_constructs = Counter()
    file_constructs = defaultdict(list)

    for js_file in Path(js_dir).rglob("*.js"):
        content = js_file.read_text(encoding='utf-8')

        # Extract detailed JavaScript constructs
        constructs = extract_top_level_constructs(content)

        # Track constructs per file and globally
        file_constructs[js_file] = constructs
        construct_names = [c['name'] for c in constructs]
        all_constructs.update(construct_names)

    # Generate markdown documentation
    doc = [
        "# JavaScript Documentation",
        f"*Auto-generated from `{js_dir}/`*\n",
        "## Constructs by Usage Frequency",
        ""
    ]

    # Most used constructs first
    for construct_name, count in all_constructs.most_common():
        doc.append(f"- `{construct_name}` ({count} files)")

    doc.extend(["\n## Constructs by File", ""])

    # Group by directory for organization
    for js_file in sorted(file_constructs.keys()):
        relative_path = js_file.relative_to(js_dir)
        doc.append(f"### {relative_path}")

        constructs = file_constructs[js_file]
        if constructs:
            for construct in constructs:
                doc.append(format_construct(construct))
        else:
            doc.append("- *No top-level constructs found*")
        doc.append("")

    # Write documentation
    file = js_dir.parent / "js_documentation.md"
    file.touch(exist_ok=True)
    file.unlink()
    file.touch()
    file.write_text('\n'.join(doc), encoding='utf-8')
    return f"Documentation written to {file}"


def extract_top_level_constructs(content: str) -> list:
    """
    Extract top-level JavaScript constructs with detailed information
    Only captures constructs at the top level (not nested)
    """
    constructs = []

    # Split content into lines and track indentation to determine top-level
    lines = content.split('\n')

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith('//') or stripped.startswith('/*'):
            continue

        # Only process lines that start at column 0 or minimal indentation (top-level)
        leading_spaces = len(line) - len(line.lstrip())
        if leading_spaces > 4:  # Skip deeply nested constructs
            continue

        # Extract same-line comment if present
        comment = extract_same_line_comment(stripped)

        # Function declarations: function name(params)
        func_match = re.match(r'function\s+([a-zA-Z_$][\w$]*)\s*\(([^)]*)\)', stripped)
        if func_match:
            name, params = func_match.groups()
            constructs.append({
                'type': 'function',
                'name': name,
                'params': clean_params(params),
                'line': i + 1,
                'comment': comment
            })
            continue

        # Function expressions: const name = function(params) or const name = (params) =>
        const_func_match = re.match(r'const\s+([a-zA-Z_$][\w$]*)\s*=\s*(?:function\s*\(([^)]*)\)|(?:\(([^)]*)\)|([a-zA-Z_$][\w$]*?))\s*=>)', stripped)
        if const_func_match:
            name = const_func_match.group(1)
            # Get params from whichever group matched
            params = const_func_match.group(2) or const_func_match.group(3) or const_func_match.group(4) or ''
            constructs.append({
                'type': 'const function',
                'name': name,
                'params': clean_params(params),
                'line': i + 1,
                'comment': comment
            })
            continue

        # Regular const declarations (non-functions): const NAME = value
        const_match = re.match(r'const\s+([a-zA-Z_$][\w$]*)\s*=', stripped)
        if const_match and 'function' not in stripped and '=>' not in stripped:
            name = const_match.group(1)
            constructs.append({
                'type': 'const',
                'name': name,
                'params': '',
                'line': i + 1,
                'comment': comment
            })
            continue

        # Class declarations: class Name
        class_match = re.match(r'class\s+([a-zA-Z_$][\w$]*)', stripped)
        if class_match:
            name = class_match.group(1)
            constructs.append({
                'type': 'class',
                'name': name,
                'params': '',
                'line': i + 1,
                'comment': comment
            })
            continue

        # Let/var declarations: let name = or var name =
        var_match = re.match(r'(let|var)\s+([a-zA-Z_$][\w$]*)\s*=', stripped)
        if var_match and 'function' not in stripped and '=>' not in stripped:
            var_type, name = var_match.groups()
            constructs.append({
                'type': var_type,
                'name': name,
                'params': '',
                'line': i + 1,
                'comment': comment
            })
            continue

    return constructs


def extract_same_line_comment(line: str) -> str:
    """Extract same-line comment from a line of code"""
    # Look for // comment (but not inside strings)
    comment_match = re.search(r'//\s*(.+)$', line)
    if comment_match:
        return comment_match.group(1).strip()

    # Look for /* comment */ (single line)
    block_comment_match = re.search(r'/\*\s*(.+?)\s*\*/', line)
    if block_comment_match:
        return block_comment_match.group(1).strip()

    return ''


def clean_params(params_str: str) -> str:
    """Clean and format parameter string"""
    if not params_str:
        return ''

    # Split by comma and clean each parameter
    params = [p.strip() for p in params_str.split(',')]
    params = [p for p in params if p]  # Remove empty params

    # Extract just the parameter names (remove default values, destructuring, etc.)
    clean_params = []
    for param in params:
        # Handle destructuring: {name, age} -> name, age
        if param.startswith('{') and '}' in param:
            destructured = param.strip('{}').split(',')
            clean_params.extend([p.strip() for p in destructured])
        # Handle array destructuring: [first, second] -> first, second
        elif param.startswith('[') and ']' in param:
            destructured = param.strip('[]').split(',')
            clean_params.extend([p.strip() for p in destructured])
        # Handle default parameters: name = 'default' -> name
        elif '=' in param:
            clean_params.append(param.split('=')[0].strip())
        # Handle rest parameters: ...args -> args
        elif param.startswith('...'):
            clean_params.append(param[3:].strip())
        else:
            clean_params.append(param)

    return ', '.join(clean_params)


def format_construct(construct: dict) -> str:
    """Format a construct for display in documentation"""
    type_icon = {
        'function': '🔧',
        'const function': '⚡',
        'const': '📌',
        'class': '🏗️',
        'let': '📝',
        'var': '📄'
    }

    icon = type_icon.get(construct['type'], '•')
    name = construct['name']
    params = construct['params']
    line = construct['line']
    comment = construct.get('comment', '')

    # Build the base construct display
    if params:
        base = f"- {icon} **{construct['type']}** `{name}({params})` *(line {line})*"
    else:
        base = f"- {icon} **{construct['type']}** `{name}` *(line {line})*"

    # Add comment if present
    if comment:
        base += f" - *{comment}*"

    return base