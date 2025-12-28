# gitree/main.py
from __future__ import annotations
import sys
if sys.platform.startswith('win'):      # fix windows unicode error on CI
    sys.stdout.reconfigure(encoding='utf-8')

from .services.tree_service import run_tree_mode
from .services.parsing_service import parse_args, correct_args
from .utilities.config import resolve_config
from .utilities.logger import Logger, OutputBuffer
from .services.basic_args_handling_service import handle_basic_cli_args, resolve_root_paths
from .services.zipping_service import zip_roots
from pathlib import Path


def main() -> None:
    """
    Main entry point for the gitree CLI tool.

    Handles argument parsing, configuration loading, and orchestrates the main
    functionality including tree printing, zipping, and file exports.

    For Contributors:
        - If you are adding features, make sure to keep the main function clean
        - Do not put implementation details here
        - Use services/ and utilities/ modules for logic, and import their functions here
    """
    args = parse_args()
    logger = Logger()
    output_buffer = OutputBuffer()


    # Resolve --no-contents-for paths
    args.no_contents_for = [Path(p).resolve() for p in args.no_contents_for]


    # Resolve configuration (handle user, global, and default config merging)
    args = resolve_config(args, logger=logger)


    # Fix any incorrect CLI args (paths missing extensions, etc.)
    args = correct_args(args)
    # This one bellow is also used for determining whether to draw tree or not
    condition_for_no_output = args.copy or args.output or args.zip 


    # if some specific Basic CLI args given, execute and return
    # Handles for --version, --init-config, --config-user, --no-config
    if handle_basic_cli_args(args): condition_for_no_output = True


    # Validate and resolve all paths
    roots = resolve_root_paths(args, logger=logger)

    # Interactive mode: select files for each root if requested
    selected_files_map = {}
    if args.interactive:
        from .services.interactive import select_files
        # We need to filter roots if user cancels selection or selects nothing?
        # Current behavior in services: if not selected_files: continue.
        # So we should probably keep that logic.
        roots_to_keep = []
        for root in roots:
            selected = select_files(
                root=root,
                output_buffer=output_buffer,
                logger=logger,
                respect_gitignore=not args.no_gitignore,
                gitignore_depth=args.gitignore_depth,
                extra_excludes=args.exclude,
                include_patterns=args.include,
                include_file_types=args.include_file_types
            )
            if selected:
                selected_files_map[root] = selected
                roots_to_keep.append(root)
        roots = roots_to_keep

    # if zipping is requested
    if args.zip is not None:
        zip_roots(args, roots, output_buffer, logger, selected_files_map)

    # else, print the tree normally
    else:       
        run_tree_mode(args, roots, output_buffer, logger, selected_files_map)


    # print the output only if not copied to clipboard or zipped or output to file
    if not condition_for_no_output:
        output_buffer.flush()


    # print the log if verbose mode
    if args.verbose:
        if not condition_for_no_output: print()
        print("LOG:")
        logger.flush()


if __name__ == "__main__":
    main()
