#!/usr/bin/env python3
import argparse, os, logging, requests, threading, time, random, queue, json, urllib 


VERSION = "1.1"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WORDLISTS_DIR = os.path.join(CURRENT_DIR, "wordlists")
BORDER = "─" * 65
DASHED_BORDER = "-" * 65

LIGHT_LIMITS = {}
LIGHT_LIMITS["spoofing-headers"] = 8
LIGHT_LIMITS["spoofing-ips"] = 5
LIGHT_LIMITS["verb-tampering-methods"] = 8
LIGHT_LIMITS["verb-tampering-arguments"] = 2
LIGHT_LIMITS["verb-tampering-headers"] = 4
LIGHT_LIMITS["web-extensions"] = 2
LIGHT_LIMITS["backup-extensions"] = 25
LIGHT_LIMITS["user-agents"] = 40


########
# MAIN #
########


def main():
    try:
        start_time = time.time()
        request_queue = queue.Queue()
        
        create_initial_request(request_queue)
        create_ip_spoofing_requests(request_queue)
        create_verb_tampering_requests(request_queue)
        create_alternate_user_agent_requests(request_queue)
        create_search_backup_requests(request_queue)
        create_url_tampering_requests(request_queue)

        responses = send_requests(request_queue)
        analysis(responses)
        
        log.debug(f"\nExecution time: {round(time.time() - start_time, 4)} seconds")
    except KeyboardInterrupt:
        os._exit(1)


#######################
# BUILD REQUEST QUEUE #
#######################


def create_initial_request(request_queue):
    request_queue.put(Request("Initial request"))


def create_ip_spoofing_requests(request_queue):
    spoofing_headers = parse_wordlist("spoofing-headers")
    spoofing_ips = args.custom_ips + parse_wordlist("spoofing-ips")
    if args.variations:
        spoofing_headers = get_case_variations(spoofing_headers)
    
    for header in spoofing_headers:
        for ip in spoofing_ips:
            request_queue.put(Request(f"Add header '{header}: {ip}'",  headers={header: ip}))


def create_verb_tampering_requests(request_queue):
    vt_methods = parse_wordlist("verb-tampering-methods")
    vt_arguments = parse_wordlist("verb-tampering-arguments")
    vt_headers = parse_wordlist("verb-tampering-headers")
    if args.variations:
        vt_methods = get_case_variations(vt_methods)
        vt_arguments = get_case_variations(vt_arguments)
        vt_headers = get_case_variations(vt_headers)
    
    for method in vt_methods:
        request_queue.put(Request(f"Use method '{method}'", method=method))

        for header in vt_headers:
            request_queue.put(Request(f"Add header '{header}: {method}'", headers={header: method}))
        
        for arg in vt_arguments:
            request_queue.put(Request(f"Add query parameter '{arg}={method}' in url", params={arg:method}))
            request_queue.put(Request(f"Add body parameter '{arg}={method}'", data={arg:method}))


def create_alternate_user_agent_requests(request_queue):
    user_agents = parse_wordlist("user-agents")
    if args.variations:
        user_agents = get_case_variations(user_agents)
    
    for user_agent in user_agents:
        request_queue.put(Request(f"Add header 'User-Agent: {user_agent}'", headers={"User-Agent": user_agent}))


def create_search_backup_requests(request_queue):
    backup_extensions = parse_wordlist("backup-extensions")
    web_extensions = parse_wordlist("web-extensions")
    if args.variations:
        backup_extensions = get_case_variations(backup_extensions, alt_caps=False, capitalize=False)
    url = urllib.parse.urlparse(args.url)

    prefix = ""
    if not url.path.split("/")[-1]:
        prefix = "index"

    payloads = []
    for web_ext in web_extensions:
        payloads.append(prefix + web_ext)
        for backup_ext in backup_extensions:
            payloads.append(prefix + backup_ext)
            payloads.append(prefix + web_ext + backup_ext)

    for payload in set(payloads):
        new_url = url._replace(path=url.path + payload)
        request_queue.put(Request(f"Change path '{new_url.path}'", url=urllib.parse.urlunparse(new_url)))


def create_url_tampering_requests(request_queue):
    ut_prefixes = parse_wordlist("url-tampering-prefixes")
    ut_suffixes = parse_wordlist("url-tampering-suffixes")
    url = urllib.parse.urlparse(args.url)
    base_paths = {url.path, alternating_caps(url.path)}

    payloads = []
    for path in base_paths:
        path_elements = path.strip("/").split("/")
        for prefix in ut_prefixes:
            payloads.append("".join(path_elements[:-1]) + "/" + prefix + path_elements[-1])
        for suffix in ut_suffixes:
            payloads.append(path.strip("/") + suffix)

    for payload in set(payloads):
        new_url = url._replace(path=payload)
        request_queue.put(Request(f"Change path '{payload}'", url=urllib.parse.urlunparse(new_url)))


def parse_wordlist(filename):
    try:
        with open(os.path.join(args.wordlists_dir, filename)) as file:
            data = []
            for line in file:
                if line.strip():
                    data.append(line.strip())
    except:
        log.critical(f"Could not open worldlist '{filename}' in {args.wordlists_dir}")
    
    if args.light and filename in LIGHT_LIMITS:
        return list(set(data[:LIGHT_LIMITS[filename]]))
    else:
        return list(set(data))


class Request:
    def __init__(self, description, url=None, method=None, headers={}, data={}, params={}):
        self.description = description
        self.url = url
        self.method = method
        self.headers = headers
        self.data = data
        self.params = params


#################
# SEND REQUESTS #
#################


def send_requests(request_queue):
    log.info(f"Ready to send {request_queue.qsize() - 1} requests using {args.threads} threads")
    if not args.quiet:
        print_title("FUZZING")
        print_response_header()

    threads = []
    responses = []
    timer = Timer()

    for _ in range(args.threads):
        t = threading.Thread(target=send_requests_thread, args=(request_queue, responses, timer))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return responses


def send_requests_thread(request_queue, responses, timer):
    session = Session()
    while True:
        if not request_queue.empty():
            if timer.is_paused():
                timer.sleep_while_paused()
                continue
            elif args.delay:
                timer.set_pause(args.delay)

        try:
            request = request_queue.get_nowait()
        except queue.Empty:
            break

        response = session.send(request)

        if response.status_code == 429 and args.stop:
            os._exit(1)
        if not args.quiet:
            print_response(response)

        responses.append(response)
        request_queue.task_done()


class Timer:
    def __init__(self):
        self.lock = threading.Lock()
        self.pause_until = 0

    def is_paused(self):
        with self.lock:
            return self.pause_until > time.time()

    def sleep_while_paused(self):
        with self.lock:
            sleep_time = self.pause_until - time.time()
        time.sleep(sleep_time)

    def set_pause(self, delay):
        try:
            if "-" in delay:
                delay_range = delay.split("-")
                float_delay = random.uniform(float(delay_range[0]), float(delay_range[1]))
            else:
                float_delay = float(delay)
        except:
            log.critical(f"Invalid delay specified '{delay}'")
        
        with self.lock:
            self.pause_until = time.time() + float_delay


class Session:
    def __init__(self):
        self.reqlib_session = requests.session()
        self.url = args.url
        self.method = args.method
        self.verify = not args.insecure
        self.allow_redirects = args.location
        self.timeout = args.timeout
        self.headers = {}
        self.cookies = {}
        self.proxy = {}
        self.data = {}
        self.data_is_json = args.json
        self._set_headers()
        self._set_cookies()
        self._set_proxy()
        self._set_data()
        requests.packages.urllib3.disable_warnings()

    def send(self, request):
        response = None
        url = request.url if request.url else self.url
        method = request.method if request.method else self.method
        headers = self.headers | request.headers
        data = self.data | request.data if not self.data_is_json else None
        json = self.data | request.data if self.data_is_json else None

        final_request = requests.Request(
            url=url,
            method=method,
            headers=headers,
            data=data,
            json=json,
            cookies=self.cookies,
            params=request.params
        )
        try:
            response = self.reqlib_session.send(
                final_request.prepare(), 
                verify=self.verify,
                proxies=self.proxy,
                timeout=self.timeout,
                allow_redirects=self.allow_redirects
            )
        except Exception as e:
            log.critical(f"Request failed : {e}")
        
        response.length = len(response.content)
        response.description = request.description
        
        return response

    def _set_headers(self):
        self.headers.update({"User-Agent": args.user_agent})
        for header in args.headers:
            try:
                key, value = header.split(":", 1)
                self.headers.update({key.strip(): value.strip()})
            except:
                log.critical(f"Invalid header '{header}'")

    def _set_proxy(self):
        if args.proxy:
            try:
                self.proxy = {
                    "http": "http://" + args.proxy.split("//")[1],
                    "https": "http://" + args.proxy.split("//")[1]
                }
            except:
                log.critical(f"Invalid proxy specified '{args.proxy}'")

    def _set_cookies(self):
        for cookie_string in args.cookies:
            for cookie in cookie_string.split(";"):
                try:
                    key, value = cookie.split("=", 1)
                    self.cookies.update({key.strip(): value.strip()})
                except:
                    log.critical(f"Invalid cookie '{cookie_string}'")

    def _set_data(self):
        if args.data:
            try:
                self.data = json.loads(args.data)
                self.data_is_json = True
            except:
                try:
                    self.data = parse_url_data(args.data)
                except:
                    log.critical(f"Invalid body data specified '{args.data}'")


############
# ANALYSIS #
############


def analysis(responses):
    initial_request = None
    for response in responses:
        if response.description == "Initial request":
            initial_request = response
    responses.remove(initial_request)

    resp_by_length = group_responses_by(responses, "length")
    resp_by_status = group_responses_by(responses, "status_code")
    successes_by_length = group_responses_by(resp_by_status.get(200, []), "length")
    
    print_title("STATISTICS")
    log.info(colorize(f"{len(responses):<8} requests sent"))
    print_stat(resp_by_status, "unique status codes")
    print_stat(resp_by_length, "unique response lengths", "bytes")
    print_stat(successes_by_length, "unique lengths of successful responses (200)", "bytes")
    
    title = ""
    to_print = []
    ignored_lengths = {initial_request.length, 0}
    alt_success_exist = bool(set(successes_by_length) - ignored_lengths)

    if alt_success_exist:
        if initial_request.status_code != 200:
            title = "[!] BYPASS FOUND [!]"
            for response in resp_by_status[200]:
                if response.length not in ignored_lengths:
                    to_print.append(response)
        else:
            title = "SAMPLE OF INTERESTING RESPONSES"
            for length, response_list in successes_by_length.items():
                if length not in ignored_lengths:
                    to_print.append(response_list[0])

    if to_print:
        print_title(title)
        print_response_header()
        for response in to_print:
            print_response(response)
    

def group_responses_by(responses, attribute):
    result = {}
    if responses:
        for response in responses:
            result.setdefault(getattr(response, attribute), []).append(response)
        result = dict(sorted(result.items(), key=lambda item: len(item[1])))

    return result


#########
# UTILS #
#########


def get_curl_command(request):
    command = "curl -v"
    command += f" {request.url}"

    if request.method != "GET":
        command += f" -X {request.method}"
    if request.body:
        command += f" -d '{request.body}'"
    
    for key, value in request.headers.items():
        if key != "Content-Length" and key != "Content-Type":
            command += f" -H '{key}: {value}'"

    return command


def parse_url_data(data):
    flat = {}
    not_flat = urllib.parse.parse_qs(data, strict_parsing=True)
    for key, value in not_flat.items():
        if len(value) == 1:
            flat[key] = value[0]
        else:
            flat[key] = value

    return flat


def get_case_variations(string_list, alt_caps=True, capitalize=True, word_separators=True):
    alpha_variations = list(string_list)
    alpha_variations += [string.upper() for string in string_list]
    alpha_variations += [string.lower() for string in string_list]
    if capitalize:
        alpha_variations += [string.capitalize() for string in string_list]
    if alt_caps:
        alpha_variations += [alternating_caps(string) for string in string_list]
    
    all_variations = list(alpha_variations)
    if word_separators:
        all_variations += [string.replace("-", "_") for string in alpha_variations]
        all_variations += [string.replace("_", "-") for string in alpha_variations]
        all_variations += [flip_word_separator(string) for string in alpha_variations]

    return set(list(all_variations))


def flip_word_separator(string):
    return string.replace("_", "§").replace("-", "_").replace("§", "-")


def alternating_caps(string):
    chars = [c.lower() for c in string]
    alpha_count = 0

    for i in range(len(chars)):
        if chars[i].isalpha():
            if alpha_count % 2 == 1:
                chars[i] = chars[i].upper()
            alpha_count += 1

    return "".join(chars)


################
# CUSTOM PRINT #
################


def colorize(string):
    if args.no_color:
        return string
    else:
        return f"\033[1;36m{string}\033[0m"


def print_title(title):
    log.info(f"\n{BORDER}\n")
    log.info(colorize(f"{title:^65}"))
    log.info(f"\n{BORDER}\n")


def print_stat(resp_dict, description, unit=""):
    if resp_dict:
        log.info(colorize(f"\n{len(resp_dict):<8} {description}"))
        for key in resp_dict.keys():
            log.info(f"{len(resp_dict[key]):<8} {key} {unit}")


def print_response_header():
    log.info(f"{"Length":<7} {"Status":<7} Description\n")


def print_response(response):
    to_print = f"{response.length:<8} {response.status_code:<6} {response.description}"
    
    if response.status_code == 200:
        to_print = colorize(to_print)
    if args.verbose or args.curl:
        to_print = f"{DASHED_BORDER}\n{to_print}\n{DASHED_BORDER}"
    if args.curl:
        to_print += f"\n{get_curl_command(response.request)}"
    
    if args.verbose:
        to_print += f"\n* {response.request.method} {response.request.url} HTTP/1.1"

        for key, value in response.request.headers.items():
            to_print += f"\n* {key}: {value}"

        if response.request.body:
            to_print += f"\n* {response.request.body}"
        
        log.debug(to_print.strip())
    else:
        log.info(to_print)


##########
# LOGGER #
##########


class CustomLogger(logging.Logger):
    def critical(self, msg, *args, **kwargs):
        super().critical(msg, *args, **kwargs)
        os._exit(1)


class CustomFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno >= logging.ERROR:
            self._style._fmt = colorize("ERROR | %(message)s")
        else:
            self._style._fmt = "%(message)s"
        
        return super().format(record)


def get_logger():
    logging.setLoggerClass(CustomLogger)
    logger = logging.getLogger(__name__)

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)
    
    if args.output:
        file_handler = logging.FileHandler(args.output, mode="w")
        file_handler.setFormatter(CustomFormatter())
        logger.addHandler(file_handler)

    return logger


##############
# ARG PARSER #
##############


def parse_args():
    parser = argparse.ArgumentParser(
        description="Pentest tool for bypassing restricted access using various techniques.",
        epilog="See https://github.com/grf0x/multibypass for examples and detailed usage.",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    required_group = parser.add_argument_group("REQUIRED")
    http_group = parser.add_argument_group("HTTP OPTIONS")
    general_group = parser.add_argument_group("GENERAL OPTIONS")
    output_group = parser.add_argument_group("OUTPUT OPTIONS")
    attack_group = parser.add_argument_group("ATTACK OPTIONS")
    
    required_group.add_argument(dest="url", help="Target URL")
    
    http_group.add_argument("-X", "--request", metavar="", dest="method", default="GET", help="HTTP method to use")
    http_group.add_argument("-H", "--header", metavar="", dest="headers", action="append", default=[], help="Add an HTTP header")
    http_group.add_argument("-d", "--data", metavar="", dest="data", help="HTTP request data")
    http_group.add_argument("-b", "--cookie", metavar="", dest="cookies", action="append", default=[], help="Add a cookie")
    http_group.add_argument("-A", "--user-agent", metavar="", dest="user_agent", default="Mozilla/5.0", help="Set the User-Agent")
    http_group.add_argument("-x", "--proxy", metavar="", help="HTTP proxy to use (e.g. http://127.0.0.1:8080)")
    http_group.add_argument("-L", "--location", action="store_true", default=False, help="Follow redirects")
    http_group.add_argument("-k", "--insecure", action="store_true", default=False, help="Allow insecure connections")
    http_group.add_argument("-m", "--max-time", metavar="", dest="timeout", default=10, type=int, help="Request timeout in seconds")

    general_group.add_argument("-h", "--help", action="help", help="Show this help message")
    general_group.add_argument("-D", "--delay", metavar="", default=0, help="Delay or delay range between requests (e.g. 0.2 or 0.5-2)")
    general_group.add_argument("-t", "--threads", metavar="", default=32, type=int, help="Number of threads")
    general_group.add_argument("-s", "--stop", action="store_true", default=False, help="Stop if the target returns HTTP 429 Too Many Requests")
    
    output_group.add_argument("-o", "--output", metavar="", help="Write output to file")
    output_group.add_argument("-q", "--quiet", action="store_true", default=False, help="Only show the final analysis")
    output_group.add_argument("-v", "--verbose", action="store_true", default=False, help="Display extra debugging information")
    output_group.add_argument("-C", "--curl", action="store_true", default=False, help="Show recommended curl commands")
    output_group.add_argument("-n", "--no-color", action="store_true", dest="no_color", default=False, help="Disable log colorization")
    
    attack_group.add_argument("-l", "--light", action="store_true", default=False, help="Perform a light attack")
    attack_group.add_argument("-V", "--variations", action="store_true", default=False, help="Also test case variations")
    attack_group.add_argument("-j", "--json", action="store_true", default=False, help="Always use a json body")
    attack_group.add_argument("-i", "--ip", metavar="", dest="custom_ips", action="append", default=[], help="Add a custom IP for spoofing attacks")
    attack_group.add_argument("-w", "--wordlists", metavar="", dest="wordlists_dir", default=DEFAULT_WORDLISTS_DIR, help="Use a custom wordlist directory")

    return parser.parse_args()


##################
# INITIALIZATION #
##################


print(f"""\033[1;36m
 __  __      _ _   _ ___
|  \\/  |_  _| | |_(_| _ )_  _ _ __ ___ ______
| |\\/| | || | |  _| | _ | || | '_ / _'(_-(_-/
|_|  |_|_.._|_|\\__|_|___/\\_, | .__\\___|__)__)
                         |__/|_|
                                        v{VERSION}
\033[0m""")

args = parse_args()
log = get_logger()

if __name__ == "__main__":
    main()
