# Decision Task Framework

This framework supports research to investigate trust in reliance on automation with the help of a *decision task framework* that aims at mapping real-life situations of uncertainty and moral dillema. The framework utilizes Django following it's MVT pattern to allow for modularizability and scalability. 

## Getting started 

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

First and formeost, the framework requires `Python3` in order to run properly with the newest version of `Django`. 

The follwoing python packages are needed for proper functioning

### Installing

Make sure Python3 is installed on your machine by typing `python3 --version` which should provide you with the currently installed version of python. If Python is not installed, please make sure [download and install](https://www.python.org/downloads/) the current version. 

1. If not already installed, install the package manager `pip`

   ```bash
   sudo easy_install pip
   ```

2. Install VirtualEnvironment.

   ```bash
   sudo pip install virtualenv
   ```

3. Create a virtual environment in a local folder in which you would like to store your development files

   ```bash
   sudo python3 -m venv virtualenvironment
   ```

4. Activate the virtual environment.

   ```
   source virtualenvironment/bin/activate
   ```

Now that you have activated the virtual environment, you can clone the project into the folder you created the virtual environment in. 

```bash
git clone https://git.rwth-aachen.de/luca.liehner/decision-task-framework.git
```

Once the project has successfully download, it is now time to install all the requirements. Navigate to the folder `decision-task-framework`and issue the follwoing command. 

```
sudo pip install -r requirements.txt
```

Once all the packages have installed you can migrate the database: 

```bash
python3 manage.py makemigration
python3 manage.py migrate
```

Before you can run the server, create a super user to access the admin panel (`http://localhost:8000/admin`)

```
 python3 manage.py createsuperuser
```

You can now run the server with:

```
python3 manage.py runserver
```



To initialze the homepage model run the 2 following commands:

```
python3 manage.py makemigrations home
python3 manage.py migrate home
```

Make sure create a post in the adminpanel of time `HOMEPAGE` and add some content that will be dispayed on your homepage. 

E voilà, you are good to go!