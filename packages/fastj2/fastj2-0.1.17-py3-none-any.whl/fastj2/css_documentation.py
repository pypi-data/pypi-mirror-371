"""
Simple CSS Documentation Generator
One method to extract all CSS classes and generate documentation
"""

import re
from pathlib import Path
from collections import Counter, defaultdict


def generate_css_documentation(css_dir: Path):
    """
    Generate CSS documentation by globbing CSS files and extracting class names
    """

    # Find all CSS files and extract classes
    all_classes = Counter()
    file_classes = defaultdict(list)

    for css_file in Path(css_dir).rglob("*.css"):
        content = css_file.read_text(encoding='utf-8')

        # Extract class names with regex
        classes = set(re.findall(r'\.([a-zA-Z][\w-]*(?:--[\w-]+)?)', content))

        # Track classes per file and globally
        file_classes[css_file] = sorted(classes)
        all_classes.update(classes)

    # Generate markdown documentation
    doc = [
        "# CSS Documentation",
        f"*Auto-generated from `{css_dir}/`*\n",
        "## Classes by Usage Frequency",
        ""
    ]

    # Most used classes first
    for class_name, count in all_classes.most_common():
        doc.append(f"- `.{class_name}` ({count} files)")

    doc.extend(["\n## Classes by File", ""])

    # Group by directory for organization
    for css_file in sorted(file_classes.keys()):
        relative_path = css_file.relative_to(css_dir)
        doc.append(f"### {relative_path}")

        if file_classes[css_file]:
            for class_name in file_classes[css_file]:
                doc.append(f"- `.{class_name}`")
        else:
            doc.append("- *No classes found*")
        doc.append("")

    # Write documentation
    file = css_dir.parent / "css_documentation.md"
    file.touch(exist_ok=True)
    file.unlink()
    file.touch()
    file.write_text('\n'.join(doc), encoding='utf-8')
    return f"Documentation written to {file}"