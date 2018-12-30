import random


class Level:
    def __init__(self, filename):
        self.name = filename
        self.nbLine = 0
        self.nbCol = 0
        self.grid = []
        # S : start
        # B : blank
        # _ : wall
        # E : enemy
        # R : Trap
        # C : Crack
        # T : Treasure
        # W : sword
        # K : golden key
        # P : magic portal
        # M : moving platform

    # generate a labyrinth with a proportion of pw wall, po obstacles, pc cracks,
    # between 1 and max_key keys, 0 and max_sword swords and 0 and max_portal portals
    def generate_solvable(self, nb_line, nb_col, pw, po, pc, max_key, max_sword, max_portal):
        if nb_line < 4 or nb_col < 4:
            print("dimensions too small")
            return
        self.generate(nb_line, nb_col, pw, po, pc, max_key, max_sword, max_portal)
        cpt = 0
        while not self.solvable() and cpt < 10:
            self.generate(nb_line, nb_col, pw, po, pc, max_key, max_sword, max_portal)
            cpt += 1
        if cpt == 10:
            print("parameters are too bad to find a solvable solution, please lower pw, po or pc")
            self.grid = []
        else:
            print("grid generated")

    def generate(self, nb_line, nb_col, pw, po, pc, max_key, max_sword, max_portal):
        self.nbLine = nb_line
        self.nbCol = nb_col
        self.grid = []
        for i in range(nb_line):
            line = ['B'] * nb_col
            self.grid.append(line)
        for i in range(nb_line):
            for j in range(nb_col):
                if random.uniform(0, 1) < pw:
                    self.grid[i][j] = '_'
                elif random.uniform(0, 1) < po:
                    if random.randint(0, 1) == 0:
                        self.grid[i][j] = 'E'
                    else:
                        self.grid[i][j] = 'R'
                elif random.uniform(0, 1) < pc:
                    self.grid[i][j] = 'C'
        for key in range(max_sword):
            self.grid[random.randint(0, nb_line-1)][random.randint(0, nb_col-1)] = 'W'
        for key in range(max_portal):
            self.grid[random.randint(0, nb_line-1)][random.randint(0, nb_col-1)] = 'P'
        for key in range(max_key):
            self.grid[random.randint(0, nb_line-1)][random.randint(0, nb_col-1)] = 'K'
        self.grid[0][0] = 'T'
        self.grid[self.nbLine - 1][self.nbCol - 1] = 'S'

    def load(self):
        file = open(self.name, "r")
        for line in file:
            if "lines : " in line:
                self.nbLine = int(line[8:])
            elif "columns : " in line:
                self.nbCol = int(line[9:])
            else:
                self.grid.append(line.strip('\n').split(","))

    def save(self):
        file = open(self.name, "w")
        file.write("lines : " + str(self.nbLine) + '\n')
        file.write("columns : " + str(self.nbCol) + '\n')
        for line in self.grid:
            tmp = ""
            for char in line:
                tmp += char+","
            file.write(tmp[:-1] + '\n')

    def display(self):
        for line in self.grid:
            for char in line:
                print(char+" ", end='')
            print()

    def player_display(self, y, x, life):
        print("life :" + str(life))
        tmp = self.grid[y][x]
        self.grid[y][x] = u"\u25A1"
        for line in self.grid:
            for char in line:
                print(char+" ", end='')
            print()
        self.grid[y][x] = tmp

    def solvable(self):
        if self.grid:
            if not self.has_key():
                return False
            if not self.way_possible("K"):
                return False
            if not self.way_possible("T"):
                return False
            return True
        else:
            print("grid not loaded")
            return False

    def has_key(self):
        for row in self.grid:
            for cell in row:
                if cell == "K":
                    return True
        return False

    def way_possible(self, objective):
        Q = []
        visited = []
        Q.append([self.nbLine - 1, self.nbCol - 1])
        visited.append([self.nbLine - 1, self.nbCol - 1])  # start is visited
        while len(Q) > 0:
            node = Q.pop()
            neighbours = [[node[0] - 1, node[1]], [node[0] + 1, node[1]], [node[0], node[1] - 1],
                          [node[0], node[1] + 1]]
            for n in neighbours:
                if 0 <= n[0] < self.nbLine and 0 <= n[1] < self.nbCol:
                    if self.grid[n[0]][n[1]] == objective:
                        return True
                    else:
                        if self.grid[n[0]][n[1]] != "_" and self.grid[n[0]][n[1]] != "C":
                            if n not in visited:
                                Q.append(n)
                                visited.append(n)
        return False