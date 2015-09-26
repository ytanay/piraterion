import operations

class Strategy(object):
  """
    This is a single strategy map.
    Strategy are essentially a mapping of bots to targets, using a prioritized queue like system for selecting targets.
    On each turn, the engine removes missions of dead pirates, and clones the current strategy for a breadth-first tactical analysis.
    In the future, this wrapping could be used to test and score destination mappings and select the best one.
  """
  def __init__(self, game=None, missions=None):
    self.game = game # Used to grab islands and reconcile stuff
    self.missions = missions if missions else {} # Maps pirate Ids to island targets. We use this ugly syntax to prevent the mission dict from leaking.
    self.targets = {} # Location targets for immediate perusal. This has precedence over long term missions
    self.operations = {} # Move to dict
  
  def clone(self, game):
    """ Creates a clone of this strategy for evaluation. """
    return Strategy(game, self.missions.copy()) # We don't care about ephemeral targets

  def mission(self, pirate):
    """ Returns the island mission (that is, an island) of a pirate """
    if pirate.id in self.missions:
      return self.game.get_island(self.missions[pirate.id]) 
  def get_mission(self, pirate):
    if pirate.id in self.missions:
      return self.missions[pirate.id]
  def set_mission(self, pirate, island):
    self.game.debug('setting mission for pirate %s : %s', pirate, island)
    if island:
      self.missions[pirate.id] = island.id

  def has_mission(self, pirate):
    return pirate.id in self.missions

  def remove_mission(self, pirate):
    """ Removes a pirate's destination """
    self.missions[pirate.id] = None

  def assign_mission(self, pirates, target):
    """ Assigns destinations for multiple pirates at once """
    for pirate in pirates:
      self.set_mission(pirate, target)

  def set_target(self, pirate, target):
    """ Sets a target location for a pirate """
    self.targets[pirate.id] = target

  def final_target(self, pirate):
    self.game.debug(self.missions)
    """ The final target for this pirate for this mission """
    ephemeral = pirate.id in self.targets
    if ephemeral:
      return ephemeral 
    mission = self.mission(pirate) # TODO: this will throw if there is no island target
    if mission:
      return mission.location

  def set_operation(self, pirate, operation):
    self.operations[pirate.id] = operation

  def reconcile_missions(self):
    """ Removes missions of dead pirates """
    for pirate in self.game.my_lost_pirates():
      self.remove_mission(pirate)

  def enroute(self, island):
    return self.target_counter[island.id]

  def untargeted(self, islands):
    return filter(lambda island: self.enroute(island) == 0, islands)

  def remap_pirate_targets(self):
    """ Counts how many pirates are heading to each island """
    self.target_counter = {}

    for island in self.game.islands():
      self.target_counter[island.id] = 0

    for pirate, target in self.missions.iteritems():
      if target != None:
        self.target_counter[target] += 1