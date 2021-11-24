# Message in A Bottle - users

This is the source code of Message in a Bottle application, self project of *Advanced Software Engineering* course,
University of Pisa.

## Team info

- The *squad id* is **<SQUAD_ID>**
- The *team leader* is *<TEAM_LEADER>*

#### Members

Mark with *bold* the person(s) that has developed this microservice.

|Name and Surname    | Email                         |
|--------------------|-------------------------------|
|*Mario Rossi*       |mario.rossi@unipi.it           |
|Antonio Lupo        |antonio.lupo@unipi.it          |
|*Susanna Lopez*     |susy.lopez@mit.edu             |


## Instructions

### Initialization

To setup the project initially you have to run these commands
inside the project's root.

`virtualenv -p python3 venv`

`source venv/bin/activate`

`pip install -r requirements.dev.txt`

### Run the project

To run the project you have to setup the flask environment,
you can do it by executing the following commands:

```shell script
cp env_file_example env_file
cp env_file_example .env
export FLASK_ENV=development
flask run
```


#### Flask routes

To show the primary routes of flask application you can issue the following command:

`flask routes`

The default swagger-ui interface is available on */ui*

#### Executing migrations

If you change something in the models package or you create a new model,
you have to run these commands to apply the modifications:

`flask db migrate -m '<message>'`

and

`flask db upgrade`


#### Application Environments

The available environments are:

- debug
- development
- testing
- production

If you want to run the application with development environment
you can run the `run.sh` script.

**Note:** if you use `docker-compose up` you are going to startup a production ready microservice, hence postgres will be used as default database and gunicorn will serve your application.

If you are developing application and you want to have the debug tools, you can start application locally (without `docker-compose`) by executing `bash run.sh`.

### Run tests

To run all the tests, execute the following command:

`python -m pytest`

You can also specify one or more specific test files, in order to run only those specific tests.
In case you also want to see the overall coverage of the tests, execute the following command:

`python -m pytest --cov=mib`

In order to know what are the lines of codes which are not covered by the tests, execute the command:

`python -m pytest --cov-report term-missing`

## Conventions

- Name of files must be snake_cased
- Name of methods, properties, variables must be snake_cased
- Name of classes must be PascalCased 
- Name of constants must be UPPERCASE 
- The class name of managers must be in the format `<BeanName>Manager`

### Future implementations

---
