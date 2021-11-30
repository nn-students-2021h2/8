import requests

try:
    from namespace_get_time.pretty_print_package import pretty_print_module
    is_imported_pretty_time = True
except ImportError as e:
    is_imported_pretty_time = False


def get_time():
    url = 'http://worldtimeapi.org/api/timezone/Europe/Moscow'
    resp = requests.get(url)
    unixtime = resp.json()['unixtime']
    if is_imported_pretty_time:
        return pretty_print_module.pretty_print(unixtime)
    else:
        return unixtime


def print_time(unixtime):
    print(unixtime)


def main():
    unixtime = get_time()
    print_time(unixtime)


if __name__ == '__main__':
    main()
