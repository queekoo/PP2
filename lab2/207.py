n=int(input())
nums=list(map(int,input().split()))


max_num = nums[0]
max_ind=0

for x in range(1,n):
    if x > max_num:
        max_num =nums[x]
        max_ind=x


print(x)