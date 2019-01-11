import copy
import random
import numpy as np

class Solver:
    def __init__(self,level):
        self.level = level
        self.damage = -10.0
        self.objective = 1000
        self.has_sword = False
        #self.v = []
        self.dead = -500

        #  reward function
        self.r = {
            'default': {
                'S': -1,  # start without treasure
                'B': -1,  # blank
                '_': -1000,  # wall
                'E': -1,  # enemy
                'R': -1,  # trap
                'C': -1,  # crack
                'T': -1,  # treasure without key
                'W': 500,  # sword
                'K': 1000,  # key
                'P': -1,  # portal
                'M': -1  # moving platform
            },
            'with_sword': {
                'W': -1
            },
            'with_key': {
                'K': -1,
                'T': 1000,
            },
            'with_treasure': {
                'S': 1000,
                'T':-1
            }
        }
        self.a = {
            0: 'u',
            1: 'd',
            2: 'r',
            3: 'l'
        }
        # initialize V0

    def get_reward(self, has_key=False, has_sword=False, has_treasure=False):
        reward = self.r['default'].copy()

        if has_key:
            reward['K'] = self.r['with_key']['K']
            reward['T'] = self.r['with_key']['T']
        if has_sword:
            reward['W'] = self.r['with_sword']['W']
        if has_treasure:
            reward['S'] = self.r['with_treasure']['S']
            reward['T'] = self.r['with_treasure']['T']
        return reward

    def buit_states(self):
        v = []
        for line in range(0, self.level.nbLine):
            v.append([[0, 0]]*self.level.nbCol)
        return v

    def solve_v_a(self, gamma, epsilon):
        return {
            (False, False, False, True): self.value_iteration(gamma, epsilon, self.get_reward(), True),
            (False, False, True, True): self.value_iteration(gamma, epsilon, self.get_reward(has_treasure=True), True),
            (False, True, False, True): self.value_iteration(gamma, epsilon, self.get_reward(has_sword=True), True),
            (False, True, True, True): self.value_iteration(gamma, epsilon, self.get_reward(has_sword=True, has_treasure=True), True),
            (True, False, False, True): self.value_iteration(gamma, epsilon, self.get_reward(has_key=True), True),
            (True, False, True, True): self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_treasure=True), True),
            (True, True, False, True): self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_sword=True), True),
            (True, True, True, True): self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_sword=True,has_treasure=True), True),
            (False, False, False, False): self.value_iteration(gamma, epsilon, self.get_reward(), False),
            (False, False, True, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_treasure=True), False),
            (False, True, False, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_sword=True), False),
            (False, True, True, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_sword=True, has_treasure=True), False),
            (True, False, False, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_key=True), False),
            (True, False, True, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_treasure=True), False),
            (True, True, False, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_sword=True), False),
            (True, True, True, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_sword=True,has_treasure=True), False)
        }

    def solve_p_i(self,gamma):
        self.policy_iteration(gamma, self.get_reward())

    def value_iteration(self, gamma, epsilon, r, critcal):
        a = ['u', 'd', 'r', 'l']
        v = self.buit_states()
        while True:
            prev_v = copy.deepcopy(v)
            delta = 0
            for y in range(0, self.level.nbLine):
                for x in range(0, self.level.nbCol):
                    q = []
                    for action in a:
                        ra = -10000  # if cell is a wall
                        p1 = 0.0
                        if action == 'u':
                            if y > 0:
                                if self.level.grid[y - 1][x] != '_':
                                    ra = r[self.level.grid[y - 1][x]]
                                    p1 = self.get_possible_moves(y-1, x, prev_v, critcal)
                        elif action == 'd':
                            if y < self.level.nbLine - 1:
                                if self.level.grid[y + 1][x] != '_':
                                    ra = r[self.level.grid[y+1][x]]
                                    p1 = self.get_possible_moves(y + 1, x, prev_v, critcal)
                        elif action == 'l':
                            if x > 0:
                                if self.level.grid[y][x - 1] != '_':
                                    ra = r[self.level.grid[y][x-1]]
                                    p1 = self.get_possible_moves(y, x - 1, prev_v, critcal)
                        else:
                            if x < self.level.nbCol - 1:
                                if self.level.grid[y][x + 1] != '_':
                                    ra = r[self.level.grid[y][x+1]]
                                    p1 = self.get_possible_moves(y, x + 1, prev_v, critcal)
                        q.append(ra + gamma * p1)
                    v[y][x] = q
                    delta = max(delta, abs(max(prev_v[y][x]) - max(v[y][x])))
            if delta < epsilon:
                return self.best_policy(v)

    def best_policy(self, v):
        res = []
        for y in range(0, self.level.nbLine):
            line = []
            for x in range(0, self.level.nbCol):
                line.append(self.a[v[y][x].index(max(v[y][x]))])
            res.append(line)
        return res

    def display_policy(self, p):
        print("displaying policy")
        for y in range(0, self.level.nbLine):
            for x in range(0, self.level.nbCol):
                if self.level.grid[y][x] != '_':
                    print(p[y][x] + " ", end='')
                else:
                    print("_ ", end='')
            print()
        print()

    def display(self, v):
        for y in range(0, self.level.nbLine):
            for x in range(0, self.level.nbCol):
                if self.level.grid[y][x] != '_':
                    print(self.a[v[y][x].index(max(v[y][x]))] + " ", end='')
                else:
                    print("_ ", end='')
            print()

    def get_possible_moves(self, y, x, prev_v, critcal):
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
        if self.level.grid[y][x] == 'R':
            loose = self.damage
            if critcal:
                loose = self.dead
            p1 = 0.1 * loose + 0.3 * max(prev_v[self.level.nbCol - 1][self.level.nbLine - 1]) + \
                 0.6 * max(prev_v[y][x])
            return p1
        if self.level.grid[y][x] == 'C':
            return self.dead
        if self.level.grid[y][x] == 'E':
            loose = self.damage
            if critcal:
                loose = self.dead
            if self.has_sword:
                return max(prev_v[y][x])
            else:
                return 0.7 * max(prev_v[y][x]) + 0.3 * loose
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

    def policy_iteration(self, gamma, r):
        #  building the initial policy
        a = ['u', 'd', 'l', 'r']
        p0 = []
        vars = []
        for y in range(0, self.level.nbLine):
            line = []
            for x in range(0, self.level.nbCol):
                line.append('u')
                vars.append(str(y) + str(x))
            p0.append(line)
        rest = []
        eqs = []
        dt = copy.deepcopy(p0)
        while True:
            for line in dt:
                print(line)
            eqs = []
            rest = []
            ctn = False
            for y in range(0, self.level.nbLine):
                for x in range(0, self.level.nbCol):
                    eq = dict.fromkeys(vars, 0)
                    eq['dead'] = 0  # adding variable for death
                    eq[str(y)+str(x)] = -1  # see policy iterations equations
                    if dt[y][x] == 'u':
                            if self.level.grid[y - 1][x] != '_' and y > 0:
                                rest.append(r[self.level.grid[y - 1][x]] * -1)
                                self.set_variables(y - 1, x, eq, gamma)
                            else:
                                rest.append(r[self.level.grid[y][x]] * -1)
                    elif dt[y][x] == 'd':
                            if self.level.grid[y + 1][x] != '_' and y < self.level.nbLine - 1:
                                rest.append(r[self.level.grid[y + 1][x]] * -1)
                                self.set_variables(y + 1, x, eq, gamma)
                            else:
                                rest.append(r[self.level.grid[y][x]] * -1)
                    elif dt[y][x] == 'l':
                            if self.level.grid[y][x - 1] != '_' and x > 0:
                                rest.append(r[self.level.grid[y][x - 1]] * -1)
                                self.set_variables(y, x - 1, eq, gamma)
                            else:
                                rest.append(r[self.level.grid[y][x]] * -1)
                    else:
                            if self.level.grid[y][x + 1] != '_' and x < self.level.nbCol - 1:
                                rest.append(r[self.level.grid[y][x + 1]] * -1)
                                self.set_variables(y, x + 1, eq, gamma)
                            else:
                                rest.append(r[self.level.grid[y][x]] * -1)
                    eqs.append(list(eq.values()))
            #adding equation if U died

            for line in eqs:
                print(line)

            eqdeath = dict.fromkeys(vars, 0)
            eqdeath[len(eqdeath)-1] = 1
            rest.append(self.dead)
            eqs.append(list(eqdeath.values()))
            ar = np.linalg.solve(eqs, rest)
            dt1 = []
            for y in range(0, self.level.nbLine):
                line = []
                for x in range(0, self.level.nbCol):
                    line.append(ar[x + y])
                dt1.append(line)

            print(dt1)
            print(len(rest))

            self.dead = ar[len(ar) - 1]
            for y in range(0, self.level.nbLine):
                for x in range(0, self.level.nbCol):
                    value = dict()
                    for act in a:
                        if act == 'u':
                            if y > 0:
                                if self.level.grid[y - 1][x] != '_':
                                    p1 = self.get_possible_move(y - 1, x, dt1) * gamma * r[self.level.grid[y - 1][x]]
                                    value[act] = p1
                        elif act == 'd':
                            if y < self.level.nbLine - 2:
                                if self.level.grid[y + 1][x] != '_':
                                    p1 = self.get_possible_move(y + 1, x, dt1) * gamma * r[self.level.grid[y + 1][x]]
                                    value[act] = p1
                        elif act == 'l':
                            if x > 0:
                                if self.level.grid[y][x - 1] != '_':
                                    p1 = self.get_possible_move(y, x - 1, dt1,) * gamma * r[self.level.grid[y][x - 1]]
                                    value[act] = p1
                        else:
                            if x < self.level.nbCol - 1:
                                if self.level.grid[y][x + 1] != '_':
                                    p1 = self.get_possible_move(y, x + 1, dt1) * gamma * r[self.level.grid[y][x + 1]]
                                    value[act] = p1
                    update = max(value, key=value.get)
                    if dt[y][x] != update:
                        ctn = True
                    dt[y][x] = update
            if not ctn:
                return

    def get_possible_move(self, y, x, prev_v):
        #  any state where dead = -1000
        if self.level.grid[y][x] == 'M':
            cpt = 0
            p = []
            if y > 0:
                cpt += 1
                p.append(prev_v[y - 1][x])
            if y < self.level.nbLine - 2:
                cpt += 1
                p.append(prev_v[y + 1][x])
            if x > 0:
                cpt += 1
                p.append(prev_v[y][x - 1])
            if x < self.level.nbCol - 1:
                cpt += 1
                p.append(prev_v[y][x + 1])
            p1 = 0
            for num in p:
                p1 += num * 1 / cpt
            return p1
        if self.level.grid[y][x] == 'R':
            p1 = 0.1 * self.damage + 0.3 * prev_v[self.level.nbCol - 1][self.level.nbLine - 1] + 0.6 * prev_v[y][x]
            return p1
        if self.level.grid[y][x] == 'C':
            return self.dead
        if self.level.grid[y][x] == 'E':
            if self.has_sword:
                return prev_v[y][x]
            else:
                return 0.7 * prev_v[y][x] + 0.3 * self.damage
        if self.level.grid[y][x] == 'P':
            p = []
            cpt = 0
            for y in range(0, self.level.nbLine):
                for x in range(0, self.level.nbCol):
                    if self.level.grid[y][x] != '_':
                        if self.level.grid[y][x] != 'C':
                            p.append(prev_v[y][x])
                        else:
                            p.append(self.dead)
                        cpt += 1
            p1 = 0
            for num in p:
                p1 += 1 / cpt * num
            # print(p)
            return p1
        return prev_v[y][x]



    def set_variables(self, y, x, eq, gamma):
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
        elif self.level.grid[y][x] == 'R':
            eq['dead'] = 0.1 * gamma
            eq[str(self.level.nbCol - 1)+str(self.level.nbLine - 1)] = 0.3 * gamma
            eq[str(y) + str(x)] = 0.6 * gamma
        elif self.level.grid[y][x] == 'C':
            eq['dead'] = 1
        elif self.level.grid[y][x] == 'E':
            if self.has_sword:
                eq[str(y) + str(x)] = 1 * gamma
            else:
                eq[str(y) + str(x)] = 0.7 * gamma
                eq['dead'] = 0.3 * gamma
            return
        elif self.level.grid[y][x] == 'P':
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
        else:
            eq[str(y) + str(x)] = 1 * gamma

