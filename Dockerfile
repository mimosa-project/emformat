FROM python:3.10.10-slim
ENV WORKDIR /app/
WORKDIR ${WORKDIR}
COPY Pipfile Pipfile.lock ${WORKDIR}
RUN apt-get update &
RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install