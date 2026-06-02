import sys, copy, time, pygame

# ─── Hằng số ───────────────────────────────────────────────────────────────
ROWS = COLS = 15
CELL = 42
MARGIN = 40
PANEL_W = 220

W  = MARGIN*2 + (COLS-1)*CELL + PANEL_W + 30
H  = MARGIN*2 + (ROWS-1)*CELL + 20
BOARD_W = MARGIN*2 + (COLS-1)*CELL

PLAYER = 1    # người chơi (X – đen)
AI     = 2    # máy       (O – trắng)

# ─── Màu ───────────────────────────────────────────────────────────────────
BG_BOARD= (210, 175, 100)
LINE_C  = (140, 100,  50)
WHITE   = (255,255,255); BLACK=(0,0,0)
BG      = (235,240,248); BLUE=(45,95,170)
RED     = (210,50,50); GREEN=(40,165,40)
ORANGE  = (240,130,0)
DARK    = (55,55,60);  GRAY=(180,180,185)
PANEL_BG= (245,248,255)
P_COLOR = (20,20,20)     # quân người – đen
AI_COLOR= (240,240,240)  # quân máy  – trắng
LAST_DOT= (255,80,80)    # chấm đỏ đánh dấu nước cuối

# ─── AI – Đánh giá & Minimax ───────────────────────────────────────────────
WIN_SCORE = 100_000_000

def check_win(board, player):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != player: continue
            for dr,dc in [(0,1),(1,0),(1,1),(1,-1)]:
                cnt=0
                for k in range(5):
                    nr,nc=r+dr*k,c+dc*k
                    if 0<=nr<ROWS and 0<=nc<COLS and board[nr][nc]==player: cnt+=1
                    else: break
                if cnt==5: return True
    return False

_SCORE_TABLE = {
    (5, 0): WIN_SCORE, (5, 1): WIN_SCORE, (5, 2): WIN_SCORE,
    (4, 2): 500_000,
    (4, 1): 50_000,
    (3, 2): 10_000,
    (3, 1): 1_000,
    (2, 2): 500,
    (2, 1): 100,
    (1, 2): 20,
    (1, 1): 5,
}

def _run_score(cnt, open_ends):
    if cnt >= 5: return WIN_SCORE
    return _SCORE_TABLE.get((cnt, open_ends), 0)

def evaluate(board, player):
    opp = 3 - player
    score = 0
    dirs = [(0,1),(1,0),(1,1),(1,-1)]
    for dr, dc in dirs:
        for r in range(ROWS):
            for c in range(COLS):
                p = board[r][c]
                if p == 0: continue
                pr, pc = r-dr, c-dc
                if 0<=pr<ROWS and 0<=pc<COLS and board[pr][pc]==p:
                    continue
                cnt = 0
                for k in range(9):
                    nr, nc = r+dr*k, c+dc*k
                    if 0<=nr<ROWS and 0<=nc<COLS and board[nr][nc]==p:
                        cnt += 1
                    else: break
                lr, lc = r-dr, c-dc
                rr, rc2 = r+dr*cnt, c+dc*cnt
                ol  = (0<=lr<ROWS  and 0<=lc<COLS  and board[lr][lc]==0)
                or_ = (0<=rr<ROWS  and 0<=rc2<COLS and board[rr][rc2]==0)
                opens = (1 if ol else 0) + (1 if or_ else 0)
                s = _run_score(cnt, opens)
                if p == player: score += s
                else:           score -= int(s * 1.2)
    return score

def get_candidates(board, radius=2):
    cands = set()
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] != 0:
                for dr in range(-radius, radius+1):
                    for dc in range(-radius, radius+1):
                        nr, nc = r+dr, c+dc
                        if 0<=nr<ROWS and 0<=nc<COLS and board[nr][nc]==0:
                            cands.add((nr,nc))
    return list(cands) if cands else [(ROWS//2, COLS//2)]

def _quick_score(board, r, c, player):
    board[r][c] = player
    s = evaluate(board, player)
    board[r][c] = 0
    return s

def minimax(board, depth, alpha, beta, is_max, ai, deadline):
    if time.time() > deadline: return evaluate(board, ai)
    if check_win(board, ai):   return WIN_SCORE + depth*1000
    if check_win(board, 3-ai): return -(WIN_SCORE + depth*1000)
    if depth == 0: return evaluate(board, ai)

    cands = get_candidates(board)
    cur = ai if is_max else 3-ai
    cands.sort(key=lambda pos: _quick_score(board, pos[0], pos[1], cur),
               reverse=is_max)
    cands = cands[:20]

    if is_max:
        best = -10**18
        for r,c in cands:
            board[r][c] = cur
            val = minimax(board, depth-1, alpha, beta, False, ai, deadline)
            board[r][c] = 0
            if val > best: best = val
            if best > alpha: alpha = best
            if beta <= alpha: break
        return best
    else:
        best = 10**18
        for r,c in cands:
            board[r][c] = cur
            val = minimax(board, depth-1, alpha, beta, True, ai, deadline)
            board[r][c] = 0
            if val < best: best = val
            if best < beta: beta = best
            if beta <= alpha: break
        return best

def ai_move(board, ai_player, depth=4, time_limit=4.0):
    opp = 3 - ai_player
    cands = get_candidates(board)
    deadline = time.time() + time_limit

    for r,c in cands:
        board[r][c] = ai_player
        if check_win(board, ai_player): board[r][c]=0; return (r,c)
        board[r][c] = 0

    for r,c in cands:
        board[r][c] = opp
        if check_win(board, opp): board[r][c]=0; return (r,c)
        board[r][c] = 0

    cands.sort(key=lambda pos: _quick_score(board, pos[0], pos[1], ai_player),
               reverse=True)
    best_val = -10**18; best_pos = cands[0]
    for r,c in cands:
        board[r][c] = ai_player
        val = minimax(board, depth-1, -10**18, 10**18, False, ai_player, deadline)
        board[r][c] = 0
        if val > best_val: best_val = val; best_pos = (r,c)
        if time.time() > deadline: break
    return best_pos

# ─── Pygame ────────────────────────────────────────────────────────────────
def rc_to_xy(r,c): return MARGIN+c*CELL, MARGIN+r*CELL
def xy_to_rc(x,y):
    c=round((x-MARGIN)/CELL); r=round((y-MARGIN)/CELL)
    if 0<=r<ROWS and 0<=c<COLS: return r,c
    return None,None

def draw_board(screen, board, last_move, font_tile, win_cells):
    pygame.draw.rect(screen, BG_BOARD, (0,0,BOARD_W+10,H))
    for r in range(ROWS):
        y=MARGIN+r*CELL
        pygame.draw.line(screen,LINE_C,(MARGIN,y),(MARGIN+(COLS-1)*CELL,y),1)
    for c in range(COLS):
        x=MARGIN+c*CELL
        pygame.draw.line(screen,LINE_C,(x,MARGIN),(x,MARGIN+(ROWS-1)*CELL),1)
    for r,c in [(3,3),(3,11),(7,7),(11,3),(11,11)]:
        pygame.draw.circle(screen,LINE_C,(MARGIN+c*CELL,MARGIN+r*CELL),4)
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]==0: continue
            x,y=rc_to_xy(r,c)
            col = P_COLOR if board[r][c]==PLAYER else AI_COLOR
            outline=(200,200,200) if board[r][c]==PLAYER else (80,80,80)
            pygame.draw.circle(screen,col,(x,y),CELL//2-3)
            pygame.draw.circle(screen,outline,(x,y),CELL//2-3,2)
            if (r,c)==last_move:
                pygame.draw.circle(screen,LAST_DOT,(x,y),5)
    if win_cells:
        for r,c in win_cells:
            x,y=rc_to_xy(r,c)
            pygame.draw.circle(screen,(255,200,0),(x,y),CELL//2-3,4)

def get_win_cells(board, player):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c]!=player: continue
            for dr,dc in [(0,1),(1,0),(1,1),(1,-1)]:
                cells=[]
                for k in range(5):
                    nr,nc=r+dr*k,c+dc*k
                    if 0<=nr<ROWS and 0<=nc<COLS and board[nr][nc]==player:
                        cells.append((nr,nc))
                    else: break
                if len(cells)==5: return cells
    return []

def main():
    pygame.init()
    screen=pygame.display.set_mode((W,H))
    pygame.display.set_caption("Bài 3 – Caro (Gomoku) – Người vs Máy")
    clock=pygame.time.Clock()

    def mkfont(sz,bold=False):
        for nm in ['segoeui','tahoma','arial']:
            try: return pygame.font.SysFont(nm,sz,bold=bold)
            except: pass
        return pygame.font.SysFont(None,sz)

    ft=mkfont(20,True); fb=mkfont(16,True); fn=mkfont(14); fs=mkfont(12)

    board=[[0]*COLS for _ in range(ROWS)]
    turn=PLAYER; last_move=None; winner=0; win_cells=[]; ai_thinking=False
    history=[]; msg="Lượt của bạn (X – Đen)"

    BTN_NEW=pygame.Rect(BOARD_W+20, H-65, 180, 44)

    def reset():
        nonlocal board,turn,last_move,winner,win_cells,ai_thinking,history,msg
        board=[[0]*COLS for _ in range(ROWS)]
        turn=PLAYER; last_move=None; winner=0; win_cells=[]; ai_thinking=False
        history=[]; msg="Lượt của bạn (X – Đen)"

    ai_timer=0; AI_DELAY=300

    while True:
        dt=clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_r: reset()
            if ev.type==pygame.MOUSEBUTTONDOWN:
                mx,my=ev.pos
                if BTN_NEW.collidepoint(mx,my): reset(); continue
                if winner or ai_thinking or turn!=PLAYER: continue
                if mx<BOARD_W:
                    r,c=xy_to_rc(mx,my)
                    if r is not None and board[r][c]==0:
                        board[r][c]=PLAYER; last_move=(r,c); history.append((r,c))
                        if check_win(board,PLAYER):
                            winner=PLAYER; win_cells=get_win_cells(board,PLAYER)
                            msg="Chúc mừng! Bạn THẮNG!"
                        else:
                            turn=AI; ai_thinking=True; ai_timer=0
                            msg="Máy đang suy nghĩ..."

        if ai_thinking and not winner:
            ai_timer+=dt
            if ai_timer>=AI_DELAY:
                ai_thinking=False
                r,c=ai_move(board, AI)
                board[r][c]=AI; last_move=(r,c); history.append((r,c))
                if check_win(board,AI):
                    winner=AI; win_cells=get_win_cells(board,AI)
                    msg="Máy THẮNG! Hãy thử lại."
                else:
                    turn=PLAYER
                    msg="Lượt của bạn (X – Đen)"
                if not winner and all(board[r][c]!=0 for r in range(ROWS) for c in range(COLS)):
                    winner=-1; msg="HÒA! Bàn cờ đã đầy."

        screen.fill(BG)
        draw_board(screen, board, last_move, fb, win_cells)

        px=BOARD_W+15; py=10; pw=PANEL_W
        pygame.draw.rect(screen,PANEL_BG,(px,py,pw,H-20),border_radius=10)
        pygame.draw.rect(screen,BLUE,(px,py,pw,H-20),2,border_radius=10)
        ipy=py+12

        def plbl(txt,f,col):
            nonlocal ipy; s=f.render(txt,True,col)
            screen.blit(s,(px+(pw-s.get_width())//2,ipy)); ipy+=s.get_height()+5

        def pline():
            nonlocal ipy; pygame.draw.line(screen,GRAY,(px+8,ipy),(px+pw-8,ipy),1); ipy+=8

        plbl("GAME CARO", ft, BLUE); pline()

        tc=GREEN if turn==PLAYER and not winner else (RED if winner else GRAY)
        plbl("Người" if turn==PLAYER else "Máy AI", fb, tc)
        pygame.draw.circle(screen,P_COLOR, (px+45,ipy+10),12)
        pygame.draw.circle(screen,(200,200,200),(px+45,ipy+10),12,2)
        ls=fn.render("Bạn (X)",True,DARK); screen.blit(ls,(px+62,ipy+3)); ipy+=28
        pygame.draw.circle(screen,AI_COLOR,(px+45,ipy+10),12)
        pygame.draw.circle(screen,(80,80,80),(px+45,ipy+10),12,2)
        ls=fn.render("Máy (O)",True,DARK); screen.blit(ls,(px+62,ipy+3)); ipy+=28
        pline()

        plbl("Luật chơi:", fb, DARK)
        for rule in ["• Thắng: 5 quân liên tiếp","• Ngang / Dọc / Chéo","• Click để đặt quân"]:
            rs=fs.render(rule,True,DARK); screen.blit(rs,(px+10,ipy)); ipy+=rs.get_height()+4
        pline()

        plbl("Nước đi gần nhất:", fb, DARK)
        show=history[-8:] if len(history)>=8 else history
        for i,pos in enumerate(reversed(show)):
            p="Bạn" if (len(history)-i)%2==1 else "Máy"
            hs=fs.render(f"{len(history)-i}. {p}: ({pos[0]+1},{pos[1]+1})",True,DARK)
            screen.blit(hs,(px+8,ipy)); ipy+=hs.get_height()+3
        pline()

        mc=GREEN if winner==PLAYER else (RED if winner==AI else (DARK if not winner else ORANGE))
        for part in [msg[i:i+22] for i in range(0,len(msg),22)]:
            ms=fn.render(part,True,mc); screen.blit(ms,(px+(pw-ms.get_width())//2,ipy)); ipy+=ms.get_height()+4

        pygame.draw.rect(screen,BLUE,BTN_NEW,border_radius=8)
        pygame.draw.rect(screen,WHITE,BTN_NEW,2,border_radius=8)
        bs=fb.render("VÁN MỚI (R)",True,WHITE)
        screen.blit(bs,(BTN_NEW.centerx-bs.get_width()//2,BTN_NEW.centery-bs.get_height()//2))

        if ai_thinking:
            dots="." * ((pygame.time.get_ticks()//400)%4)
            ts=fn.render(f"AI suy nghĩ{dots}",True,ORANGE)
            screen.blit(ts,(10,H-25))

        pygame.display.flip()

if __name__=="__main__":
    main()
