"""
  This is a temporary Oversight controller until Daniel finishes his JesusNG score function
"""
class Oversight(object):
  """Oversight is god. Ask, andit will respond."""
  def __init__(self, game):
    super(Oversight, self).__init__()
    self.game = game
    self.RAN = False

  def proceed(self):
    if self.RAN:
      return False
    self.RAN = True
    return True
  
  def consider(self, strategy):
    self.strategy = strategy

  def decree(self):
    return self.strategy