class Solution:
    def completePrime(self, num: int) -> bool:
        if num == 1 or num == 2:
            return False
        is_prime = True
        num_str = str(num)
        nums_list = list()
        for n in num_str:
            nums_list.append(int(n))
        nums_list.append(num)
        for i in nums_list:
            mid = i//2
            start = 2
            if i == 1 :
                return False
            while start<=mid:                   
                if i%start==0:
                    is_prime = False
                    return is_prime
                start= start+1
        return is_prime

print(Solution().completePrime(257))