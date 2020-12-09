'''
Created on 2020/12/09

@author: sakurai
'''
from os import listdir
from os.path import basename
from os.path import join
from os import sep
from subprocess import CalledProcessError
from subprocess import check_call
from subprocess import DEVNULL
from subprocess import PIPE
from subprocess import run
from subprocess import TimeoutExpired
from sys import argv
from sys import stderr
from tempfile import TemporaryDirectory


def members(archive):
    p = run(("7z", "l", archive),
            stdout=PIPE, stderr=DEVNULL, universal_newlines=True)

    lines = iter(p.stdout.splitlines())
    for line in lines:
        if line.startswith("-------------------"):
            break

    for line in lines:
        if line.startswith("-------------------"):
            break
        yield line[53:].lstrip()


def walk(archive, label):
    for member in set(members(archive)):
        target = sep.join([label, member])
        yield target
        with TemporaryDirectory() as directory:
            try:
                check_call(("7z", "e", archive, member),
                           stdout=DEVNULL, stderr=DEVNULL, cwd=directory,
                           universal_newlines=True, timeout=15)
            except CalledProcessError:
                pass
            except TimeoutExpired as e:
                print(e, "->", target, file=stderr)
            else:
                try:
                    yield from walk(join(directory, listdir(directory)[0]),
                                    target)
                except IndexError as e:
                    print(e, "->", target, file=stderr)


def main():
    for path in walk(argv[1], basename(argv[1])):
        print(path)


if __name__ == '__main__':
    main()
