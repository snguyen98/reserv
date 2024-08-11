# Reserv

Reserv is a simple, lightweight Flask application which provides a generic booking system. 

## About



## Installation

### Dependencies

Reserv can run on any operating system that has Python (preferably 3.12) installed. The app requires several Python packages to be installed, see Step 4 of the [Deployment](#Deployment) section for instructions.

### Deployment

Download a release from the [repo](https://github.com/snguyen98/Reserv/tree/main/release) or build your own release (see [Build](#Build) section) and follow these instructions:
1. Copy file `Reserv-release-[version].zip` from the releases folder to your environment. See the [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/deploying/) for hosting platform options if you do not have your own server.
2. Unzip the contents and navigate to the directory of the unzipped contents in a bash console or command prompt.
3. Run the deployment script using the command: `python deploy.py [deployment location] --no-backup`  
   You can add optional arguments for log file location and enabling backups. Use the command `python deploy.py --help` for more details.
4. It is recommended to create a virtual environment to install the Python dependencies in the next step, however this is optional. See the [Installation](https://virtualenv.pypa.io/en/latest/installation.html) and [User Guide](https://virtualenv.pypa.io/en/latest/user_guide.html) for `virtualenv` for more details.
5. Navigate to the `Reserv` folder and run the command: `pip install -r 'requirements.txt'`. Confirm the packages were installed successfully, if not, run the command `pip install [package-name]` manually.
6. Configure your WSGI server to run the application. Please refer to the [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/deploying/) for further instructions on configuring your Flask app to production.

### Initialising the database

Once your WSGI server is configured, you'll need to initialise your Reserv database and create users before you can use the app.

Navigate to your deployment folder and run the following command:
```
flask --app reserv init-db
```
This will create the necessary tables in your SQL database. If any errors are displayed, you can view the log file at `[deployment folder]/instance/logs`.

### Creating users

Now you'll need to create users to log into Reserv. Run the following command:
```
flask --app reserv create-user [user id] [display name] [password] [status]
```
Notes:
- `user id` and `display name` are unique fields.
- `status` can be `active`, `inactive` or `terminated`. Only `active` users can log into the system.

As of version 0.2.3, the newly created user will need to be assigned a role. Run the following command:
```
flask --app reserv assign-role [user id] [role name]
```
Notes:
- `user id` references the same field used to create the user in the above command
- `role name` can be:
  - `admin` - Can view and cancel bookings but cannot book for themselves.
  - `user` - Can view bookings and book for themselves.
  - `guest` - Can only view bookings.

### Configuration

When you first run the app, it will create an instance folder alongside the Flask application so you should have two folders in your deployment folder:
- `Reserv` - Contains the Flask app of the release you deployed.
- `instance` - Contains the data and configuration relating to your instance of the app.

In the instance folder, you should see:
- `data/schedule.db` - A SQLite database containing tables of booking and user data.
- `app.key` - A unique key for your instance of Reserv.

By default, the app uses the config file in `[deployment location]/reserv/config-default.yaml` but you can create a custom config file and place it in the instance folder.

## Development

### Build

## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
```

## Authors

Contributors names and contact info

ex. Sang Nguyen

## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release

## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details
