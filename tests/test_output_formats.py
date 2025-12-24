import unittest
import json
import tempfile
from pathlib import Path
import sys
import os

# Adjust path to find gitree package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from gitree.services.output_formatters import (
    build_tree_data,
    format_json,
    format_text_tree,
    write_outputs
)


class TestOutputFormats(unittest.TestCase):
    def setUp(self):
        """Create a temporary directory structure for testing."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.test_dir.name)

        # Create test structure:
        # root/
        #   file1.txt
        #   file2.py
        #   folder1/
        #     file3.txt
        #     file4.py
        #   folder2/
        #     subfolder/
        #       file5.txt

        (self.root / "file1.txt").touch()
        (self.root / "file2.py").touch()
        (self.root / "folder1").mkdir()
        (self.root / "folder1" / "file3.txt").touch()
        (self.root / "folder1" / "file4.py").touch()
        (self.root / "folder2").mkdir()
        (self.root / "folder2" / "subfolder").mkdir()
        (self.root / "folder2" / "subfolder" / "file5.txt").touch()

    def tearDown(self):
        """Clean up temporary directory."""
        self.test_dir.cleanup()

    def test_build_tree_data_structure(self):
        """Test that build_tree_data creates correct hierarchical structure."""
        tree_data = build_tree_data(
            root=self.root,
            depth=None,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None
        )

        # Check root node
        self.assertEqual(tree_data["type"], "directory")
        self.assertIn("children", tree_data)

        # Check children exist
        children = tree_data["children"]
        self.assertGreater(len(children), 0)

        # Find and verify a file node
        file_nodes = [c for c in children if c["type"] == "file"]
        self.assertGreater(len(file_nodes), 0)
        self.assertIn("name", file_nodes[0])

        # Find and verify a directory node
        dir_nodes = [c for c in children if c["type"] == "directory"]
        self.assertGreater(len(dir_nodes), 0)
        self.assertIn("children", dir_nodes[0])

    def test_build_tree_data_respects_depth(self):
        """Test that depth limiting works correctly."""
        tree_data = build_tree_data(
            root=self.root,
            depth=1,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None
        )

        # At depth 1, we should see root's immediate children but not deeper
        children = tree_data["children"]
        for child in children:
            if child["type"] == "directory":
                # Directories at depth 1 should have no children (depth limit reached)
                self.assertEqual(len(child.get("children", [])), 0)

    def test_build_tree_data_respects_excludes(self):
        """Test that extra_ignores filters out files."""
        tree_data = build_tree_data(
            root=self.root,
            depth=None,
            show_all=False,
            extra_ignores=["*.py"],
            respect_gitignore=False,
            gitignore_depth=None
        )

        # Verify no .py files in the tree
        def check_no_py_files(node):
            if node["type"] == "file":
                self.assertFalse(node["name"].endswith(".py"))
            for child in node.get("children", []):
                check_no_py_files(child)

        check_no_py_files(tree_data)

    def test_format_json(self):
        """Test JSON formatting."""
        tree_data = build_tree_data(
            root=self.root,
            depth=1,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None
        )

        json_output = format_json(tree_data)

        # Verify it's valid JSON
        parsed = json.loads(json_output)
        self.assertEqual(parsed["type"], "directory")
        self.assertIn("children", parsed)

    def test_format_text_tree(self):
        """Test text tree formatting."""
        tree_data = build_tree_data(
            root=self.root,
            depth=1,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None
        )

        text_output = format_text_tree(tree_data, emoji=True)

        # Verify output contains tree characters
        self.assertIn("├─", text_output)
        self.assertIn("└─", text_output)

        # Verify root name is first line
        lines = text_output.split("\n")
        self.assertGreater(len(lines), 0)

    def test_format_text_tree_with_emoji(self):
        """Test text tree formatting with emoji disabled (shows icons)."""
        tree_data = build_tree_data(
            root=self.root,
            depth=1,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None
        )

        text_output = format_text_tree(tree_data, emoji=False)

        # When emoji=False, emoji icons should be shown
        self.assertIn("📄", text_output)  # FILE_EMOJI
        self.assertIn("📂", text_output)  # NORMAL_DIR_EMOJI

    def test_write_outputs_json(self):
        """Test writing JSON output to file."""
        tree_data = build_tree_data(
            root=self.root,
            depth=1,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None
        )

        json_path = self.root / "output.json"

        write_outputs(
            tree_data=tree_data,
            json_path=str(json_path),
            txt_path=None,
            md_path=None,
            emoji=True
        )

        # Verify file was created
        self.assertTrue(json_path.exists())

        # Verify content is valid JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
            parsed = json.loads(content)
            self.assertEqual(parsed["type"], "directory")

    def test_write_outputs_txt(self):
        """Test writing TXT output to file."""
        tree_data = build_tree_data(
            root=self.root,
            depth=1,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None
        )

        txt_path = self.root / "output.txt"

        write_outputs(
            tree_data=tree_data,
            json_path=None,
            txt_path=str(txt_path),
            md_path=None,
            emoji=True
        )

        # Verify file was created
        self.assertTrue(txt_path.exists())

        # Verify content has tree structure
        with open(txt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn("├─", content)
            self.assertIn("└─", content)

    def test_write_outputs_md(self):
        """Test writing Markdown output to file."""
        tree_data = build_tree_data(
            root=self.root,
            depth=1,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None
        )

        md_path = self.root / "output.md"

        write_outputs(
            tree_data=tree_data,
            json_path=None,
            txt_path=None,
            md_path=str(md_path),
            emoji=True
        )

        # Verify file was created
        self.assertTrue(md_path.exists())

        # Verify content has markdown code block
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertTrue(content.startswith("```\n"))
            self.assertTrue(content.endswith("```\n"))

    def test_write_outputs_multiple_formats(self):
        """Test writing to multiple formats simultaneously."""
        tree_data = build_tree_data(
            root=self.root,
            depth=1,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None
        )

        json_path = self.root / "output.json"
        txt_path = self.root / "output.txt"
        md_path = self.root / "output.md"

        write_outputs(
            tree_data=tree_data,
            json_path=str(json_path),
            txt_path=str(txt_path),
            md_path=str(md_path),
            emoji=True
        )

        # Verify all files were created
        self.assertTrue(json_path.exists())
        self.assertTrue(txt_path.exists())
        self.assertTrue(md_path.exists())

    def test_write_outputs_with_whitelist(self):
        """Test that whitelist filtering works in build_tree_data."""
        file1_path = str((self.root / "file1.txt").absolute())
        file3_path = str((self.root / "folder1" / "file3.txt").absolute())

        whitelist = {file1_path, file3_path}

        tree_data = build_tree_data(
            root=self.root,
            depth=None,
            show_all=False,
            extra_ignores=[],
            respect_gitignore=False,
            gitignore_depth=None,
            whitelist=whitelist
        )

        # Verify only whitelisted files appear in tree
        def collect_file_names(node):
            files = []
            if node["type"] == "file":
                files.append(node["name"])
            for child in node.get("children", []):
                files.extend(collect_file_names(child))
            return files

        file_names = collect_file_names(tree_data)
        self.assertIn("file1.txt", file_names)
        self.assertIn("file3.txt", file_names)
        self.assertNotIn("file2.py", file_names)
        self.assertNotIn("file4.py", file_names)


if __name__ == '__main__':
    unittest.main()
