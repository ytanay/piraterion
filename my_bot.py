"""
piraterion
  a bot for playing a slighly nonsensical pirates game.
  round 22
"""

import operations

operations = operations.Operations() # Fun fact: this is only global used in the entire bot! That's an 800% reduction in globals!

def do_turn(game):
  """ 
    Here is a simplified description of the turn mechanism.
    We create a Strategy control singleton which stores pirates and their corresponding targets for the lifetime of the game.
    On every turn, we update our strategy controller by giving the mission handler the new game reference and execute the turn.
    For naming conventions we went with a slightly militaristic scheme (see https://en.wikipedia.org/wiki/Military_science)
    In short:
      Operations - coordination of strategy generation
        Strategy - long term overall goals (mostly of political value. Just kidding, but then again...)
        Tactician - tactical decision making (generates strategies)
      Assessments - logical tests which determine the value of certain tactics
  """
  
  global operations
  operations.execute(game) # Updates the strategy and execute the turn