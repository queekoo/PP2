n=int(input())
nums=list(map(int,input().split()))


max_num = nums[0]

for x in nums:
    if x > max_num:
        max_num = x

print(max_num)
