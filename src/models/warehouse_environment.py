"""
Môi trường quản lý kho cho bài toán Bin Packing
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Item:
    """Đại diện cho một món hàng"""
    id: int
    size: int
    name: str = ""
    
    def __repr__(self):
        return f"Item({self.id}, size={self.size})"


class Bin:
    """Đại diện cho một thùng/kho"""
    def __init__(self, capacity: int, bin_id: int = 0):
        self.capacity = capacity
        self.bin_id = bin_id
        self.items: List[Item] = []
        self.remaining = capacity
    
    def can_fit(self, item: Item) -> bool:
        """Kiểm tra có thể thêm item vào bin không"""
        return self.remaining >= item.size
    
    def add_item(self, item: Item) -> bool:
        """Thêm item vào bin"""
        if self.can_fit(item):
            self.items.append(item)
            self.remaining -= item.size
            return True
        return False
    
    def remove_item(self, item: Item) -> bool:
        """Xóa item khỏi bin"""
        if item in self.items:
            self.items.remove(item)
            self.remaining += item.size
            return True
        return False
    
    def get_utilization(self) -> float:
        """Tính tỷ lệ sử dụng của bin"""
        return (self.capacity - self.remaining) / self.capacity if self.capacity > 0 else 0
    
    def __repr__(self):
        return f"Bin{self.bin_id}(used={self.capacity-self.remaining}/{self.capacity}, items={len(self.items)})"


class WarehouseEnvironment:
    """Môi trường quản lý kho hàng"""
    
    def __init__(self, bin_capacity: int):
        self.bin_capacity = bin_capacity
        self.items: List[Item] = []
        self.bins: List[Bin] = []
        self.next_item_id = 0
        self.next_bin_id = 0
    
    def add_item(self, size: int, name: str = "") -> Item:
        """Thêm một món hàng vào danh sách"""
        if size <= 0:
            raise ValueError("Kích thước phải > 0")
        if size > self.bin_capacity:
            raise ValueError(f"Kích thước {size} vượt quá sức chứa thùng {self.bin_capacity}")
        
        item = Item(id=self.next_item_id, size=size, name=name or f"Item{self.next_item_id}")
        self.items.append(item)
        self.next_item_id += 1
        return item
    
    def add_items_batch(self, sizes: List[int]):
        """Thêm nhiều món hàng cùng lúc"""
        for size in sizes:
            self.add_item(size)
    
    def reset(self):
        """Reset lại môi trường (xóa tất cả bins)"""
        self.bins = []
        self.next_bin_id = 0
    
    def create_bin(self) -> Bin:
        """Tạo một bin mới"""
        bin_obj = Bin(capacity=self.bin_capacity, bin_id=self.next_bin_id)
        self.bins.append(bin_obj)
        self.next_bin_id += 1
        return bin_obj
    
    def get_total_bins(self) -> int:
        """Lấy tổng số bins đã sử dụng"""
        return len(self.bins)
    
    def get_statistics(self) -> Dict:
        """Thống kê về việc sắp xếp"""
        if not self.bins:
            return {
                'total_bins': 0,
                'total_items': len(self.items),
                'avg_utilization': 0,
                'total_waste': 0
            }
        
        total_used = sum(bin.capacity - bin.remaining for bin in self.bins)
        total_capacity = len(self.bins) * self.bin_capacity
        avg_util = total_used / total_capacity if total_capacity > 0 else 0
        
        return {
            'total_bins': len(self.bins),
            'total_items': len(self.items),
            'avg_utilization': avg_util,
            'total_waste': total_capacity - total_used,
            'bin_details': [(f"Bin{b.bin_id}", b.get_utilization()) for b in self.bins]
        }
    
    def print_solution(self, title: str = "Giải pháp"):
        """In ra giải pháp"""
        print(f"\n{'='*60}")
        print(f"{title}")
        print(f"{'='*60}")
        
        if not self.bins:
            print("Chưa có bins nào được sử dụng.")
            return
        
        for bin in self.bins:
            used = bin.capacity - bin.remaining
            util = bin.get_utilization() * 100
            print(f"\n{bin} - Sử dụng: {util:.1f}%")
            if bin.items:
                items_str = ", ".join([f"{item.name}({item.size})" for item in bin.items])
                print(f"  Items: {items_str}")
        
        stats = self.get_statistics()
        print(f"\n{'='*60}")
        print(f"Tổng số bins: {stats['total_bins']}")
        print(f"Tổng số items: {stats['total_items']}")
        print(f"Tỷ lệ sử dụng trung bình: {stats['avg_utilization']*100:.2f}%")
        print(f"Tổng không gian lãng phí: {stats['total_waste']}")
        print(f"{'='*60}\n")

