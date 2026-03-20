# Start from Ubuntu latest image
FROM ubuntu:latest

# Install python and nano
RUN apt-get update && apt-get install -y python3-dev nano pip

# Set working directory
WORKDIR /app

# Install pandas overriding environment protection
RUN pip install --break-system-packages pandas

# Run when container starts
ENTRYPOINT ["python"]
CMD ["sleep infinity"]