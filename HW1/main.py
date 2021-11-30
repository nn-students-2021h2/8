def all_eq(lst):
    if type(lst) != list or any(type(lst[i]) != str for i in range(len(lst))):
        print('Error! Argument is not "list" or elements of list are not strings.\nEmpty list was returned.\n')
        return []
    max_len = max(len(el) for el in lst)
    res = []
    for el in lst:
        res.append(el + '_'*(max_len-len(el)))
    return res
