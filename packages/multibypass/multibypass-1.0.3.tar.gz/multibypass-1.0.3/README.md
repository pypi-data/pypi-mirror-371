<a href="https://github.com/grf0x/multibypass/">
  <img src=".img/logo.png"/>
</a>

## Installation

```bash
pipx install multibypass
```

## Usage

```console
usage: multibypass [-X ] [-H ] [-p ] [-j] [-x ] [-L] [-i] [-m ] [-h] [-d ] [-t ] 
[-s] [-o ] [-q] [-v] [-C] [-n] [-si ] [-sh ] [-vm ] [-vh ] [-va ] [-c] [-l] [-V] url

Pentest tool for bypassing restricted access using various techniques

positional arguments:
  url                   target url

http options:
  -X, --method          http method to use (default: GET)
  -H, --header          add an http header (key:value) (default: [])
  -p, --body-param      add a body parameter (key=value) (default: [])
  -j, --json            use a json body (default: False)
  -x, --proxy           http proxy to use (default: None)
  -L, --location        follow redirects (default: False)
  -i, --insecure        allow insecure connections (default: False)
  -m, --timeout         request timeout in seconds (default: 10)

general options:
  -h, --help            show this help message
  -d, --delay           delay or delay range between requests in seconds (e.g. 0.1 or 0.1-2) (default: 0)
  -t, --threads         number of threads (default: 32)
  -s, --stop            stop if the target returns 429 too many requests (default: False)

output options:
  -o, --output          write output to file (default: None)
  -q, --quiet           only show the final analysis (default: False)
  -v, --verbose         display extra debugging information (default: False)
  -C, --curl            show recommended curl commands (default: False)
  -n, --no-color        disable log colorization (default: False)

attack options:
  -si, --spoof-ip       add a custom ip (ip spoofing attack) (default: [])
  -sh, --spoof-header   add a custom header (ip spoofing attack) (default: [])
  -vm, --vt-method      add a custom method (verb tampering attack) (default: [])
  -vh, --vt-header      add a custom header (verb tampering attack) (default: [])
  -va, --vt-argument    add a custom argument (verb tampering attack) (default: [])
  -c, --custom          only test custom data (default: False)
  -l, --light           only test custom data and small subsets of default wordlists (default: False)
  -V, --variations      test case variations (default: False)
  ```

