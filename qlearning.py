import math
from random import choice, uniform
from copy import copy
from enum import Enum
from numpy import std

from game import Level
from player import Player
from cli import CliWindows, CliCurses


class DIRECTION(Enum):
    UP = 0
    DOWN = 1
    RIGHT = 2
    LEFT = 3


REWARDS = {
    'death': -500,
    'default': {
        'S': -1,     # Starting position
        'E': -1,     # Enemy
        'B': -1,     # Blank
        'R': -1,     # Trap
        'C': -1,     # Crack
        'W': 500,    # Sword
        'K': 1000,   # Golden key
        'P': -1,     # Magic portal
        'T': -1,     # Treasure
        'M': -1,     # Moving platform
        '_': -1000,  # Wall
    },
    'with_sword': {
        'W': -1,
    },
    'with_key': {
        'T': 1000,
        'K': -1,
    },
    'with_treasure': {
        'S': 1000,
        'T': -1
    }
}

DIRS = {
    DIRECTION.UP: '^',
    DIRECTION.DOWN: 'v',
    DIRECTION.RIGHT: '>',
    DIRECTION.LEFT: '<'
}

MOVES = {
    DIRECTION.UP: Player.move_up,
    DIRECTION.DOWN: Player.move_down,
    DIRECTION.LEFT: Player.move_left,
    DIRECTION.RIGHT: Player.move_right
}

MAX_ITER = 100000


class QLearning:
    """QLearning framework."""

    def __init__(self, level, cli=None, default_q=100,
                 alpha=0.1, gamma=0.9, epsilon=0.01, eps_strategy='constant'):
        """Initializes algorithm parameters.

        Args:
            level (Level): The level with which the algorithm will train.
            cli (CliWindows or CliCurses): Command line interface used for
                logging.
            default_q (float): Default Q value for unexplored states.
            alpha (float): Learning rate, between 0 and 1.
            gamma (float): Discount factor, between 0 and 1.
            epsilon (float): Probability of making a random move.
            eps_strategy (string): Epsilon strategy. If 'decrease' the value of
                epsilon will decrease with the number of train iteration. If
                'constant', the value of epsilon will remain the same throughout
                the learning process.
        Raises:
            ValueError: If an argument has an unexpected value.
        """

        # Environment parameters
        self.level = level
        self.level_name = level.name
        self.grid = copy(level.grid)
        self.player = Player(level)
        self.cli = cli

        # Algorithm parameters
        self.Q = dict()
        self.default_q = default_q
        if alpha > 1 or alpha < 0:
            raise ValueError("Learning rate 'alpha' must be between 0 and 1.")
        self._alpha = alpha
        if gamma > 1 or gamma < 0:
            raise ValueError("Discount factor 'gamma' must be between 0 and 1.")
        self._gamma = gamma
        self.time = 0
        if epsilon > 1 or epsilon < 0:
            raise ValueError("Epsilon must be between 0 and 1.")
        self._epsilon = epsilon
        self._o_epsilon = epsilon
        if eps_strategy not in ('constant', 'decrease'):
            raise ValueError("Invalid epsilon strategy: {}".format(eps_strategy))
        self.epsilon_strategy = eps_strategy
        self.iter_at_lift = 0
        self.iter = 0
        self.last_policy = dict()

    def log(self, *args, **kwargs):
        """Uses the command line interface to log data."""
        if self.cli is not None:
            self.cli.display(*args, **kwargs)

    def get_state(self, state=None, direction=None):
        """Returns the state of the player represented by a tuple with the
        following data: (x position, y position, has_key, has_sword,
        has_treasure). If a direction is provided, the function returns what
        the player state would be if it made a move in this direction.

        Args:
            state (tuple): Origin state. If not provided, the current state of
                the player is used.
            direction (DIRECTION): Direction to consider for the next player
                move.

        Returns:
            (tuple) Player state.
        """
        if state is None:
            x = self.player.x_pos
            y = self.player.y_pos
            has_key = self.player.has_key
            has_sword = self.player.has_sword
            has_treasure = self.player.has_treasure
        else:
            x = state[0]
            y = state[1]
            has_key = state[2]
            has_sword = state[3]
            has_treasure = state[4]

        if direction == DIRECTION.RIGHT:
            x += 1
        if direction == DIRECTION.LEFT:
            x -= 1

        if direction == DIRECTION.UP:
            y -= 1
        if direction == DIRECTION.DOWN:
            y += 1

        return x, y, has_key, has_sword, has_treasure

    def absolute_policy(self, **player_attrs):
        """Returns the best direction to take for each possible state of the
        player.

        Args:
            **player_attrs: Player attributes to consider. For example,
                a dict with 'has_sword' set to True.

        Returns:
            (matrix) Policy.
        """
        if player_attrs is None:
            player_attrs = dict()

        policy = list()

        for y in range(self.level.nbLine):
            policy.append(list())
            for x in range(self.level.nbCol):
                if self.grid[y][x] in ('_', 'P'):
                    policy[y].append('█')
                elif self.grid[y][x] == 'M':
                    policy[y].append('-')
                else:
                    state = (x, y,
                             player_attrs.get('has_key', False),
                             player_attrs.get('has_sword', False),
                             player_attrs.get('has_treasure', False))
                    best_q = self.get_max_next_q(origin_state=state, absolute=True)
                    policy[y].append(DIRS[best_q[0]])

        return policy

    def save_last_policy(self):
        possible_states = []
        for has_key in (True, False):
            for has_sword in (True, False):
                for has_treasure in (True, False):
                    possible_states.append((has_key, has_sword, has_treasure))

        for state in possible_states:
            last_policy = self.absolute_policy(
                has_key=state[0],
                has_sword=state[1],
                has_treasure=state[2],
            )
            self.last_policy[state] = last_policy

    def policy_distance(self):
        """Computes the distance between the previous iteration's policy and the
        current's policy."""
        total_distance = 0
        possible_states = []
        for has_key in (True, False):
            for has_sword in (True, False):
                for has_treasure in (True, False):
                    possible_states.append((has_key, has_sword, has_treasure))

        for state in possible_states:
            current_policy = self.absolute_policy(
                has_key=state[0],
                has_sword=state[1],
                has_treasure=state[2],
            )
            for x in range(self.level.nbCol):
                for y in range(self.level.nbLine):
                    try:
                        if self.last_policy[state][y][x] != current_policy[y][x]:
                            total_distance += 1
                    except KeyError:
                        total_distance += 1

        return total_distance

    def get_max_next_q(self, origin_state=None, absolute=False):
        """Computes the best Q value neighbouring a specified state and the
        corresponding action.

        Args:
            origin_state (tuple): Player state to consider as origin. If None,
                the current player state is used.
            absolute (bool): If set to True, will always return the same action
                if several maximums are found.

        Returns:
            (DIRECTION) best action,
            (float) best action Q value.
        """
        if origin_state is None:
            origin_state = self.get_state()
        q_values = {
            DIRECTION.UP: self.Q.get(
                self.get_state(state=origin_state, direction=DIRECTION.UP),
                self.default_q
            ),
            DIRECTION.DOWN: self.Q.get(
                self.get_state(state=origin_state, direction=DIRECTION.DOWN),
                self.default_q
            ),
            DIRECTION.LEFT: self.Q.get(
                self.get_state(state=origin_state, direction=DIRECTION.LEFT),
                self.default_q
            ),
            DIRECTION.RIGHT: self.Q.get(
                self.get_state(state=origin_state, direction=DIRECTION.RIGHT),
                self.default_q
            )
        }
        maximums = []
        max_value = -math.inf

        for direction, q in q_values.items():
            if q > max_value:
                maximums = [(direction, q)]
                max_value = q
            elif q == max_value:
                maximums.append((direction, q))

        if absolute:
            return maximums[0]

        return choice(maximums)

    def display_q(self):
        """Displays the Q table for the current player state."""
        for y in range(self.level.nbLine):
            for x in range(self.level.nbCol):
                if self.player.x_pos == x and self.player.y_pos == y:
                    color = 'red'
                else:
                    color = 'default'
                self.cli.display("[{:.2f}]".format(self.Q.get(
                        (x, y, self.player.has_key, self.player.has_sword,
                         self.player.has_treasure),
                        self.default_q)
                    ),
                    end="", color=color)
            self.cli.display()

    def reset(self):
        """Resets the player and level objects used by the algorithm."""
        self.player = Player(self.level, HP=1)
        self.level.load(self.level_name)

    @property
    def epsilon(self):
        """Returns the epsilon parameter used in the epsilon-strategy."""
        # If stuck in an iteration, increase value of epsilon.
        if self.epsilon_strategy == 'decrease' and self.time > 1000:
            self._epsilon = 0.1
            self.iter_at_lift = self.iter
        return self._epsilon

    def update_q(self, state, reward, max_q_next_action):
        """Update the Q table for the specified state.

        Args:
            state (tuple): State to update.
            reward (float): Reward value for reaching `state`.
            max_q_next_action (float): Maximum next reward value at state.
        """
        self.Q[state] = self.Q.get(state, self.default_q)
        self.Q[state] += self._alpha * (reward + self._gamma
                                        * max_q_next_action - self.Q[state])

    @staticmethod
    def get_reward(state, player_cell, is_dead):
        """Computes the reward for a player reaching a cell with a specified
        state.

        Args:
            state (tuple): Player state when reaching the cell.
            player_cell (string): Cell type reached.
            is_dead (bool): Whether the player is dead or not.

        Returns:
            (float) Reward value.
        """
        # If the player was killed, reward is constant...
        if is_dead:
            return REWARDS['death']

        reward = REWARDS['default'][player_cell]

        # Look for overrides if the player had a particular object
        # when reaching `ply_cell`. 'grid_reaction' is only executed
        # more than once if the player stepped on a cell that
        # affects position. Therefore we can use `s_after_move`.
        if state[2]:  # Player had a key.
            reward = REWARDS['with_key'].get(player_cell, reward)
        if state[3]:  # Player had a sword.
            reward = REWARDS['with_sword'].get(player_cell, reward)
        if state[4]:  # Player had the treasure.
            reward = REWARDS['with_treasure'].get(player_cell, reward)

        return reward

    def train(self):
        """Trains the player on the level. The algorithm uses an epsilon-greedy
        strategy to avoid local optimums. The next move is thus the move that
        maximises the expected reward with (1-epsilon) probability and a random
        move with epsilon probability.
        """
        wins = [1, 0]
        total_wins = 0
        self.iter = 0
        self._epsilon = self._o_epsilon
        while True:
            if self.iter - self.iter_at_lift > 5000 or self.iter > MAX_ITER:
                break
            if self.epsilon_strategy == 'decrease':
                self._epsilon = max(0, self._epsilon - 0.001)
            # self.save_last_policy()
            self.iter += 1

            # Display every 10 iterations.
            if self.iter % 10 == 0:
                self.cli.clear()
                self.log("ε = {:.3f}, α = {:.2f}, γ = {:.2f}"
                         .format(self.epsilon, self._alpha, self._gamma))
                self.log("Iteration {} [victories = {} ({:.1%})]".format(
                    self.iter, total_wins, total_wins/self.iter))
                self.log("Number of iterations since last ε increase: {}".format(
                    self.iter - self.iter_at_lift
                ))
                self.log("Distance to last policy: {}".format(
                    self.policy_distance()
                ))
                self.log("Victory percentage over last 100 periods: {}%".format(
                    sum(wins)
                ))
                self.log("Variance: {}".format(std(wins)))
                # self.display_q()
                for line in self.absolute_policy():
                    self.log(line)
            self.reset()

            self.time = 0
            while not (self.player.is_dead() or self.player.win):

                # Choose next cell in grid.
                if uniform(0, 1) < self.epsilon:
                    # Choose random strategy with probability `epsilon`.
                    next_direction = choice(list(MOVES.keys()))
                else:
                    # Otherwise choose best move according to Q table.
                    best_q = self.get_max_next_q()
                    next_direction = best_q[0]

                # Go to next cell
                player_moved = MOVES[next_direction](self.player)

                if player_moved:
                    # Get state after stepping on the next cell.
                    s_after_move = self.get_state()

                    # Trigger all events that could happen after the move. For
                    # example, if the player stepped on a moving platform or
                    # fell in a crack. If an object was on the cell, pick it up.
                    reaction_happened = False
                    while self.player.grid_reaction():
                        reaction_happened = True
                        if self.player.is_dead():
                            break

                    # The final cell reached tells us the reward for going to
                    # `s_after_move`.
                    s_after_reaction = self.get_state()
                    ply_cell = self.grid[s_after_reaction[1]][s_after_reaction[0]]
                    reward = self.get_reward(s_after_move,
                                             ply_cell, self.player.is_dead())

                    # Estimate optimal future value.
                    max_q_value = self.get_max_next_q()[1]
                    # if self.player.is_dead():
                    #     max_q_value = 0

                    # If the player was moved by a chain reaction, we need to
                    # update the final landing cell as well.
                    if reaction_happened:
                        reward_after_reaction = self.get_reward(
                            s_after_reaction, ply_cell, self.player.is_dead())
                        self.update_q(s_after_reaction,
                                      reward_after_reaction, max_q_value)
                else:
                    # If the player wasn't able to move (i.e. there was a wall
                    # in `next_direction`), we retrieve the state that would
                    # have been reached otherwise in order to update its Q
                    # value.
                    s_after_move = self.get_state(direction=next_direction)
                    reward = REWARDS['default']['_']
                    max_q_value = reward

                # Update Q value
                self.update_q(s_after_move, reward, max_q_value)

                # if interactive:
                #     self.display_q()
                #     self.cli.display(self.get_state())

                self.time += 1

            has_won = 1 if self.player.win else 0
            total_wins += has_won
            wins.append(has_won)
            if len(wins) > 100:
                wins.pop(0)

        return {
            'win_percentage': total_wins / self.iter,
            'wins': total_wins,
            'niter': self.iter
        }
