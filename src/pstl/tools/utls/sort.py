def sort_list(list1,list2):
    list1,list2=(list(t) for t in zip(*sorted(zip(list1,list2))))
    return list1,list2
    
