
n = int(input())
nums = list(map(int, input().split()))

count = 0
for x in nums:
    if x > 0:      
        count += 1  

print(count)
        
