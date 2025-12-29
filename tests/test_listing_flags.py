from gitree.constants.constant import FILE_EMOJI, EMPTY_DIR_EMOJI, NORMAL_DIR_EMOJI
from tests.base_setup import BaseCLISetup


class TestListingFlags(BaseCLISetup):

    @staticmethod
    def __build_name_with_emoji(file_name: str, emoji: str):
        return emoji + " " + file_name


    def test_entry_point_emoji(self):
        # Create empty and simple directories to test both emojis
        (self.root / "empty_folder").mkdir()
        (self.root / "folder").mkdir()
        (self.root / "folder" / "nested.txt").write_text('foo')
        result = self._run_cli("--emoji")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn(self.__build_name_with_emoji('file.txt', FILE_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('nested.txt', FILE_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('empty_folder', EMPTY_DIR_EMOJI), result.stdout)
        self.assertIn(self.__build_name_with_emoji('folder', NORMAL_DIR_EMOJI), result.stdout)


    def test_entry_point_no_files(self):
        # Additional structure specific to this test
        (self.root / "folder").mkdir()
        (self.root / "folder" / "nested.txt").write_text("nested")

        result = self._run_cli("--no-files")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("folder", result.stdout)
        self.assertNotIn("file.txt", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


    def test_entry_point_max_depth(self):
        (self.root / "folder").mkdir()
        (self.root / "folder" / "nested.txt").write_text("nested")

        result = self._run_cli("--max-depth", "1")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertIn("file.txt", result.stdout)
        self.assertIn("folder", result.stdout)
        self.assertNotIn("nested.txt", result.stdout)


    def test_entry_point_no_limit(self):
        # Override base structure for this test
        (self.root / "file.txt").unlink()
        (self.root / "folder").mkdir()

        for i in range(30):  # default limit is 20
            (self.root / "folder" / f"file{i}.txt").write_text("data")

        result = self._run_cli("--no-limit")

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(result.stdout.strip())

        for i in range(30):
            self.assertIn(f"file{i}.txt", result.stdout)


    def test_entry_point_hidden_items(self):
        # Create hidden files and directories
        (self.root / ".hidden_file.txt").write_text("hidden")
        (self.root / ".hidden_dir").mkdir()
        (self.root / ".hidden_dir" / "nested.txt").write_text("nested")

        # Test without --hidden-items flag (default behavior)
        result_default = self._run_cli()

        self.assertEqual(result_default.returncode, 0, msg=result_default.stderr)
        self.assertTrue(result_default.stdout.strip())
        self.assertIn("file.txt", result_default.stdout)
        self.assertNotIn(".hidden_file.txt", result_default.stdout)
        self.assertNotIn(".hidden_dir", result_default.stdout)

        # Test with --hidden-items flag
        result_with_flag = self._run_cli("--hidden-items")

        self.assertEqual(result_with_flag.returncode, 0, msg=result_with_flag.stderr)
        self.assertTrue(result_with_flag.stdout.strip())
        self.assertIn("file.txt", result_with_flag.stdout)
        self.assertIn(".hidden_file.txt", result_with_flag.stdout)
        self.assertIn(".hidden_dir", result_with_flag.stdout)
