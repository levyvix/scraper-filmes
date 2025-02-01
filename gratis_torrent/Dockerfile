FROM python:3.12-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Set the working directory
WORKDIR /gratis_torrent

# Copy the contents of the current directory into the working directory
COPY . .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint
CMD ["uv", "run", "dag.py"]