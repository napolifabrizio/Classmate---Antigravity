# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_VERSION=2.0.1
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
# libsndfile1 is required by soundfile
# libportaudio2 and libasound2 are required by soundcard/pyaudio
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libsndfile1 \
    libportaudio2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set the working directory in the container
WORKDIR /app

# Copy the poetry files to install dependencies first (for better caching)
COPY pyproject.toml poetry.lock ./

# Install project dependencies
# Note: we skip installing the project itself (--no-root) until code is copied
RUN poetry install --no-interaction --no-ansi --no-root

# Copy the rest of the application code
COPY . .

# Install the project itself
RUN poetry install --no-interaction --no-ansi

# Expose the Streamlit port
EXPOSE 8501

# Command to run the application
# We use 0.0.0.0 to ensure it's accessible outside the container
CMD ["streamlit", "run", "source/classmate/tools/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
