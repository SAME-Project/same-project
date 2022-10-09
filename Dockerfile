FROM python

COPY . .

RUN pip install .

RUN cd /data/transformation

ARG DEBIAN_FRONTEND=noninteractive

RUN same init

CMD ["same", "run", "--persist-temp-files", "--no-deploy", "-t", "ocean"]