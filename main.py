import bot


def main():
    f = open('token.txt')  # create token.txt wint your token
    token = f.read()
    b = bot.Bot(token)
    b.work()


if __name__ == '__main__':
    main()
