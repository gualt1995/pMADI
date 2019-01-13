from game import Level
from player2 import Player2
from cli import get_cli
from qlearning import QLearning, MOVES
from solver import Solver
from time import time

DISPLAY_CHAR = {
    'player': ('p', 'Player'),
    'life': ('♥', 'Player life'),
    '_': ('█', 'Wall'),
    'B': (' ', 'Empty cell'),
    'M': ('-', 'Moving platform'),
    'S': ('◦', 'Starting position'),
    'E': ('E', 'Enemy'),
    'R': ('▲', 'Trap'),
    'C': ('C', 'Crack'),
    'T': ('T', 'Treasure'),
    'W': ('†', 'Sword'),
    'K': ('K', 'Golden key'),
    'P': ('◯', 'Magic portal'),
}

GAME = {
    'player_moved': False,
    'level': None,
    'player': None,
    'user_loop': False
}


def display_legend():
    """Draws the legend table: each symbol and its signification are displayed
    in the CLI."""
    cli.display('Legend:')
    for cell_type, desc in DISPLAY_CHAR.items():
        cli.display('[{}]{}'.format(desc[0], desc[1]), end='\n\r')
    cli.display(end='\n\r')


def display_grid(level, player):
    """Draws the level in the CLI."""
    cli.display('+{}'.format('---+'*level.nbCol))
    for li, line in enumerate(level.grid):
        cli.display('|', end='')
        for col, char in enumerate(line):
            if li == player.y_pos and col == player.x_pos:
                color = 'yellow'
                c = DISPLAY_CHAR.get('player', 'p')[0]
            else:
                color = 'default'
                c = DISPLAY_CHAR.get(char, char)[0]
            c = c*3 if char in ('_', 'M') else ' {} '.format(c)
            cli.display(c, end='', style='bold', color=color)
            if col != level.nbCol - 1:
                cli.display('', end=' ')
        cli.display('|')
        if li != level.nbLine - 1:
            cli.display('+{}'.format('   +' * level.nbCol))
    cli.display('+{}'.format('---+' * level.nbCol))


def display_all():
    """Displays all screen elements in the following order: toolbar, level,
    legend, status bar."""

    # Clear screen
    cli.clear()
    # Draw game
    display_grid(GAME['level'], GAME['player'])
    cli.display("Player life: {}".format(
        DISPLAY_CHAR['life'][0] * GAME['player'].life), style='bold')

    objects = list()
    if GAME['player'].has_key:
        objects.append(DISPLAY_CHAR['K'][0])
    if GAME['player'].has_sword:
        objects.append(DISPLAY_CHAR['W'][0])
    if GAME['player'].has_treasure:
        objects.append(DISPLAY_CHAR['T'][0])
    cli.display("Player objects: {}".format(objects), style='bold')

    cli.display("Player position: [ {} ][ {} ]".format(
        GAME['player'].x_pos, GAME['player'].y_pos), style='bold')
    display_legend()
    cli.display_status()


def load_level():
    """Generates a new random level."""
    GAME['level'] = Level()
    GAME['level'].generate_solvable(8, 12, 0.2, 0.4, 0.05, 1, 3, 3)
    GAME['level'].save('tmp')
    GAME['player'] = Player2(GAME['level'])
    display_all()
    cli.display_toolbar()
    cli.handle_action()


def start_qlearning():
    """Start qlearning process on the current level."""
    ql = QLearning(GAME['level'], cli,
                   eps_strategy='decrease',
                   epsilon=1, player_health=1)
    start = time()
    stats = ql.train()
    duration = time() - start

    cli.clear_status()
    cli.add_status("QLearning done [{} victories ({:.1%} of {} iterations)]".format(
        stats['wins'], stats['win_percentage'], stats['niter']))
    cli.add_status("Time: {:.2f} secs".format(duration))

    GAME['user_loop'] = True
    while GAME['user_loop']:
        ql.reset()
        GAME['player'] = ql.player
        cli.add_status("Press any key to perform next step in learned policy.")
        cli.add_status("Press (e) to quit.")
        display_all()

        while not (ql.player.is_dead() or ql.player.win) \
                and GAME['user_loop']:

            cli.handle_action()
            best_q = ql.get_max_next_q()
            next_direction = best_q[0]
            MOVES[next_direction](ql.player)
            _, continue_reaction = ql.player.grid_reaction()
            while continue_reaction:
                _, continue_reaction = ql.player.grid_reaction()
                if ql.player.is_dead():
                    break
            display_all()
            player_attrs = {
                'has_key': ql.player.has_key,
                'has_sword': ql.player.has_sword,
                'has_treasure': ql.player.has_treasure,
                'critical': ql.player.life <= 1
            }
            # ql.display_q()
            for line in ql.policy(**player_attrs):
                ql.log(line)

        # End of game
        cli.clear_status()
        if GAME['player'].is_dead():
            cli.add_status('GAME OVER')
            cell = GAME['level'].grid[GAME['player'].y_pos][GAME['player'].x_pos]
            if cell == 'C':
                cli.add_status('You fell into a crack and died.')
            elif cell == 'E':
                cli.add_status('An enemy killed you.')
            elif cell == 'R':
                cli.add_status('You walked into a deadly trap.')
            else:
                cli.add_status('You died.')
        else:
            cli.add_status('GAME WON')

        display_all()
        cli.display("Press any key to continue.")
        cli.handle_action()
        cli.clear_status()

    display_all()
    cli.display("Press (e) to quit.")
    cli.wait_for_action('e')


def user_play():
    """Start the user loop where the user can play the game using the arrow keys
    on linux or WASD/ZQSD on windows."""
    cli.add_action('KEY_UP', (
        lambda: GAME.__setitem__('player_moved', GAME['player'].move_up())))
    cli.add_action('KEY_DOWN', (
        lambda: GAME.__setitem__('player_moved', GAME['player'].move_down())))
    cli.add_action('KEY_RIGHT', (
        lambda: GAME.__setitem__('player_moved', GAME['player'].move_right())))
    cli.add_action('KEY_LEFT', (
        lambda: GAME.__setitem__('player_moved', GAME['player'].move_left())))

    GAME['user_loop'] = True
    while GAME['user_loop']:

        GAME['player'] = Player2(GAME['level'])
        cli.add_status("You can play with ZQSD on Windows or the arrow keys on unix.")
        cli.add_status("Press (e) to exit.")

        while not (GAME['player'].win or GAME['player'].is_dead()):

            display_all()

            # Reset game state
            GAME['player_moved'] = False

            # Handle user input
            cli.handle_action()
            _, continue_reaction = GAME['player'].grid_reaction()
            while continue_reaction:
                _, continue_reaction = GAME['player'].grid_reaction()
                if GAME['player'].is_dead():
                    break

        # End of game
        cli.clear_status()
        if GAME['player'].is_dead():
            cli.add_status('GAME OVER')
            cell = GAME['level'].grid[GAME['player'].y_pos][GAME['player'].x_pos]
            if cell == 'C':
                cli.add_status('You fell into a crack and died.')
            elif cell == 'E':
                cli.add_status('An enemy killed you.')
            elif cell == 'R':
                cli.add_status('You walked into a deadly trap.')
            else:
                cli.add_status('You died.')
        if GAME['player'].win:
            cli.add_status('GAME WON')

        if not GAME['user_loop']:
            break

        display_all()
        cli.display("Press any key to continue.")
        cli.handle_action()
        cli.clear_status()

    display_all()
    cli.display("Press (e) to quit.")
    cli.wait_for_action('e')


def quit_app():
    cli.close()
    exit(0)


def get_policy_disp(p, state):
    DISP = {
        'u': '^',
        'r': '>',
        'd': 'v',
        'l': '<'
    }
    policy = list()
    for y in range(GAME['level'].nbLine):
        policy.append(list())
        for x in range(GAME['level'].nbCol):
            if GAME['level'].grid[y][x] in ('_', 'P'):
                policy[y].append('█')
            elif GAME['level'].grid[y][x] == 'M':
                policy[y].append('-')
            else:
                policy[y].append(DISP[p[state][y][x]])

    return policy


def start_value_iteration():
    cli.clear_status()
    display_all()

    cli.display("Starting Value Iteration...")
    solver = Solver(GAME['level'])
    policy = solver.solve_v_a(0.9, 0.000000000000000000000000000001)
    cli.add_status("Value iteration done.")

    GAME['user_loop'] = True
    while GAME['user_loop']:
        GAME['level'].load(GAME['level'].name)
        player = Player2(GAME['level'], HP=1)
        GAME['player'] = player
        cli.add_status("Press (space) to apply next move in policy.")
        cli.add_status("Press (q) to quit.")

        while not (player.is_dead() or player.win) \
                and GAME['user_loop']:

            state = player.get_state()
            x, y = player.x_pos, player.y_pos
            next_direction = policy[state][y][x]
            display_all()
            for line in get_policy_disp(policy, state):
                cli.display(line)
            # cli.display("Next direction is {}".format(next_direction))
            cli.handle_action()

            if next_direction == 'u': player.move_up()
            if next_direction == 'd': player.move_down()
            if next_direction == 'l': player.move_left()
            if next_direction == 'r': player.move_right()

            _, continue_reaction = player.grid_reaction()
            while continue_reaction:
                _, continue_reaction = player.grid_reaction()
                if player.is_dead():
                    break

        # End of game
        cli.clear_status()
        if GAME['player'].is_dead():
            cli.add_status('GAME OVER')
            cell = GAME['level'].grid[GAME['player'].y_pos][GAME['player'].x_pos]
            if cell == 'C':
                cli.add_status('You fell into a crack and died.')
            elif cell == 'E':
                cli.add_status('An enemy killed you.')
            elif cell == 'R':
                cli.add_status('You walked into a deadly trap.')
            else:
                cli.add_status('You died.')
        if GAME['player'].win:
            cli.add_status('GAME WON')

        if not GAME['user_loop']:
            break

        display_all()
        cli.display("Press any key to continue.")
        cli.handle_action()
        cli.clear_status()

    display_all()
    cli.display("Press (e) to quit.")
    cli.wait_for_action('e')


def start_policy_iteration():
    pass


def optimize_menu():
    cli.add_action("1", start_value_iteration)
    cli.add_action("2", start_policy_iteration)
    cli.add_action("3", start_qlearning)

    cli.clear_status()
    cli.add_status("Press (1) to start Value Iteration algorithm.")
    cli.add_status("Press (2) to start resolution with Linear Programming.")
    cli.add_status("Press (3) to start QLearning algorithm.")

    display_all()
    cli.wait_for_action('1', '2', '3', 'e')


if __name__ == "__main__":
    cli = get_cli()
    cli.add_action('exit', quit_app, toolbar=True)
    cli.add_action('load level', load_level, toolbar=True)
    cli.add_action('play', user_play, toolbar=True)
    cli.add_action('optimize', optimize_menu, toolbar=True)

    GAME['level'] = Level()
    GAME['level'].load("instances/lvl-n8-0")
    # GAME['level'].load("tmp")
    GAME['player'] = Player2(GAME['level'])

    display_all()
    cli.display_toolbar()
    cli.wait_for_action('e', 'l', 'p', 'o')
