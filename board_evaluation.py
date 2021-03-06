from ai2048 import e_effective_link as link,e_power_corner as corner,e_power_corner_stability as stab,score,entrapment
#link,corner,stab
def function(subtree):
    board = subtree.cur.board
    ans = 0
    for y in range(4):
        for x in range(4):
            ans+=board[y][x]*link(board,[x,y])
    
    ans+=score(board)
    k=corner(board)
    ans+=k[0]*k[1]
    for y in range(4):
        for x in range(4):
            ans+=board[y][x]*link(board,[x,y])
            ans-=entrampment(board,[x,y])
    return int(ans)
