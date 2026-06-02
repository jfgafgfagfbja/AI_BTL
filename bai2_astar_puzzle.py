import heapq, sys, random, pygame

# ─── Màu ───────────────────────────────────────────────────────────────────
WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(180,180,185)
BG=(235,240,248); BLUE=(45,95,170); LT_BLUE=(180,215,255)
RED=(210,50,50); GREEN=(40,165,40); ORANGE=(240,130,0)
DARK=(55,55,60); PANEL_BG=(245,248,255)
TILE_CLR=(70,120,200); TILE_EMPTY=(220,225,235); TILE_CORRECT=(60,170,80)
TILE_WRONG=(200,80,80); TILE_TXT=WHITE; PANEL_LINE=(160,165,180)

GOAL = (1,2,3,4,5,6,7,8,0)   # 0 = ô trống

# ─── Thuật toán A* ─────────────────────────────────────────────────────────
def manhattan(state):
    total = 0
    for i, v in enumerate(state):
        if v == 0: continue
        gr, gc = (v-1)//3, (v-1)%3
        cr, cc = i//3,      i%3
        total += abs(gr-cr) + abs(gc-cc)
    return total

def get_neighbors(state):
    idx = state.index(0)
    r, c = idx//3, idx%3
    nbrs = []
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r+dr, c+dc
        if 0<=nr<3 and 0<=nc<3:
            ni = nr*3+nc
            lst = list(state); lst[idx],lst[ni] = lst[ni],lst[idx]
            nbrs.append(tuple(lst))
    return nbrs

def is_solvable(state):
    inv = 0
    s = [x for x in state if x != 0]
    for i in range(len(s)):
        for j in range(i+1, len(s)):
            if s[i] > s[j]: inv += 1
    return inv % 2 == 0

def astar(start):
    """Trả về list các trạng thái từ start → GOAL, hoặc None."""
    if start == GOAL: return [start]
    h = manhattan(start)
    heap = [(h, 0, start, [start])]   # (f, g, state, path)
    visited = {}
    while heap:
        f, g, state, path = heapq.heappop(heap)
        if state in visited and visited[state] <= g:
            continue
        visited[state] = g
        for nb in get_neighbors(state):
            ng = g + 1
            if nb in visited and visited[nb] <= ng:
                continue
            nh = manhattan(nb)
            nf = ng + nh
            heapq.heappush(heap, (nf, ng, nb, path+[nb]))
            if nb == GOAL:
                return path + [nb]
    return None

def shuffle_puzzle():
    s = list(GOAL)
    for _ in range(200):
        idx = s.index(0)
        r, c = idx//3, idx%3
        dirs = []
        for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr,nc=r+dr,c+dc
            if 0<=nr<3 and 0<=nc<3: dirs.append((nr*3+nc,))
        ni = random.choice(dirs)[0]
        s[idx],s[ni] = s[ni],s[idx]
    t = tuple(s)
    return t if is_solvable(t) else shuffle_puzzle()

# ─── Pygame ────────────────────────────────────────────────────────────────
CELL = 110    # kích thước ô puzzle
GAP  = 8

def draw_puzzle(screen, state, ox, oy, font_tile, highlight_wrong=False):
    for i, v in enumerate(state):
        r, c = i//3, i%3
        x = ox + c*(CELL+GAP); y = oy + r*(CELL+GAP)
        if v == 0:
            pygame.draw.rect(screen, TILE_EMPTY, (x,y,CELL,CELL), border_radius=12)
            pygame.draw.rect(screen, GRAY, (x,y,CELL,CELL), 2, border_radius=12)
        else:
            correct_pos = (v-1)//3*3 + (v-1)%3
            if highlight_wrong and state[correct_pos] != v:
                col = TILE_WRONG
            elif v == state[i] and state == GOAL:
                col = TILE_CORRECT
            else:
                col = TILE_CLR
            pygame.draw.rect(screen, col, (x,y,CELL,CELL), border_radius=12)
            pygame.draw.rect(screen, WHITE, (x,y,CELL,CELL), 2, border_radius=12)
            txt = font_tile.render(str(v), True, TILE_TXT)
            screen.blit(txt, (x+CELL//2-txt.get_width()//2, y+CELL//2-txt.get_height()//2))

def draw_button(screen, rect, text, font, active=True):
    col = BLUE if active else GRAY
    pygame.draw.rect(screen, col, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    s = font.render(text, True, WHITE)
    screen.blit(s, (rect.centerx-s.get_width()//2, rect.centery-s.get_height()//2))

def main():
    pygame.init()
    W, H = 900, 740
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Bài 2 – A* – Giải bài toán 8-Puzzle")
    clock = pygame.time.Clock()

    def mkfont(sz, bold=False):
        for nm in ['segoeui','tahoma','arial']:
            try: return pygame.font.SysFont(nm, sz, bold=bold)
            except: pass
        return pygame.font.SysFont(None, sz)

    ft   = mkfont(21, True)
    fb   = mkfont(16, True)
    fn   = mkfont(14)
    fs   = mkfont(12)
    ftile= mkfont(42, True)

    current  = shuffle_puzzle()
    solution = None   # list of states
    step_idx = 0
    solving  = False
    msg      = "Nhấn SOLVE để A* giải"
    msg_col  = DARK
    auto     = False; auto_t = 0; DELAY = 500

    BTN_SHUFFLE = pygame.Rect(60,  668, 180, 44)
    BTN_SOLVE   = pygame.Rect(260, 668, 180, 44)
    BTN_PREV    = pygame.Rect(460, 668, 80,  44)
    BTN_NEXT    = pygame.Rect(555, 668, 80,  44)
    BTN_AUTO    = pygame.Rect(650, 668, 120, 44)

    PUZ_OX = 60; PUZ_OY = 120
    GOAL_OX= 520; GOAL_OY= 120

    while True:
        dt = clock.tick(60)
        display_state = solution[step_idx] if solution else current

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_SPACE: auto = not auto
                elif ev.key == pygame.K_RIGHT:
                    if solution and step_idx < len(solution)-1: step_idx += 1
                elif ev.key == pygame.K_LEFT:
                    if solution and step_idx > 0: step_idx -= 1
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx,my = ev.pos
                if BTN_SHUFFLE.collidepoint(mx,my):
                    current = shuffle_puzzle(); solution=None; step_idx=0
                    msg="Đã xáo trộn – nhấn SOLVE"; msg_col=DARK; auto=False
                elif BTN_SOLVE.collidepoint(mx,my):
                    msg="Đang tìm lời giải A*..."; msg_col=BLUE
                    pygame.display.flip()
                    sol = astar(current)
                    if sol:
                        solution = sol; step_idx = 0
                        msg=f"Tìm thấy! {len(sol)-1} bước  |  ← → hoặc AUTO"
                        msg_col = GREEN
                    else:
                        msg="Không tìm thấy lời giải!"; msg_col=RED
                elif BTN_PREV.collidepoint(mx,my):
                    if solution and step_idx>0: step_idx-=1; auto=False
                elif BTN_NEXT.collidepoint(mx,my):
                    if solution and step_idx<len(solution)-1: step_idx+=1; auto=False
                elif BTN_AUTO.collidepoint(mx,my):
                    if solution: auto=not auto

        if auto and solution:
            auto_t += dt
            if auto_t >= DELAY:
                auto_t = 0
                if step_idx < len(solution)-1: step_idx += 1
                else: auto = False

        screen.fill(BG)

        pygame.draw.rect(screen, BLUE, (0,0,W,52))
        ts = ft.render("THUẬT TOÁN A* – Giải bài toán 8-Puzzle", True, WHITE)
        screen.blit(ts,(W//2-ts.get_width()//2,14))

        lbl1 = fb.render("Trạng thái hiện tại", True, BLUE)
        screen.blit(lbl1,(PUZ_OX,90))
        draw_puzzle(screen, display_state, PUZ_OX, PUZ_OY, ftile,
                    highlight_wrong=(display_state!=GOAL))

        lbl2 = fb.render("Trạng thái đích", True, GREEN)
        screen.blit(lbl2,(GOAL_OX,90))
        draw_puzzle(screen, GOAL, GOAL_OX, GOAL_OY, ftile)

        info_x = 60; info_y = PUZ_OY + 3*(CELL+GAP) + 20
        h_val = manhattan(display_state)
        g_val = step_idx if solution else 0
        f_val = g_val + h_val
        infos = [
            (f"g(n) = {g_val}", "Chi phí đã đi"),
            (f"h(n) = {h_val}", "Manhattan heuristic"),
            (f"f(n) = {f_val}", "= g + h"),
        ]
        for j,(val,desc) in enumerate(infos):
            vx = info_x + j*170
            pygame.draw.rect(screen,WHITE,(vx,info_y,155,56),border_radius=8)
            pygame.draw.rect(screen,BLUE,(vx,info_y,155,56),2,border_radius=8)
            vs = fb.render(val,True,BLUE)
            ds = fs.render(desc,True,DARK)
            screen.blit(vs,(vx+8,info_y+6)); screen.blit(ds,(vx+8,info_y+30))

        if solution:
            prog_x=60; prog_y=info_y+72
            prog_txt=fb.render(f"Bước {step_idx} / {len(solution)-1}",True,DARK)
            screen.blit(prog_txt,(prog_x,prog_y))
            bar_w=580; bar_h=14; bx=60; by=prog_y+28
            pygame.draw.rect(screen,GRAY,(bx,by,bar_w,bar_h),border_radius=7)
            if len(solution)>1:
                fill=int(bar_w*step_idx/(len(solution)-1))
                pygame.draw.rect(screen,BLUE,(bx,by,fill,bar_h),border_radius=7)

            if display_state==GOAL:
                done=fb.render("✔ HOÀN THÀNH! Tất cả ô đúng vị trí.",True,GREEN)
                screen.blit(done,(60,prog_y+48))

        guide_x=520; guide_y=PUZ_OY+3*(CELL+GAP)+20
        lines=[
            ("Hướng dẫn:", fb, BLUE),
            ("SHUFFLE: xáo trộn puzzle", fn, DARK),
            ("SOLVE: A* tìm lời giải", fn, DARK),
            ("← / →: bước trước/sau", fn, DARK),
            ("AUTO: tự động phát lại", fn, DARK),
            ("SPACE: dừng/tiếp tục", fn, DARK),
        ]
        for txt,f,col in lines:
            s=f.render(txt,True,col); screen.blit(s,(guide_x,guide_y)); guide_y+=s.get_height()+6

        ms=fn.render(msg,True,msg_col); screen.blit(ms,(10,644))

        draw_button(screen,BTN_SHUFFLE,"SHUFFLE",fb)
        draw_button(screen,BTN_SOLVE,  "SOLVE",  fb)
        draw_button(screen,BTN_PREV,   "◀ Trước",fn, solution is not None and step_idx>0)
        draw_button(screen,BTN_NEXT,   "Sau ▶",  fn, solution is not None and step_idx<(len(solution)-1 if solution else 0))
        draw_button(screen,BTN_AUTO,   "AUTO ▶" if not auto else "⏸ DỪNG", fb, solution is not None)

        pygame.display.flip()

if __name__ == "__main__":
    main()
