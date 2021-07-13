def find(key, data, ch='multi'):
    # print'called')
    global count
    global item

    def best_key(l, ch):
        global d_key1
        lst = list(l.values())
        lst.sort(reverse=True)
        l1 = []
        for j in range(len(l)):
            for key in l:
                if lst[0] != 0:
                    if l[key] == lst[j] and lst[j] / lst[0] > 0.5:
                        if key not in l1:
                            l1.append(key)
        l = l1
        return l

    # ----------------------------xxxx-----------------------------------------------------------

    def find2(key, small, ch='multi'):

        if ch == 'reverse':

            d_key1 = item[::-1]
            key1 = key[::-1]
        else:

            d_key1 = item
            key1 = key

        count = 0
        for j in range(len(small)):
            char = d_key1[j]
            val = ord(char)
            if key1[j] in 'qwertyuiopasdfghjklzxcvbnm':
                if key1[j] == d_key1[j] or key1[j] == chr(val + 32):
                    count += 1

            elif key1[j] in 'QWERTYUIOPASDFGHJKLZXCVBNM':
                if key1[j] == d_key1[j] or key1[j] == chr(val - 32):
                    count += 1

            else:
                if key1[j] == d_key1[j]:
                    count += 1
        return count + .1  # To give this method higher priority as it checks letter from beginning and end.

    # ------------------------xxx-------------------------------------------
    def replace(string):
        s = ''
        for i in string:
            if i != ' ':
                s = s + i
        return s

    # --------------------------------------------------------------

    try:
        global l
        l = {}
        for d in data:
            for item in d:

                if key == item:
                    return [key]

                '''1st finding method'''
                if ' ' in item:
                    eff_dict_item = replace(item)
                else:
                    eff_dict_item = item
                if ' ' in key:
                    eff_key = replace(key)
                else:
                    eff_key = key

                '''1st Check for no. of letters matching the key'''

                if (key in item or key in eff_dict_item) or eff_key in eff_dict_item:
                    if (len(key) >= len(eff_dict_item) / 2) or (len(key) >= len(item) / 2):
                        l[item] = len(key)  # Makes a list having occurrences of each letter

                    elif len(item) > 10 and len(key) >= 3:
                        l[item] = len(key)

        '''2nd finding method'''

        if ' ' in key:
            key = replace(key)

        for d in data:
            for item in d:
                if ' ' in item:
                    origin_item = item
                    item = replace(item)
                else:
                    origin_item = item

                if len(item) >= len(key):

                    count = find2(key, key)
                    count2 = find2(key, key, 'reverse')

                else:

                    count = find2(key, item)
                    count2 = find2(key, item, 'reverse')

                '''Replaces list if occurrence is more in 2nd find method'''
                if origin_item in l:
                    if l[origin_item] < count2 + count != 0:
                        l[origin_item] = count2 + count
                elif origin_item not in l and count2 + count != 0:
                    l[origin_item] = count2 + count

        res = best_key(l, ch)
        return res


    except NameError as e:
        return 'NOTHING HERE!'
