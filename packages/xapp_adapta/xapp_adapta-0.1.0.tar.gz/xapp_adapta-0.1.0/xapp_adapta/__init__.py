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


def copy_with(dir, fn=shutil.copy2):
    # ah, OS kind is for later as Windows/MacOS ...
    path = os.path.dirname(__file__) + "/"
    home_local = os.path.expanduser("~/.local/share/")
    shutil.copytree(path + dir, home_local + dir, dirs_exist_ok=True, copy_function=fn)


# make_local icons and desktop files
def make_local():
    copy_with("applications")
    copy_with("icons")
    copy_with("locale")


# using as a copy function?
def remove(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    return dst


# ininstall
def remove_local():
    copy_with("applications", fn=remove)
    copy_with("icons", fn=remove)
    copy_with("locale", fn=remove)
