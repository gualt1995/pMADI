import game
import player
import os

level_1 = game.Level("Level_1")
level_1.load()
#level_1.generate_solvable(8,30,0.3,0.1,0.1,1,1,3)
print("is level solvable " + str(level_1.solvable()))
print("level layout : ")
level_1.display()
#level_1.save()
#print(u"\u25C7")
input("Press Enter to continue, use ZSQD to move")
os.system('cls')
p1 = player.Player(level_1)
level_1.player_display(p1.y_pos, p1.x_pos, p1.life)
#p1.move_down()

while not p1.win and not p1.is_dead():
    moved = False
    key = player.getKey()
    #print(key[0])
    if key[0] == 122:
        moved = p1.move_up()  # z
    elif key[0] == 115:
        moved = p1.move_down()  # s
    elif key[0] == 113:
        moved = p1.move_left()  # q
    elif key[0] == 100:
        moved = p1.move_right()  # d
    if moved:
        chain = p1.grid_reaction()
        while chain:
            chain = p1.grid_reaction()
        os.system('cls')
        level_1.player_display(p1.y_pos, p1.x_pos, p1.life)

if p1.life == 0:
    if level_1.grid[p1.y_pos][p1.x_pos] == 'C':
        print("you feel into a crack and died")
    elif level_1.grid[p1.y_pos][p1.x_pos] == 'E':
        print("an enemy killed you")
    elif level_1.grid[p1.y_pos][p1.x_pos] == 'R':
        print("you walked into a deadly trap")
    else:
        print("you died")
else:
    print("you won")
input("Press Enter to close")
