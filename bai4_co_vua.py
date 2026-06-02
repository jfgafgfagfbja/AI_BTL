import sys, time, copy, pygame

# ─── Hằng số ───────────────────────────────────────────────────────────────
CELL   = 70
ROWS   = COLS = 8
BOARD_PX = CELL * COLS
PANEL_W  = 250
W = BOARD_PX + PANEL_W + 10
H = BOARD_PX + 50

WHITE_S = 'W'; BLACK_S = 'B'
PIECES  = 'KQRBNPkqrbnp'

VALUES = {'P':100,'N':320,'B':330,'R':500,'Q':900,'K':20000,
          'p':100,'n':320,'b':330,'r':500,'q':900,'k':20000}

# ─── Màu ───────────────────────────────────────────────────────────────────
LIGHT_SQ=(240,217,181); DARK_SQ=(181,136,99)
SEL_CLR =(186,202,43,180); MOVE_CLR=(186,202,43,120)
CHECK_CLR=(220,50,50)
BG=(30,30,35); PANEL_BG=(40,44,52)
WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(160,160,165)
BLUE=(100,149,237); GREEN=(80,180,80); RED=(210,60,60); ORANGE=(230,130,40)

# ─── Unicode cờ vua ────────────────────────────────────────────────────────────
UNICODE = {
    'K':'♔','Q':'♕','R':'♖','B':'♗','N':'♘','P':'♙',
    'k':'♚','q':'♛','r':'♜','b':'♝','n':'♞','p':'♟',
}

# ─── Bàn cờ & luật đi ─────────────────────────────────────────────────────────
INIT_BOARD = [
    ['r','n','b','q','k','b','n','r'],
    ['p','p','p','p','p','p','p','p'],
    ['.','.','.','.','.','.','.','.' ],
    ['.','.','.','.','.','.','.','.' ],
    ['.','.','.','.','.','.','.','.' ],
    ['.','.','.','.','.','.','.','.' ],
    ['P','P','P','P','P','P','P','P'],
    ['R','N','B','Q','K','B','N','R'],
]

def new_board(): return [list(row) for row in INIT_BOARD]

def is_white(p): return p.isupper() and p!='.'
def is_black(p): return p.islower()
def is_empty(p): return p=='.'
def opponent(color): return 'B' if color=='W' else 'W'
def piece_color(p):
    if is_white(p): return 'W'
    if is_black(p): return 'B'
    return None

def in_board(r,c): return 0<=r<8 and 0<=c<8

def raw_moves(board, r, c, ep_sq, castling):
    p = board[r][c]; moves = []
    if p=='.': return moves
    color = piece_color(p); pt = p.upper()
    opp_fn = is_black if color=='W' else is_white

    def add(nr,nc,promo=False):
        if not in_board(nr,nc): return
        t=board[nr][nc]
        if opp_fn(t) or is_empty(t):
            if promo and nr in (0,7) and pt=='P':
                for pp in (['Q','R','B','N'] if color=='W' else ['q','r','b','n']):
                    moves.append((r,c,nr,nc,pp))
            else:
                moves.append((r,c,nr,nc,None))

    if pt=='P':
        d=-1 if color=='W' else 1
        start_r=6 if color=='W' else 1
        if in_board(r+d,c) and is_empty(board[r+d][c]):
            add(r+d,c,True)
            if r==start_r and is_empty(board[r+2*d][c]):
                add(r+2*d,c)
        for dc in [-1,1]:
            nr,nc=r+d,c+dc
            if in_board(nr,nc):
                if opp_fn(board[nr][nc]):
                    add(nr,nc,True)
                elif (nr,nc)==ep_sq:
                    moves.append((r,c,nr,nc,'ep'))
    elif pt=='N':
        for dr,dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            add(r+dr,c+dc)
    elif pt=='K':
        for dr in [-1,0,1]:
            for dc in [-1,0,1]:
                if dr==0 and dc==0: continue
                add(r+dr,c+dc)
        if color=='W' and r==7 and c==4:
            if castling.get('WK') and board[7][5]=='.' and board[7][6]=='.' and board[7][7]=='R':
                moves.append((r,c,7,6,'castle'))
            if castling.get('WQ') and board[7][3]=='.' and board[7][2]=='.' and board[7][1]=='.' and board[7][0]=='R':
                moves.append((r,c,7,2,'castle'))
        if color=='B' and r==0 and c==4:
            if castling.get('BK') and board[0][5]=='.' and board[0][6]=='.' and board[0][7]=='r':
                moves.append((r,c,0,6,'castle'))
            if castling.get('BQ') and board[0][3]=='.' and board[0][2]=='.' and board[0][1]=='.' and board[0][0]=='r':
                moves.append((r,c,0,2,'castle'))
    elif pt in ('B','R','Q'):
        dirs=[]
        if pt in ('B','Q'): dirs+=[(-1,-1),(-1,1),(1,-1),(1,1)]
        if pt in ('R','Q'): dirs+=[(-1,0),(1,0),(0,-1),(0,1)]
        for dr,dc in dirs:
            nr,nc=r+dr,c+dc
            while in_board(nr,nc):
                t=board[nr][nc]
                if is_empty(t): moves.append((r,c,nr,nc,None)); nr+=dr; nc+=dc
                elif opp_fn(t): moves.append((r,c,nr,nc,None)); break
                else: break
    return moves

def apply_move(board, move, ep_sq, castling):
    r,c,nr,nc,flag=move
    b=[row[:] for row in board]; p=b[r][c]; color=piece_color(p)
    new_ep=None; new_cast=dict(castling)

    if flag=='ep':
        cap_r=r; b[cap_r][nc]='.'
    elif flag=='castle':
        if nc==6:  b[r][7]='.'; b[r][5]=('R' if color=='W' else 'r')
        elif nc==2:b[r][0]='.'; b[r][3]=('R' if color=='W' else 'r')
    elif flag and flag!='ep':
        p=flag

    b[nr][nc]=p; b[r][c]='.'

    if p.upper()=='P' and abs(nr-r)==2:
        new_ep=((r+nr)//2,c)

    if p=='K': new_cast['WK']=False; new_cast['WQ']=False
    elif p=='k': new_cast['BK']=False; new_cast['BQ']=False
    if (r,c)==(7,7) or (nr,nc)==(7,7): new_cast['WK']=False
    if (r,c)==(7,0) or (nr,nc)==(7,0): new_cast['WQ']=False
    if (r,c)==(0,7) or (nr,nc)==(0,7): new_cast['BK']=False
    if (r,c)==(0,0) or (nr,nc)==(0,0): new_cast['BQ']=False

    return b, new_ep, new_cast

def find_king(board, color):
    k='K' if color=='W' else 'k'
    for r in range(8):
        for c in range(8):
            if board[r][c]==k: return r,c
    return None,None

def is_attacked(board, r, c, by_color, ep_sq, castling):
    for rr in range(8):
        for cc in range(8):
            if piece_color(board[rr][cc])==by_color:
                for mv in raw_moves(board,rr,cc,ep_sq,castling):
                    if mv[2]==r and mv[3]==c: return True
    return False

def in_check(board, color, ep_sq, castling):
    kr,kc=find_king(board,color)
    if kr is None: return False
    return is_attacked(board,kr,kc,opponent(color),ep_sq,castling)

def legal_moves(board, color, ep_sq, castling):
    moves=[]
    for r in range(8):
        for c in range(8):
            if piece_color(board[r][c])==color:
                for mv in raw_moves(board,r,c,ep_sq,castling):
                    nb,nep,ncast=apply_move(board,mv,ep_sq,castling)
                    if mv[4]=='castle':
                        mid_c=5 if mv[3]==6 else 3
                        king_sq=(mv[0],mv[1])
                        if is_attacked(board,king_sq[0],king_sq[1],opponent(color),ep_sq,castling): continue
                        if is_attacked(nb,mv[0],mid_c,opponent(color),nep,ncast): continue
                    if not in_check(nb,color,nep,ncast):
                        moves.append(mv)
    return moves

# ─── Đánh giá vị trí ───────────────────────────────────────────────────────────────
PST = {
    'P': [
        [0,0,0,0,0,0,0,0],[50,50,50,50,50,50,50,50],[10,10,20,30,30,20,10,10],
        [5,5,10,25,25,10,5,5],[0,0,0,20,20,0,0,0],[5,-5,-10,0,0,-10,-5,5],
        [5,10,10,-20,-20,10,10,5],[0,0,0,0,0,0,0,0]
    ],
    'N': [
        [-50,-40,-30,-30,-30,-30,-40,-50],[-40,-20,0,0,0,0,-20,-40],
        [-30,0,10,15,15,10,0,-30],[-30,5,15,20,20,15,5,-30],
        [-30,0,15,20,20,15,0,-30],[-30,5,10,15,15,10,5,-30],
        [-40,-20,0,5,5,0,-20,-40],[-50,-40,-30,-30,-30,-30,-40,-50]
    ],
    'B': [
        [-20,-10,-10,-10,-10,-10,-10,-20],[-10,0,0,0,0,0,0,-10],
        [-10,0,5,10,10,5,0,-10],[-10,5,5,10,10,5,5,-10],
        [-10,0,10,10,10,10,0,-10],[-10,10,10,10,10,10,10,-10],
        [-10,5,0,0,0,0,5,-10],[-20,-10,-10,-10,-10,-10,-10,-20]
    ],
    'R': [
        [0,0,0,0,0,0,0,0],[5,10,10,10,10,10,10,5],[-5,0,0,0,0,0,0,-5],
        [-5,0,0,0,0,0,0,-5],[-5,0,0,0,0,0,0,-5],[-5,0,0,0,0,0,0,-5],
        [-5,0,0,0,0,0,0,-5],[0,0,0,5,5,0,0,0]
    ],
    'Q': [
        [-20,-10,-10,-5,-5,-10,-10,-20],[-10,0,0,0,0,0,0,-10],
        [-10,0,5,5,5,5,0,-10],[-5,0,5,5,5,5,0,-5],
        [0,0,5,5,5,5,0,-5],[-10,5,5,5,5,5,0,-10],
        [-10,0,5,0,0,0,0,-10],[-20,-10,-10,-5,-5,-10,-10,-20]
    ],
    'K': [
        [-30,-40,-40,-50,-50,-40,-40,-30],[-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],[-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],[-10,-20,-20,-20,-20,-20,-20,-10],
        [20,20,0,0,0,0,20,20],[20,30,10,0,0,10,30,20]
    ],
}

def pst_score(p, r, c):
    pt=p.upper()
    if pt not in PST: return 0
    table=PST[pt]
    if is_white(p): return table[r][c]
    else:           return table[7-r][c]

def evaluate_board(board):
    score = 0
    white_pawns = [0]*8; black_pawns = [0]*8
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == '.': continue
            v = VALUES.get(p.upper(), 0) + pst_score(p, r, c)
            score += v if is_white(p) else -v
            if p == 'P': white_pawns[c] += 1
            elif p == 'p': black_pawns[c] += 1

    for c in range(8):
        if white_pawns[c] > 1: score -= 20 * (white_pawns[c]-1)
        if black_pawns[c] > 1: score += 20 * (black_pawns[c]-1)
        if white_pawns[c] > 0:
            if (c==0 or white_pawns[c-1]==0) and (c==7 or white_pawns[c+1]==0):
                score -= 15
        if black_pawns[c] > 0:
            if (c==0 or black_pawns[c-1]==0) and (c==7 or black_pawns[c+1]==0):
                score += 15
    return score

def _mvv_lva(board, mv):
    _,_,nr,nc,flag = mv
    victim = board[nr][nc]
    if flag == 'ep': return 100
    if victim != '.':
        v_val = VALUES.get(victim.upper(), 0)
        a_val = VALUES.get(board[mv[0]][mv[1]].upper(), 0)
        return 1000 + v_val - a_val//10
    if flag == 'castle': return 50
    if flag and flag != 'ep': return 200
    return 0

def _order_moves(board, moves):
    return sorted(moves, key=lambda mv: _mvv_lva(board, mv), reverse=True)

def quiescence(board, alpha, beta, is_max, ep_sq, castling, deadline):
    if time.time() > deadline: return evaluate_board(board)
    stand_pat = evaluate_board(board)
    if is_max:
        if stand_pat >= beta: return beta
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha: return alpha
        beta = min(beta, stand_pat)

    color = 'W' if is_max else 'B'
    moves = legal_moves(board, color, ep_sq, castling)
    captures = [mv for mv in moves
                if board[mv[2]][mv[3]] != '.' or mv[4] in ('ep', 'Q','q','R','r','B','b','N','n')]
    for mv in _order_moves(board, captures):
        nb, nep, ncast = apply_move(board, mv, ep_sq, castling)
        v = quiescence(nb, alpha, beta, not is_max, nep, ncast, deadline)
        if is_max:
            alpha = max(alpha, v)
            if alpha >= beta: return beta
        else:
            beta = min(beta, v)
            if beta <= alpha: return alpha
    return alpha if is_max else beta

def minimax_chess(board, depth, alpha, beta, is_max, ep_sq, castling, deadline):
    if time.time() > deadline: return evaluate_board(board)
    color = 'W' if is_max else 'B'
    moves = legal_moves(board, color, ep_sq, castling)
    if not moves:
        return (-50000 + depth*100) if in_check(board, color, ep_sq, castling) else 0
    if depth == 0:
        return quiescence(board, alpha, beta, is_max, ep_sq, castling, deadline)

    for mv in _order_moves(board, moves):
        nb, nep, ncast = apply_move(board, mv, ep_sq, castling)
        v = minimax_chess(nb, depth-1, alpha, beta, not is_max, nep, ncast, deadline)
        if is_max:
            alpha = max(alpha, v)
            if alpha >= beta: return beta
        else:
            beta = min(beta, v)
            if beta <= alpha: return alpha
    return alpha if is_max else beta

def ai_choose(board, ep_sq, castling, depth=4, time_limit=5.0):
    moves = legal_moves(board, 'B', ep_sq, castling)
    if not moves: return None
    deadline = time.time() + time_limit
    best_mv = moves[0]; best_val = 10**9

    for mv in _order_moves(board, moves):
        nb, nep, ncast = apply_move(board, mv, ep_sq, castling)
        v = minimax_chess(nb, depth-1, -10**9, 10**9, True, nep, ncast, deadline)
        if v < best_val: best_val = v; best_mv = mv
        if time.time() > deadline: break
    return best_mv

# ─── Pygame ────────────────────────────────────────────────────────────────
def sq_rect(r,c): return pygame.Rect(c*CELL, r*CELL, CELL, CELL)

def draw_board(screen, board, sel, legal, last_move, check_r, check_c, font_piece):
    for r in range(8):
        for c in range(8):
            base = LIGHT_SQ if (r+c)%2==0 else DARK_SQ
            col  = base
            if (r,c)==(check_r,check_c): col=CHECK_CLR
            elif sel and (r,c)==(sel[0],sel[1]): col=(186,202,43)
            elif last_move and (r,c) in [(last_move[0],last_move[1]),(last_move[2],last_move[3])]:
                col=tuple(min(255,v+40) for v in base)
            pygame.draw.rect(screen,col,sq_rect(r,c))

    for mv in legal:
        nr,nc=mv[2],mv[3]
        cx,cy=nc*CELL+CELL//2, nr*CELL+CELL//2
        t=board[nr][nc]
        if t!='.':
            pygame.draw.rect(screen,(186,202,43,60),sq_rect(nr,nc),4)
        else:
            pygame.draw.circle(screen,(186,202,43),(cx,cy),12)

    for r in range(8):
        for c in range(8):
            p=board[r][c]
            if p=='.': continue
            u=UNICODE.get(p,'?')
            tc=WHITE if is_white(p) else (20,20,20)
            shadow_col=(80,80,80) if is_white(p) else (200,200,200)
            ps=font_piece.render(u,True,shadow_col)
            screen.blit(ps,(c*CELL+CELL//2-ps.get_width()//2+2,r*CELL+CELL//2-ps.get_height()//2+2))
            ps=font_piece.render(u,True,tc)
            screen.blit(ps,(c*CELL+CELL//2-ps.get_width()//2,r*CELL+CELL//2-ps.get_height()//2))

    for i in range(8):
        fc=pygame.font.SysFont(None,18)
        rs=fc.render(str(8-i),True,DARK_SQ if i%2==0 else LIGHT_SQ)
        screen.blit(rs,(3,i*CELL+3))
        cs=fc.render(chr(ord('a')+i),True,DARK_SQ if (i+7)%2==0 else LIGHT_SQ)
        screen.blit(cs,(i*CELL+CELL-12,BOARD_PX-16))

def main():
    pygame.init()
    screen=pygame.display.set_mode((W,H))
    pygame.display.set_caption("Bài 4 – Cờ Vua – Người (Trắng) vs Máy (Đen)")
    clock=pygame.time.Clock()

    def mkfont(sz,bold=False):
        for nm in ['segoeui','tahoma','arial']:
            try: return pygame.font.SysFont(nm,sz,bold=bold)
            except: pass
        return pygame.font.SysFont(None,sz)

    def mkufont(sz):
        for nm in ['segoeuisymbol','symbola','dejavusans','freesans','unifont']:
            try:
                f=pygame.font.SysFont(nm,sz)
                if f.render('♔',True,WHITE).get_width()>10: return f
            except: pass
        return pygame.font.SysFont(None,sz)

    fp=mkufont(52); ft=mkfont(20,True); fb=mkfont(16,True); fn=mkfont(14); fs=mkfont(12)

    board=new_board()
    castling={'WK':True,'WQ':True,'BK':True,'BQ':True}
    ep_sq=None; turn='W'
    sel=None; legal_for_sel=[]
    last_move=None; winner=None; ai_thinking=False; ai_timer=0; AI_DELAY=200
    history=[]; msg="Lượt của bạn (Trắng)"
    check_sq=(None,None)

    def reset():
        nonlocal board,castling,ep_sq,turn,sel,legal_for_sel,last_move
        nonlocal winner,ai_thinking,ai_timer,history,msg,check_sq
        board=new_board()
        castling={'WK':True,'WQ':True,'BK':True,'BQ':True}
        ep_sq=None; turn='W'; sel=None; legal_for_sel=[]
        last_move=None; winner=None; ai_thinking=False; ai_timer=0
        history=[]; msg="Lượt của bạn (Trắng)"; check_sq=(None,None)

    BTN_NEW=pygame.Rect(BOARD_PX+20, H-60, 200, 44)

    while True:
        dt=clock.tick(60)
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT: pygame.quit(); sys.exit()
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_r: reset()
            if ev.type==pygame.MOUSEBUTTONDOWN:
                mx,my=ev.pos
                if BTN_NEW.collidepoint(mx,my): reset(); continue
                if winner or ai_thinking or turn!='W': continue
                if mx>=BOARD_PX: continue
                c_click=mx//CELL; r_click=my//CELL
                if not in_board(r_click,c_click): continue

                if sel:
                    for mv in legal_for_sel:
                        if mv[2]==r_click and mv[3]==c_click:
                            board,ep_sq,castling=apply_move(board,mv,ep_sq,castling)
                            last_move=mv; history.append(mv); sel=None; legal_for_sel=[]
                            turn='B'
                            kr,kc=find_king(board,'B')
                            check_sq=(kr,kc) if in_check(board,'B',ep_sq,castling) else (None,None)
                            moves_b=legal_moves(board,'B',ep_sq,castling)
                            if not moves_b:
                                winner='W' if in_check(board,'B',ep_sq,castling) else 'D'
                                msg="Bạn THẮNG! Chiếu hết!" if winner=='W' else "HÒA! Stalemate."
                            else:
                                ai_thinking=True; ai_timer=0; msg="Máy đang suy nghĩ..."
                            break
                    else:
                        if piece_color(board[r_click][c_click])=='W':
                            sel=(r_click,c_click)
                            legal_for_sel=legal_moves(board,'W',ep_sq,castling)
                            legal_for_sel=[mv for mv in legal_for_sel if mv[0]==r_click and mv[1]==c_click]
                        else:
                            sel=None; legal_for_sel=[]
                else:
                    if piece_color(board[r_click][c_click])=='W':
                        sel=(r_click,c_click)
                        legal_for_sel=legal_moves(board,'W',ep_sq,castling)
                        legal_for_sel=[mv for mv in legal_for_sel if mv[0]==r_click and mv[1]==c_click]

        if ai_thinking and not winner:
            ai_timer+=dt
            if ai_timer>=AI_DELAY:
                ai_thinking=False
                mv=ai_choose(board,ep_sq,castling)
                if mv:
                    board,ep_sq,castling=apply_move(board,mv,ep_sq,castling)
                    last_move=mv; history.append(mv)
                    turn='W'
                    kr,kc=find_king(board,'W')
                    check_sq=(kr,kc) if in_check(board,'W',ep_sq,castling) else (None,None)
                    moves_w=legal_moves(board,'W',ep_sq,castling)
                    if not moves_w:
                        winner='B' if in_check(board,'W',ep_sq,castling) else 'D'
                        msg="Máy THẮNG! Chiếu hết!" if winner=='B' else "HÒA! Stalemate."
                    else:
                        msg="Lượt của bạn (Trắng)"
                        if check_sq[0] is not None: msg+=" – Bạn đang bị chiếu!"

        screen.fill(BG)
        draw_board(screen,board,sel,legal_for_sel,last_move,check_sq[0],check_sq[1],fp)

        px=BOARD_PX+5; py=0; pw=PANEL_W+5
        pygame.draw.rect(screen,PANEL_BG,(px,py,pw,H))
        iy=10

        def plbl(txt,f,col):
            nonlocal iy; s=f.render(txt,True,col)
            screen.blit(s,(px+(pw-s.get_width())//2,iy)); iy+=s.get_height()+5
        def pline():
            nonlocal iy; pygame.draw.line(screen,(70,75,85),(px+8,iy),(px+pw-8,iy),1); iy+=8
        def ptxt(txt,f,col,ox=10):
            nonlocal iy; s=f.render(txt,True,col)
            screen.blit(s,(px+ox,iy)); iy+=s.get_height()+4

        plbl("Cờ VUA", ft, (200,200,220)); pline()
        tc=GREEN if turn=='W' and not winner else (RED if winner else GRAY)
        plbl("Trắng (Bạn)" if turn=='W' else "Đen (Máy)", fb, tc)
        pline()

        mc=GREEN if winner=='W' else (RED if winner=='B' else (ORANGE if winner=='D' else WHITE))
        for part in [msg[i:i+25] for i in range(0,len(msg),25)]:
            ptxt(part,fn,mc)
        pline()

        ptxt("Luật chơi:", fb, (200,200,220))
        for rule in ["• Click quân để chọn","• Click ô xanh để đi",
                     "• Bạn chơi Trắng","• Chiếu hết = thắng"]:
            ptxt(rule,fs,(160,165,175))
        pline()

        ptxt("Lịch sử nước đi:", fb, (200,200,220))
        cols_map='abcdefgh'
        show=history[-10:]
        for i,mv in enumerate(show):
            r1,c1,r2,c2,_=mv
            mv_str=f"{cols_map[c1]}{8-r1}→{cols_map[c2]}{8-r2}"
            color_str="Trắng" if (len(history)-len(show)+i)%2==0 else "Đen"
            ptxt(f"{len(history)-len(show)+i+1}. {color_str}: {mv_str}",fs,(160,165,175))
        pline()

        ptxt("R = Ván mới",fs,(120,125,135))

        pygame.draw.rect(screen,BLUE,BTN_NEW,border_radius=8)
        bs=fb.render("VÁN MỚI (R)",True,WHITE)
        screen.blit(bs,(BTN_NEW.centerx-bs.get_width()//2,BTN_NEW.centery-bs.get_height()//2))

        if ai_thinking:
            dots="."*((pygame.time.get_ticks()//400)%4)
            ts=fs.render(f"AI đang tính{dots}",True,ORANGE)
            screen.blit(ts,(px+10,H-85))

        pygame.display.flip()

if __name__=="__main__":
    main()
