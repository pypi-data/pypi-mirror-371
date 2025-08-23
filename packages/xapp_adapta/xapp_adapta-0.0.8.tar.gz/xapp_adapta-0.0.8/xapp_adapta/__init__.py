# module initialization
# These are the command imports
# N.B. Ignore the errors and warnings, as the pyproject.toml does use these
from .adapta_test import main as test  # pyright: ignore
from .adapta_main import main  # pyright: ignore
import shutil
from pathlib import Path
import os
import sys

here = Path(__file__).parent
sys.path.insert(0, str(here))
import xapp_adapta.so as so

print(so.hello())


def copy_with(dir):
    # ah, OS kind is for later as Windows/MacOS ...
    path = os.path.dirname(__file__) + "/"
    home_local = os.path.expanduser("~/.local/share/")
    shutil.copytree(path + dir, home_local + dir, dirs_exist_ok=True)


# make_local icons and desktop files
def make_local():
    copy_with("applications")
    copy_with("icons")
    copy_with("locale")
