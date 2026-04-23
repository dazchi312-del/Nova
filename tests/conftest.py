"""
Shared pytest fixtures for Nova test suite.
"""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def tmp_experiment_dir(tmp_path):
    exp_root = tmp_path / "experiments"
    exp_root.mkdir()
    return exp_root
