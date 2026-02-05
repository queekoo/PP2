n = int(input())
a = list(map(int, input().split()))

used = []

for x in a:
    if x in used:
        print("NO")
    else:
        print("YES")
        used.append(x)
