# Build environment for online-randomizer and the pokered-randomizer base ROM
#
# This container image is for building the toolchain and dependencies:
#   * rgbds 0.2.5
#   * Python 2.7 + pypng for the old pret/pokemontools (extras/)
#   * uv + Python 3.12 with the project's locked dependencies in /opt/venv
#   * ImageMagick 7 for convert_sprites.sh
#
# To run the randomizer, bind-mount the repo at /app (see README).


ARG DEBIAN_VERSION=trixie

FROM docker.io/library/debian:${DEBIAN_VERSION}-slim AS rgbds

ARG RGBDS_VERSION=0.2.5
ARG RGBDS_SHA256=97980dff6022a33a34177dc19c182462f22bdc4038d69af5917eb1105fc6f160

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential bison pkg-config libpng-dev curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /src
# The release tarball ships stale object files, hence `make clean` first.
# -fcommon: rgbds of this era defines globals in headers, which modern GCC
# (-fno-common by default) rejects at link time.
RUN curl -fsSLO https://github.com/gbdev/rgbds/releases/download/v${RGBDS_VERSION}/rgbds-${RGBDS_VERSION}.tar.gz \
 && echo "${RGBDS_SHA256}  rgbds-${RGBDS_VERSION}.tar.gz" | sha256sum -c - \
 && tar xzf rgbds-${RGBDS_VERSION}.tar.gz \
 && make clean \
 && make rgbasm rgblink rgbfix YACC="bison -y" CFLAGS="-O2 -fcommon" \
 && for tool in rgbasm rgblink rgbfix; do \
      install -m 755 $tool /usr/local/bin/$tool-${RGBDS_VERSION}; \
    done


# Debian no longer packages Python 2, so borrow the interpreter from the last
# official python:2.7 image. It lives entirely under /usr/local and only needs
# glibc and zlib from the host system for what pokemontools uses.
# pypng 0.0.19 is the last release that still runs on Python 2.
FROM docker.io/library/python:2.7.18-slim-buster AS python2
RUN pip install --no-cache-dir pypng==0.0.19


FROM docker.io/library/debian:${DEBIAN_VERSION}-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      make git curl ca-certificates imagemagick-7.q16hdri \
 && rm -rf /var/lib/apt/lists/*

COPY --from=python2 /usr/local/bin/python2.7 /usr/local/bin/
COPY --from=python2 /usr/local/lib/libpython2.7.so.1.0 /usr/local/lib/
COPY --from=python2 /usr/local/lib/python2.7 /usr/local/lib/python2.7
RUN ln -s python2.7 /usr/local/bin/python2 \
 && ldconfig \
 && python2 -c "import png, zlib, argparse"

COPY --from=rgbds /usr/local/bin/ /usr/local/bin/
COPY --from=ghcr.io/astral-sh/uv:0.9.5 /uv /uvx /usr/local/bin/

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    MAKEFLAGS="PYTHON=python2"

WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen

CMD ["uv", "run", "app.py"]
