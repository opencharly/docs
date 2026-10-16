"""Exercise the drift gate at its real Git boundary, including new routes."""

import pathlib
import subprocess
import tempfile
import unittest


GATE = pathlib.Path(__file__).with_name("check_drift.sh").resolve()


class DriftGateTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = pathlib.Path(self.temp.name)
        self.git("init", "--quiet")
        self.git("config", "user.name", "Drift gate test")
        self.git("config", "user.email", "drift-test@example.invalid")
        self.page = self.repo / "src/content/docs/index.md"
        self.page.parent.mkdir(parents=True)
        self.page.write_text("committed page\n")
        self.git("add", "src/content/docs")
        self.git("commit", "--quiet", "-m", "baseline")

    def git(self, *args):
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True, capture_output=True, text=True,
        )

    def gate(self):
        return subprocess.run(
            ["bash", str(GATE)], cwd=self.repo, capture_output=True, text=True,
        )

    def test_clean_content(self):
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("regeneration is a no-op", result.stdout)

    def test_modified_content(self):
        self.page.write_text("regenerated page\n")
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("DRIFT:", result.stdout)

    def test_deleted_content(self):
        self.page.unlink()
        self.assertEqual(self.gate().returncode, 1)

    def test_untracked_route_without_tracked_diff(self):
        route = self.page.parent / "reference/new-version/plugin.md"
        route.parent.mkdir(parents=True)
        route.write_text("new generated route\n")
        self.assertEqual(self.git("diff", "--exit-code").returncode, 0)
        result = self.gate()
        self.assertEqual(result.returncode, 1)
        self.assertIn("?? src/content/docs/reference/new-version/plugin.md", result.stdout)

    def test_staged_content(self):
        self.page.write_text("staged generated page\n")
        self.git("add", "src/content/docs")
        self.assertEqual(self.gate().returncode, 1)

    def test_unrelated_change(self):
        (self.repo / "STYLE.md").write_text("unrelated style edit\n")
        self.assertEqual(self.gate().returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
