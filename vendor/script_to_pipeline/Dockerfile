FROM python:3.9 as base

RUN useradd -m pipeline
USER pipeline
WORKDIR /home/pipeline
ENV _PACHYDERM_PIPELINE_CONTAINER True

COPY entrypoint.py .
COPY script_to_pipeline script_to_pipeline
ENTRYPOINT ["python3", "entrypoint.py"]

FROM base as opencv

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* \
USER pipeline
