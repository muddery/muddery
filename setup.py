import os
import sys
from setuptools import setup, find_packages

os.chdir(os.path.dirname(os.path.realpath(__file__)))

VERSION_PATH = os.path.join('muddery', 'VERSION.txt')
OS_WINDOWS = os.name == "nt"

def get_requirements():
    """
    To update the requirements for Muddery, edit the requirements.txt
    file, or win_requirements.txt for Windows platforms.
    """
    filename = 'win_requirements.txt' if OS_WINDOWS else 'requirements.txt'
    with open(filename, 'r') as f:
        req_lines = f.readlines()
    reqs = []
    for line in req_lines:
        # Avoid adding comments.
        line = line.split('#')[0].strip()
        if line:
            reqs.append(line)
    return reqs


def get_scripts():
    """
    Determine which executable scripts should be added. For Windows,
    this means creating a .bat file.
    """
    if OS_WINDOWS:
        batpath = os.path.join("bin", "windows", "muddery.bat")
        scriptpath = os.path.join(sys.prefix, "Scripts", "muddery_launcher.py")
        with open(batpath, "w") as batfile:
            batfile.write("@\"%s\" \"%s\" %%*" % (sys.executable, scriptpath))
        return [batpath, os.path.join("bin", "windows", "muddery_launcher.py")]
    else:
        return [os.path.join("bin", "unix", "muddery")]


def get_version():
    """
    When updating the Muddery package for release, remember to increment the
    version number in muddery/VERSION.txt
    """
    return open(VERSION_PATH).read().strip()


def package_data():
    """
    By default, the distribution tools ignore all non-python files.

    Make sure we get everything.
    """
    file_set = []
    for root, dirs, files in os.walk('muddery'):
        for f in files:
            if '.git' in f.split(os.path.normpath(os.path.join(root, f))):
                # Prevent the repo from being added.
                continue
            file_name = os.path.relpath(os.path.join(root, f), 'muddery')
            file_set.append(file_name)
    return file_set

# setup the package
setup(
    name='muddery',
    version=get_version(),
    author = "Lu Yijun",
    maintainer = "Lu Yijun",
    maintainer_email = "",
    url = "http://www.muddery.org",
    description='An online text game framework.',
    packages=find_packages(),
    scripts=get_scripts(),
    install_requires=get_requirements(),
    package_data={'': package_data()},
    zip_safe=False
)
