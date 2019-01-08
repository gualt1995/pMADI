import copy
import random
import numpy as np

class Solver:
    def __init__(self,level):
        #  reward function
        self.dead = -100
        self.r = {
            'S': -1,    # start without treasure
            'B': -1,    # blank
            '_': -10,   # wall
            'E': -1,   # enemy
            'R': -1,   # trap
            'C': self.dead,   # crack
            'T': -1,    # treasure without key
            'W': 1000000000000000,    # sword
            'K': -1,    # key
            'P': -1,   # portal
            'M': -1    # moving platform
        }
        self.a = {
            0: 'u',
            1: 'd',
            2: 'r',
            3: 'l'
        }
        #  transition towards the following cells (normalized when calculated)
        #  everything at one except the following :
        #  R : dead 0.1 Start 0.3 nothing 0.6
        #  P : every cell except walls
        #  M : available cells around
        # initialize V0
        self.v = []
        for line in range(0, level.nbLine):
            self.v.append([[0, 0]]*level.nbCol)
        self.has_sword = False
        '''v_key = []
        for line in range(0, level.nbLine):
            v_key.append([0]*level.nbCol)
        v_treasure = []
        for line in range(0, level.nbLine):
            v_treasure.append([0]*level.nbCol)'''
        self.level = level

    def value_iteration(mdp, epsilon=0.001):
        "Solving an MDP by value iteration. [Fig. 17.4]"
        U1 = dict([(s, 0) for s in mdp.states])
        R, T, gamma = mdp.R, mdp.T, mdp.gamma
        while True:
            U = U1.copy()
            delta = 0
            for s in mdp.states:
                U1[s] = R(s) + gamma * max([sum([p * U[s1] for (p, s1) in T(s, a)])
                                            for a in mdp.actions(s)])
                delta = max(delta, abs(U1[s] - U[s]))
            if delta < epsilon * (1 - gamma) / gamma:
                return U


    def value_iteration(self, gamma, epsilon):
        a = ['u', 'd', 'r', 'l']
        # TODO add randomness for certain cells
        v = copy.deepcopy(self.v)
        while True:
            prev_v = copy.deepcopy(v)
            delta = 0
            #print(delta)
            for y in range(0, self.level.nbLine):
                for x in range(0, self.level.nbCol):
                    q = []
                    for action in a:
                        ra = -10000
                        p1 = 0.0
                        if action == 'u':
                            if y > 0:
                                if self.level.grid[y - 1][x] != '_':
                                    ra = self.r[self.level.grid[y - 1][x]]
                                    p1 = self.get_possible_moves(y-1, x, prev_v)
                        elif action == 'd':
                            if y < self.level.nbLine-2:
                                if self.level.grid[y + 1][x] != '_':
                                    ra = self.r[self.level.grid[y+1][x]]
                                    p1 = self.get_possible_moves(y + 1, x, prev_v)
                        elif action == 'l':
                            if x > 0:
                                if self.level.grid[y][x - 1] != '_':
                                    ra = self.r[self.level.grid[y][x-1]]
                                    p1 = self.get_possible_moves(y, x - 1, prev_v)

                        else:
                            if x < self.level.nbCol - 1:
                                if self.level.grid[y][x + 1] != '_':
                                    ra = self.r[self.level.grid[y][x+1]]
                                    p1 = self.get_possible_moves(y, x + 1, prev_v)
                        q.append(ra + gamma * p1)

                    #print(max(q))
                    #print(v[y][x], prev_v[y][x], max(q))
                    v[y][x] = q
                    #print(v[y][x], prev_v[y][x], max(q))
                    #print("------------------------------------------")
                    delta = max(delta, abs(max(prev_v[y][x]) - max(v[y][x])))
            print(delta)
            if delta < epsilon:
                for line in v:
                    for cell in line:
                        print(str(cell)+'#####', end='')
                    print()
                return v

    def best_policy(self, v):
        res = []
        for y in range(0, self.level.nbLine):
            line = []
            for x in range(0, self.level.nbCol):
                line.append(self.a[v[y][x].index(max(v[y][x]))])
            res.append(line)
        return res

    def display(self, v):
        for y in range(0, self.level.nbLine):
            for x in range(0, self.level.nbCol):
                if self.level.grid[y][x] != '_':
                    print(self.a[v[y][x].index(max(v[y][x]))] + " ", end='')
                else:
                    print("_ ", end='')
            print()

    def get_possible_moves(self, y, x, prev_v):
        #  any state where dead = -1000
        if self.level.grid[y][x] == 'M':
            cpt = 0
            p = []
            if y > 0:
                cpt += 1
                p.append(max(prev_v[y-1][x]))
            if y < self.level.nbLine - 2:
                cpt += 1
                p.append(max(prev_v[y+1][x]))
            if x > 0:
                cpt += 1
                p.append(max(prev_v[y][x-1]))
            if x < self.level.nbCol - 1:
                cpt += 1
                p.append(max(prev_v[y][x+1]))
            p1 = 0
            for num in p:
                p1 += num * 1/cpt
            return p1
        if self.level.grid[y][x] == 'T':
            p1 = 0.1 * self.dead + 0.3 * max(prev_v[self.level.nbCol - 1][self.level.nbLine - 1]) + \
                 0.6 * max(prev_v[y][x])
            return p1
        if self.level.grid[y][x] == 'C':
            return -1000
        if self.level.grid[y][x] == 'E':
            if self.has_sword:
                return max(prev_v[y][x])
            else:
                return 0.7 * max(prev_v[y][x]) + 0.3 * self.dead #  loosing hp
        if self.level.grid[y][x] == 'P':
            p = []
            cpt = 0
            for y in range(0, self.level.nbLine):
                for x in range(0, self.level.nbCol):
                    if self.level.grid[y][x] != '_':
                        if self.level.grid[y][x] != 'C':
                            p.append(max(prev_v[y][x]))
                        else:
                            p.append(self.dead)
                        cpt += 1
            p1 = 0
            for num in p:
                p1 += 1/cpt * num
            #print(p)
            return p1
        return max(prev_v[y][x])

    def policy_iteration(self, gamma, epsilon):
        #TODO change p0
        a = ['u', 'd', 'r', 'l']
        p0 = []
        vars = []
        for y in range(0, self.level.nbLine):
            line = []
            for x in range(0, self.level.nbCol):
                vars.append(str(y)+ str(x))
                line.append(random.choice(a))
            p0.append(line)
        rest = []
        eqs = []
        dt = copy.deepcopy(p0)
        while True:
            for y in range(0, self.level.nbLine):
                for x in range(0, self.level.nbCol):
                    eq = dict.fromkeys(vars, 0)
                    eq['dead'] = 0
                    eq[str(y)+str(x)] = -1  # voir les equations
                    if dt[y][x] == 'u':
                        if y > 0:
                            if self.level.grid[y - 1][x] != '_':
                                rest.append(self.r[self.level.grid[y - 1][x]])
                                self.set_variables(y - 1, x, eq, gamma)
                    elif dt[y][x] == 'd':
                        if y < self.level.nbLine - 2:
                            if self.level.grid[y + 1][x] != '_':
                                rest.append(self.r[self.level.grid[y + 1][x]])
                                self.set_variables(y + 1, x, eq, gamma)
                    elif dt[y][x] == 'l':
                        if x > 0:
                            if self.level.grid[y][x - 1] != '_':
                                rest.append(self.r[self.level.grid[y][x - 1]])
                                self.set_variables(y, x - 1, eq, gamma)

                    else:
                        if x < self.level.nbCol - 1:
                            if self.level.grid[y][x + 1] != '_':
                                rest.append(self.r[self.level.grid[y][x + 1]])
                                self.set_variables(y, x + 1, eq, gamma)
                    eqs.append(eq)
            x = np.linalg.solve(eqs, rest)
            #TODO build dt1
            dt1 = []
            for y in range(0, self.level.nbLine):
                for x in range(0, self.level.nbCol):
                    for act in action:
                        dt1[y][x] = 0
                    q = []
                    for action in a:
                        ra = -10000
                        p1 = 0.0


                    # print(max(q))
                    # print(v[y][x], prev_v[y][x], max(q))
                    v[y][x] = q
                    # print(v[y][x], prev_v[y][x], max(q))
                    # print("------------------------------------------")
                    delta = max(delta, abs(max(prev_v[y][x]) - max(v[y][x])))
            print(delta)
            if delta < epsilon:
                for line in v:
                    for cell in line:
                        print(str(cell) + '#####', end='')
                    print()
                return v

    def set_variables(self, y, x, eq, gamma):
        #  any state where dead = -1000
        if self.level.grid[y][x] == 'M':
            cpt = 0
            p = []
            if y > 0:
                cpt += 1
                p.append(str(y - 1) + str(x))
            if y < self.level.nbLine - 2:
                cpt += 1
                p.append(str(y + 1) + str(x))
            if x > 0:
                cpt += 1
                p.append(str(y) + str(x - 1))
            if x < self.level.nbCol - 1:
                cpt += 1
                p.append(str(y) + str(x + 1))
            for num in p:
                eq[num] = 1/cpt * gamma
            return
        if self.level.grid[y][x] == 'T':
            eq['dead'] = 0.1 * gamma
            eq[str(self.level.nbCol - 1)+str(self.level.nbLine - 1)] = 0.3 * gamma
            eq[str(y) + str(x)] = 0.6 * gamma
            return
        if self.level.grid[y][x] == 'C':
            eq['dead'] = 1
            return
        if self.level.grid[y][x] == 'E':
            if self.has_sword:
                eq[str(y) + str(x)] = 1 * gamma
            else:
                eq[str(y) + str(x)] = 0.7 * gamma
                eq['dead'] = 0.3 * gamma
            return
        if self.level.grid[y][x] == 'P':
            p = []
            cpt = 0
            nb_dead = 0
            for y in range(0, self.level.nbLine):
                for x in range(0, self.level.nbCol):
                    if self.level.grid[y][x] != '_':
                        if self.level.grid[y][x] != 'C':
                            p.append(str(y) + str(x))
                        else:
                            nb_dead += 1
                        cpt += 1
            eq['dead'] = nb_dead/cpt * gamma
            for var in p:
                eq[var] = 1/cpt * gamma
            return
        eq[str(y) + str(x)] = 1 * gamma
        return
