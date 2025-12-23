# main.py
from __future__ import annotations
import sys, io, pyperclip
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path
from .services.draw_tree import draw_tree, print_summary 
from .services.zip_project import zip_project
from .services.parser import parse_args
from .utilities.utils import get_project_version
import subprocess
import platform

def copy_to_clipboard(text: str) -> bool:
    """
    Attempts to copy text to clipboard using multiple methods.
    Returns True if successful, False otherwise.
    """
    # 1. Try pyperclip
    try:
        if pyperclip.is_available():
            pyperclip.copy(text)
            return True
    except Exception:
        pass

    # 2. Try native OS commands as fallback
    system = platform.system()
    try:
        if system == "Windows":
            subprocess.run("clip", input=text.strip(), text=True, check=True, shell=True)
            return True
        elif system == "Darwin":  # macOS
            subprocess.run("pbcopy", input=text, text=True, check=True)
            return True
        elif system == "Linux":
            # Try wl-copy (Wayland)
            try:
                subprocess.run(["wl-copy"], input=text, text=True, check=True)
                return True
            except FileNotFoundError:
                pass
            
            # Try xclip (X11)
            try:
                subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, check=True)
                return True
            except FileNotFoundError:
                pass
            
            # Try xsel (X11)
            try:
                subprocess.run(["xsel", "--clipboard", "--input"], input=text, text=True, check=True)
                return True
            except FileNotFoundError:
                pass
    except Exception:
        pass

    return False

def main() -> None:
    args = parse_args()

    if args.version:
        print(get_project_version())
        return

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"Error: path not found: {root}", file=sys.stderr)
        raise SystemExit(1)

    # Initial check removed to allow fallback attempts later
    if args.copy and not pyperclip.is_available():
        pass
        
    # If --no-limit is set, disable max_items
    max_items = None if args.no_limit else args.max_items

    if args.out is not None:     # TODO: relocate this code for file output
        # Determine filename
        filename = args.out
        # Add .txt extension only if no extension provided
        if not Path(filename).suffix:
            filename += '.txt'

    if args.copy or args.out is not None:
        # Capture stdout
        output_buffer = io.StringIO()
        original_stdout = sys.stdout
        sys.stdout = output_buffer

    # if zipping is requested
    if args.zip is not None:
        zip_project(
            root=root,
            zip_stem=args.zip,
            show_all=args.all,
            extra_ignores=args.ignore,
            respect_gitignore=not args.no_gitignore,
            gitignore_depth=args.gitignore_depth,
            ignore_depth=args.ignore_depth,
            depth=args.depth,
            no_files=args.no_files,
        )
    else:       # else, print the tree normally
        draw_tree(
            root=root,
            depth=args.depth,
            show_all=args.all,
            extra_ignores=args.ignore,
            respect_gitignore=not args.no_gitignore,
            gitignore_depth=args.gitignore_depth,
            max_items=max_items,
            ignore_depth=args.ignore_depth,
            no_files=args.no_files,
            emoji=args.emoji,
        )

        if args.summary:        # call summary if requested
            print_summary(root)

        if args.out is not None:     # that file output code again
            # Write to file
            content = output_buffer.getvalue()

            # Wrap in markdown code block if .md extension
            if filename.endswith('.md'):
                content = f"```\n{content}```\n"

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

        if args.copy:       # Capture output if needed for clipboard
            content = output_buffer.getvalue() + "\n"
            if not copy_to_clipboard(content):
                print("Warning: Could not copy to clipboard. Please install a clipboard utility (xclip, wl-copy) or ensure your environment supports it.", file=sys.stderr)
            else:
                print("Output copied to clipboard!", file=sys.stderr)


if __name__ == "__main__":
    main()
