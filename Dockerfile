FROM python:3.7.2-stretch

ARG pip_index_url="http://nexus/repository/pypi-all/simple"
ARG pip_trusted_host="nexus"
ARG pip_extra_index_url="https://nexus.jx.b.whoknows.com/repository/pypi-all/simple"

ENV PIP_INDEX_URL=$pip_index_url
ENV PIP_TRUSTED_HOST=$pip_trusted_host
ENV PIP_EXTRA_INDEX_URL=$pip_extra_index_url

EXPOSE 5000

WORKDIR /app

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD ./infrabot /app/infrabot

ENTRYPOINT ["python"]
CMD ["infrabot/app.py"]
