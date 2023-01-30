import os
import pytest
from src.miz_format import *
import pathlib, sys

parent_dir = str(pathlib.Path(__file__).parent.parent.parent)
sys.path.append(parent_dir)


@pytest.fixture
def settings():
    load_settings()
