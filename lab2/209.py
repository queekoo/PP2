n = int(input())
arr = list(map(int, input().split()))

max_val = max(arr)
min_val = min(arr)

for i in range(n):
    if arr[i] == max_val:
        arr[i] = min_val

for x in arr:
    print(x, end=" ")
