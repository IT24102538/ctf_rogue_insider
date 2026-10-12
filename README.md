# Operation: Rogue Insider

A self-contained, six-stage cybersecurity training CTF about investigating
an insider data breach at Nexus Corp. The stages cover web reconnaissance
and steganography, IDOR and hash cracking, prompt injection, network forensics,
Linux privilege escalation, and x86-64 ROP.

## Start here

1. Install Docker Engine with Compose v2, Python 3.9+, and pip.
2. Extract this folder and open a terminal here.
3. Build and start the challenge:

   ```sh
   docker compose up -d --build
   ```

4. Start the scoring dashboard in another terminal:

   ```sh
   ./start_dashboard.sh
   ```

5. Open [http://localhost:5000](http://localhost:5000), register a player,
   and use the dashboard to follow all six stages.

See [INSTALL_INSTRUCTIONS.txt](./INSTALL_INSTRUCTIONS.txt) for Windows setup,
ports, requirements, and shutdown instructions.

## Project layout

- `docker-compose.yml` — starts the six isolated challenge services.
- `ctf_dashboard/` — Flask scoring dashboard; its SQLite database is created
  locally when the dashboard first starts.
- `stage01/`–`stage06/` — challenge service source, assets, and Dockerfiles.
- `Official_Walkthrough.md` — instructor solution guide.
- `CTF_Project_Initiation_Document.md` — architecture diagram, port/network map,
  deployment plan, validation matrix, risk assessment, and contributor roles.
- `passwords.txt`, `hash.txt`, and `custom_wordlist.txt` — challenge reference
  wordlists and instructor/test data.

## Portability notes

Services bind to localhost only. Ensure the listed ports are free before
starting. Stage 06 is an x86-64 binary exploitation challenge; an x86-64 host
is recommended. Docker Desktop on ARM may use emulation, depending on its
configuration. Image builds require internet access for their base images and
packages.

This is an intentionally vulnerable, local training environment. Do not
expose its ports to a public network. The full bundle contains flags, reference
credentials, and solutions; keep it instructor-only if preserving challenge
integrity matters.

See [CTF_Project_Initiation_Document.md](./CTF_Project_Initiation_Document.md)
for the architecture, deployment, validation, and risk plan. Its validation
matrix describes checks to perform; it does not imply that they have been run.
