class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        checkinglist = {}
        max_length = 0
        start = 0

        for i in range(len(s)):
            if s[i] in checkinglist and checkinglist[s[i]] >= start:
                start = checkinglist[s[i]] + 1

        checkinglist[s[i]] = i

        max_length = max(max_length, i - start + 1)

        return max_length


def polyndrome(s):
    return s == s[::-1]


print(polyndrome('abba'))


value_to_roman = [
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I")
]