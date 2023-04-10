FROM python:3.11 as base

FROM base as python-deps
# Install pipenv and dependencies
RUN pip install pipenv
# Install packages
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install

FROM base as runtime
# Copy virtual environment from python-deps
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"
# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser
# Copy application
COPY Certs Certs
COPY DataLogger DataLogger

# Run application
CMD ["python", "-u", "DataLogger/IFTTTNotification.py"]
