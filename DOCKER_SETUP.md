# Installing the backend using Docker

### Pre-requisites

1. docker-compose

### Installation

- Clone Frappe Docker repo

```bash
git clone https://github.com/frappe/frappe_docker
cd frappe_docker
```

- Run this command

```bash
docker-compose -p cdd -f pwd.yml up -d
```

- Note: The above command will only install Frappe
- If you want to include other custom apps, see https://github.com/frappe/frappe_docker/blob/main/docs/custom-apps.md. For ongoing development this option is not recommended since Docker does not properly cache git repositories. Sometimes when you make a commit, Docker will not pull it. As a workaround, you will need to log into the container and do the installation of the custom app from within the container

#### Install custom apps

- Log in to the **backend** container as below

```bash
docker-compose -p cdd -f pwd.yml exec backend bash
```

- Once inside the container, navigate to **frappe-bench** directory and run the following commands to install the apps

```bash
bench get-app --branch main insights
bench get-app --branch main https://gitlab.com/steve.nyaga/gis.git
bench get-app --branch main https://github.com/e3tools/participatory-backend.git
./env/bin/pip install -r apps/gis/requirements.txt
```

#### Setting up geoserver-rest

- Log into the container as root. The **-u 0** option stands for root user who has ID=0

```bash
docker-compose -p cdd -f docker-compose.yml exec -u 0 backend bash
```
- Run the following commands

```bash
apt-get install software-properties-common
add-apt-repository ppa:ubuntugis/ppa 
apt-get update
apt-get install gdal-bin -y
apt-get install libgdal-dev -y
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip3 install GDAL
pip3 install pygdal=="`gdal-config --version`.*"

# install geoserver-rest globally. geoserver-rest will not install in virtual environment so you can comment it out in the requirements.txt file while setting up 
# for developer setup. However, for production
pip install geoserver-rest
```

#### Install custom-apps into the site

- Install the apps onto the default site

```bash
bench --site frontend install-app insights
bench --site frontend install-app gis
bench --site frontend install-app participatory-backend
```
