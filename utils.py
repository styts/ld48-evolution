import sys
import os


def resource_path(relative):
    """Used by pyInstaller. Correct path prefix when running as frozen app/exe"""

    if getattr(sys, 'frozen', None):
        basedir = sys._MEIPASS  # production
    else:
        basedir = os.path.join(os.path.dirname(__file__))  # dev

    #print basedir

    return os.path.join(
        basedir,
        relative
    )
