#!/usr/bin/env python3

import argparse, os, logging, requests, threading, time, random, queue


VERSION = "1.0"
CURRENT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DEFAULT_USER_AGENT = "Mozilla/5.0"
LIGHT_SPOOFING_HEADERS = 8
LIGHT_SPOOFING_IPS = 5
LIGHT_VT_METHODS = 5
BORDER = "─" * 65
DASHED_BORDER = "-" * 65


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
        responses = send_requests(request_queue)
        analysis(responses)
        log.debug(f"\nExecution time: {round(time.time() - start_time, 4)} seconds")
    except KeyboardInterrupt:
        os._exit(1)


#######################
# BUILD REQUEST QUEUE #
#######################


def create_initial_request(request_queue):
    add_request_to_queue(request_queue, "Initial request")


def create_ip_spoofing_requests(request_queue):
    spoofing_headers = args.spoofing_headers + get_default_data("spoofing-headers", LIGHT_SPOOFING_HEADERS)
    spoofing_ips = args.spoofing_ips + get_default_data("spoofing-ips", LIGHT_SPOOFING_IPS)

    if args.case_variations:
        spoofing_headers = get_case_variations(spoofing_headers)
    
    for header in spoofing_headers:
        for ip in spoofing_ips:
            add_request_to_queue(request_queue, f"Add header '{header}: {ip}'",  headers={header: ip})


def create_verb_tampering_requests(request_queue):
    vt_methods = args.vt_methods + get_default_data("verb-tampering-methods", LIGHT_VT_METHODS)
    vt_arguments = args.vt_arguments + get_default_data("verb-tampering-arguments")
    vt_headers = args.vt_headers + get_default_data("verb-tampering-headers")

    if args.case_variations:
        vt_methods = get_case_variations(vt_methods)
        vt_arguments = get_case_variations(vt_arguments)
        vt_headers = get_case_variations(vt_headers)

    for method in vt_methods:
        add_request_to_queue(request_queue, f"Use method '{method}'", method=method)
        
        for header in vt_headers:
            add_request_to_queue(request_queue, f"Add header '{header}: {method}'", headers={header: method})

        for arg in vt_arguments:
            add_request_to_queue(request_queue, f"Add query parameter '{arg}={method}' in url", params={arg:method})
            add_request_to_queue(request_queue, f"Add body parameter '{arg}={method}'", data={arg:method})


def add_request_to_queue(request_queue, description, method=None, headers={}, params={}, data={}):
    if not method:
        method = args.method

    request = requests.Request(url=args.url, method=method, params=params, data=data, headers=headers)
    request.description = description
    request_queue.put(request)


def get_default_data(filename, light_limit=None):
    with open(os.path.join(CURRENT_DIRECTORY, "wordlists", filename)) as file:
        data = []
        for line in file:
            if line.strip():
                data.append(line.strip())
    
    if args.custom:
        return []
    elif args.light:
        return data[:light_limit]
    else:
        return data


#################
# SEND REQUESTS #
#################


def send_requests(request_queue):
    log.info(f"Ready to send {request_queue.qsize() - 1} requests using {args.threads} threads")
    
    if not args.quiet:
        print_title("FUZZING")
        print_response_header()

    if args.insecure:
        try:
            old_ciphers = ":HIGH:!DH:!aNULL"
            requests.packages.urllib3.disable_warnings()
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += old_ciphers
            requests.packages.urllib3.contrib.pyopenssl.util.ssl_.DEFAULT_CIPHERS += old_ciphers
        except:
            pass

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
    session = get_request_session()

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

        try:
            if args.json:
                request.json = dict(session.data, **request.data)
                request.data = {}
            else:
                request.data = dict(session.data, **request.data)
            prepared = session.prepare_request(request)
            response = session.send(prepared, timeout=session.timeout, allow_redirects=session.allow_redirects)
        except (requests.exceptions.ProxyError, requests.exceptions.InvalidProxyURL) as e:
            log.critical(f"Invalid proxy specified '{args.proxy}'")
        except Exception as e:
            log.critical(f"Request failed : {e}")

        if response.status_code == 429 and args.stop:
            os._exit(1)

        response.length = len(response.content)
        response.description = request.description
        responses.append(response)

        if not args.quiet:
            print_response(response)

        request_queue.task_done()


"""
Note: timeout, allow_redirects, and data are not real session attributes.
They are added here for convenience so that all relevant request information
is available in one place.
"""
def get_request_session():
    session = requests.Session()
    session.verify = not args.insecure
    session.allow_redirects = args.location
    session.timeout = args.timeout
    session.headers = {"User-Agent": DEFAULT_USER_AGENT}
    session.data = {}

    for header in args.headers:
        try:
            key, value = header.split(":", 1)
            session.headers.update({key.strip(): value.strip()})
        except:
            log.critical(f"Invalid header '{header}'")
    
    for param in args.body_params:
        try:
            key, value = param.replace(":", "=").split("=", 1)
            session.data.update({key.strip(): value.strip()})
        except:
            log.critical(f"Invalid body parameter '{param}'")

    if args.proxy:
        try:
            session.proxies = {"http": args.proxy, "https": args.proxy}
        except:
            log.critical(f"Invalid proxy specified '{args.proxy}'")

    return session 


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


def remove_duplicates(lst):
    return list(set(lst))


def get_case_variations(string_list):
    alpha_variations = list(string_list)
    alpha_variations += [string.upper() for string in string_list]
    alpha_variations += [string.lower() for string in string_list]
    alpha_variations += [string.capitalize() for string in string_list]
    alpha_variations += [alternating_caps(string) for string in string_list]
    alpha_variations = remove_duplicates(alpha_variations)

    all_variations = [string.replace("-", "_") for string in alpha_variations]
    all_variations += [string.replace("_", "-") for string in alpha_variations]
    all_variations += [flip_word_separator(string) for string in alpha_variations]
    all_variations = [string.strip("-") for string in all_variations]

    return remove_duplicates(all_variations)


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

    return ''.join(chars)


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
        description="Pentest tool for bypassing restricted access using various techniques",
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    http_group = parser.add_argument_group("http options")
    general_group = parser.add_argument_group("general options")
    output_group = parser.add_argument_group("output options")
    attack_group = parser.add_argument_group("attack options")
    
    parser.add_argument(dest="url", help="target url")
    
    http_group.add_argument("-X", "--method", metavar="", dest="method", default="GET", help="http method to use")
    http_group.add_argument("-H", "--header", metavar="", dest="headers", action="append", default=[], help="add an http header (key:value)")
    http_group.add_argument("-p", "--body-param", metavar="", dest="body_params", action="append", default=[], help="add a body parameter (key=value)")
    http_group.add_argument("-j", "--json", action="store_true", default=False, help="use a json body")
    http_group.add_argument("-x", "--proxy", metavar="", dest="proxy", help="http proxy to use")
    http_group.add_argument("-L", "--location", action="store_true", default=False, help="follow redirects")
    http_group.add_argument("-i", "--insecure", action="store_true", default=False, help="allow insecure connections")
    http_group.add_argument("-m", "--timeout", metavar="", default=10, type=int, help="request timeout in seconds")

    general_group.add_argument("-h", "--help", action="help", help="show this help message")
    general_group.add_argument("-d", "--delay", metavar="", default=0, help="delay or delay range between requests in seconds (e.g. 0.1 or 0.1-2)")
    general_group.add_argument("-t", "--threads", metavar="", default=32, type=int, help="number of threads")
    general_group.add_argument("-s", "--stop", action="store_true", default=False, help="stop if the target returns 429 too many requests")
    
    output_group.add_argument("-o", "--output", metavar="", help="write output to file")
    output_group.add_argument("-q", "--quiet", action="store_true", default=False, help="only show the final analysis")
    output_group.add_argument("-v", "--verbose", action="store_true", default=False, help="display extra debugging information")
    output_group.add_argument("-C", "--curl", action="store_true", default=False,  help="show recommended curl commands")
    output_group.add_argument("-n", "--no-color", action="store_true", dest="no_color", default=False,help="disable log colorization")
    
    attack_group.add_argument("-si", "--spoof-ip", metavar="", dest="spoofing_ips", action="append", default=[], help="add a custom ip (ip spoofing attack)")
    attack_group.add_argument("-sh", "--spoof-header", metavar="", dest="spoofing_headers", action="append", default=[], help="add a custom header (ip spoofing attack)")
    attack_group.add_argument("-vm", "--vt-method", metavar="", dest="vt_methods", action="append", default=[], help="add a custom method (verb tampering attack)")
    attack_group.add_argument("-vh", "--vt-header", metavar="", dest="vt_headers", action="append", default=[], help="add a custom header (verb tampering attack)")
    attack_group.add_argument("-va", "--vt-argument", metavar="", dest="vt_arguments", action="append", default=[], help="add a custom argument (verb tampering attack)")
    attack_group.add_argument("-c", "--custom", action="store_true", default=False, help="only test custom data")
    attack_group.add_argument("-l", "--light", action="store_true", default=False, help="only test custom data and small subsets of default wordlists")
    attack_group.add_argument("-V", "--variations", action="store_true", dest="case_variations", default=False, help="test case variations")

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
