# The script create a zip file to upload as a BioT plugin.
# Assumptions 
# 1. The handler function is in the index.py (its zipped specifically)
# 2. The venv directory is called seedenv (seedenv/lib/python3.11/site-packages is zipped specifically)
# 3. Some dependencies are NOT zipped - base things like pip

import shutil
import traceback
import sysconfig

dist_path = "../dist"

try: 

    path = sysconfig.get_paths()["purelib"]

    print("Copy dependencies from ", path)

    shutil.copytree(
        path,
        dist_path, 
        symlinks=True, 
        ignore=shutil.ignore_patterns("pip", 'pkg_resources', 'setuptools', '_distutils_hack', 'distutils-precedence.pth',
                               '*.dist-info'))
    
    print("Copy src directory")

    shutil.copytree('./src', dist_path + "/src", symlinks=True)

    print("Copy index.py file")

    shutil.copyfile("./index.py", dist_path + "/index.py") 

    print("Zip")

    shutil.make_archive("plugin", "zip", dist_path)

    shutil.rmtree(dist_path)


except Exception:
    shutil.rmtree(dist_path)
    print("packing plugin failed with error: ", traceback.format_exc())