from os.path import dirname, join
from subprocess import check_call
from os import remove
from glob import glob

if __name__ == "__main__":
    dist = join(dirname(__file__), "dist")
    for path in glob(join(dist, "*")):
        remove(path)

    check_call("python -m build".split())
    check_call("python -m twine upload --repository pypi dist/* --verbose".split())
