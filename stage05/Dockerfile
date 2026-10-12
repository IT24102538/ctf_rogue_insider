FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

# Install SSH + net-tools (provides /usr/sbin/netstat) + gcc to compile binary
RUN apt-get update && apt-get install -y \
    openssh-server \
    net-tools \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd

# ── Player user (credentials revealed by decoding Stage 04 ICMP PCAP) ──
RUN useradd -m -s /bin/bash dev
RUN echo 'dev:SecretPass!2026' | chpasswd

# ── Custom MOTD / Nexus Corp Banner ──────────────────────────────────────
RUN echo '  _   _                            ____                   ' > /etc/motd && \
    echo ' | \ | | _____  ___   _ ___     / ___|___  _ __ _ __      ' >> /etc/motd && \
    echo ' |  \| |/ _ \ \/ / | | / __|   | |   / _ \| `__| `_ \     ' >> /etc/motd && \
    echo ' | |\  |  __/>  <| |_| \__ \   | |__| (_) | |  | |_) |    ' >> /etc/motd && \
    echo ' |_| \_|\___/_/\_\\\\__,_|___/    \____\___/|_|  | .__/     ' >> /etc/motd && \
    echo '                                               |_|        ' >> /etc/motd && \
    echo '==========================================================' >> /etc/motd && \
    echo ' WARNING: UNAUTHORIZED ACCESS IS STRICTLY PROHIBITED.' >> /etc/motd && \
    echo ' This system is the property of Nexus Corp. All activity' >> /etc/motd && \
    echo ' is logged and monitored. Support: contact ARIA AI Bot.' >> /etc/motd && \
    echo '==========================================================' >> /etc/motd && \
    sed -i 's/#PrintMotd yes/PrintMotd yes/' /etc/ssh/sshd_config

# ── Flags ────────────────────────────────────────────────────────────────
RUN echo 'CTF{p4th_h1j4ck_r00t_pr1v3sc}' > /root/root_flag.txt
RUN chmod 600 /root/root_flag.txt

# Stage 06 breadcrumb — revealed after reaching root in Stage 05
RUN printf '=== CLASSIFIED NEXUS CORP MEMO ===\n\nInvestigation has uncovered a second server running a\ncustom vault binary. This asset requires further analysis.\n\nSSH Access:\n  Host : localhost  Port : 2223\n  User : analyst\n  Pass : V4ult4n4lyst!\n\nBinary location: ~/vault.elf\n\nHandle with extreme care.\n==================================\n' \
    > /root/stage06_hint.txt
RUN chmod 600 /root/stage06_hint.txt

# ── Compile the vulnerable SUID binary ───────────────────────────────────
COPY system-check.c /tmp/system-check.c
RUN gcc -o /usr/local/bin/system-check /tmp/system-check.c \
    && chmod u+s /usr/local/bin/system-check \
    && rm /tmp/system-check.c

# ── Confirm netstat exists at real path (so normal run works) ────────────
# /usr/sbin/netstat is installed via net-tools
# The PATH hijack replaces this at runtime when /tmp is prioritised

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]