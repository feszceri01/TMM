# usr/bin/env/python3

# CITS1401 Semester 1 2015 Project 2
# Student 1 Name: E.L.Fetzer            Student no: 21516694
# Twelve Men's Morris
# This is the completed skeleton code for the project
# completed using the graphics.py library provided by John M. Zelle

# this code is not meant to be necessarily readable! It's
# purpose is to solve a given problem!
from graphics import *
import random
import math

wSize = 600
allLocs = []
player_circles = [[], []]
player_colors = [color_rgb(255,255,228), color_rgb(0,0,0)]
bg_clr = color_rgb(92,129,152)
turn = 0
status = None

def main():
    # controls the flow of the program by calling methods to allow the players to put their pieces
    # and then move them; alternately, if a mill is made, invites the player to remove opponents
    # piece and decides which player has won. Uses the AImove function for Player 2 (the computer).
    global status
    global player_circles
    
    win = GraphWin("TMM", wSize, wSize)
    win.autoflush = False
    win.setBackground(bg_clr)
    win.setCoords(0, 0, wSize, wSize)
    optns = dispIntro(win)
    clearWin = Rectangle(Point(-wSize-5,-wSize-5), Point(wSize+5,wSize+5))
    clearWin.setFill(bg_clr)
    clearWin.draw(win)
    status = Text(Point(wSize/2, wSize/18), "")
    status.setSize(wSize//32)
    status.draw(win)
    ptList, btns = drawBoard(win)
    win.autoflush = True  

    # start the game
    while True: 
        player = optns[1]
        circles, occup, unOccup, linesOccup = setUpGame(win, ptList)
        playGame(win, ptList, occup, unOccup, linesOccup, player, circles, btns)


def neighbours(loc1, loc2):
    # returns true if there two vertices loc1 and loc2 are neighbouring adjacent
    # vertices of the allLoc point, false otherwise
    return ((abs(loc1[0] - loc2[0]) == 1 and loc1[1] == loc2[1]) or 
            (loc1[0] == loc2[0] and (loc1[1] - loc2[1] + 8) % 8) in {1, 7})


def blocked(Occup, unOccup):
    # Occup is a list of occupied points/locations by a Player and unOccup are free locations
    # returns True if all pieces of the Player are blocked, False otherwise.
    for oc in Occup:
        for un in unOccup:
            if neighbours(oc, un):
                return False  
    return True


def isLine(Occup, linesOccup):
    # Occup is a list of occupied locations by a Player and linesOccup are the Player's mills
    # returns True if a line (mill) has been made with the last move and updates linesOccup (mills)
    # otherwise returns False
    ret = False
    for loc1 in Occup:
        for loc2 in Occup:
            if not neighbours(loc1, loc2):
                continue
            for loc3 in Occup:
                if not neighbours(loc2, loc3):
                    continue
                # check that all the pieces are on the straight line
                if not (loc1[0] == loc3[0] or loc1[1] == loc3[1]):
                    continue
                if len({loc1[0], loc2[0], loc3[0]}) == 1 and loc2[1] % 2 != 1:
                    continue
                if loc1 == loc3:
                    continue
                if not ((loc1, loc2, loc3) in linesOccup or (loc3, loc2, loc1) in linesOccup):
                    linesOccup.append((loc1, loc2, loc3))
                    ret = True
    # update the mills
    for mill in linesOccup.copy():
        if not (mill[0] in Occup and mill[1] in Occup and mill[2] in Occup):
            linesOccup.remove(mill)
    return ret

def removePiece(win, ptList, Player, Occup, unOccup, linesOccup, Circles):
    # performs the removal of a piece as per the game rules
    # and updates Occup, unOccup and Circles lists. Uses the AIRemove function
    # to make a valid (intelligent) removal for Player 2 (the computer)
    removable = []
    for loc in Occup:
        in_line = False
        for line in linesOccup:
            if loc in line:
                in_line = True
                break
        if not in_line:
            removable.append(loc)
    if len(removable) == 0:
        status.setText("Player %d: No enemy piece can be removed" % (Player+1))
        time.sleep(1)
        return
    status.setText("Player %d: Select an enemy piece to remove" % (Player+1))
    if Player == 0:
        pt = win.getMouse()
        nn = findNN(pt, map(lambda x: ptList[x[0]][x[1]], removable))[0]
        loc = removable[nn]
    else:
        nn = AIremove(win, Occup, unOccup, Circles, Player, removable)
    loc = removable[nn]
    for i in range(4):
        Circles[loc[0]][loc[1]].setOutline(player_colors[Player-1])
        time.sleep(0.1)
        Circles[loc[0]][loc[1]].setOutline(player_colors[Player])
        time.sleep(0.1)
    time.sleep(0.5)
    hideCircle(win, Circles[loc[0]][loc[1]], player_colors[Player-1])
    Occup.remove(loc)
    unOccup.append(loc)


def AImove(win, ptList, cColor, Player, Occup, linesOccup, Circles, unOccup):
    # replaces the random function by this so that the computer (Player 2) performs a (very) intelligent move
    global status
    global player_circles
    
    isMove = not turn < 24
    if not isMove:
        status.setText("Player 2: Insert a piece to a position")
    else:
        status.setText("Player 2: Select a piece to move")
    time.sleep(0.5)
    nn = -1
    nn_1 = -1
    movable = []
    goodFlag = True
    if isMove:
        for loc in Occup:
            for un in unOccup:
                if neighbours(loc, un):
                    movable.append(loc)
                    break
    if not isMove:
        lOccup =  linesOccup.copy()
        for i, loc in enumerate(unOccup):
            if isLine(Occup+[loc], lOccup):
                nn = i
    else:
        for i, loc in enumerate(movable):
            for j, un in enumerate(unOccup):
                if neighbours(loc, un):
                    occup = Occup.copy()
                    lOccup = linesOccup.copy()
                    occup.remove(loc)
                    occup.append(un)
                    if isLine(occup, lOccup):
                        nn = i
                        nn_1 = j
                        break
            if nn >= 0:
                break
    if nn < 0:
        enemy = []
        for i in range(3):
            for j in range(8):
                if not ((i, j) in Occup or (i, j) in unOccup):
                    enemy.append((i, j))
        linesEnemy = []
        isLine(enemy, linesEnemy)
        if not isMove:
            for i, loc in enumerate(unOccup):
                if isLine(enemy+[loc], linesEnemy):
                    nn = i
            if nn < 0:
                nn = random.randint(0, len(unOccup)-1)
        else:
            for i, loc in enumerate(movable):
                for j, un in enumerate(unOccup):
                    if neighbours(loc, un):
                        if isLine(enemy + [un], linesEnemy):
                            nn = i
                            nn_1 = j
                            break
                if nn >= 0:
                    break
            if nn < 0:
                goodFlag = False
                nn = random.randint(0, len(movable) - 1)
                loc = movable[nn]
                adj = []
                for un in unOccup:
                    if neighbours(loc, un):
                        adj.append(un)
                nn = random.randint(0, len(adj) - 1)
                un = adj[nn]
    if not isMove:
        loc = unOccup[nn]
        moveCircle(win, player_circles[Player][-1], ptList[loc[0]][loc[1]])
        Circles[loc[0]][loc[1]] = player_circles[Player][-1]
        player_circles[Player] = player_circles[Player][:-1]
        unOccup.remove(loc)
        Occup.append(loc)
    else:
        if goodFlag:
            loc = movable[nn]
            un = unOccup[nn_1]
        status.setText('Player 2: Select a place to move the piece')
        Circles[loc[0]][loc[1]].setOutline(color_rgb(255, 255, 255))
        time.sleep(0.5)
        Circles[loc[0]][loc[1]].setOutline(cColor)
        moveCircle(win, Circles[loc[0]][loc[1]], ptList[un[0]][un[1]])
        Circles[un[0]][un[1]] = Circles[loc[0]][loc[1]]
        Circles[loc[0]][loc[1]] = None
        Occup.remove(loc)
        Occup.append(un)
        unOccup.remove(un)
        unOccup.append(loc)


def AIremove(win, Occup, unOccup, Circles, Player, removable):
    # extension to the above function. Replaces the random function by this so that the computer (Player 2)
    # performs a valid (intelligent) removal of an enemy piece and returns the index of the removable list to remove
    nn = -1
    if turn >= 24:
        for i, loc in enumerate(removable):
            for un in unOccup:
                if neighbours(loc, un):
                    occ = Occup.copy()
                    lOcc = []
                    isLine(occ, lOcc)
                    occ.remove(loc)
                    occ.append(un)
                    if isLine(occ, lOcc):
                        nn = i
                        break
            if nn >= 0:
                break
    else:
        for i, loc in enumerate(removable):
            for un in unOccup:
                occ = Occup.copy()
                lOcc = []
                isLine(occ, lOcc)
                occ.append(un)
                if isLine(occ, lOcc):
                    goodRemoveFlag = False
                    for mill in lOcc:
                        if loc in mill:
                            goodRemoveFlag = True
                            break
                    if goodRemoveFlag:
                        nn = i
                        break
            if nn >= 0:
                break
    if nn < 0:
        nn = random.randint(0, len(removable)-1)
    return nn


def movePiece(win, ptList, cColor, Player, Occup, linesOccup, Circles, unOccup):
    # this function performs a valid move for a Player (1 or 2) and updates the relevant lists.
    # it uses the AImove function to make a valid (intelligent) move for Player 2 (the computer)
    # win is the GraphWin object, ptList is defined in drawBoard(), cColor is the color of pieces,
    # Occup is a list of occupied locations by the Player, linesOccup is a list of lines (mills)
    # of the Player, Circles is a list of the circles (pieces) and unOccup is a list of unOccup locations
    if Player == 0:
        movable = []
        for loc in Occup:
            for un in unOccup:
                if neighbours(loc, un):
                    movable.append(loc)
                    break
        while True:
            status.setText('Player 1: Select a piece to move')
            pt = win.getMouse()
            nn = findNN(pt, map(lambda x: ptList[x[0]][x[1]], movable))[0]
            loc = movable[nn]
            adj = [loc]
            for un in unOccup:
                if neighbours(loc, un):
                    adj.append(un)
            Circles[loc[0]][loc[1]].setOutline(color_rgb(255, 255, 255))
            status.setText('Player 1: Select a place to move the piece')
            pt = win.getMouse()
            nn = findNN(pt, map(lambda x: ptList[x[0]][x[1]], adj))[0]
            un = adj[nn]
            Circles[loc[0]][loc[1]].setOutline("black")
            if nn != 0:
                break
        moveCircle(win, Circles[loc[0]][loc[1]], ptList[un[0]][un[1]])
        Circles[un[0]][un[1]] = Circles[loc[0]][loc[1]]
        Circles[loc[0]][loc[1]] = None
        Occup.remove(loc)
        unOccup.append(loc)
        unOccup.remove(un)
        Occup.append(un)
    else:
        AImove(win, ptList, cColor, Player, Occup, linesOccup, Circles, unOccup)


def drawBoard(win):
    # draws the board and populates the global list allLocs[] which contains all valid locations in ptList
    # returns ptList which is a 3x8 list of lists containing Point objects and btns which is a list of
    # Rectangle and Text objects representing widgets. At the top level ptList contains the 3 squares
    # (biggest first). At the second level, it contains the 8 Points that define each square
    # e.g. ptList[2][1] is the inner most square's 2nd Point. For each square, the bottom left is the
    # first Point.
    bk = wSize / 8
    ptList = []
    for i in range(1, 4):
        ptList.append([Point(bk*i,bk*i),Point(bk*i,4*bk),Point(bk*i,bk*(8-i)),Point(4*bk,bk*(8-i)),
                       Point(bk*(8-i),bk*(8-i)),Point(bk*(8-i), 4*bk),Point(bk*(8-i),bk*i),Point(4*bk,bk*i)])
        pp = Polygon(ptList[-1])
        pp.setWidth(6)
        pp.setOutline(color_rgb(255,255,0))
        pp.setOutline(color_rgb(223,223,203))
        pp.draw(win)
        for j in range(8):
            allLocs.append((i-1, j))
    for i in range(8):
        ll = Line(ptList[0][i], ptList[2][i])
        ll.setWidth(6)
        ll.setFill(color_rgb(255,255,0))
        ll.setFill(color_rgb(223,223,203))
        ll.draw(win)
    for i, p in allLocs:
        c = Circle(ptList[i][p], 5)
        c.setFill(color_rgb(200,200,180))
        c.draw(win)
    btns = [Rectangle(Point((wSize/2-wSize/8)/2,wSize//50),Point((wSize/2-wSize/8),wSize/11)),
            Rectangle(Point(wSize/2+wSize/8, wSize/50),Point(wSize/8*7-(wSize/8*7-wSize/2)/6,wSize/11)),
            Text(Point(((wSize/2-wSize/8)/2+(wSize/2-wSize/8))/2,(wSize/11+wSize/50)/2),"Play Again?"),
            Text(Point(((wSize/2+wSize/8)+(wSize/8*7-(wSize/8*7-wSize/2)/6))/2,(wSize/11+wSize/50)/2),"Quit?")]
    btns[0].setFill(color_rgb(255,255,245))
    btns[1].setFill(color_rgb(255,255,245))
    btns[2].setSize(wSize//45)
    btns[3].setSize(wSize//45)
    btns[2].setStyle("italic")
    btns[3].setStyle("italic")
    return ptList, btns


def setUpGame(win, ptList):
    # called each time a new round is started to set up the lists and player circles.
    # does not create a new window but rather discards previous references. Returns a
    # 3x8 list of lists containg references to Circle objects for the players, occup which
    # is a list of lists representing the players occupied positions, unOccup which is a
    # 3x8 list of lists containg the ptList positions which are unnocupied, and linesOccup
    # which is a list of lines (mills) of the Player
    win.autoflush = False
    if player_circles[0]:
        for i in range(len(player_circles[0])):
            player_circles[0][i].undraw()
    if player_circles[1]:
        for i in range(len(player_circles[1])):
            player_circles[1][i].undraw()         
    player_circles[0][:] = []
    player_circles[1][:] = []
    for i in range(12):
        player_circles[0].append(Circle(Point(wSize*0.05, wSize/16+wSize*7/8*i/(24/2-1)), wSize//34))
        player_circles[1].append(Circle(Point(wSize*0.95, wSize/16+wSize*7/8*i/(24/2-1)), wSize//34))
        player_circles[0][i].setFill(player_colors[0])
        player_circles[0][i].draw(win)
        player_circles[1][i].setFill(player_colors[1])
        player_circles[1][i].draw(win)
    circles       = []
    occup         = [[], []]
    linesOccup    = [[], []]
    win.autoflush = True
    for pl in ptList:
        circles.append([])
        for pt in pl:
            circles[-1].append(None)
    unOccup = allLocs.copy()
    return circles, occup, unOccup, linesOccup


def dispIntro(win):
    chkbox1 = Rectangle(Point(0.1*wSize,wSize/1.9), Point(0.15*wSize,wSize/1.75))
    chkbox2 = chkbox1.clone()
    chkbox2.move(0.75*wSize, 0)
    objects = [Text(Point(wSize/2, wSize/1.2),"QAT"),
               Text(Point(wSize/4, wSize/1.6),"Player 1"),
               Text(Point(wSize/(4/3), wSize/1.6),"Player 2"),
               chkbox1,
               chkbox2,
               Circle(Point((chkbox1.getP1().getX()+chkbox1.getP2().getX())/2,wSize/1.6),wSize//34),
               Circle(Point((chkbox2.getP1().getX()+chkbox2.getP2().getX())/2,wSize/1.6),wSize//34),
               Text(Point(chkbox1.getP2().getX()*1.5,(chkbox1.getP1().getY()+chkbox1.getP2().getY())/2),"Human"),
               Text(Point(chkbox2.getP2().getX()*0.85,(chkbox2.getP1().getY()+chkbox2.getP2().getY())/2),"Computer"),
               Rectangle(Point(0.4*wSize, wSize/30),Point(0.6*wSize, wSize/7.5)),
               Text(Point((0.6*wSize+0.4*wSize)/2,(wSize/30+wSize/7.5)/2),"Play"),
               Line(Point(chkbox1.getP1().getX(), wSize/1.25),Point(chkbox2.getP2().getX(),wSize/1.25)),
               Text(Point((chkbox1.getP1().getX()+chkbox2.getP2().getX())/2,wSize/1.375),"Select which player goes first")]
    objects[0].setStyle("bold")
    objects[0].setSize(wSize//26)
    objects[1].setSize(wSize//34)
    objects[2].setSize(wSize//34)
    objects[3].setFill(color_rgb(0,0,0))
    objects[5].setFill(player_colors[0])
    objects[6].setFill(player_colors[1])
    objects[-1].setSize(wSize//42)
    objects[-2].setWidth(3)
    objects[-3].setSize(wSize//36)
    objects[-5].setSize(wSize//44)
    objects[-6].setSize(wSize//44)
    for o in objects:
        o.draw(win)
    optns = [1,0]
    while True:
        pt = win.getMouse()
        if isClicked(pt, objects[3]):
            objects[3].setFill(color_rgb(0,0,0))
            objects[4].setFill(bg_clr)
            optns = [1,0]
        if isClicked(pt, objects[4]):
            objects[4].setFill(color_rgb(0,0,0))
            objects[3].setFill(bg_clr)
            optns = [0,1]
        if isClicked(pt, objects[-4]):
            break     
    return optns


def moveCircle(win, circle, dest):
    # animates the move of the selected player piece circle to a point dest on the board
    repetitions = circle.getRadius()
    cp = circle.getCenter()
    for i in range(circle.getRadius()):
        t = math.sin(i * math.pi / 2 / (repetitions-1))
        x = cp.getX() + (dest.getX() - cp.getX()) * t
        y = cp.getY() + (dest.getY() - cp.getY()) * t
        circle.move(int(x) - circle.getCenter().getX(), int(y) - circle.getCenter().getY())
        time.sleep((wSize/1500) / repetitions)
        

def hideCircle(win, circle, cColor):
    # animates the removal of a player piece circle in a position on the board
    repetitions = circle.getRadius()
    for i in range(repetitions, -1, -1):
        win.autoflush = False
        circle.undraw()
        win.autoflush = True
        circle = Circle(circle.getCenter(), i)
        circle.setFill(cColor)
        circle.draw(win)
        time.sleep(.25 / repetitions)
    circle.undraw()
    

def playGame(win, ptList, occup, unOccup, linesOccup, player, circles, btns):
    # helper function to play a round of Qat that modifies the parameter input lists
    # once a player wins lets the user decide to replay or quit the game. If the
    # user decides to quit, closes the window. Alternatively if the user decides
    # to replay, discards all the previous references and resets the game.
    global turn
		
    while True:
        if turn >= 24 and (blocked(occup[player], unOccup) or len(occup[player-1]) == 0):
            # game finished
            win.autoflush = False
            status.move(0, 0.89*wSize)
            status.setText("Player %d wins!" % (1-player+1))
            status.setFace("courier")
            status.setStyle("bold")
            status.setSize(wSize//26)
            for i in btns:
                i.draw(win)
            win.autoflush = True
            while True:
                pt = win.getMouse()
                if isClicked(pt, btns[0]):
                    for i in btns:
                        i.undraw()
                    occup[0][:] = []
                    occup[1][:] = []
                    status.setSize(wSize//32)
                    status.setFace("arial")
                    status.setStyle("normal")
                    status.move(0, -0.89*wSize)
                    if circles:
                        for i in circles:
                            for j in i:
                                if j:
                                    j.undraw()
                    turn = 0
                    break
                if isClicked(pt, btns[1]): 
                    win.close()
                    sys.exit(0)
            break
        status.setTextColor(player_colors[player])
        if player == 0:
            # user makes move
            if turn < 24:
                # insert new piece
                status.setText("Player 1: Insert a piece to a position")
                pt = win.getMouse()
                nn = findNN(pt, map(lambda x: ptList[x[0]][x[1]], unOccup))[0]
                loc = unOccup[nn]
                moveCircle(win, player_circles[player][-1], ptList[loc[0]][loc[1]])
                circles[loc[0]][loc[1]] = player_circles[player][-1]
                player_circles[player] = player_circles[player][:-1]
                occup[player].append(loc)
                unOccup.remove(loc)
            else:
                movePiece(win, ptList, player_colors[player], player, occup[player], linesOccup[player], circles, unOccup)
        else:
            # computer makes move
            AImove(win, ptList, player_colors[player], player, occup[player], linesOccup[player], circles, unOccup)
        if isLine(occup[player], linesOccup[player]):
            removePiece(win, ptList, player, occup[1-player], unOccup, linesOccup[1-player], circles)
        player = 1 - player
        turn += 1


def isClicked(pt, b):
    # returns true if the mouse clicked pt on an area bounded by a Rectangle object b
    return (pt.getX() >= b.getP1().getX() and pt.getX() <= b.getP2().getX() and 
            pt.getY() >= b.getP1().getY() and pt.getY() <= b.getP2().getY())


def findNN(pt, ptList):
    # finds the nearest location to a point pt in ptList so that the user is only required
    # to click near the location to place/select/move a piece and not exactly on top of it
    # returns the distance d and index location nn in ptList of the nearest point
    d = wSize * 2
    nn = -1
    for i, p in enumerate(ptList):
        dist = math.sqrt((pt.getX() - p.getX()) ** 2 + (pt.getY() - p.getY()) ** 2)
        if dist < d:
            d = dist 
            nn = i
    return nn, d


if __name__ == "__main__":
    main()
