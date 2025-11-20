"""
Chương trình chính: hỗ trợ chạy demo, chế độ tương tác,
và đọc/ghi file dữ liệu (input -> output) — thời gian chạy cho mỗi thuật toán.
"""

import argparse
import sys
import io
import time
from contextlib import redirect_stdout

from models.warehouse_environment import WarehouseEnvironment
from models.algorithms import BinPackingAlgorithms


def build_env_from_sizes(bin_capacity, sizes):
    """Khởi tạo WarehouseEnvironment và thêm batch items (list sizes)."""
    env = WarehouseEnvironment(bin_capacity=bin_capacity)
    env.add_items_batch(sizes)
    return env


def read_input_file(path):
    """
    Đọc file input.
    Định dạng hỗ trợ (linh hoạt):
      - Dòng đầu: bin_capacity (int)
      - Các dòng sau: kích thước items (mỗi dòng 1 số) hoặc 1 dòng nhiều số cách nhau khoảng trắng
      - Dòng bắt đầu bằng '#' sẽ bị coi là comment và bỏ qua
    Trả về: (bin_capacity: int, sizes: list[int])
    """
    sizes = []
    bin_capacity = None
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if bin_capacity is None:
                # first non-empty, non-comment line => capacity
                try:
                    bin_capacity = int(line.split()[0])
                except ValueError:
                    raise ValueError(f"Dòng đầu file input phải là số nguyên (sức chứa). Dòng: {line}")
                # if there are more numbers on same line, treat them as sizes
                parts = line.split()[1:]
                for p in parts:
                    if p:
                        sizes.append(int(p))
            else:
                # parse sizes from following lines (space separated allowed)
                parts = line.split()
                for p in parts:
                    sizes.append(int(p))
    if bin_capacity is None:
        raise ValueError("File input rỗng hoặc không có thông tin sức chứa.")
    return bin_capacity, sizes


def write_output_file(output_path, header_text, summary_results, detail_texts):
    """
    Ghi kết quả ra file output.
    - header_text: tiêu đề / mô tả (str)
    - summary_results: list of tuples (name, num_bins, avg_util, runtime_seconds)
    - detail_texts: list of strings (chi tiết từng thuật toán) cùng thứ tự với summary_results
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header_text + "\n\n")
        f.write("=" * 100 + "\n")
        f.write("SO SÁNH CÁC THUẬT TOÁN\n")
        f.write("=" * 100 + "\n")
        f.write(f"{'Thuật toán':<36} {'Số bins':<10} {'Tỷ lệ sử dụng':<16} {'Thời gian (s)'}\n")
        f.write("-" * 100 + "\n")
        for name, num_bins, util, runtime in summary_results:
            runtime_str = f"{runtime:.3f}" if isinstance(runtime, (int, float)) else str(runtime)
            f.write(f"{name:<36} {num_bins:<10} {util*100:>6.2f}%{'':<9} {runtime_str}\n")
        f.write("=" * 100 + "\n\n")

        # Ghi chi tiết kết quả cho từng thuật toán
        for (name, _, _, runtime), detail in zip(summary_results, detail_texts):
            f.write("\n" + "#" * 100 + "\n")
            f.write(f"KẾT QUẢ THUẬT TOÁN: {name}\n")
            f.write(f"Thời gian chạy: {runtime:.6f} s\n")
            f.write("#" * 100 + "\n")
            f.write(detail + "\n")


def run_algorithms_and_capture(bin_capacity, sizes, algorithms):
    """
    Chạy từng thuật toán trên 1 bản sao môi trường (độc lập),
    thu thập kết quả summary và chi tiết (chuỗi).
    Trả về (summary_results, detail_texts)
    - summary_results: [(name, num_bins, avg_util, runtime_seconds), ...]
    - detail_texts: [string_output_of_env.print_solution(), ...]
    """
    summary_results = []
    detail_texts = []

    for name, algorithm in algorithms:
        start_time = time.perf_counter()
        try:
            # Tạo môi trường mới cho mỗi thuật toán để kết quả không bị chồng chéo
            env = build_env_from_sizes(bin_capacity, sizes)

            result = algorithm(env)

            # chuẩn hoá
            if isinstance(result, tuple) and len(result) >= 2:
                bins, num_bins = result[0], result[1]
            else:
                num_bins = int(result)

            stats = env.get_statistics() if hasattr(env, 'get_statistics') else {}
            avg_util = stats.get('avg_utilization', 0.0)

            # Capture stdout của env.print_solution() vào chuỗi
            buf = io.StringIO()
            with redirect_stdout(buf):
                try:
                    env.print_solution(title=f"Kết quả {name}")
                except TypeError:
                    env.print_solution()
            detail_output = buf.getvalue()

            end_time = time.perf_counter()
            runtime = end_time - start_time

            summary_results.append((name, num_bins, avg_util, runtime))
            detail_texts.append(detail_output)

        except Exception as e:
            end_time = time.perf_counter()
            runtime = end_time - start_time
            # nếu lỗi, vẫn ghi lại thông tin lỗi trong detail (vẫn ghi runtime)
            summary_results.append((name, float('inf'), 0.0, runtime))
            detail_texts.append(f"Lỗi khi chạy thuật toán {name}: {e}\nThời gian tính tới lỗi: {runtime:.6f} s")

    return summary_results, detail_texts


def run_demo():
    """Chạy demo mặc định (như trước) nhưng sử dụng hàm chung."""
    print("=" * 70)
    print("BIN PACKING PROBLEM - QUẢN LÝ KHO VÀ TỐI ƯU HÓA LƯU TRỮ")
    print("=" * 70)

    # dữ liệu mẫu
    bin_capacity = 100
    sizes = [50, 40, 30, 30, 25, 25, 20, 15, 15, 10, 10, 10, 5, 5]

    print(f"\nSức chứa mỗi thùng: {bin_capacity}")
    print(f"Số lượng món hàng: {len(sizes)}")
    print(f"Kích thước các món hàng: {sizes}")
    print(f"Tổng kích thước: {sum(sizes)}")
    print(f"Số bins tối thiểu lý thuyết: {(sum(sizes) + bin_capacity - 1) // bin_capacity}")

    algorithms = [
        ("First Fit (Tham lam)", BinPackingAlgorithms.first_fit),
        ("Best Fit (Tham lam)", BinPackingAlgorithms.best_fit),
        ("First Fit Decreasing", BinPackingAlgorithms.first_fit_decreasing),
        ("Knapsack-based (Quy hoạch động)", BinPackingAlgorithms.knapsack_based),
        ("Branch and Bound (Nhánh cận)", BinPackingAlgorithms.branch_and_bound),
    ]

    summary, details = run_algorithms_and_capture(bin_capacity, sizes, algorithms)

    # In bảng tóm tắt với thời gian
    print("\n\n" + "=" * 70)
    print("SO SÁNH CÁC THUẬT TOÁN")
    print("=" * 70)
    print(f"{'Thuật toán':<40} {'Số bins':<12} {'Tỷ lệ sử dụng':<16} {'Thời gian (s)'}")
    print("-" * 70)
    for name, num_bins, util, runtime in summary:
        if num_bins == float('inf'):
            nb_display = "Lỗi"
        else:
            nb_display = str(num_bins)
        print(f"{name:<40} {nb_display:<12} {util*100:>6.2f}%{'':<9} {runtime:.3f}")
    print("=" * 70)


def interactive_mode():
    """Chế độ tương tác (giữ nguyên logic cũ)."""
    print("\n" + "=" * 70)
    print("CHẾ ĐỘ TƯƠNG TÁC - BIN PACKING PROBLEM")
    print("=" * 70)

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


def run_from_files(input_path, output_path):
    """Đọc input_path, chạy tất cả thuật toán, ghi output_path."""
    bin_capacity, sizes = read_input_file(input_path)

    header = (
        "BIN PACKING - KẾT QUẢ CHẠY TỪ FILE\n"
        f"Input file: {input_path}\n"
        f"Sức chứa mỗi thùng: {bin_capacity}\n"
        f"Số lượng món hàng: {len(sizes)}\n"
        f"Kích thước món hàng: {sizes}\n"
    )

    algorithms = [
        ("First Fit (Tham lam)", BinPackingAlgorithms.first_fit),
        ("Best Fit (Tham lam)", BinPackingAlgorithms.best_fit),
        ("First Fit Decreasing", BinPackingAlgorithms.first_fit_decreasing),
        ("Knapsack-based (Quy hoạch động)", BinPackingAlgorithms.knapsack_based),
        ("Branch and Bound (Nhánh cận)", BinPackingAlgorithms.branch_and_bound),
    ]

    summary, details = run_algorithms_and_capture(bin_capacity, sizes, algorithms)

    write_output_file(output_path, header, summary, details)
    print(f"Kết quả đã ghi vào: {output_path}")


def parse_args_and_run():
    parser = argparse.ArgumentParser(description="Bin Packing demo with file I/O")
    parser.add_argument('--input', '-i', help="Đường dẫn file input (nếu có)")
    parser.add_argument('--output', '-o', help="Đường dẫn file output (nếu có)")
    parser.add_argument('--demo', action='store_true', help="Chạy demo mẫu (mặc định)")
    parser.add_argument('--interactive', action='store_true', help="Chạy chế độ tương tác")
    args = parser.parse_args()

    # ưu tiên interactive nếu có
    if args.interactive:
        interactive_mode()
        return

    if args.input:
        out = args.output if args.output else (args.input + ".out.txt")
        try:
            run_from_files(args.input, out)
        except Exception as e:
            print(f"Lỗi khi chạy từ file: {e}")
        return

    # default: run demo
    run_demo()


if __name__ == "__main__":
    parse_args_and_run()



#how to run:
#python3 main.py --input ./input_1.txt --output ./output_1.txt