---
title: LeetCode高频题解
tags: [学习路径]
category: 学习路径
created: 2026-08-27
updated: 2026-08-27
difficulty: ⭐⭐
status: ✅ 内容已完善
priority: 一般
pre: []
aliases: [LeetCode高频题解]
---

# LeetCode 高频题解

> **文档说明**：按题型分类的高频面试题，每题含思路分析和代码实现。配合[[算法刷题指南与题型模板]]使用。

---

## 一、数组/双指针

### 1. 两数之和（LeetCode 1）
**思路**：哈希表，遍历数组时检查target-nums[i]是否在哈希表中。
```python
def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i
```
时间O(n)，空间O(n)

### 2. 三数之和（LeetCode 15）
**思路**：排序+双指针，固定一个数，左右指针找另外两个。
```python
def threeSum(nums):
    nums.sort()
    result = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]: continue
        l, r = i + 1, len(nums) - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0: l += 1
            elif s > 0: r -= 1
            else:
                result.append([nums[i], nums[l], nums[r]])
                while l < r and nums[l] == nums[l+1]: l += 1
                while l < r and nums[r] == nums[r-1]: r -= 1
                l += 1; r -= 1
    return result
```

### 3. 移动零（LeetCode 283）
**思路**：双指针，慢指针指向非零位置，快指针遍历。
```python
def moveZeroes(nums):
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1
```

### 4. 盛最多水的容器（LeetCode 11）
**思路**：双指针从两端向中间，每次移动较短的一边。
```python
def maxArea(height):
    l, r, ans = 0, len(height) - 1, 0
    while l < r:
        ans = max(ans, min(height[l], height[r]) * (r - l))
        if height[l] < height[r]: l += 1
        else: r -= 1
    return ans
```

---

## 二、滑动窗口

### 5. 无重复字符的最长子串（LeetCode 3）
**思路**：滑动窗口+哈希表记录字符最后出现位置。
```python
def lengthOfLongestSubstring(s):
    seen = {}
    left = ans = 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1
        seen[ch] = right
        ans = max(ans, right - left + 1)
    return ans
```

### 6. 最小覆盖子串（LeetCode 76）
**思路**：滑动窗口，先扩大窗口包含所有字符，再缩小窗口。
```python
def minWindow(s, t):
    from collections import Counter
    need = Counter(t)
    missing = len(t)
    left = start = end = 0
    for right, ch in enumerate(s, 1):
        if need[ch] > 0: missing -= 1
        need[ch] -= 1
        if missing == 0:
            while left < right and need[s[left]] < 0:
                need[s[left]] += 1
                left += 1
            if end == 0 or right - left < end - start:
                start, end = left, right
    return s[start:end]
```

---

## 三、链表

### 7. 反转链表（LeetCode 206）
**思路**：迭代，三个指针prev/curr/next。
```python
def reverseList(head):
    prev = None
    curr = head
    while curr:
        next_node = curr.next
        curr.next = prev
        prev = curr
        curr = next_node
    return prev
```

### 8. 环形链表（LeetCode 141）
**思路**：快慢指针，相遇则有环。
```python
def hasCycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast: return True
    return False
```

### 9. 合并两个有序链表（LeetCode 21）
**思路**：虚拟头节点，比较两个链表节点值。
```python
def mergeTwoLists(l1, l2):
    dummy = ListNode(0)
    curr = dummy
    while l1 and l2:
        if l1.val < l2.val:
            curr.next = l1; l1 = l1.next
        else:
            curr.next = l2; l2 = l2.next
        curr = curr.next
    curr.next = l1 or l2
    return dummy.next
```

### 10. 链表倒数第N个节点（LeetCode 19）
**思路**：快慢指针，快指针先走N步。
```python
def removeNthFromEnd(head, n):
    dummy = ListNode(0, head)
    slow = fast = dummy
    for _ in range(n): fast = fast.next
    while fast.next:
        slow = slow.next
        fast = fast.next
    slow.next = slow.next.next
    return dummy.next
```

---

## 四、二叉树

### 11. 二叉树最大深度（LeetCode 104）
**思路**：递归，max(左子树深度, 右子树深度) + 1。
```python
def maxDepth(root):
    if not root: return 0
    return max(maxDepth(root.left), maxDepth(root.right)) + 1
```

### 12. 翻转二叉树（LeetCode 226）
**思路**：递归交换左右子树。
```python
def invertTree(root):
    if root:
        root.left, root.right = root.right, root.left
        invertTree(root.left)
        invertTree(root.right)
    return root
```

### 13. 层序遍历（LeetCode 102）
**思路**：BFS队列，逐层处理。
```python
from collections import deque
def levelOrder(root):
    if not root: return []
    queue, result = deque([root]), []
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left: queue.append(node.left)
            if node.right: queue.append(node.right)
        result.append(level)
    return result
```

### 14. 最近公共祖先（LeetCode 236）
**思路**：递归，左右子树分别找p和q。
```python
def lowestCommonAncestor(root, p, q):
    if not root or root == p or root == q: return root
    left = lowestCommonAncestor(root.left, p, q)
    right = lowestCommonAncestor(root.right, p, q)
    if left and right: return root
    return left or right
```

---

## 五、动态规划

### 15. 爬楼梯（LeetCode 70）
**思路**：DP，dp[i] = dp[i-1] + dp[i-2]。
```python
def climbStairs(n):
    if n <= 2: return n
    prev2, prev1 = 1, 2
    for _ in range(3, n + 1):
        prev2, prev1 = prev1, prev1 + prev2
    return prev1
```

### 16. 最大子数组和（LeetCode 53）
**思路**：DP，dp[i] = max(dp[i-1]+nums[i], nums[i])。
```python
def maxSubArray(nums):
    curr = ans = nums[0]
    for num in nums[1:]:
        curr = max(num, curr + num)
        ans = max(ans, curr)
    return ans
```

### 17. 零钱兑换（LeetCode 322）
**思路**：完全背包，dp[i] = min(dp[i-coin]+1)。
```python
def coinChange(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1
```

### 18. 最长递增子序列（LeetCode 300）
**思路**：DP，dp[i] = max(dp[j]+1) for j<i and nums[j]<nums[i]。
```python
def lengthOfLIS(nums):
    dp = [1] * len(nums)
    for i in range(1, len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

---

## 六、栈/队列

### 19. 有效的括号（LeetCode 20）
**思路**：栈，左括号入栈，右括号匹配出栈。
```python
def isValid(s):
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    for ch in s:
        if ch in mapping:
            if not stack or stack.pop() != mapping[ch]:
                return False
        else:
            stack.append(ch)
    return not stack
```

### 20. 每日温度（LeetCode 739）
**思路**：单调栈，存索引，温度高时出栈计算。
```python
def dailyTemperatures(temperatures):
    n = len(temperatures)
    result = [0] * n
    stack = []
    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev = stack.pop()
            result[prev] = i - prev
        stack.append(i)
    return result
```

---

## 七、二分查找

### 21. 搜索插入位置（LeetCode 35）
**思路**：标准二分，返回left即插入位置。
```python
def searchInsert(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target: return mid
        elif nums[mid] < target: left = mid + 1
        else: right = mid - 1
    return left
```

### 22. 搜索旋转排序数组（LeetCode 33）
**思路**：二分，判断哪一半有序，再判断target在哪一半。
```python
def search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left + right) // 2
        if nums[mid] == target: return mid
        if nums[left] <= nums[mid]:  # 左半有序
            if nums[left] <= target < nums[mid]: right = mid - 1
            else: left = mid + 1
        else:  # 右半有序
            if nums[mid] < target <= nums[right]: left = mid + 1
            else: right = mid - 1
    return -1
```

---

## 八、回溯

### 23. 全排列（LeetCode 46）
**思路**：回溯，used数组标记已使用元素。
```python
def permute(nums):
    result = []
    def backtrack(path, used):
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]: continue
            used[i] = True
            path.append(nums[i])
            backtrack(path, used)
            path.pop()
            used[i] = False
    backtrack([], [False] * len(nums))
    return result
```

### 24. 子集（LeetCode 78）
**思路**：回溯，每个元素选或不选。
```python
def subsets(nums):
    result = []
    def backtrack(start, path):
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()
    backtrack(0, [])
    return result
```

---

## 关联笔记
[[算法刷题指南与题型模板]] · [[排序算法全景对比]] · [[动态规划与贪心]] · [[树与二叉树核心]]

> 💡 **刷题建议**：先理解模板，再按题型刷。每题先想5分钟思路，写不出来就看题解，理解后自己写一遍。
