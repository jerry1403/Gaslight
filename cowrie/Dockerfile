FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Create honeypot user
RUN useradd --create-home --shell /bin/bash --user-group honeypot

# Set up working directory
WORKDIR /cowrie

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install asyncssh requests

# Create necessary directories
RUN mkdir -p var/log

# Generate SSH host key
RUN ssh-keygen -t rsa -f ssh_host_key -N ""

# Copy our simple honeypot
COPY simple_honeypot.py ./
COPY entrypoint.sh /entrypoint.sh

# Make files executable
RUN chmod +x /entrypoint.sh
RUN chmod +x simple_honeypot.py

# Set proper ownership
RUN chown -R honeypot:honeypot /cowrie

# Switch to honeypot user
USER honeypot

# Create volume for logs
VOLUME ["/cowrie/var"]

# Expose SSH port
EXPOSE 2222

CMD ["/entrypoint.sh"]