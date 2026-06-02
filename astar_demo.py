import heapq

graph = {
    'A': [('C', 9), ('D', 7), ('E', 13), ('F', 20)],
    'C': [('H', 6)],
    'D': [('E', 4), ('H', 8)],
    'E': [('I', 3), ('K', 4)],
    'F': [('G', 4), ('I', 6)],
    'H': [('K', 5)],
    'K': [('B', 6), ('I', 9)],
    'I': [('B', 5)],
    'G': [],
    'B': []
}


heuristic = {
    'A': 14,
    'B': 0,
    'C': 15,
    'D': 6,
    'E': 8,
    'F': 7,
    'G': 12,
    'H': 10,
    'I': 4,
    'K': 2
}



def astar(graph, heuristic, start, goal):
    
    open_list = []
    heapq.heappush(open_list, (heuristic[start], start, [start], 0))

   
    closed_set = {}  
    step = 0

    print("=" * 65)
    print(f"  THUẬT TOÁN A*  |  Start: {start}  →  Goal: {goal}")
    print("=" * 65)

    while open_list:
        
        open_display = [(n, g, heuristic[n], g + heuristic[n])
                        for (f, n, p, g) in open_list]
        open_display.sort(key=lambda x: x[3])
        print(f"\n{'─'*65}")
        print(f"OPEN  : {[(x[0], f'f={x[3]}') for x in open_display]}")
        print(f"CLOSED: {list(closed_set.keys())}")

        
        f_cur, current, path, g_cur = heapq.heappop(open_list)

        step += 1
        print(f"\n[Bước {step}] Lấy ra: {current}  |  g={g_cur}, h={heuristic[current]}, f={f_cur}")

        if current in closed_set and closed_set[current] <= g_cur:
            print(f"  → {current} đã có trong CLOSED với g tốt hơn, bỏ qua.")
            continue

        closed_set[current] = g_cur
        print(f"  → Thêm {current} vào CLOSED")

        if current == goal:
            print(f"\n{'=' * 65}")
            print(f"  ĐÃ TÌM THẤY ĐƯỜNG ĐI!")
            print(f"  Đường đi: {' → '.join(path)}")
            print(f"  Chi phí : {g_cur}")
            print(f"{'=' * 65}")
            return path, g_cur

        print(f"  → Mở rộng {current}: các kề = {graph[current]}")
        for neighbor, cost in graph[current]:
            new_g = g_cur + cost
            new_f = new_g + heuristic[neighbor]

            if neighbor in closed_set and closed_set[neighbor] <= new_g:
                print(f"     {neighbor}: đã có trong CLOSED (g={closed_set[neighbor]} ≤ {new_g}), bỏ qua")
                continue

            new_path = path + [neighbor]
            heapq.heappush(open_list, (new_f, neighbor, new_path, new_g))
            print(f"     {neighbor}: g={new_g}, h={heuristic[neighbor]}, f={new_f} → thêm vào OPEN")

    print("\n❌ Không tìm thấy đường đi!")
    return None, float('inf')


if __name__ == "__main__":
    path, cost = astar(graph, heuristic, start='A', goal='B')
