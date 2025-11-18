"""
Các thuật toán giải bài toán Bin Packing
"""

from typing import List, Tuple

from .warehouse_environment import Bin


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
            # Thử đặt vào bin hiện có
            for bin in env.bins:
                if bin.add_item(item):
                    placed = True
                    break
            
            # Nếu không đặt được, tạo bin mới
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
            
            # Tìm bin tốt nhất (còn ít không gian nhất nhưng vẫn đủ)
            for bin in env.bins:
                if bin.can_fit(item) and bin.remaining < min_remaining:
                    best_bin = bin
                    min_remaining = bin.remaining
            
            if best_bin:
                best_bin.add_item(item)
            else:
                # Tạo bin mới nếu không có bin nào phù hợp
                new_bin = env.create_bin()
                new_bin.add_item(item)
        
        return env.bins, len(env.bins)
    
    @staticmethod
    def first_fit_decreasing(env) -> Tuple[List, int]:
        """"Thuật toán First Fit Decreasing:
        Sắp xếp items theo thứ tự giảm dần rồi áp dụng First Fit"""
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
        """Thuật toán dựa trên Knapsack (Quy hoạch động):"""
        pass
    
    @staticmethod
    def _solve_knapsack(items: List, capacity: int) -> List:
        """"Giải bài toán knapsack 0/1 bằng quy hoạch động"""
        pass
    
    @staticmethod
    def branch_and_bound(env, max_bins: int = None) -> Tuple[List, int]:
        """
        Thuật toán Nhánh và Cận (Branch and Bound):
        Tìm kiếm giải pháp tối ưu bằng cách duyệt cây quyết định
        và cắt tỉa các nhánh không khả thi.
        """