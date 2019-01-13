import numpy as np
import copy


def solve_p_i(gamma, level):
    return {
        (False, False, False, True): policy_iteration(gamma, level, get_reward(), True, False),
        (False, True, False, True): policy_iteration(gamma, level, get_reward(has_sword=True), True, True),
        (True, False, False, True): policy_iteration(gamma, level, get_reward(has_key=True), True),
        (True, False, True, True): policy_iteration(gamma, level,
                                                        get_reward(has_key=True, has_treasure=True), True),
        (True, True, False, True): policy_iteration(gamma, level, get_reward(has_key=True, has_sword=True),
                                                        True, True),
        (True, True, True, True): policy_iteration(gamma, level,
                                                       get_reward(has_key=True, has_sword=True, has_treasure=True),
                                                       True, True),
        (False, False, False, False): policy_iteration(gamma, level, get_reward(), False),
        (False, True, False, False): policy_iteration(gamma, level, get_reward(has_sword=True), False, True),
        (True, False, False, False): policy_iteration(gamma, level, get_reward(has_key=True), False),
        (True, False, True, False): policy_iteration(gamma, level,
                                                         get_reward(has_key=True, has_treasure=True), False),
        (True, True, False, False): policy_iteration(gamma, level, get_reward(has_key=True, has_sword=True),
                                                         False, True),
        (True, True, True, False): policy_iteration(gamma, level, get_reward(has_key=True, has_sword=True,
                                                                                        has_treasure=True), False, True)
    }


def get_reward(has_key=False, has_sword=False, has_treasure=False):
    r = {
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
            'T': -1
        }
    }
    reward = r['default'].copy()
    if has_key:
        reward['K'] = r['with_key']['K']
        reward['T'] = r['with_key']['T']
    if has_sword:
        reward['W'] = r['with_sword']['W']
    if has_treasure:
        reward['S'] = r['with_treasure']['S']
        reward['T'] = r['with_treasure']['T']
    return reward


def init_p_i(level, variables, p0):
    for y in range(0, level.nbLine):
        line = []
        for x in range(0, level.nbCol):
            if y == 0:
                line.append('d')
            else:
                line.append('u')
            variables.append(str(y) + str(x))
        p0.append(line)


def set_variables(level, y, x, eq, gamma, has_sword):
    if level.grid[y][x] == 'R':
        eq['dead'] = 0.1 * gamma
        eq[str(level.nbCol - 1) + str(level.nbLine - 1)] = 0.3 * gamma
        eq[str(y) + str(x)] = 0.6 * gamma
    elif level.grid[y][x] == 'C':
        eq['dead'] = 1
    elif level.grid[y][x] == 'E':
        if has_sword:
            eq[str(y) + str(x)] = 1 * gamma
        else:
            eq[str(y) + str(x)] = 0.7 * gamma
        eq['dead'] = 0.3 * gamma
        return
    else:
        eq[str(y) + str(x)] = 1 * gamma


def define_equations(y, x, dt, level, eq, rest, gamma, r, has_sword):
    if level.grid[y][x] not in ('P','M'):
        if dt[y][x] == 'u':
            if y > 0 and level.grid[y - 1][x] != '_':
                rest.append(r[level.grid[y - 1][x]] * -1)
                set_variables(level,y - 1, x, eq, gamma,has_sword)
            else:
                rest.append(r[level.grid[y][x]] * -1)
        elif dt[y][x] == 'd':
            if y < level.nbLine - 1 and level.grid[y + 1][x] != '_':
                rest.append(r[level.grid[y + 1][x]] * -1)
                set_variables(level,y + 1, x, eq, gamma,has_sword)
            else:
                rest.append(r[level.grid[y][x]] * -1)
        elif dt[y][x] == 'l':
            if x > 0 and level.grid[y][x - 1] != '_':
                rest.append(r[level.grid[y][x - 1]] * -1)
                set_variables(level,y, x - 1, eq, gamma,has_sword)
            else:
                rest.append(r[level.grid[y][x]] * -1)
        else:
            if x < level.nbCol - 1 and level.grid[y][x + 1] != '_':
                rest.append(r[level.grid[y][x + 1]] * -1)
                set_variables(level,y, x + 1, eq, gamma,has_sword)
            else:
                rest.append(r[level.grid[y][x]] * -1)
    else:
        if level.grid[y][x] == 'P':
            rest.append(0)
            p = []
            cpt = 0
            nb_dead = 0
            for y in range(0, level.nbLine):
                for x in range(0, level.nbCol):
                    if level.grid[y][x] != '_':
                        if level.grid[y][x] != 'C':
                            p.append(str(y) + str(x))
                        else:
                            nb_dead += 1
                        cpt += 1
            eq['dead'] = nb_dead / cpt * gamma
            for var in p:
                if eq[var] != -1:
                    eq[var] = 1 / cpt * gamma
        if level.grid[y][x] == 'M':
            rest.append(0)
            cpt = 0
            p = []
            if y > 0:
                if level.grid[y][x] != '_':
                    cpt += 1
                    p.append(str(y - 1) + str(x))
            if y < level.nbLine - 1:
                if level.grid[y][x] != '_':
                    cpt += 1
                    p.append(str(y + 1) + str(x))
            if x > 0:
                if level.grid[y][x] != '_':
                    cpt += 1
                    p.append(str(y) + str(x - 1))
            if x < level.nbCol - 1:
                if level.grid[y][x] != '_':
                    cpt += 1
                    p.append(str(y) + str(x + 1))
            for num in p:
                eq[num] = (1 / cpt) * gamma


def build_dt1(level,ar,dt1):
    cpt = 0
    for y in range(0, level.nbLine):
        line = []
        for x in range(0, level.nbCol):
            line.append(ar[cpt])
            cpt += 1
        dt1.append(line)


def policy_iteration(gamma, level, r, crtical,has_sword=True):
    a = ['u', 'd', 'l', 'r']
    p0 = []
    variables = []
    init_p_i(level, variables, p0)
    dt = copy.deepcopy(p0)
    cpt = 0
    while cpt < 500:
        cpt += 1
        eqs = []
        rest = []
        ctn = False
        for y in range(0, level.nbLine):
            for x in range(0, level.nbCol):
                eq = dict.fromkeys(variables, 0)
                eq['dead'] = 0  # adding variable for death
                eq[str(y) + str(x)] = -1  # see policy iterations equations
                define_equations(y, x, dt, level, eq, rest, gamma, r,has_sword)
                eqs.append(list(eq.values()))
        # adding equation if U died
        eqdeath = dict.fromkeys(variables, 0)
        eqdeath[len(eqdeath) - 1] = 1
        rest.append(500)
        eqs.append(list(eqdeath.values()))
        ar = np.linalg.solve(eqs, rest)
        dt1 = []
        build_dt1(level, ar, dt1)
        #TODO dead = ar[len(ar) - 1]
        #TODO check if r is good or not
        for y in range(0, level.nbLine):
            for x in range(0, level.nbCol):
                value = dict()
                for act in a:
                    if level.grid[y][x] not in ('P', 'M', '_'):
                        if act == 'u':
                            if y > 0:
                                if level.grid[y - 1][x] != '_':
                                    p1 = get_possible_move(y - 1, x, dt1, level,has_sword) * gamma + r[level.grid[y - 1][x]]
                                    value[act] = p1
                        elif act == 'd':
                            if y < level.nbLine - 1:
                                if level.grid[y + 1][x] != '_':
                                    p1 = get_possible_move(y + 1, x, dt1,level,has_sword) * gamma + r[level.grid[y + 1][x]]
                                    value[act] = p1
                        elif act == 'l':
                            if x > 0:
                                if level.grid[y][x - 1] != '_':
                                    p1 = get_possible_move(y, x - 1, dt1,level,has_sword) * gamma + r[level.grid[y][x - 1]]
                                    value[act] = p1
                        else:
                            if x < level.nbCol - 1:
                                if level.grid[y][x + 1] != '_':
                                    p1 = get_possible_move(y, x + 1, dt1,level,has_sword) * gamma +  r[level.grid[y][x + 1]]
                                    value[act] = p1
                    else:
                        value[act] = 0
                update = max(value, key=value.get)
                if dt[y][x] != update:
                    ctn = True
                dt[y][x] = update
        #print("-----------------------------------------------------")
        #for line in dt:
        #    print(line)
        if not ctn:
            return dt
    return dt


def get_possible_move(y, x, dt1, level,has_sword):
    damage = -10
    dead = -100
    if level.grid[y][x] == 'R':
        p1 = 0.1 * damage + 0.3 * dt1[level.nbCol - 1][level.nbLine - 1] + 0.6 * dt1[y][x]
        return p1
    elif level.grid[y][x] == 'C':
        return dead
    elif level.grid[y][x] == 'E':
        if has_sword:
            return dt1[y][x]
        else:
            return 0.7 * dt1[y][x] + 0.3 * dead
    else:
        return dt1[y][x]





