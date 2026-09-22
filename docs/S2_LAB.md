# S2 — operational literacy: the artisanal deploy (APP-03)

You SSH to your own VM, run `hello-world` by hand, prove the full HTTP contract,
then kill it — and see why an unsupervised process does not survive. Commands
are labelled **[VM]** (over SSH) or **[client]** (your laptop).

## 0. Access & versions

```bash
# [client]
chmod 400 dbai.pem
ssh -i dbai.pem ubuntu@<VM_IP>
# [VM] — the profile already installed git + uv; do NOT install another uv
uv --version          # must match the pinned S2 profile
git --version
ssh-keygen -t ed25519 # add the PUBLIC key to GitHub for git-over-SSH
```

## 1. The YAML trap → repair → contract

The starter ships `config/settings.yaml` with **deliberate faults** (a tab
indent and a missing space after a colon — see `fixtures/s2/settings.broken.yaml`).
A clean launch fails with a YAML error **before** the app binds a port:

```bash
# [VM]
uv sync
uv run hello-world     # crashes: yaml.scanner.ScannerError (nothing bound yet)
# fix config/settings.yaml (spaces, not tabs; "key: value"), then:
uv run hello-world     # now serving on 0.0.0.0:8000
```

Prove the contract:

```bash
# [VM] (or [client] against <VM_IP>:8000)
curl -i localhost:8000/          # 200 JSON incl hostname
curl -i localhost:8000/health    # 200
curl -i localhost:8000/boom      # 500
curl -i localhost:8000/nope      # 404
curl -i -X POST localhost:8000/  # 405
```

## 2. The death drill — no supervisor

Stop the foreground app with **Ctrl-C**. It stays stopped because nothing
supervises it — *not* because you closed an editor window:

```bash
# [VM]
# Ctrl-C in the app's terminal
ss -ltn | grep :8000     # gone — nothing listening
# [client]
curl -i http://<VM_IP>:8000/   # curl: (7) Connection refused
```

This stopwatch (manual steps + wall-clock) is the baseline the S5 pipeline beats.

## 3. S2 evidence contract

Submit under `evidence/s2/`:

| File | Proves |
|---|---|
| `curl-ok.png` | `[client]` curl → 200 while the app runs |
| `curl-dead.png` | `[client]` curl → Connection refused after the death drill |
| `scavenger.md` | kernel / disk / RAM / PID 1 / auth-log findings (homework) |
| `stopped.png` | the AWS instance in state **Stopped** (cost discipline, homework) |

Record the artisanal-deploy **time and manual-step count** in `JOURNAL.md` for
the later S5 comparison. Preserve all S1 coursework during the repair.
