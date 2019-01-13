import copy
import time

def timer(f):
    def wrapper(*args):
        t0=time.time()
        res=f(*args)
        t='%.2f' % (time.time()-t0)
        print("Temps d'execution : ",t," secondes")
        return res
    return wrapper


class Solver:
    def __init__(self, level):
        self.level = level
        self.damage = -2
        self.objective = 1000
        self.has_sword = False
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

    @timer
    def solve_v_a(self, gamma, epsilon):
        return {
            (False, False, False, True): self.value_iteration(gamma, epsilon, self.get_reward(), True, False),
            (False, True, False, True): self.value_iteration(gamma, epsilon, self.get_reward(has_sword=True), True, True),
            (True, False, False, True): self.value_iteration(gamma, epsilon, self.get_reward(has_key=True), True),
            (True, False, True, True): self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_treasure=True), True),
            (True, True, False, True): self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_sword=True), True, True),
            (True, True, True, True): self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_sword=True,has_treasure=True), True, True),
            (False, False, False, False): self.value_iteration(gamma, epsilon, self.get_reward(), False),
            (False, True, False, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_sword=True), False, True),
            (True, False, False, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_key=True), False),
            (True, False, True, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_treasure=True), False),
            (True, True, False, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_sword=True), False, True),
            (True, True, True, False):  self.value_iteration(gamma, epsilon, self.get_reward(has_key=True, has_sword=True,has_treasure=True), False, True)
        }

    def value_iteration(self, gamma, epsilon, r, critcal, has_sword=False):
        self.has_sword = has_sword
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
                        #if self.level.grid[y][x] not in ('P', 'M'):
                        if action == 'u':
                            if y > 0:
                                if self.level.grid[y - 1][x] != '_':
                                    ra = r[self.level.grid[y - 1][x]]
                                    p1 = self.get_possible_moves(y-1, x, prev_v, critcal)
                        elif action == 'd':
                            if y < self.level.nbLine - 1:
                                if self.level.grid[y + 1][x] != '_':
                                    ra = r[self.level.grid[y+1][x]]
                                    p1 = self.get_possible_moves(y + 1, x, prev_v,critcal)
                        elif action == 'l':
                            if x > 0:
                                if self.level.grid[y][x - 1] != '_':
                                    ra = r[self.level.grid[y][x-1]]
                                    p1 = self.get_possible_moves(y, x - 1, prev_v,critcal)
                        else:
                            if x < self.level.nbCol - 1:
                                if self.level.grid[y][x + 1] != '_':
                                    ra = r[self.level.grid[y][x+1]]
                                    p1 = self.get_possible_moves(y, x + 1, prev_v,critcal)
                        q.append(ra + gamma * p1)
                        #else:
                        #   q = [-1000, -1000]
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
        """if self.level.grid[y][x] == 'M':
            cpt = 0
            p = []
            rev = []
            if y > 0:
                if self.level.grid[y - 1][x] != '_':
                    cpt += 1
                    p.append(max(prev_v[y-1][x]))
                    rev.append(r[self.level.grid[y-1][x]])
            if y < self.level.nbLine - 2:
                if self.level.grid[y - 1][x] != '_':
                    cpt += 1
                    p.append(max(prev_v[y+1][x]))
                    rev.append(r[self.level.grid[y+1][x]])
            if x > 0:
                if self.level.grid[y - 1][x] != '_':
                    cpt += 1
                    p.append(max(prev_v[y][x-1]))
                    rev.append(r[self.level.grid[y][x-1]])
            if x < self.level.nbCol - 1:
                if self.level.grid[y - 1][x] != '_':
                    cpt += 1
                    p.append(max(prev_v[y][x+1]))
                    rev.append(r[self.level.grid[y][x+1]])
            p1 = 0
            for num in p:
                p1 += num * 1/cpt
            return p1"""
        if self.level.grid[y][x] == 'R':
            loose = self.damage
            if critcal:
                loose = self.dead
            p1 = 0.1 * loose + 0.3 * max(prev_v[self.level.nbLine - 1][self.level.nbCol - 1]) + \
                 0.6 * max(prev_v[y][x])
            return p1
        elif self.level.grid[y][x] == 'C':
            return self.dead
        elif self.level.grid[y][x] == 'E':
            loose = self.damage
            if critcal:
                loose = self.dead
            if self.has_sword:
                return max(prev_v[y][x])
            else:
                return 0.7 * max(prev_v[y][x]) + 0.3 * loose
        else:
            return max(prev_v[y][x])
        """elif self.level.grid[y][x] == 'P':
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
            return p1"""


