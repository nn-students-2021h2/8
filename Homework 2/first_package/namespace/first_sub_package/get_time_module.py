import requests


def get_time():
    url = 'http://worldtimeapi.org/api/timezone/Europe/Moscow'
    resp = requests.get(url)
    unixtime = resp.json()['unixtime']
    try:
        from namespace.second_sub_package import pretty_print_module

        return pretty_print_module.pretty_print(unixtime)

    except ImportError as e:
        print("Sorry")
        return unixtime


def print_time(unixtime):
    print(unixtime)


def main():
    unixtime = get_time()
    print_time(unixtime)


if __name__ == '__main__':
    main()
