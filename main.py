from game import Level
from player2 import Player
from cli import get_cli
from qlearning import QLearning, MOVES

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
    'running_policy': False
}


def display_legend():
    cli.display('Legend:')
    for cell_type, desc in DISPLAY_CHAR.items():
        cli.display('[{}]{}'.format(desc[0], desc[1]), end='\n\r')
    cli.display(end='\n\r')


def display_grid(level, player):
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
    # Clear screen
    cli.clear()
    # Draw game
    cli.display_toolbar()
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
    GAME['level'] = Level()
    GAME['level'].generate_solvable(10, 10, 0.2, 0.4, 0.05, 1, 3, 3)
    GAME['level'].save('tmp')
    GAME['player'] = Player(GAME['level'])
    display_all()
    cli.handle_action()


def start_qlearning():
    # ql = QLearning(GAME['level'], cli)
    ql = QLearning(GAME['level'], cli, eps_strategy='decrease', epsilon=1)
    stats = ql.train()

    cli.add_action("e", lambda: GAME.__setitem__('running_policy', False))
    cli.add_status("QLearning done [{} victories ({:.1%} of {} iterations)]".format(
        stats['wins'], stats['win_percentage'], stats['niter']))
    cli.add_status("Press any key to perform next step in learned policy.")
    cli.add_status("Press (e) to exit qlearning mode.")
    display_all()

    GAME['running_policy'] = True
    while GAME['running_policy']:
        ql.reset()
        GAME['player'] = ql.player
        while not (ql.player.is_dead() or ql.player.win):
            cli.handle_action()
            best_q = ql.get_max_next_q()
            next_direction = best_q[0]
            MOVES[next_direction](ql.player)
            while ql.player.grid_reaction():
                if ql.player.is_dead():
                    break
                continue
            display_all()
            ql.log("{:.3f} -> {}".format(best_q[1], best_q[0]))
            ql.display_q()

        # End of game
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
        cli.clear_status()

    cli.clear_status()
    display_all()
    cli.handle_action()


def user_loop():
    cli.add_action('KEY_UP', (
        lambda: GAME.__setitem__('player_moved', GAME['player'].move_up())))
    cli.add_action('KEY_DOWN', (
        lambda: GAME.__setitem__('player_moved', GAME['player'].move_down())))
    cli.add_action('KEY_RIGHT', (
        lambda: GAME.__setitem__('player_moved', GAME['player'].move_right())))
    cli.add_action('KEY_LEFT', (
        lambda: GAME.__setitem__('player_moved', GAME['player'].move_left())))

    while not (GAME['player'].win or GAME['player'].is_dead()):
        display_all()

        # Reset game state
        GAME['player_moved'] = False

        # Handle user input
        cli.handle_action()
        while GAME['player'].grid_reaction():
            continue

    # End of game
    if GAME['player'].is_dead():
        cli.add_status('GAME OVER')
        cell = GAME['level'].grid[GAME['player'].y_pos][GAME['player'].x_pos]
        if cell == 'C':
            cli.add_status('You fell into a crack and died.')
        elif cell == 'B':
            cli.add_status('An enemy killed you.')
        elif cell == 'R':
            cli.add_status('You walked into a deadly trap.')
        else:
            cli.add_status('You died.')
    else:
        cli.add_status('GAME WON')
    display_all()

    cli.wait_for_input()


def quit_app():
    # cli.close()
    exit(0)


if __name__ == "__main__":
    cli = get_cli()
    cli.add_action('quit', quit_app, toolbar=True)
    cli.add_action('load level', load_level, toolbar=True)
    cli.add_action('start playing', user_loop, toolbar=True)
    cli.add_action('optimize', start_qlearning, toolbar=True)

    GAME['level'] = Level()
    GAME['level'].load("Level_1")
    GAME['player'] = Player(GAME['level'])

    display_all()
    cli.handle_action()
