#!/usr/bin/python
"""Command line utilities"""

import hashlib
import re
import sys

# must be a DNS label (at most 63 characters, matching regex
# [a-z0-9]([-a-z0-9]*[a-z0-9])?): e.g. "my-name"
allowed_first_re = re.compile(r"^[a-z0-9]$")
allowed_re = re.compile(r"^[-a-z0-9]$")
passing_re = re.compile(r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")

PREFIX = ""
SUFFIX = "-kube"


class InvalidBranch(Exception):
    """Simple failure exception class."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def add_prefix(namespace):
    """Derp, add the prefix."""
    if PREFIX:
        return PREFIX + "-" + namespace
    else:
        return namespace


def fix_length(branch):
    """Make sure the branch name is not too long."""
    if branch == "":
        raise InvalidBranch(branch)

    if len(branch) < (63 - len(PREFIX) - 1):
        # quick finish if the branch name is already a valid
        # docker namespace name
        return add_prefix(branch)
    else:
        # too long, truncate but add a bit-o-hash to increase the
        # odds that we're still as unique as the branch name
        branch_hash = hashlib.sha256(branch).hexdigest()
        # prefix it, cut it at the 60th character and add 3
        # characters of the hashed 'full' branch name.  Even
        # if you take a long branch and add -v2, you'll get
        # a unique but reproducable namespace.
        branch = add_prefix(branch)[:60] + branch_hash[:3]
        return branch


def make_namespace(branch=None):
    """
    Take the branch name and return the docker namespace.

    some invalid branch names
    >>> create_namespace_name('')
    Traceback (most recent call last):
        ...
    InvalidBranch: ''

    >>> create_namespace_name('-this')
    'jenkins-this'

    >>> create_namespace_name('and_this')
    'jenkins-andthis'

    # some valid ones
    >>> create_namespace_name('and-this')
    'jenkins-and-this'

    >>> create_namespace_name('andthis')
    'jenkins-andthis'

    >>> create_namespace_name('AnDtHiS')
    'jenkins-andthis'

    >>> create_namespace_name('How-Now_Brown_Cow')
    'jenkins-how-nowbrowncow'

    >>> create_namespace_name('abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnopqrstuvwxyz0123456789')
    'jenkins-abcdefghijklmnopqrstuvwxyz0123456789abcdefghijklmnop5f8'

    """
    if branch is None:
        branch = sys.argv[1]

    branch = branch.lower()

    if not passing_re.match(branch):
        name = ""
        try:
            if allowed_first_re.match(branch[0]):
                name += branch[0]
        except IndexError:
            raise InvalidBranch(branch)

        for c in branch[1:]:
            if allowed_re.match(c):
                name += c
        branch = name

    if branch.endswith(SUFFIX):
        branch = branch[:-1 * len(SUFFIX)]

    return(fix_length(branch))


def make_nodeport(namespace=None):
    """
    Take the namespace and hash to a port.

    valid port numbers are the range (30000-32768)
    we want to take a namespace and turn it into a port
    number in a reproducable way with reasonably good
    distribution / low odds of hitting an already used port

    >>> create_nodeport_value('abc')
    32767

    >>> create_nodeport_value('abcdef')
    32405

    """
    # grab 10^4 bits pseudo-entropy and mod them into 30000-32768
    # 10 gives us a 3x bigger number than we actually need.
    if namespace is None:
        namespace = sys.argv[1]

    hash_val = int(hashlib.sha256(namespace).hexdigest()[0:10], 16)
    port = 30000 + (hash_val % 2768)  # 2768 = 32768 - 30000

    return port


if __name__ == "__main__":
    import doctest
    doctest.testmod()
