FROM gcr.io/jenkinsxio/builder-python37:2.0.856-211

ARG pip_index_url="http://nexus/repository/pypi-all/simple"
ARG pip_trusted_host="nexus"
ARG pip_extra_index_url

ENV PIP_INDEX_URL=$pip_index_url
ENV PIP_TRUSTED_HOST=$pip_trusted_host
ENV PIP_EXTRA_INDEX_URL=$pip_extra_index_url

EXPOSE 5000

WORKDIR /app

COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD ./infrabot /app/infrabot

ENTRYPOINT ["python3"]
CMD ["infrabot/app.py"]