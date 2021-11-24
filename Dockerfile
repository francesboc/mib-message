#
# Docker file for Message in a Bottle v1.0
#
FROM python:3.8
LABEL maintainer="<squa_id>_squad"
LABEL version="1.0"
LABEL description="Message in a Bottle User Microservice"

# creating the environment
COPY . /app
# setting the workdir
WORKDIR /app

# installing all requirements
RUN ["pip", "install", "-r", "requirements.prod.txt"]

# exposing the port
EXPOSE 5000/tcp

# Main command
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]