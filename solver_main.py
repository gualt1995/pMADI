import solver
import game

game = game.Level()
game.load("level_0")
game.display()
sol = solver.Solver(game)
#policy = sol.solve_v_a(0.5, 0.001)
policy = sol.solve_p_i(0.5)
#game.visualize(policy)
#v = va.value_iteration(0.5, 0.001)
#v = sol.policy_iteration(1,False)
#va.display(v)
#res = va.best_policy(v)
#level_1.visualize(res)
