import tactician, strategy, assessor
from oversight import Oversight

class Operations(object):
  """ 
    Operations is essentially the task runner. 
    Much like in the military, it is responsible for making strategic choices based on tactical intelligence.
    Operations produces a list of pirates, and then forces these pirates through a set of rigorous logical assessments, finally deciding on a single strategy for each one.
    These strategies are give back to the strategy controller, which rates them and decides whether to commit or re-assess the strategic choices made by it.
    Operations are aided by Tactics, which in turn are aided by Assessments.
    Operations may be given instructions by Oversight during the game to change tactical behaviors.
  """ 
  def __init__(self, tactics=None):
    self.tactics = tactics if tactics else self.default_tactics()
    self.strategy = strategy.Strategy() # Our long term strategy

  def execute(self, game):
    """
      This is the core task runner. Its job is to coordinate tacticians in isolated environments (think cloned sandboxes)
      It is overseen by an instance of Oversight, a separate module which tracks and monitors the operation of the bot.
      Oversight's word (well, code) is law. 
        It runs ROI calculations to determine how many permutations of the pirate list we can afford to scan.
        It is in charge of rating strategy combinations and selecting one to apply for this turn
    """

    self.game = game
    oversight = Oversight(game)

    while oversight.proceed():
      oversight.consider(self.strategize(self.permutate())) # Strategize using a random permutation of the pirate list, and give it to Oversight for consideration
    
    self.sail(oversight.decree()) # Gets the final decision from oversight and sets sail!

  def strategize(self, pirates):
    """ 
      This is strategy computation method.
      It starts with a list of pirates, and runs the first through the specified list of tactical assessments.
      When a tactic concludes it has no beneficial effect on the current pirate, it return False. The next tactic is evaluated.
      When a tactic has performed a state operation on a pirate, it returns True. This signals the ranker to discard the current pirate and move on.
      When a tactic produces a target, it returns a tuple of the following form ([force], target). All the pirates in the force list are assigned the target and removed from the pool.
      TODO: address issue of tactic ordering and pirate ordering (i.e. losing possible permutations). SHOULD WE REMOVE?
    """

    strategy = self.strategy.clone(self.game)
    tactical = tactician.Tactician(self.game, strategy, pirates, assessor.Assessor(self.game, strategy, pirates))
    
    while len(pirates) > 0:
      strategy.remap_pirate_targets()
      pirate = pirates[0]
      self.game.debug('looking at pirate %d', pirate.id)
      for tactic in self.tactics:
        decision = getattr(tactical, tactic)(pirate)
        if decision == False or decision == None: # It's verbose, but important
          #self.game.debug('skipping tactic %s', tactic)
          continue # Try the next tactic
        elif isinstance(decision, (int, long)): # This means an opcode
          self.game.debug('got opcode %s', tactic)
          strategy.set_operation(pirate, decision)
          break # Move on to the next pirate
        elif isinstance(decision[0], list):
          self.game.debug('multiple applied %s', tactic)
          for member in decision[0]:
            strategy.set_mission(member, decision[1])
            if pirate.id != member.id:
              pirates.remove(member)
        else:
          self.game.debug('single tactic %s %s', tactic, strategy.target_counter)
          strategy.set_mission(decision[0], decision[1])
          
      pirates.remove(pirate)
    return strategy

  def permutate(self):
    return self.game.my_pirates()

  def sail(self, strategy):
    """ Now we're in business """
    game = self.game
    for pirate in self.game.my_pirates():
      state_change = getattr(strategy.operations, str(pirate.id), None)
      if state_change: # When we get state changes, we cannot move the pirate further
        self.state_change(pirate, state_change)
        continue
      target = strategy.final_target(pirate) # Get a location for this pirate
      if not target:
        game.debug('no target for pirate %s', pirate.id)
        continue

      if target == pirate.location: # Nothing to do here
        game.debug('target is same as current location %s', pirate.id)
        continue

      direction = game.get_directions(pirate, target)[0] #self.geography.to(pirate, target) # Go go heuristic A*
      game.set_sail(pirate, direction)
    self.strategy = strategy # Go Go garbage collection

  def default_tactics(self):
    """ Returns a set of default tactics. When adding tactical behaviors, please leave a quick note regarding their expected behavior"""
    return [
      # 'cloak', # Should we cloak this pirate?
      'reveal', # Should we reveal this pirate?
      'escape', # Should this pirate escape?
      'ideal_state_strategy', # Have we captured all the islands?
      'group_attack_strategy', # Can we attack an island as a group?
      'edge_attack', # Can we corner the enemy?
      'lone_wolf_attack', # Can we attack a single enemy?
      'standard_targeting' # Simple individual targeting
    ]

  def set_tactical_behavior(self, tactics):
    """ Modifies the tactical behavior for this turn """
    self.tactics = tactics