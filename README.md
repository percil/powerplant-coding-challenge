# powerplant-coding-challenge

## The guy

My name is Olivier Perceval and I have more than 15 years of coding experience, mainly in Java. I work as a freelancer
since 5-ish years.

If you should have any further questions regarding this solution, feel free to contact me (here's
my [LinkedIn](https://www.linkedin.com/in/operceval/)).

## Challenge

### Accepted.

I was somehow delighted to take part to this challenge as it changes for standard CRUD one Java developer faces in his
everyday life :-) (thanks for that)

### The scope

As mentioned in your [GitHub repo](https://github.com/gem-spaas/powerplant-coding-challenge), the following aspects were
taken into account:

- this very README.md file explaining why 42 is the answer
- the exposition on port 8888
- a working and relevant results for every provided payload

As extra's, I added:

- a few unit tests
- a Dockerfile

### How-to

#### The tools

The development was made using [PyCharm](https://www.jetbrains.com/pycharm/) on [Ubuntu 20.04](https://ubuntu.com/).

#### The pre-requisites

In order to make this project work, you'll have to install the following tools:

- a runtime: [python](https://www.python.org/), please use at least python 3.8 (as this solution wasn't tested with the
  elder ones)
- a package installer: pip (provided with python)
- [Docker](https://www.docker.com/)

#### The installation

First, you'll have to install the dependencies by typing `pip install -r requirements.txt`

As the solution contains more than one file, you'll have to set your `PYTHONPATH` by
typing `export PYTHONPATH=.:$PYTHONPATH` (if running on UNIX-based systems)

Then simply run the application by tying `python app/app.py`

Then, you should have something looking like the following lines:

```
INFO:     Started server process [83770]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```

You may now test the solution. For your convenience, you may import the [Postman](https://www.postman.com/) collection
available in the folder `./tests/postman`

#### The tests

Assuming the installation is already done, the tests can be executed by
typing `python -m unittest discover -s tests -p '*_test.py'`

#### Docker

In order to execute this solution as a Docker image, you'll have to build the image
first `docker build -t engie_challenge:latest .`

Then run the container with `docker build -t engie_challenge:latest .`

The output should look like:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8888 (Press CTRL+C to quit)
```