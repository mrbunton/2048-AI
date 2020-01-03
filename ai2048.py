from math import log
from game2048 import Game


###############
#HELPER METHODS
###############

def closest_upper (board,coord):
    ans = -1
    val = board[coord[1]][coord[0]]
    for y in range(4):
        for x in range(4):
            if [x,y] != coord and board[y][x] > val and (ans == -1 or ans > board[y][x]):
                ans = board[y,x]
    return ans


def closest_lower (board,coord):
    ans = -1
    val = board[coord[1]][coord[0]]
    for y in range(4):
        for x in range(4):
            if [x,y] != coord and board[y][x] < val and (ans == -1 or ans < board[y][x]):
                ans = board[y,x]
    return ans


def copy_board (a):
    ans = list([list(),list(),list(),list()])
    for i in range(4):
        for y in range(4):
            ans[i].append(a[i][y])
    return ans


def count_zeros (a):
    ans = 0
    for line in a:
        for square in line:
            if square == 0:
                ans+=1
    return ans
    


###################
#EVALUATION METHODS
###################

def e_effective_link(board, coord): # piece is trapped inbetween larger and smaller peace
    val = board[coord[1]][coord[0]]
    links = []
    for i in range(4):
        try:
            links.append(board[coord[1]+(i%2)*2-1][coord[0]+(i//2)*2-1])
        except:
            pass
    ans=0
    if closest_upper(board,coord) in links:
        ans+=0.5
    if closest_lower(board,coord) in links:
        ans+=0.5
    return ans
        
    
    
def e_power_corner(board): #largest peice in corner
    val = 0
    ans=True
    for y in range(4):
        for x in range(4):
            if board[y][x]>val:
                if not(x*y==0 or y == 4 or x==4):
                    ans = False
                else:
                    ans = True
                val = board[y][x]
    return int(ans)
                    
            
def e_power_corner_stability(board,coord): #given peice is stable in corner
    val = board[coord[1]][coord[0]]
    x_line = board[coord[1]]
    y_line = [board[i][coord[1]] for i in range(4)]
    return min(1,min(x_line),min(y_line))
    

def score(board):
    ans=0
    for line in board:
        for square in line:
            if square > 2:
                
                ans+= int(log(square,2)-1)*square
    return ans




#############################
#EVALUATION FUNCTIONS
#############################

#fct type 1
def basic_fct(subtrees):
    adv = 0
    for i in subtrees:
        adv+=i.value()
    if len(subtrees) == 0:
        return 0
    return int(adv/len(subtrees))
    
    

def basic_fct2(subtree):
    return score(subtree.cur.board)
    







################################
#POSSIBILITY TREE DATA STRUCTURE
################################

class Tree:
    cur: int # represents the board at the current state
    subtrees: list
    
    def __init__(self,cur, subtrees = []):
        self.cur = cur
        self.subtrees = subtrees

    def add(self,tree):
        self.subtrees.append(tree)



class Decision (Tree): #possible player moves

    def __init__(self,cur, subtrees = None,moves = None):
        self.cur = cur
        if subtrees is None:
            subtrees=list()
        self.subtrees = subtrees
        if moves is None:
            moves=list()
        self.moves = moves
        self.val = None

    
    def deduct(self): #deduct 'optimum' move according to model
        if not self.subtrees:
            self.val = 0
            return 0
        val = -1
        ans = -1
        for t,k in zip(self.subtrees, self.moves):
            if t.value()>val or ans ==-1:
                ans = k
                val = t.value()
        self.val = val
        return ans
    

    def value(self):
        if self.val is None:
            self.deduct()
            
        assert (self.val is not None)
            
        return self.val
    


class Reaction (Tree): # possible tile drops

    def __init__(self,cur,subtrees = None, fct = None, fct2 = None):
        self.cur = cur
        if subtrees is None:
            subtrees=list()
        self.subtrees = subtrees
        self.fct = fct
        self.fct2 = fct2
        self.val = None


    def value(self):
        if self.val is not None:
            return self.val
        if self.fct == None or self.fct2 == None:
            raise RuntimeError
        
        if not self.subtrees:
            return self.fct2(self)
        
        self.val = self.fct(self.subtrees)
        return self.val



def create_tree(o_game, turns_ahead, fct,fct2):
    game = Game()
    game.board = copy_board(o_game.board)
    tree = Decision(game, [])
    assert(not tree.subtrees)
    
    for move in range(1,5):
        #print("move", move)
        g = Game()
        g.board = copy_board(game.board)
        g.move(move)
        #g.pb()
        if g.board != game.board:
            tree.moves.append(move)
            subtree = Reaction(g,None,fct,fct2)
            #print("appending to tree",tree)
            tree.add(subtree)
            
            ast = count_zeros(g.board)*2
            #print("stage2")
            
            for k in range(ast):
                
                tg = Game()
                tg.board = copy_board(g.board)
                tg.spawn_tile(k%(ast//2),((k//(ast//2))*2+2),True)
                #print("appending to tree",subtree)
                if turns_ahead>1:
                    subtree.add(create_tree(tg,turns_ahead-1,fct,fct2))
    return tree
def find_move(game,m, fct, fct2):
    tree = create_tree(game,m,basic_fct,basic_fct2)
    return tree.deduct()
    

if __name__ == '__main__':
    game = Game()
    game.board=[[0,2,0,8],[0,0,0,4],[0,0,0,2],[0,0,0,0]]
    tree = create_tree(game,1,basic_fct,basic_fct2)
    game.pb()