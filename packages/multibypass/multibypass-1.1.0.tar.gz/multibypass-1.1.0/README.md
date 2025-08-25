<p align="center">
  <a href="https://github.com/grf0x/multibypass/">
    <img src="https://github.com/grf0x/multibypass/blob/master/.img/logo.png" width="90%"/>
  </a>
</p>
<br/>
<p align="center">
  Pentest tool for bypassing <code>4xx</code> restrictions and spotting unusual <code>200 OK</code> responses.<br/>
  Quickly uncovers misconfigurations and weak access controls.
</p>
<br/>
<p align="center">
  <a href="https://github.com/grf0x/multibypass/">
    <img src="https://github.com/grf0x/multibypass/blob/master/.img/example.png" width="90%"/>
  </a>
</p>

## Installation

```bash
pipx install multibypass
```

## Usage

```
usage: multibypass [-X ] [-H ] [-d ] [-b ] [-A ] [-x ] [-L] [-k] [-m ] [-h] [-D ] [-t ] [-s]
                   [-o ] [-q] [-v] [-C] [-n] [-l] [-V] [-i ] [-w ] url

Pentest tool for bypassing restricted access using various techniques.

REQUIRED:
  url                Target URL

HTTP OPTIONS:
  -X, --request      HTTP method to use (default: GET)
  -H, --header       Add an HTTP header (default: [])
  -d, --data         HTTP request data (default: None)
  -b, --cookie       Add a cookie (default: [])
  -A, --user-agent   Set the User-Agent (default: Mozilla/5.0)
  -x, --proxy        HTTP proxy to use (e.g. http://127.0.0.1:8080) (default: None)
  -L, --location     Follow redirects (default: False)
  -k, --insecure     Allow insecure connections (default: False)
  -m, --max-time     Request timeout in seconds (default: 10)

GENERAL OPTIONS:
  -h, --help         Show this help message
  -D, --delay        Delay or delay range between requests (e.g. 0.2 or 0.5-2) (default: 0)
  -t, --threads      Number of threads (default: 32)
  -s, --stop         Stop if the target returns HTTP 429 Too Many Requests (default: False)

OUTPUT OPTIONS:
  -o, --output       Write output to file (default: None)
  -q, --quiet        Only show the final analysis (default: False)
  -v, --verbose      Display extra debugging information (default: False)
  -C, --curl         Show recommended curl commands (default: False)
  -n, --no-color     Disable log colorization (default: False)

ATTACK OPTIONS:
  -l, --light        Perform a light attack (default: False)
  -V, --variations   Also test case variations (default: False)
  -i, --ip           Add a custom IP for spoofing attacks (default: [])
  -w, --wordlists    Use a custom wordlist directory (default: install-dir/wordlists)
  ```


## Implemented Bypass Techniques

### Verb Tampering
Use non-standard or alternative HTTP methods to bypass access controls.

**Examples:**
- If `GET /admin` is blocked then `POST /admin`, `HEAD /admin` or `TRACE /admin` can work.
- Some WAFs/firewalls only filter `GET`/`POST` and let others through.
- `GET /admin?method=POST`

### IP Spoofing via Header Injection
Add an header to impersonate a trusted client, such as an internal, localhost or corporate IP.

**Examples:**
- `X-Forwarded-For: 127.0.0.1`
- `X-Client-IP: 10.0.0.1`
- `X-Real-IP: 127.0.0.1`

### Paths with Alternate Casing
Some servers or filters are case-sensitive, others are not. Changing letter case can bypass filters.

**Examples:**
- `/ADMIN` vs `/admin`
- `/file.PHp` vs `/file.php`

### Searching for Backup Files
Look for misconfigured or forgotten backup/temporary files that bypass access restrictions.

**Examples:**
- `/admin.bak`, `/admin.old`, `/index.php~`, `/config.php.save`
- Git/SVN metadata: `/.git/`, `/.svn/`
- IDE/editor leftovers: `index.php.swp`, `index.php.bak`

### Various Filter Evasion Techniques
Trick input validation and filtering logic.

**Examples:**
- Encoding: `%2E%2E%2F`
- Double encoding: `%252E%252E%252F`
- Path traversal: `../`
