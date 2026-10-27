from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from proofline.classify import cues_for_path
from proofline.run_test import redact


class ProoflineTests(unittest.TestCase):
    def test_path_cues(self):
        cues = cues_for_path(".github/workflows/auth-config.yml")
        self.assertIn("ci", cues)
        self.assertIn("auth", cues)
        self.assertIn("configuration", cues)

    def test_redaction(self):
        value = redact("TOKEN=abc123 password: secret Bearer abc.def")
        self.assertNotIn("abc123", value)
        self.assertNotIn("secret", value)
        self.assertNotIn("abc.def", value)

    def test_cli_writes_evidence_for_explicit_failing_test(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
            (repo / "auth_config.py").write_text("value = 1\n")
            subprocess.run(["git", "add", "."], cwd=repo, check=True)
            subprocess.run(["git", "-c", "user.email=a@b.test", "-c", "user.name=test", "commit", "-m", "initial"], cwd=repo, check=True, stdout=subprocess.DEVNULL)
            (repo / "auth_config.py").write_text("value = 2\n")
            output = repo / "evidence"
            env = {**os.environ, "PYTHONPATH": str(Path(__file__).parents[1] / "src")}
            result = subprocess.run([sys.executable, "-m", "proofline", "check", "--test", "python -c \"print('TOKEN=abc')\"; exit 4", "--output-dir", str(output)], cwd=repo, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((output / "proofline-report.json").read_text())
            self.assertEqual(report["test"]["status"], "failed")
            self.assertNotIn("abc", report["test"]["output_redacted"])
            self.assertIn("auth", report["changes"][0]["cues"])
