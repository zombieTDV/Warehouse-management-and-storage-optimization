import pytest
from models.warehouse_environment import Item, Bin, WarehouseEnvironment

def test_bin_add_remove_and_utilization():
    b = Bin(capacity=100, bin_id=0)
    item = Item(id=0, size=30, name="A")
    assert b.can_fit(item) is True
    assert b.add_item(item) is True
    assert b.remaining == 70
    assert pytest.approx(b.get_utilization(), rel=1e-9) == 0.30  # 30/100
    # Removing
    assert b.remove_item(item) is True
    assert b.remaining == 100
    # Can't add an item too large
    big = Item(id=1, size=200, name="big")
    assert b.can_fit(big) is False
    assert b.add_item(big) is False

def test_add_item_validations():
    env = WarehouseEnvironment(bin_capacity=100)
    # size <= 0 should raise
    with pytest.raises(ValueError):
        env.add_item(0)
    with pytest.raises(ValueError):
        env.add_item(-5)
    # size > capacity should raise
    with pytest.raises(ValueError):
        env.add_item(101)

def test_add_items_batch_create_bins_and_statistics():
    env = WarehouseEnvironment(bin_capacity=100)
    env.add_items_batch([50, 50, 30])
    assert len(env.items) == 3

    # initially no bins
    stats_empty = env.get_statistics()
    assert stats_empty['total_bins'] == 0
    assert stats_empty['avg_utilization'] == 0

    # create two bins and distribute items manually
    b0 = env.create_bin()
    b1 = env.create_bin()
    # add first two items to bin0, third item to bin1
    assert b0.add_item(env.items[0]) is True  # 50
    assert b0.add_item(env.items[1]) is True  # 50 => full
    assert b1.add_item(env.items[2]) is True  # 30

    stats = env.get_statistics()
    assert stats['total_bins'] == 2
    assert stats['total_items'] == 3
    # total used = 50+50+30 = 130, total capacity = 2*100 = 200
    assert pytest.approx(stats['avg_utilization'], rel=1e-9) == 130 / 200
    # waste = 200 - 130 = 70
    assert stats['total_waste'] == 70

def test_reset_clears_bins_but_keeps_items():
    env = WarehouseEnvironment(bin_capacity=100)
    env.add_items_batch([10, 20])
    env.create_bin()
    assert env.get_total_bins() == 1
    env.reset()
    assert env.get_total_bins() == 0
    # Items should remain in the env.items list
    assert len(env.items) == 2

def test_print_solution_outputs(capsys):
    env = WarehouseEnvironment(bin_capacity=100)
    env.add_items_batch([40, 60])
    b = env.create_bin()
    # add both items to the same bin so it becomes full
    assert b.add_item(env.items[0]) is True
    assert b.add_item(env.items[1]) is True

    # Capture stdout from print_solution
    env.print_solution(title="Test Solution")
    captured = capsys.readouterr()
    out = captured.out

    # Basic assertions on printed content (Vietnamese strings present in implementation)
    assert "Test Solution" in out
    assert "Tổng số bins" in out
    assert "Tổng số items" in out
    assert "Bin0" in out or "Bin0(" in out
    # Check numeric summary
    assert "Tổng số bins: 1" in out

