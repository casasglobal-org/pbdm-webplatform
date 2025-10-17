FROM docker.io/python:3.10-bookworm AS base
RUN apt-get update && apt-get install -y cython3 \
    proj-bin \
    gdal-bin \
    libgdal-dev \
    libproj-dev \
    libgeos-dev \
    libpq-dev \
    postgresql-client \
    libgl1 \
    libgl1-mesa-glx \
    ffmpeg \
    nano \
    gettext \
    && apt-get clean

FROM base AS stage1
RUN useradd -m user
WORKDIR /home/user
USER user
COPY --chown=user:user . .
ENV PATH=/home/user/.local/bin:$PATH

FROM stage1 AS stage2
# In Bookworm we use pyproj=3.4.1 and gdal 3.6.2
ENV PROJ_VER=3.4.1
ENV GDAL_VER=3.6.2
#RUN sed -i 's/${GDAL_VER}/3.6.2.11/g' requirements.txt
RUN sed -i 's/${PROJ_VER}/3.4.1/g' requirements.txt
RUN pip install --upgrade pip; \
    pip install --prefer-binary -r requirements.txt; \
    pip install gunicorn whitenoise

FROM stage2 AS stage3
COPY --chown=user:user docker/settings.py casas_web_portal/casas_web_portal/settings.py
ENV DJANGO_SETTINGS_MODULE='casas_web_portal.settings'
COPY --chown=user:user --chmod=744 docker/start.sh .

EXPOSE 8080

CMD [ "./start.sh" ]
