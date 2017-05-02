# Portinus
Portinus is a tool that creates a systemd service out of a docker-compose.yml file.

## Why Portinus? Why not use docker application bundles/swarm/deploy?
Docker Application Bundles deployed via swarm are great, but in order to support horizontal scaling for many of the features in docker, you lose much of the composability and many features, such as network_modes and some other more complex interdependencies.

## Usage
*NOTE*: For all possible options, please use `portinus --help` and `portinus <command> --help` for more information.

### Requirements:
* docker
* docker-compose
* systemd
* python3

### To create a service:
```
sudo portinus create --name foo --source /home/justin/foo --env /home/justin/environment-file
```

* Where `/home/justin/foo` is a directory containing a `docker-compose.yml` file.
* Where `/home/justin/environment-file` is a systemd EnvironmentFile formated list of key-pairs. These values can be used in the docker-compose.yml file
* This will create a service named `portinus-foo` that will be enabled on boot and started as soon as it is created. 
* The files it runs will only be a snapshot of the source folder at the time portinus is executed.
* Any files generated using paths such as `./` in the `docker-compose.yml` file will be removed during installation. All 'updates' are clean installs.

### To disable a service on boot
Just treat it like any other systemd service:
```
sudo systemctl disable portinus-foo.service
```

### To remove a service
```
sudo portinus remove --name foo
```

* Only the name is required to remove a service
* The service will be disabled and removed from systemd
* The environment file and installed copy of the service will all be removed
