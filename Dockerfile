# Python support can be specified down to the minor or micro version
# (e.g. 3.6 or 3.6.3).
# OS Support also exists for jessie & stretch (slim and full).
# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
FROM python:3.6

LABEL Name=spirent-result-portal Version=0.0.1
EXPOSE 8080

WORKDIR /app

# Using pip to install dependencies:
COPY ./requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Copy source code
COPY . .

# Run init script
ENTRYPOINT ["./docker-entrypoint.sh"]