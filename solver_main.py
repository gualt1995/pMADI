import solver
import game

level_1 = game.Level("Level_1")
level_1.load()
level_1.display()
va = solver.Solver(level_1)
v = va.value_iteration(0.5, 0.001)
va.display(v)
res = va.best_policy(v)
level_1.visualize(res)
