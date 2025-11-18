"""
Các thuật toán giải bài toán Bin Packing
"""

from typing import List, Tuple
import copy
from .warehouse_environment import Bin, Item


class BinPackingAlgorithms:
    """Các thuật toán giải bài toán Bin Packing"""
    
    @staticmethod
    def first_fit(env) -> Tuple[List, int]:
        """
        Thuật toán First Fit (Tham lam):
        Với mỗi item, tìm bin đầu tiên có thể chứa nó.
        Nếu không có bin nào, tạo bin mới.
        """
        env.reset()
        
        for item in env.items:
            placed = False
            for bin in env.bins:
                if bin.add_item(item):
                    placed = True
                    break
            
            if not placed:
                new_bin = env.create_bin()
                new_bin.add_item(item)
        
        return env.bins, len(env.bins)
    
    @staticmethod
    def best_fit(env) -> Tuple[List, int]:
        """
        Thuật toán Best Fit (Tham lam):
        Với mỗi item, tìm bin có không gian còn lại nhỏ nhất
        nhưng vẫn đủ để chứa item.
        """
        env.reset()
        
        for item in env.items:
            best_bin = None
            min_remaining = float('inf')
            
            for bin in env.bins:
                if bin.can_fit(item) and bin.remaining < min_remaining:
                    best_bin = bin
                    min_remaining = bin.remaining
            
            if best_bin:
                best_bin.add_item(item)
            else:
                new_bin = env.create_bin()
                new_bin.add_item(item)
        
        return env.bins, len(env.bins)
    
    @staticmethod
    def first_fit_decreasing(env) -> Tuple[List, int]:
        """
        Thuật toán First Fit Decreasing:
        Sắp xếp items theo thứ tự giảm dần rồi áp dụng First Fit.
        FFD thường cho kết quả tốt hơn First Fit thông thường.
        """
        def bubble_sort(items: List):
            for i in range(len(items)):
                for j in range(0, len(items)-i-1):
                    if items[j].size < items[j+1].size:
                        items[j], items[j+1] = items[j+1], items[j]
        env.reset()
        bubble_sort(env.items)
        return BinPackingAlgorithms.first_fit(env)
    
    @staticmethod
    def knapsack_based(env) -> Tuple[List, int]:
        """
        Thuật toán dựa trên Knapsack (Quy hoạch động):
        Chiến lược: Lấp đầy từng thùng một sao cho thùng đó đầy nhất có thể (Item-Oriented).
        Đây là cách tiếp cận tham lam trên từng thùng.
        """
        env.reset()
        items_to_pack = env.items[:]
        while items_to_pack:
            new_bin = env.create_bin()
            capacity = new_bin.capacity 
            chosen_items = BinPackingAlgorithms._solve_knapsack(items_to_pack, capacity)            
            for item in chosen_items:
                new_bin.add_item(item)
                items_to_pack.remove(item)
                
        return env.bins, len(env.bins)
    
    @staticmethod
    def _solve_knapsack(items: List[Item], capacity: int) -> List[Item]:
        """
        Giải bài toán Knapsack 0/1:
        Tìm tập con các items có tổng kích thước <= capacity và lớn nhất có thể.
        Ở đây: Value của item chính là Size của nó (để lấp đầy khoảng trống).
        """
        n = len(items)
        K = [[0 for x in range(capacity + 1)] for x in range(n + 1)]
  
        for i in range(n + 1):
            for w in range(capacity + 1):
                if i == 0 or w == 0:
                    K[i][w] = 0
                elif items[i-1].size <= w:
                    K[i][w] = max(items[i-1].size + K[i-1][w-items[i-1].size], K[i-1][w])
                else:
                    K[i][w] = K[i-1][w]
  
        res = K[n][capacity]
        w = capacity
        chosen_items = []
        
        for i in range(n, 0, -1):
            if res <= 0:
                break
            if res == K[i-1][w]:
                continue
            else:
                chosen_items.append(items[i-1])
                res = res - items[i-1].size
                w = w - items[i-1].size
                
        return chosen_items
    
    @staticmethod
    def branch_and_bound(env, max_bins: int = None) -> Tuple[List, int]:
        """
        Thuật toán Nhánh và Cận (Branch and Bound):
        Tìm kiếm giải pháp tối ưu bằng cách duyệt cây quyết định
        và cắt tỉa các nhánh không khả thi.
        """
        env.reset()
        items = env.items
        # Sắp xếp giảm dần để tối ưu quá trình duyệt
        sorted_items = sorted(items, key=lambda x: x.size, reverse=True)
        
        best_min_bins = len(items) + 1
        best_allocation = []
        
        current_bins_remaining = []
        current_allocation = []
        
        def backtrack(index):
            nonlocal best_min_bins, best_allocation
            
            # Điều kiện dừng
            if index == len(sorted_items):
                num_bins = len(current_bins_remaining)
                if num_bins < best_min_bins:
                    best_min_bins = num_bins
                    best_allocation = copy.deepcopy(current_allocation)
                return

            item = sorted_items[index]
            
            # Cắt tỉa (Pruning)
            if len(current_bins_remaining) >= best_min_bins:
                return
            
            # Cắt tỉa bổ sung: Lower Bound
            remaining_size = sum(i.size for i in sorted_items[index:])
            min_additional_bins = (remaining_size + env.bin_capacity - 1) // env.bin_capacity
            if len(current_bins_remaining) + min_additional_bins >= best_min_bins:
                return

            # Thử đặt vào các thùng hiện có
            for i in range(len(current_bins_remaining)):
                if current_bins_remaining[i] >= item.size:
                    current_bins_remaining[i] -= item.size
                    current_allocation[i].append(item)
                    
                    backtrack(index + 1)
                    
                    current_allocation[i].pop()
                    current_bins_remaining[i] += item.size
            
            # Thử đặt vào thùng mới
            if len(current_bins_remaining) + 1 < best_min_bins:
                current_bins_remaining.append(env.bin_capacity - item.size)
                current_allocation.append([item])
                
                backtrack(index + 1)
                
                current_allocation.pop()
                current_bins_remaining.pop()

        backtrack(0)
        
        env.reset()
        if best_allocation:
            for bin_items in best_allocation:
                new_bin = env.create_bin()
                for item in bin_items:
                    new_bin.add_item(item)
                    
        return env.bins, len(env.bins)
