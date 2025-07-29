#!/usr/bin/env python3
"""
Generate a tree-like folder structure for a Python project (folders only) and append it to README.md
"""

import os
from pathlib import Path

def should_ignore(path_name):
    """Check if a file/folder should be ignored"""
    ignore_patterns = {
        '__pycache__',
        '.git',
        '.pytest_cache',
        '.venv',
        'venv',
        'env',
        '.env',
        'node_modules',
        '.DS_Store',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.gitignore',
        '.coverage',
        'htmlcov',
        'dist',
        'build',
        '*.egg-info'
    }
    
    return any(pattern in path_name or path_name.endswith(pattern.replace('*', '')) 
               for pattern in ignore_patterns)

def generate_tree(directory, prefix="", max_depth=None, current_depth=0):
    """Generate tree structure recursively (folders only)"""
    if max_depth is not None and current_depth >= max_depth:
        return []
    
    directory = Path(directory)
    tree_lines = []
    
    # Get all items and filter to only directories
    try:
        items = list(directory.iterdir())
        # Filter to only directories and exclude ignored patterns
        items = [item for item in items if item.is_dir() and not should_ignore(item.name)]
        items.sort(key=lambda x: x.name.lower())
    except PermissionError:
        return [f"{prefix}[Permission Denied]"]
    
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        
        # Choose the appropriate connector
        connector = "└── " if is_last else "├── "
        
        # Add the current directory
        tree_lines.append(f"{prefix}{connector}{item.name}/")
        
        # Recurse into subdirectory
        extension = "    " if is_last else "│   "
        tree_lines.extend(
            generate_tree(
                item, 
                prefix + extension, 
                max_depth, 
                current_depth + 1
            )
        )
    
    return tree_lines

def update_readme_with_tree(project_name=None, max_depth=4):
    """Generate tree and update README.md"""
    current_dir = Path.cwd()
    
    if project_name is None:
        project_name = current_dir.name
    
    print(f"Generating folder tree structure for: {project_name}")
    
    # Generate the tree
    tree_lines = [f"{project_name}/"]
    tree_lines.extend(generate_tree(current_dir, max_depth=max_depth))
    
    # Create the tree section
    tree_section = "\n## Project Structure (Folders Only)\n\n```\n" + "\n".join(tree_lines) + "\n```\n"
    
    readme_path = current_dir / "README.md"
    
    # Read existing README or create new one
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if project structure section already exists
        if "## Project Structure" in content:
            # Replace existing section
            lines = content.split('\n')
            new_lines = []
            skip_section = False
            
            for line in lines:
                if line.strip().startswith("## Project Structure"):
                    skip_section = True
                    continue
                elif skip_section and line.startswith("## ") and not line.strip().startswith("## Project Structure"):
                    skip_section = False
                    new_lines.append(line)
                elif not skip_section:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines).rstrip() + '\n'
        
        # Append the new tree section
        updated_content = content.rstrip() + '\n' + tree_section
    else:
        # Create new README
        updated_content = f"# {project_name}\n" + tree_section
    
    # Write back to README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ README.md updated with folder structure!")
    print(f"📁 Found {len(tree_lines)-1} folders in the project")
    
    # Also print to console
    print("\nGenerated folder structure:")
    print("=" * 50)
    for line in tree_lines:
        print(line)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate project folder tree structure (folders only)")
    parser.add_argument("--name", "-n", help="Project name (default: current folder name)")
    parser.add_argument("--depth", "-d", type=int, default=4, help="Maximum depth to traverse (default: 4)")
    parser.add_argument("--print-only", "-p", action="store_true", help="Only print to console, don't update README")
    
    args = parser.parse_args()
    
    if args.print_only:
        # Just print the tree
        current_dir = Path.cwd()
        project_name = args.name or current_dir.name
        tree_lines = [f"{project_name}/"]
        tree_lines.extend(generate_tree(current_dir, max_depth=args.depth))
        
        for line in tree_lines:
            print(line)
    else:
        # Update README
        update_readme_with_tree(args.name, args.depth)