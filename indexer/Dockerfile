FROM dipdup/dipdup:8

WORKDIR /home/dipdup

# Switch to root to install dependencies globally
USER root

# Copy requirements
COPY requirements.txt .

# Install dependencies using the system python, which is usually where pip is
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Ensure the system site-packages are on the path for DipDup's own environment
ENV PYTHONPATH="/usr/local/lib/python3.12/site-packages:/home/dipdup/src"

# Switch back to the default dipdup user
USER dipdup

# Copy everything
COPY . .
