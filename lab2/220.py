n = int(input())
d = {}

for _ in range(n):
    cmd = input().split()

    if cmd[0] == "set":
        k, v = cmd[1], cmd[2]
        d[k] = v
    elif cmd[0] == "get":
        k = cmd[1]
        if k in d:
            print(d[k])
        else:
            print("KE: no key", k, "found in the document")


    