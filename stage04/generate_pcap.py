
from scapy.all import wrpcap, IP, TCP, UDP, ICMP, Raw, ARP, Ether
import random
import base64

random.seed(0x1337)  # reproducible PCAP


CREDENTIAL   = "dev:SecretPass!2026_CTF{1cmp_tunn3l_c0v3rt_ch4nn3l}"
B64_PAYLOAD  = base64.b64encode(CREDENTIAL.encode()).decode()


ATTACKER_IP  = "192.168.1.105"   
C2_IP        = "45.33.32.156"   
COVERT_ID    = 0x1337            

# ── Helpers ───────────────────────────────────────────────────────────
def rand_internal():
    return f"192.168.1.{random.randint(2, 100)}"

def rand_external():
    choices = ["8.8.8.8", "1.1.1.1", "13.107.21.200", "151.101.1.67"]
    return random.choice(choices)

packets = []

# ── 1. ARP noise (20 packets) ─────────────────────────────────────────
for _ in range(20):
    src = rand_internal()
    dst = rand_internal()
    pkt = (Ether(src="aa:bb:cc:dd:ee:01", dst="ff:ff:ff:ff:ff:ff") /
           ARP(op=random.choice([1, 2]),
               hwsrc="aa:bb:cc:dd:ee:" + format(random.randint(0, 255), '02x'),
               psrc=src, pdst=dst))
    packets.append(pkt)

# ── 2. HTTP cleartext noise (25 packets) ─────────────────────────────
paths = ["/", "/index.html", "/login", "/api/users", "/static/logo.png",
         "/dashboard", "/api/v1/status", "/favicon.ico"]
for _ in range(25):
    src = rand_internal()
    sport = random.randint(49152, 65535)
    body = f"GET {random.choice(paths)} HTTP/1.1\r\nHost: nexus-corp.internal\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n\r\n"
    pkt = (IP(src=src, dst="10.0.0.1") /
           TCP(sport=sport, dport=80, flags="PA", seq=random.randint(1000,999999)) /
           Raw(load=body.encode()))
    packets.append(pkt)
    # ACK reply
    reply = (IP(src="10.0.0.1", dst=src) /
             TCP(sport=80, dport=sport, flags="A"))
    packets.append(reply)

# ── 3. TLS encrypted noise (20 packets) ──────────────────────────────
for _ in range(20):
    src = rand_internal()
    sport = random.randint(49152, 65535)
    # Fake TLS ClientHello header
    tls_hello = (b'\x16\x03\x01' +                   # TLS Record header
                 random.randint(50,200).to_bytes(2,'big') +
                 b'\x01\x00' +                        # ClientHello
                 bytes([random.randint(0,255) for _ in range(38)]))
    pkt = (IP(src=src, dst=rand_external()) /
           TCP(sport=sport, dport=443, flags="PA") /
           Raw(load=tls_hello))
    packets.append(pkt)

# ── 4. Normal ICMP pings — decoys (standard 32-byte padding) ─────────
for i in range(14):
    src = rand_internal()
    dst = rand_external()
    standard_data = b'abcdefghijklmnopqrstuvwxyz012345'  # 32 bytes, Windows-style
    pkt  = (IP(src=src, dst=dst) /
            ICMP(type=8, code=0, id=random.randint(0x0100, 0x0FFF), seq=i) /
            Raw(load=standard_data))
    reply= (IP(src=dst, dst=src) /
            ICMP(type=0, code=0, id=random.randint(0x0100, 0x0FFF), seq=i) /
            Raw(load=standard_data))
    packets.append(pkt)
    packets.append(reply)

# ── 5. UDP DNS queries (noise) ────────────────────────────────────────
domains = [b'\x06nexus\x04corp\x00', b'\x03www\x06google\x03com\x00',
           b'\x03api\x06github\x03com\x00']
for _ in range(12):
    src = rand_internal()
    pkt = (IP(src=src, dst="192.168.1.1") /
           UDP(sport=random.randint(1024,65535), dport=53) /
           Raw(load=b'\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' +
               random.choice(domains)))
    packets.append(pkt)

# ── 6. COVERT CHANNEL — ICMP data exfiltration ───────────────────────
# Split B64 payload into 8-char chunks, one per ICMP packet
CHUNK_SIZE = 8
chunks = [B64_PAYLOAD[i:i+CHUNK_SIZE] for i in range(0, len(B64_PAYLOAD), CHUNK_SIZE)]

for seq_num, chunk in enumerate(chunks):
    # Outbound covert ping (attacker → C2)
    covert_out = (IP(src=ATTACKER_IP, dst=C2_IP) /
                  ICMP(type=8, code=0, id=COVERT_ID, seq=seq_num) /
                  Raw(load=chunk.encode()))
    # Inbound reply (C2 → attacker) — echoes the data
    covert_in  = (IP(src=C2_IP, dst=ATTACKER_IP) /
                  ICMP(type=0, code=0, id=COVERT_ID, seq=seq_num) /
                  Raw(load=chunk.encode()))
    packets.append(covert_out)
    packets.append(covert_in)

# ── 7. More HTTP noise after covert channel ───────────────────────────
for _ in range(18):
    src = rand_internal()
    sport = random.randint(49152, 65535)
    body = f"POST /api/v1/auth HTTP/1.1\r\nHost: nexus-corp.internal\r\nContent-Type: application/json\r\nContent-Length: 42\r\n\r\n"
    pkt = (IP(src=src, dst="10.0.0.2") /
           TCP(sport=sport, dport=8080, flags="PA") /
           Raw(load=body.encode()))
    packets.append(pkt)

# ── Shuffle to mix noise with covert traffic ──────────────────────────
# Keep covert packets embedded non-contiguously (more realistic)
random.shuffle(packets)

# ── Write PCAP ────────────────────────────────────────────────────────
output = 'nexus_traffic_capture.pcap'
wrpcap(output, packets)

print(f"[+] PCAP generated: {output}")
print(f"[+] Total packets:  {len(packets)}")
print(f"[+] Covert chunks:  {len(chunks)} ICMP packets (id=0x{COVERT_ID:04X})")
print(f"[+] Attacker IP:    {ATTACKER_IP} → {C2_IP}")
print(f"[+] B64 payload:    {B64_PAYLOAD}")
print(f"[+] Decoded creds:  {CREDENTIAL}")
print()
print("Wireshark filter: icmp")
print("Look for: ICMP id=0x1337 from 192.168.1.105 to 45.33.32.156")
