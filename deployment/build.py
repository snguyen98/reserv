import shutil
import os

current_dir = os.path.dirname(os.path.realpath(__file__))
temp_path = os.path.join(current_dir, "temp")
deploy_script_path = os.path.join(current_dir, "deploy.py")

version_path = "../src/app/version.txt"
src_rel_path = "../src"
dest_rel_path = "../release"

with open(os.path.join(current_dir, version_path), "rt") as f:
    version = f.read()

src_path = os.path.join(current_dir, src_rel_path)
dest_path = os.path.join(current_dir, dest_rel_path, version)

if os.path.isdir(dest_path):
    shutil.rmtree(dest_path)

shutil.copytree(src_path, dest_path)

key_path = os.path.join(dest_path, "app/app.key")
config_path = os.path.join(dest_path, "app/config.yaml")

os.remove(key_path)
os.remove(config_path)

zip_path = os.path.join(dest_path, "app")

shutil.make_archive(os.path.join(temp_path, "app"), "zip", dest_path)
shutil.rmtree(zip_path)
shutil.copy(deploy_script_path, temp_path)

shutil.make_archive(os.path.join(dest_path, f"app-release-{version}"), "zip", temp_path)
shutil.rmtree(temp_path)

readme_path = os.path.join(dest_path, "readme.txt")

with open(readme_path, "w") as file:
    file.write("Instructions for deployment:\n")
    file.write("1. Copy file app-release-[version].zip to your environment.\n")
    file.write("2. Unzip the contents.")
    file.write("3. Using bash or command prompt, navigate to the directory of the unzipped contents.\n")
    file.write("3. Run the command 'python deploy.py [path]' where path is the location to deploy to. This command will:\n")
    file.write("    a. Create a backup of your current application if it exists.\n")
    file.write("    b. Unzip the app.zip file containing the release to deploy into the supplied location.\n")
    file.write("    c. Clean up any files used for deployment.\n")
    file.write("4. Run the application. Please refer to the flask documentation for deploying to production: https://flask.palletsprojects.com/en/2.3.x/deploying/")