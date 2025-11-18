"""
Chương trình chính để chạy demo và chế độ tương tác
"""
from models.warehouse_environment import WarehouseEnvironment
from models.algorithms import BinPackingAlgorithms

def run_demo():
    """Chạy demo các thuật toán"""
    print("=" * 70)
    print("BIN PACKING PROBLEM - QUẢN LÝ KHO VÀ TỐI ƯU HÓA LƯU TRỮ")
    print("=" * 70)
    
    # Tạo môi trường
    bin_capacity = 100
    env = WarehouseEnvironment(bin_capacity=bin_capacity)
    
    print(f"\nSức chứa mỗi thùng: {bin_capacity}")
    
    # Thêm các món hàng
    sizes = [50, 40, 30, 30, 25, 25, 20, 15, 15, 10, 10, 10, 5, 5]
    env.add_items_batch(sizes)
    
    print(f"Số lượng món hàng: {len(env.items)}")
    print(f"Kích thước các món hàng: {[item.size for item in env.items]}")
    print(f"Tổng kích thước: {sum(sizes)}")
    print(f"Số bins tối thiểu lý thuyết: {(sum(sizes) + bin_capacity - 1) // bin_capacity}")
    
    algorithms = [
        ("First Fit (Tham lam)", BinPackingAlgorithms.first_fit),
        ("Best Fit (Tham lam)", BinPackingAlgorithms.best_fit),
        ("First Fit Decreasing", BinPackingAlgorithms.first_fit_decreasing),
        ("Knapsack-based (Quy hoạch động)", BinPackingAlgorithms.knapsack_based),
        ("Branch and Bound (Nhánh cận)", BinPackingAlgorithms.branch_and_bound),
    ]
    
    results = []
    
    for name, algorithm in algorithms:
        print(f"\n\n{'='*70}")
        print(f"THUẬT TOÁN: {name}")
        print(f"{'='*70}")
        
        try:
            bins, num_bins = algorithm(env)
            env.print_solution(title=f"Kết quả {name}")
            results.append((name, num_bins, env.get_statistics()['avg_utilization']))
        except Exception as e:
            print(f"Lỗi: {e}")
    
    # So sánh kết quả
    print("\n\n" + "="*70)
    print("SO SÁNH CÁC THUẬT TOÁN")
    print("="*70)
    print(f"{'Thuật toán':<40} {'Số bins':<12} {'Tỷ lệ sử dụng'}")
    print("-"*70)
    for name, num_bins, util in results:
        print(f"{name:<40} {num_bins:<12} {util*100:.2f}%")
    print("="*70)


def interactive_mode():
    """Chế độ tương tác để người dùng tự nhập dữ liệu"""
    
    print("\n" + "="*70)
    print("CHẾ ĐỘ TƯƠNG TÁC - BIN PACKING PROBLEM")
    print("="*70)
    
    try:
        bin_capacity = int(input("\nNhập sức chứa của mỗi thùng: "))
        num_items = int(input("Nhập số lượng món hàng: "))
        
        env = WarehouseEnvironment(bin_capacity=bin_capacity)
        
        print(f"\nNhập kích thước {num_items} món hàng:")
        for i in range(num_items):
            while True:
                try:
                    size = int(input(f"  Item {i+1}: "))
                    env.add_item(size)
                    break
                except ValueError as e:
                    print(f"  Lỗi: {e}. Vui lòng nhập lại.")
        
        print("\nChọn thuật toán:")
        print("1. First Fit")
        print("2. Best Fit")
        print("3. First Fit Decreasing")
        print("4. Knapsack-based")
        print("5. Branch and Bound")
        print("6. Chạy tất cả")
        
        choice = input("Lựa chọn (1-6): ")
        
        algorithms = {
            '1': ("First Fit", BinPackingAlgorithms.first_fit),
            '2': ("Best Fit", BinPackingAlgorithms.best_fit),
            '3': ("First Fit Decreasing", BinPackingAlgorithms.first_fit_decreasing),
            '4': ("Knapsack-based", BinPackingAlgorithms.knapsack_based),
            '5': ("Branch and Bound", BinPackingAlgorithms.branch_and_bound),
        }
        
        if choice == '6':
            for name, algo in algorithms.values():
                print(f"\n{'='*70}")
                print(f"THUẬT TOÁN: {name}")
                bins, num_bins = algo(env)
                env.print_solution()
        elif choice in algorithms:
            name, algo = algorithms[choice]
            print(f"\n{'='*70}")
            print(f"THUẬT TOÁN: {name}")
            bins, num_bins = algo(env)
            env.print_solution()
        else:
            print("Lựa chọn không hợp lệ!")
            
    except Exception as e:
        print(f"Lỗi: {e}")


if __name__ == "__main__":
    # Chạy demo
    run_demo()
    
    # Hoặc chạy chế độ tương tác
    # interactive_mode()