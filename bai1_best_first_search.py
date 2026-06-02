import heapq, math, sys, pygame

# ─── Màu ───────────────────────────────────────────────────────────────────────
WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(180,180,185)
BG=(235,240,248); BLUE=(45,95,170); LT_BLUE=(173,216,230)
RED=(210,50,50); GREEN=(40,165,40); ORANGE=(240,130,0)
YELLOW=(255,215,0); DARK=(55,55,60)
EDGE_C=(160,160,175); PATH_C=(255,110,0)
VISITED_C=(100,145,230); OPEN_C=(255,225,80)
PANEL_BG=(245,248,255)

# ─── Bản đồ phường ───────────────────────────────────────────────────────────────
NODES = {
    'Chợ':         (390, 75),
    'Trường học':  (175, 185),
    'Bệnh viện':   (625, 185),
    'Công viên':   (100, 340),
    'UBND':        (340, 295),
    'Nhà thờ':     (570, 330),
    'Trạm xăng':   (205, 450),
    'Siêu thị':    (460, 450),
    'Trường THPT': (85,  560),
    'Nhà hàng':    (335, 548),
    'Khách sạn':   (625, 508),
    'Bưu điện':    (725, 330),
}
EDGES = [
    ('Chợ','Trường học'),('Chợ','Bệnh viện'),
    ('Trường học','Công viên'),('Trường học','UBND'),
    ('Bệnh viện','UBND'),('Bệnh viện','Nhà thờ'),('Bệnh viện','Bưu điện'),
    ('Công viên','Trạm xăng'),('UBND','Trạm xăng'),('UBND','Siêu thị'),
    ('Nhà thờ','Siêu thị'),('Nhà thờ','Khách sạn'),('Nhà thờ','Bưu điện'),
    ('Trạm xăng','Trường THPT'),('Trạm xăng','Nhà hàng'),
    ('Siêu thị','Nhà hàng'),('Siêu thị','Khách sạn'),
    ('Trường THPT','Nhà hàng'),('Nhà hàng','Khách sạn'),
]

def edist(a, b):
    x1,y1=NODES[a]; x2,y2=NODES[b]
    return math.hypot(x2-x1, y2-y1)

def build_graph():
    G = {n: [] for n in NODES}
    for u, v in EDGES:
        w = round(edist(u, v), 1)
        G[u].append((v, w)); G[v].append((u, w))
    return G

def best_first_search(G, start, goal):
    """Greedy Best First Search – ưu tiên node có h(n) nhỏ nhất."""
    counter = 0
    heap = [(edist(start, goal), counter, start, [start])]
    visited = set()
    steps = []
    while heap:
        h, _, node, path = heapq.heappop(heap)
        if node in visited:
            continue
        visited.add(node)
        open_now = [n for _,_,n,_ in heap]
        steps.append({'node': node, 'path': list(path),
                      'visited': set(visited), 'open': list(open_now)})
        if node == goal:
            return path, steps
        for nb, _ in G[node]:
            if nb not in visited:
                counter += 1
                heapq.heappush(heap, (edist(nb, goal), counter, nb, path+[nb]))
    return None, steps

# ─── Pygame ───────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    W, H = 1030, 730
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Bài 1 – Best First Search – Bản đồ Phường")
    clock = pygame.time.Clock()

    def mkfont(sz, bold=False):
        for name in ['segoeui','tahoma','arial']:
            try: return pygame.font.SysFont(name, sz, bold=bold)
            except: pass
        return pygame.font.SysFont(None, sz)

    fs = mkfont(12); fn = mkfont(14); fb = mkfont(15, True); ft = mkfont(20, True)

    G = build_graph()
    start_n = 'Chợ'; goal_n = 'Trường THPT'
    path, steps = best_first_search(G, start_n, goal_n)
    step_idx = 0; auto = False; auto_t = 0; DELAY = 750
    sel = None   # 'start' or 'goal'

    def rerun():
        nonlocal path, steps, step_idx, auto
        path, steps = best_first_search(G, start_n, goal_n)
        step_idx = 0; auto = False

    MAP_W = 810; PANEL_X = MAP_W + 5

    while True:
        dt = clock.tick(60)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE:   auto = not auto
                elif ev.key == pygame.K_RIGHT and step_idx < len(steps)-1: step_idx += 1
                elif ev.key == pygame.K_LEFT  and step_idx > 0: step_idx -= 1
                elif ev.key == pygame.K_r:     rerun()
                elif ev.key == pygame.K_s:     sel = 'start'
                elif ev.key == pygame.K_g:     sel = 'goal'
                elif ev.key == pygame.K_ESCAPE: sel = None
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                for name, (nx, ny) in NODES.items():
                    if math.hypot(mx-nx, my-ny) < 25:
                        if sel == 'start':   start_n = name; sel = None; rerun()
                        elif sel == 'goal':  goal_n  = name; sel = None; rerun()
                        break

        if auto:
            auto_t += dt
            if auto_t >= DELAY:
                auto_t = 0
                if step_idx < len(steps)-1: step_idx += 1
                else: auto = False

        cur = steps[step_idx] if steps else {}
        cur_node  = cur.get('node', '')
        cur_path  = cur.get('path', [])
        visited   = cur.get('visited', set())
        open_set  = set(cur.get('open', []))
        found     = (cur_node == goal_n)

        # ── Draw ────────────────────────────────────────────────────────────────────
screen.fill(BG)
        # Title bar
        pygame.draw.rect(screen, BLUE, (0,0,W,52))
        ts = ft.render("BEST FIRST SEARCH  –  Tìm đường trong bản đồ phường", True, WHITE)
        screen.blit(ts, (W//2-ts.get_width()//2, 14))

        # Map background
        pygame.draw.rect(screen, WHITE, (5,57,MAP_W-5,H-70), border_radius=8)
        pygame.draw.rect(screen, GRAY,  (5,57,MAP_W-5,H-70), 2, border_radius=8)

        # Edges
        for u, v in EDGES:
            x1,y1=NODES[u]; x2,y2=NODES[v]
            on = any((cur_path[i]==u and cur_path[i+1]==v) or
                     (cur_path[i]==v and cur_path[i+1]==u)
                     for i in range(len(cur_path)-1)) if len(cur_path)>1 else False
            pygame.draw.line(screen, PATH_C if on else EDGE_C, (x1,y1),(x2,y2), 4 if on else 2)
            mx2,my2=(x1+x2)//2,(y1+y2)//2
            wt = int(round(edist(u,v)/10)*10)
            ws = fs.render(str(wt), True, DARK)
            screen.blit(ws,(mx2-ws.get_width()//2, my2-8))

        # Nodes
        for name,(nx,ny) in NODES.items():
            if   name==start_n:  fc=GREEN;      bc=(0,120,0)
            elif name==goal_n:   fc=RED;        bc=(150,0,0)
            elif name==cur_node: fc=ORANGE;     bc=(180,75,0)
            elif name in visited:fc=VISITED_C;  bc=BLUE
            elif name in open_set:fc=OPEN_C;   bc=(175,145,0)
            else:                fc=(218,220,228); bc=GRAY
            pygame.draw.circle(screen, bc, (nx,ny), 24)
            pygame.draw.circle(screen, fc, (nx,ny), 22)
            words = name.split()
            for i, w in enumerate(words):
                lb = fs.render(w, True, BLACK)
                oy = (-7+(i*13)) if len(words)>1 else -6
                screen.blit(lb,(nx-lb.get_width()//2, ny+oy))

        # Panel
        pygame.draw.rect(screen, PANEL_BG, (PANEL_X,57,W-PANEL_X-3,H-70), border_radius=8)
        pygame.draw.rect(screen, BLUE,     (PANEL_X,57,W-PANEL_X-3,H-70), 2, border_radius=8)
        py = 70; pw = W-PANEL_X-3; pmid = PANEL_X+pw//2

        def ptext(txt,f,col,ox=8):
            nonlocal py; s=f.render(txt,True,col); screen.blit(s,(PANEL_X+ox,py)); py+=s.get_height()+3
        def pline():
            nonlocal py; pygame.draw.line(screen,GRAY,(PANEL_X+6,py),(W-8,py),1); py+=6
        def pcenter(txt,f,col):
            nonlocal py; s=f.render(txt,True,col); screen.blit(s,(pmid-s.get_width()//2,py)); py+=s.get_height()+3

        pcenter("THÔNG TIN", fb, BLUE); pline()
        ptext("Xuất phát:", fn, BLACK); ptext(start_n, fb, GREEN); py+=2
        ptext("Đích đến:",  fn, BLACK); ptext(goal_n,  fb, RED);   py+=2
        pline()
        ptext(f"Bước: {step_idx+1} / {len(steps)}", fn, BLACK)
        if cur_node: ptext(f"Đang xét: {cur_node}", fb, ORANGE)
        if found: ptext("ĐÃ TÌM THẤY!", fb, GREEN); ptext(f"{len(cur_path)-1} cạnh", fn,(0,130,0))
        pline()

        pcenter("Chú thích:", fb, BLACK)
        legend = [(GREEN,"Xuất phát"),(RED,"Đích đến"),(ORANGE,"Đang xét"),
                  (VISITED_C,"Đã thăm"),(OPEN_C,"Trong OPEN"),((218,220,228),"Chưa thăm")]
        for col,lbl in legend:
            pygame.draw.circle(screen, col,   (PANEL_X+16, py+7), 8)
            pygame.draw.circle(screen, BLACK, (PANEL_X+16, py+7), 8, 1)
            ls=fs.render(lbl,True,BLACK); screen.blit(ls,(PANEL_X+28,py)); py+=19
        pline()

        pcenter("Điều khiển:", fb, BLACK)
        for c in ["← / → : xem từng bước","SPACE : tự động chạy",
                  "R : chạy lại","S : đổi điểm xuất phát",
                  "G : đổi điểm đích","(click vào node)"]:
            ptext(c, fs, (70,70,80))

        # Status bar
        if sel=='start':  st=">>> Click chọn ĐIỂM XUẤT PHÁT <<<"; sc=GREEN
        elif sel=='goal': st=">>> Click chọn ĐIỂM ĐÍCH <<<";      sc=RED
        elif found:       st=f"✓ {' → '.join(cur_path)}";          sc=(0,135,0)
        elif auto:        st="Đang chạy... (SPACE để dừng)";       sc=BLUE
        else:             st="SPACE=Tự động  |  ←/→=Từng bước  |  S/G=Đổi điểm"; sc=DARK
        ss=fn.render(st,True,sc); screen.blit(ss,(10,H-28))

        pygame.display.flip()

if __name__ == "__main__":
    main()
