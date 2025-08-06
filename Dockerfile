# See https://testdriven.io/blog/docker-best-practices/ for recommendations
# on writing dockerfiles for python projects.

# We use a build stage to build a wheel which we then copy and install
# in the second stage to minimize image size. This is mostly needed
# because setuptools_scm needs the full version info from git and git
# itself but including that in the final image would bloat its size.

# we are using the official python image with just a version tag here
# it comes with many tools needed to build and compile python packages
# which increases it's size but is helpful for building
FROM harbor.cta-observatory.org/proxy_cache/python:3.12 AS builder

# Add full repository, needed for setuptools_scm to assign proper version
COPY . /repo/

# build the wheel
RUN python -m pip install --no-cache-dir build \
    && cd repo \
    && python -m build --wheel


# second stage, copy and install wheel
# We are using the official python 3.11 image
# as base image in the slim variant to reduce image size.
FROM harbor.cta-observatory.org/proxy_cache/python:3.12-slim
COPY --from=builder /repo/dist /tmp/dist

RUN python -m pip install --no-cache-dir /tmp/dist/* \
    && rm -r /tmp/dist

RUN addgroup --system ctao && adduser --system --group ctao
USER ctao
