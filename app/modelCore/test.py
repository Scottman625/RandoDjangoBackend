for i in range(200):
        string = str(i)
        phone = '0910000000'
        p = phone[:-len(string)] + string
        print(p)