FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    gcc \
    gdb \
    python3 \
    python3-pip \
    binutils \
    file \
    openssh-server \
    && pip3 install --no-cache-dir pwntools \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd

# ── Player account (credentials in Stage 05 /root/stage06_hint.txt) ──────
RUN useradd -m -s /bin/bash analyst
RUN echo 'analyst:V4ult4n4lyst!' | chpasswd

# ── Flag (readable only by root — requires successful ROP shell) ──────────
RUN echo 'CTF{r0p_ch41n_v4ult_br34ch3d}' > /root/vault_flag.txt
RUN chmod 600 /root/vault_flag.txt

# ── Compile vault.elf ─────────────────────────────────────────────────────
# Flags:
#   -no-pie           → fixed binary base (gadget addresses are static)
#   -fno-stack-protector → no canary (enables clean overflow)
#   NX enabled by default → stack not executable → forces ROP
#   -w                → suppress gets() deprecation warning
WORKDIR /home/analyst
COPY vault.c .
RUN gcc -o vault.elf vault.c -no-pie -fno-stack-protector -w \
    && chown root:root vault.elf \
    && chmod 4755 vault.elf \
    && rm vault.c

# ── Verify binary security properties ────────────────────────────────────
RUN echo "[*] Binary security profile:" && \
    file vault.elf && \
    python3 -c "from pwn import *; e=ELF('./vault.elf'); print('NX:',e.nx,'PIE:',e.pie,'Canary:',e.canary)"

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
