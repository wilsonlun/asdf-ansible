import urllib.request
import json
import sys
import platform

from packaging.specifiers import SpecifierSet
from packaging.version import Version

if (len(sys.argv) != 2):
    raise ValueError("Missing version argument")

ver_str=sys.argv[1]

url = 'https://pypi.org/pypi/ansible/json'
response = urllib.request.urlopen(url)
response_data = response.read().decode('utf-8')
data = json.loads(response_data)
versions = data['releases']

if not ver_str in versions.keys():
    print("No matching distribution found for {}".format(ver_str))
    exit(1)
else:
    ver = Version(ver_str)
    # ansible 2.5 is the first official release to support python3 
    python3_support = ver.major >= 3 or (ver.major == 2 and ver.minor >= 5)

    if not python3_support:
        print("Ansible 2.4 and below is not supported. Consider install a higher version.")
        exit(1)
    
    release_info = versions[ver_str]
    yanked = release_info[0]['yanked'] if release_info and release_info[0] else False

    if yanked:
        print("The version to be installed was yanked. Consider install other version.")
        exit(1)
    
    specifier_str = release_info[0]['requires_python']
    if specifier_str is not None:
        specifiers = SpecifierSet(specifier_str)
        platform_ver = platform.python_version()
        if not specifiers.contains(platform_ver):
            print("Installed python version ({}) does not meet python versions required by the package: {}".format(platform_ver, specifiers))
            exit(1)
    
    