n = int(input())

d = {}

for i in range(n):
    num = input()
    if num in d:
        d[num] += 1
    else:
        d[num] = 1

count = 0
for x in d:
    if d[x] == 3:
        count += 1

print(count)
