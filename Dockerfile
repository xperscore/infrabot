FROM python:3.7.2-stretch

ARG pip_index_url="http://nexus.jx.whoknows.com/repository/pypi-all/simple"
ARG pip_trusted_host="nexus.jx.whoknows.com"
ARG pip_extra_index_url

ENV PIP_INDEX_URL=$pip_index_url
ENV PIP_TRUSTED_HOST=$pip_trusted_host
ENV PIP_EXTRA_INDEX_URL=$pip_extra_index_url

EXPOSE 5000

WORKDIR /app

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD infrabot /app

ENTRYPOINT ["python"]
CMD ["app.py"]
