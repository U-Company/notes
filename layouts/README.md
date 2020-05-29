# layouts

We use some layouts (templates) for developing:

## python service layout

If you want to use this one, you must do this:

    pip install cookiecutter
    cookiecutter https://github.com/U-Company/python-service-layout.git
    cookiecutter python-service-layout

After that, you get consistent service with template for tests, deploying to registries, monitoring and more other 
useful things. You can see this layout [here](https://github.com/U-Company/python-service-layout/blob/master/README.md)

We have some commands:


**Create conda environment**

    make config

**Build python package and docker container**

    make build

**Publish python package and docker container to private pypi-registry**

    VERSION=a.b.c TAG=<docker-container-tag> make publish
    
**Clean source of python package**

    make clean

**Install all packages dependencies** 

    make deps

**Running**: 

    make run
    make run-full
    make run-env
    make run-rebuild

**Tests**:

    make test-integration
    make test-unit
    make test
