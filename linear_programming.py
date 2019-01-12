import game

def reward_dict():
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
    return r



def setup_var(level,m, variables,
              has_key=False, has_sword=False, has_treasure=False, critical=True):
    variables['dead'] = m.addVar(vtype=GRB.CONTINUOUS,lb=-500,up=-500)
    for y in range(level.nbLine):
        for x in range(level.nbCol):
            if level.grid[y][x] == '_':
                if level.grid[y][x] in ('M','P'):
                    variables[(x, y, has_key, has_sword, has_treasure, critical)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                                            lb=0, ub=0)
                else:
                    variables[(x, y, has_key, has_sword, has_treasure, critical)] = m.addVar(vtype=GRB.CONTINUOUS,
                                                                                                    lb=-GRB.INFINITY)
    m.update()


def get_reward(variable):
        reward = reward_dict()['default'].copy()
        if variable.has_key:
            reward['K'] = reward['with_key']['K']
            reward['T'] = reward['with_key']['T']
        if variable.has_sword:
            reward['W'] = reward['with_sword']['W']
        if variable.has_treasure:
            reward['S'] = reward['with_treasure']['S']
            reward['T'] = reward['with_treasure']['T']
        return reward

def get_variable(x,y,variables):
        return variables(x,y,va.has_key,has_sword,va.has_treasure,va.critical)


def set_cstr(va, variables,m,level, gamma):
    n_c = (va.y+m[0],va.x+m[1]) # the coordinate of the player after the movement
    if level.grid[n_c[0],n_c[1]] == 'M':
        cpt = 0
        possible_var = []
        if n_c[0] > 0 and level.grid[n_c[0] - 1,n_c[1]] != '_':
            cpt += 1
            possible_var.append(get_variable(n_c[0] - 1, n_c[1], variables))
        if n_c[0] < level.nbLine - 1 and level.grid[n_c[0] + 1,n_c[1]] != '_':
            cpt += 1
            possible_var.append(get_variable(n_c[0] + 1, n_c[1], variables))
        if n_c[1] > 0 and level.grid[n_c[0],n_c[1] - 1] != '_':
            cpt += 1
            possible_var.append(get_variable(n_c[0], n_c[1] - 1, variables))
        if n_c[1] < level.nbCol - 1 and level.grid[n_c[0],n_c[1] + 1] != '_':
            cpt += 1
            possible_var.append(get_variable(n_c[0], n_c[1] + 1, variables))
        det = 1/cpt * gamma
        m.addConstr(va >= get_reward(va) + quicksum(det * possible_var))
    elif level.grid[[n_c[0]][n_c[1]]] == 'R':
        m.addConstr(va >= get_reward(va) + quicksum(0.1 * gamma * variables['dead'],
                                                    0.3 * gamma * get_variable(level.nbCol - 1,level.nbLine - 1,variables),
                                                    0.6* gamma * get_variable(n_c[0],n_c[1],variables)))
    elif level.grid[[n_c[0]][n_c[1]]] == 'C':
        m.addConstr(va >= get_reward(va) + gamma * variables['dead'])
    elif level.grid[[n_c[0]][n_c[1]]] == 'E':
        if va.has_sword:
            m.addConstr(va >= get_reward(va) + gamma * get_variable(n_c[0], n_c[1], variables))
        else:
            m.addConstr(va >= get_reward(va) + quicksum(0.7 * gamma * get_variable(n_c[0], n_c[1], variables),
                                                        03. * gamma * variables['dead']))
        return
    elif level.grid[[n_c[0]][n_c[1]]] == 'P':
        possible_var = []
        cpt = 0
        nb_dead = 0
        for y in range(0, level.nbLine):
            for x in range(0, level.nbCol):
                if level.grid[y][x] != '_':
                    if level.grid[y][x] != 'C':
                        possible_var.append(get_variable(y, x, variables))
                    else:
                        nb_dead += 1
                    cpt += 1
        p_dead = (nb_dead / cpt) * gamma
        m.addConstr(va >= get_reward(va) + quicksum(1/cpt * gamma * possible_var, p_dead * variables['dead']))
    else:
        m.addConstr(va >= get_reward(va) + gamma * get_variable(n_c[0],n_c[1],variables))


def pl(level):
    m = Model("pdm")
    variables = dict()
    possible_val = (True,False)
    for has_key in possible_val:
        for has_sword in possible_val:
            for has_treasure in possible_val:
                setup_var(level, m, variables, has_key, has_sword, has_treasure, critical=True)
                setup_var(level, m, variables, has_key, has_sword, has_treasure, critical=False)
    for va in variables.keys():
        set_cstr(va,variables,(-1,0),level)
        set_cstr(va,variables,(1,0),level)
        set_cstr(va,variables,(0,-1),level)
        set_cstr(va,variables,(0,1),level)

    obj = quicksum(list(variables.values()))
    m.setObjective(obj, GRB.MINIMIZE)