from opcodes import Opcode #TODO: change name

class Tactician(object):
  """ 
    This is the tactic list.
    To implement a tactic, create a new member method - it will receive a pirate on each call.
    You may either:
      a) Return Operational Suggestion Code from Opcode (one of Opcode.CLOAK, Opcode.REVEAL, etc..) to be applied on the pirate you were given.
      b) Return a tuple of the form ([force], target), where [force] is a subset of pirates from the available pirates list and target is a location or island
      c) Return a list of tuples of the form [([force, target])], where each tuple is as above. NOTE: Oversight is not a babysitter. Don't duplicate your references.
      d) Do nothing and return False
    Your tactic has access to a member object called "assessor". It is already bound to the game object and to the available pirate list for this tactical evaluation.
    Please, for the love of all that is holy, (there's a Bible matkonet coming up, so I'm allowed to say stuff like that), keep a separation of concerns:
      Tactical operations may use assessments and behaviors to produce targets.
      They MAY NOT perform their own assessments (i.e. scan the game state). If you need to assess things, add a member to Assessor
    One last thing, and we cannot stress this enough:
      Never, ever, under any circumstance, (incl. kidnapping, torture or any attempt at forceful submission) SHALL YOU MODIFIY GAME STATE INSIDE THE EXECUTION SCOPE OF A TACTIC.
    TODO: lure enemies away? ace?
  """
  def __init__(self, game, strategy, pirates, assessor):
    self.game = game
    self.pirates = pirates
    self.assessor = assessor
    self.strategy = strategy

  def cloak(self, pirate):

    """ This tactic determines whether a pirate is in need of cloaking """
    game = self.game
    assessor = self.assessor
    island = self.strategy.of(pirate)

    if pirate.is_cloaked or not game.can_cloak() or not island:
      return False

    force = assessor.force_around(pirate)
    opposition = assessor.opposition_around(pirate)
    has_threat = assessor.has_threat(force, opposition)

    if len(assessor.opposition_around(island)) == 1 \
      and game.distance(island, pirate) < 8 \
      and (has_threat or island.team_capturing == game.ENEMY) \
      and len(force) == 1:
        return Opcode.CLOAK

  def reveal(self, pirate):
    if pirate.is_cloaked \
      and self.strategy.has(pirate) \
      and self.assessor.distance(priate, self.strategy.get(pirate)) < 3 \
      and not self.assessor.has_threat(self.force_around(pirate), self.opposition_around(pirate)):
      return Opcode.REVEAL

  def escape(self, pirate):
    return False # Don't change this. I haven't yet added support for ephermal targeting

    """ This tactic determines wheter a pirate should escape (i.e. run away) """
    game = self.game
    full_force = len(self.assessor.force_around(pirate, Opcode.EVERYONE))
    
    for enemy in game.enemy_pirates():
      if assessor.distance(pirate, enemy) >= 6 and not self.game.is_capturing(enemy):
        continue
      opposition = len(self.assessor.opposition_around(enemy, 3)) # TODO: get_attack_radius()
      if (full_force <= opposition):
          return (pirate, self.assessor.escape_direction(pirate), Opcode.EPHEMERAL)

  def ideal_state_strategy(self, pirate):
    return False

  def group_attack_strategy(self, pirate):
    return False # Same as above. This need ephermal targeting too.
    force = self.assessor.force_around(pirate)
    if len(force) <= 1:
      return False

    targets = self.assessor.ideal_targets(force, self.strategy)
    if len(targets) == 0:
      return False

    if self.assessor.should_formate(force):
      return [(force[0], Opcode.STAY), (force[1:], force[0].location)]
    else:
      return (force, targets[0])

  def edge_attack(self, pirate):
    pass

  def lone_wolf_attack(self, pirate):
    pass

  def one_one_one(self, pirate):
    pass

  def standard_targeting(self, pirate):
    game = self.game
    safe_islands = self.assessor.safe_islands() # Safe islands in the game
    islands = self.strategy.untargeted(safe_islands) # Try getting only untargeted islands
    target = None

    if len(islands) == 0: # If we don't have untargeted islands
      islands = safe_islands
      if len(islands) == 0: 
        return False # No safe islands to go to
      islands = filter(lambda island: (self.strategy.enroute(island) >= 3 and self.strategy.get_mission(pirate) != island.id) or (game.get_pirate_on(island) != pirate and self.assessor.safe_to_capture(island)), islands)
      if len(islands) == 0:
        return False
      target = self.assessor.closest_of(islands, pirate)
    else:
      abandoned_island = self.assessor.abandoned_island(islands)
      if abandoned_island and game.distance(pirate, abandoned_island) > 8:
        target = abandoned_island
    return (pirate, target)