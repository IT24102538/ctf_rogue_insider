#!/usr/bin/env python3
import base64
import binascii
import sys

from scapy.all import ICMP, IP, Raw, rdpcap

TARGET_FILE = "nexus_traffic_capture.pcap"
SOURCE_IP = "192.168.1.105"
DEST_IP = "45.33.32.156"
ICMP_ID = 0x1337


def extract_base64_chunks(pcap_path: str) -> str:
    chunks = {}

    for pkt in rdpcap(pcap_path):
        if IP not in pkt or ICMP not in pkt or Raw not in pkt:
            continue

        ip = pkt[IP]
        icmp = pkt[ICMP]

        if (
            ip.src == SOURCE_IP
            and ip.dst == DEST_IP
            and icmp.id == ICMP_ID
            and icmp.type == 8
        ):
            chunks[icmp.seq] = pkt[Raw].load.decode("ascii")

    if not chunks:
        raise ValueError("No covert ICMP packets found. Check the PCAP file or filter values.")

    return "".join(chunks[i] for i in sorted(chunks))


def main() -> None:
    pcap_path = sys.argv[1] if len(sys.argv) > 1 else TARGET_FILE

    try:
        encoded = extract_base64_chunks(pcap_path)
        decoded = base64.b64decode(encoded).decode("utf-8")
        if "CTF{" not in decoded:
            raise ValueError(
                "This capture contains credentials but no CTF flag. "
                "It is likely an older PCAP; rebuild the Stage 04 image "
                "and download the capture again."
            )
        print("Base64 payload:", encoded)
        print("Decoded text:", decoded)
    except (OSError, ValueError, binascii.Error, UnicodeDecodeError) as exc:
        print(f"Error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
