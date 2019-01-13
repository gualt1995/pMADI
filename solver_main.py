import value_iteration
import game
import policy_iteration

game = game.Level()
game.load("level_1")
game.display()
sol = value_iteration.Solver(game)
#policy = sol.solve_v_a(0.5, 0.000000000000000000000000000001)
policy = policy_iteration.solve_p_i(0.5,game)
#game.display_policy(policy)
game.visualize(policy)
#v = va.value_iteration(0.5, 0.001)
#v = sol.policy_iteration(1,False)
#va.display(v)
#res = va.best_policy(v)
#level_1.visualize(res)
