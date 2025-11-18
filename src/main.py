from models.Storage import Storage

def main():
    items = [4, 8, 1.5, 3, 2]
    S = Storage(items, bin_capacity=10.0)
    # place item 0 into a new bin (bin_index omitted)
    b0 = S.move(0)          # creates bin 0 and places item 0 (size 4)
    b1 = S.move(1)          # creates bin 1 and places item 1 (size 8)
    S.move(2, bin_index=0)  # place item 2 (1.5) into bin 0 (fits)
    print(S.bins_loads())   # [5.5, 8.0]
    S.undo_move()           # removes item 2
    print(S.assignment)     # item 2 unplaced

    

if __name__ == "__main__":
    main()
    