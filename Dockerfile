FROM python:3.9-alpine3.13
    # its a python docker img for alpine version
    # we will be using this img as the base for all the further pkgs & dependencies
    # alpine is the lightweight and efficient ver of linux
    # its ideal(best) for docker
    # it has no unnecessary dependency
LABEL maintainer="samuraijack"
    # its the name of the user who created/maintained this Docker file/img/container

ENV PYTHONUNBUFFERED 1
    # it is recommended when running python in docker containers
    # it tells python to not buffer(delay) the output
    # so the output will directly be printed on the console without any delay
    # so we can see the logs immediately on screen

COPY ./requirements.txt /tmp/requirements.txt
    # copy file 'requirements.txt' from our local storage to docker img/container
    # it will be used to install python pkgs into docker img/container
    # these pkgs will be used in both dev & prod environments
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
    # copy file 'requirements.dev.txt' from our local storage to docker img/container
    # these pkgs will be used in only dev environment
COPY ./app /app
    # copy dir '/app' (django project files) from our local storage to docker img/container
WORKDIR /app
    # it will be the directory in docker container from where commands will automatically execute when we run commands in docker container
    # so we wont hv to give full path of django files stored in docker container everytime executing any command in docker
    # its the same directory where the django project will be copied in docker container
EXPOSE 8000
    # it let docker container to expose port 8000
    # now if any machine want to access this container then it can access thru port 8000

ARG DEV=false
    # it set development environment as false
    # it will be overridden by value of argument 'DEV' set in 'docker-compose.myl' file when running img thru 'docker-compose.yml' file

# we could use 'RUN' for each line below separately but it will create a new image layer for each command,
# so we used one 'RUN' block for all the commands lines to keep the image lightweight and efficient
# so basically we used all the commands as only one command but broke down every command by syntax '&& \'
RUN python -m venv /py && \
    # it will create a virtual environment to store our dependencies
    # this will avoid the conflict between base image(python) dependencies and project dependencies
    # also this doesnt make the img much heavy
    /py/bin/pip install --upgrade pip && \
        # here we specify full path of virtual environment and upgrade 'pip' inside it
    apk add --update --no-cache postgresql-client && \
        # here, we installed dependency 'postgresql-client' for adaptor 'psycopg2' inside our alpine image
        # 'psycopg2' is a postgresql adaptor use to connect with python
        # 'postgresql-client' dependency is required to install & run the adaptor 'psycopg2',
        # so its a permanent dependency, and
        # we neither going to remove it after installing 'psycopg2' and nor in production environment
    apk add --update --no-cache --virtual .tmp-build-deps \
        # this will set a virtual dependency pkg '.tmp-build-deps' and group below listed dependencies into it
        build-base postgresql-dev musl-dev && \
            # these dependencies are also required, only to install the adaptor 'psycopg2',
            # so, after creation of img/container we will delete these dependencies both in dev & prod env
    /py/bin/pip install -r /tmp/requirements.txt && \
        # here we specify full path of virtual environment, and
        # install pkgs (listed in file '/tmp/requirements.txt' stored in docker container) inside virtual env
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
        # here we removing dir '/tmp' from docker container once the img/container is created
        # dir '/tmp' storing extra dependencies we wont be needing after creation of img
        # so deleting this dir to make the img lightweight and efficient
    apk del .tmp-build-deps && \
        # it will delete the dependencies grouply installed as pkg '.tmp-build-deps' above
        # after creation of img/container we are deleting these dependencies both in dev & prod env
        # so deleting this pkg make the img lightweight and efficient
    adduser \
        # it creates a new user inside our img
        # bydefault there is only 'root' user which will hv all the permissions and accesses,
        # so its not gud to use the 'root' user as it will be dangerous if it got virus or hacked etc.
        # so we creating a user with much less permissions and run our app inside img thru this new user only
        --disabled-password \
            # disabling password for this user to login to the img; he can directly access the img
        --no-create-home \
            # this command will restrict the img from creating dir 'home' for this new user
            # bcz its of no use and not having this will keep the img lightweight
        django-user
            #  this is the name of the user we are creating for our image

ENV PATH="/py/bin:$PATH"
    # PATH and $PATH are different here
    # this will create a environment variable 'PATH'
    # first part contains virtual environment path(/py/bin) and second part contains system path variable($PATH)
    # system path var '$PATH' is automatically created in linux os and windows too,
    # and it contains locations of all the directories containing executables,
    # so executables can run directly without specifying their path everytime
    # now, since we are using virtual env, so we will execute all the commands & executables inside it only,
    # so to avoid specifying virtual env path everytime while giving any command, we will create an env var 'PATH' storing location of virtual env with system path var '$PATH'

USER django-user
    # it will switch the user to 'django-user'
    # until now, everything was done by 'root' user
    # but now everything will be done by 'django-user' user
