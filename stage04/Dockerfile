FROM python:3.9-slim

# Install scapy to generate the PCAP at build time
RUN pip install --no-cache-dir scapy==2.5.0

WORKDIR /app

# Copy generator — runs during docker build to produce the PCAP
COPY generate_pcap.py .
RUN python3 generate_pcap.py

# Serve both files via HTTP for player download
EXPOSE 8082
CMD ["python3", "-m", "http.server", "8082"]
COPY index.html .
