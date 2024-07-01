import shutil
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
temp_path = os.path.join(current_dir, "temp")

version_path = "../../src/app/version.txt"
src_rel_path = "../../src"
dest_rel_path = "../../release"

with open(os.path.join(current_dir, version_path), "rt") as f:
    version = f.read()

src_path = os.path.join(current_dir, src_rel_path)
dest_path = os.path.join(current_dir, dest_rel_path, version)

try:
    shutil.rmtree(temp_path)
    os.makedirs(temp_path)
except:
    pass

try:
    shutil.rmtree(dest_path)
except:
    pass

shutil.copytree(src_path, dest_path, ignore=shutil.ignore_patterns("__pycache__", "instance"))

shutil.make_archive(base_name=os.path.join(temp_path, "app"), format="zip", root_dir=os.path.join(dest_path, "app"))
shutil.rmtree(os.path.join(dest_path, "app"))

deploy_folder = os.path.join(current_dir, "../deploy")

for filename in os.listdir(deploy_folder):
    shutil.copy(os.path.join(deploy_folder, filename), temp_path)

shutil.make_archive(base_name=os.path.join(dest_path, f"app-release-{version}"), format="zip", root_dir=temp_path)
shutil.rmtree(temp_path)
