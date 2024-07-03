Instructions for deployment

1. Copy file app-release-[version].zip from the releases folder to your environment.
2. Unzip the contents.
3. Using bash or command prompt, navigate to the directory of the unzipped contents.
3. Run the command 'python deploy.py [path]' where path is the location to deploy to. This command will:
    a. Create a backup of your current application if it exists in the folder backup/app_<DATE>_<VERSION>.
    b. Unzip the app.zip file containing the release to deploy into the supplied location.
    c. Clean up any files used for deployment.
4. Run the application. Please refer to the flask documentation for deploying to production: https://flask.palletsprojects.com/en/2.3.x/deploying/