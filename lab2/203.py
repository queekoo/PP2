n = int(input())
numbers = list(map(int, input().split()))

total = 0
i = 0  

while i < n:
    total += numbers[i]
    i += 1  

print(total)
