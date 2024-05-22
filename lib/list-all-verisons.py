import urllib.request
import json
import re

VERSION_PATTERN = r"""
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\.]?
            (?P<pre_l>alpha|a|beta|b|preview|pre|c|rc)
            [-_\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\.]?
                (?P<post_l>post|rev|r)
                [-_\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\.]?
            (?P<dev_l>dev)
            [-_\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\+(?P<local>[a-z0-9]+(?:[-_\.][a-z0-9]+)*))?       # local version
"""
regex = re.compile(r"^\s*" + VERSION_PATTERN + r"\s*$", re.VERBOSE | re.IGNORECASE)

url = 'https://pypi.org/pypi/ansible/json'
response = urllib.request.urlopen(url)
response_data = response.read().decode('utf-8')
data = json.loads(response_data)
versions = data['releases']

for version, release_info in versions.items():
    match = regex.search(version)
    release = tuple(int(i) for i in match.group("release").split("."))
    major = release[0] if len(release) >= 1 else 0
    minor =  release[1] if len(release) >= 2 else 0

    python3_support = major >= 3 or (major >= 2 and minor >= 5)
    yanked = release_info[0]['yanked'] if release_info and release_info[0] else False

    if python3_support and not yanked:
        print(version)