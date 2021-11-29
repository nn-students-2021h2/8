from datetime import datetime


def all_eq(lst):
    try:
        maxLength = len(max(lst, key=len))
        return [word + '_' * (maxLength - len(word)) for word in lst]
    except TypeError:
        # *Logging*
        currentTime = datetime.now().time()
        print(f"{currentTime} - an exception in function 'all_eq(lst)': incorrect element type")
        return None
    except ValueError:
        currentTime = datetime.now().time()
        print(f"{currentTime} - an exception in function 'all_eq(lst)': arg is an empty sequence")
        return None


def test():
    lst1 = ["Hello", "Programming", "School", "2021", "Python", "!"]
    lst2 = [1, 2, 3]
    lst3 = []
    lst4 = ['']
    lst5 = ["Hello", ["World!"]]

    if result := all_eq(lst1):  # Now we can test the function ourselves
        print(result)

    if result := all_eq(lst2):
        print(result)

    if result := all_eq(lst3):
        print(result)

    if result := all_eq(lst4):
        print(result)

    if result := all_eq(lst5):
        print(result)


def main():
    test()


main()
