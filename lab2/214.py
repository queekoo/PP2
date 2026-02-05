n = int(input())
a = list(map(int, input().split()))

d = {}

for x in a:
    if x in d:
        d[x] += 1
    else:
        d[x] = 1

best = a[0]

for x in d:
    if d[x] > d[best] or (d[x] == d[best] and x < best):
        best = x

print(best)
