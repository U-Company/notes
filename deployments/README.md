# Prepare config for pip (Ubuntu)

Before publishing, you need to create file `~/.pypirc` like this:

    [distutils]
    index-servers=
        pypi
        private_pypi
    
    [pypi]
    repository: https://upload.pypi.org/legacy/ 
    username: <username_pypi>
    password: <password_pypi>
    
    [private_pypi]
    repository: <private-pypi-registry>
    username: <username_private_pipy_registry>
    password: <password_private_pipy_registry>
    
You must to set this file into `$HOME` directory. If you want to change location of `.pypirc`, you need cutomize class in `setup.py`:

    # this is your project's setup.py script

    import os
    from distutils.command.register import register as register_orig
    from distutils.command.upload import upload as upload_orig

    from setuptools import setup


    class register(register_orig):

        def _get_rc_file(self):
            return os.path.join('.', '.pypirc')

    class upload(upload_orig):

        def _get_rc_file(self):
            return os.path.join('.', '.pypirc')

    setup(
        name='myproj',
        ...
        cmdclass={
            'register': register,
            'upload': upload,
        }
    )
    
You can read more [here](https://ru.stackoverflow.com/questions/1228778/%d0%9a%d0%b0c%d1%82%d0%be%d0%bc%d0%bd%d1%8b%d0%b9-%d0%bf%d1%83%d1%82%d1%8c-%d0%b4%d0%be-pypirc) in russian or here in [english](https://stackoverflow.com/questions/37845125/custom-location-for-pypirc-file).

Note that some imports in the IDE may be marked as not found. Do not be afraid of this. Everything works fine from the console.

# Publish package to private_pypi pypi server

Before publish, set differences into CHANGELOG.md, setup.py version. After that, you need to create new release into master branch on 
github. Now, you need update package:

    python setup.py bdist_wheel upload -r private_pypi
    
This command push your image to pypi-package-registry

## Remove package from pypi server

You can remove a package from the server with the command:

    curl --form ":action=remove_pkg" --form "name=<name package>" --form "version=<version>" http://<login>:<pass>@<host>:<port>/

or using a schell-script:

    #!/bin/bash
    # $1 - package name $2 - package version
    curl --form ":action=remove_pkg" --form "name=$1" --form "version=$2" http://<login>:<pass>@<host>:<port>/



# Installing package from private pypi repository

You must lay the config file `pip.conf` into `~/.pip/`:

    [global]	
    timeout = 3
    retries = 0
    extra-index-url =
        https://pypi.org/simple
        http://<login-1>:<password-1>@<your-host-1>:<your-port-1>
        http://<your-host-2>:<your-port-2>
    trusted-host = 
        pypi.python.org
        pypi.org
        <your-host-1>:<your-port-1>
        <your-host-2>:<your-port-2>
        
If you want to use some environments, you can create some `pip.conf` files. To specify the file location you can use `PIP_CONFIG_FILE` unix environment.

# Publish image into docker registry (for local development and testing)

Before build, you need add `pip.conf` into `.secrets`. You can see template [here](https://github.com/Hedgehogues/docker-compose-deploy/blob/master/.deploy/.secrets/pip.conf)

From the root directory build the image

    docker-compose -f .deploy/docker-compose.full.yml build
    
After that, you must find the line with next text (last lines):

    Successfully built <image-id>
    Successfully tagged <image-name>:latest
    
Now, you must set tag for image:

    docker tag <image-id> <private-docker-registry>/<project>-<version>-<service-name>:<the-same-version-setup.py>
    
Please, add insecure-registry parameters to `/etc/docker/daemon.json` (first time):

    {
        "insecure-registries" : [ "<private-docker-registry-schema>://<private-docker-registry-host>:<private-docker-registry-port>" ]
    }
    
And restart docker (first time):

    sudo service docker restart

Now, login in docker registry with your login and password (first time):

    docker login <private-docker-registry> -u="<username>" -p="<password>"
    
Push the image:

    docker push <private-docker-registry>/<project>-<version>-<service-name>:<the-same-version-setup.py>
    
After that, you need remove image:

    docker rmi <image-id> --force

You can see images:

    http://<private-docker-registry>/v2/_catalog
    
You can see all versions for image:

    http://<private-docker-registry>/v2/<image-name>/tags/list
 
Or concrete versions:

    http://<private-docker-registry>/v2/<image-name>/tags/list
    
If you want remove specific version from pypi-registry, you can do this:

    curl --form ":action=remove_pkg" --form "name=pkg" --form "version=0.0.0" 0.0.0.0:1234 -H "Authorization: Basic <base64-string>"

    
**Notice**: while docker image building, we fix all environment variables includes ports and endpoints. After that, you cannot to change them. We will fix it in the future
