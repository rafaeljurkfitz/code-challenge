# registry.gitlab.com/meltano/meltano:latest is also available in GitLab Registry
ARG MELTANO_IMAGE=meltano/meltano:latest
FROM $MELTANO_IMAGE

WORKDIR /project

# Install any additional requirements
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy over Meltano project directory
COPY . /project
RUN meltano install

# Test my all extractors
# RUN meltano config tap-postgres test
# RUN meltano config tap-csv test
# RUN meltano config tap-duckdb test
# RUN meltano config tap-duckdb-postgres test

RUN mkdir -p /project/output/ /project/output/data /project/output/data/csv /project/output/data/postgres 

# Don't allow changes to containerized project files
ENV MELTANO_PROJECT_READONLY=1

# Expose default port used by `meltano ui`
EXPOSE 5000

ENTRYPOINT ["meltano"]
