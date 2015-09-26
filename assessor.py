import math
from opcodes import Opcode
class Assessor(object):
  """ A collection of assessment procedures. I beg you to keep this stateless. """
  def __init__(self, game, strategy, pirates):
    self.game = game
    self.pirates_left = pirates
    self.strategy = strategy

  def ideal_targets(self, force, strategy):
    """ Returns a list of targets for our force """
    game = self.game
    islands = self.islands_being_captured()
    ideals = []
    for island in islands:
        force = self.sort_by_distance_to_target(force, island)
        opposition = len(self.opposition_around(island, 6))
        strength = len(force) # Get the attacking strength
        leader = force[0]
        if (opposition == strength or (opposition == strength-1 and strength > 2)) and self.arrival_in_time(leader, island) and (strategy.heading_to(island) <= 1 or strategy.of(leader) == island):
          ideals.append(island)
    return sorted(ideals, key=lambda island: game.distance(force[0], island)) # Is this naive?

  def islands_being_captured(self):
    """ Returns a list of islands being captured currently """
    return filter(lambda island: island.team_capturing == self.game.ENEMY, self.game.not_my_islands())

  def has_threat(self, force, opposition):
    """ Are two armadas threatning each other? """
    return len(opposition) >= len(force) or not (self.is_alone(force, self.game.ME) and self.is_alone(opposition, self.game.ENEMY))

  def is_alone(self, entity, kind):
    """ Is a given pirate isolated? """
    if len(entity) != 1:
      return False

    group = game.my_pirates() if kind == self.game.ME else game.enemy_pirates()
    for pirate in group:
      if entity[0] != pirate and self.game.in_range(entity[0], pirate):
        return False
    return True

  def potential_threats(self, leader):
    """ Potential threats to an armada leader """
    enemies = self.opposition_around(leader, 8) # TODO: Param
    groups = []
    for enemy in enemies:
      groups.append(self.opposition_around(enemy, Assessor.ATTACK_RADIUS + 1.5)) # TODO: Param
    return max(groups, key=lambda group: len(group))

  def arrival_in_time(self, pirate, target):
    """ Will this pirate arrive before the target is captured? """
    return (self.game.distance(target, pirate) - 2 < target.capture_turns - target.turns_being_captured)

  def force_around(self, leader, options=None):
    """ Our force around a leader, including the leader """
    game = self.game
    pirates = game.my_pirates()
    return filter(lambda pirate: game.in_range(pirate, leader) and (options == Opcode.EVERYONE or (not game.is_capturing(pirate) or (game.is_capturing(pirate) and self.strategy.mission(pirate).turns_being_captured < 10))), pirates) # Filter powerless pirates
  
  def sort_by_distance_to_target(self, pirates, target):
    """ Sort a list of pirate by their distance to a target """
    return sorted(pirates, key=lambda pirate: self.game.distance(pirate, target)) # Sort the pirates by distance to target. May I note how moronic it was to design these two collection utilites with opposing signatures (filter(filterer, list), sorted(list, sorter))?

  def opposition_around(self, target, distance, options=None):
    """ Opposing force around a target """
    game = self.game
    enemies = game.enemy_pirates()
    return filter(lambda enemy: self.distance(enemy, target) < distance and not game.is_capturing(enemy), enemies)

  def distance(self, entity1, entity2):
    """ Aerial distance of two entites """
    if type(entity1) is not tuple:
      loc1 = entity1.location
    else:
      loc1 = entity1

    if type(entity2) is not tuple:
      loc2 = entity2.location
    else:
      loc2 = entity2

    a = loc1[0] - loc2[0]
    b = loc1[1] - loc2[1]
    return math.sqrt(math.pow(a,2) + math.pow(b,2))

  def closest_of(self, targets, entity):
    """ Get the target closest to an entity """
    return min(targets, key=lambda target: self.game.distance(entity, target))

  def flip(self, direction):
    return ({
      's': 'n',
      'e': 'w',
      'n': 's',
      'w': 'e'
      })[direction]

  def all_but(self, direction):
    return ({
      'n': ['e', 'w'],
      's': ['e', 'w'],
      'w': ['n', 's'],
      'e': ['n', 's']
      })[direction]

  def survives_escape(self, pirate_destination, enemy, potential_direction):
    enemy_destination = self.game.destination(enemy, self.game.get_directions(enemy, pirate)[0])
    return game.in_range(enemy_destination, pirate_destination)

  def escpape_direction(self, pirate, enemy):
    direction = self.flip(self.game.get_directions(pirate, enemy)[0])
    pirate_destination = game.destination(pirate, direction)

    if game.is_passable(pirate_destination):
      return direction

    directions = self.all_but(direction)
    
    option1 = self.distance(game.destination(pirate, directions[0]), self.game.destination(enemy, self.game.get_directions(enemy, pirate)[0]))
    option2 = self.distance(game.destination(pirate, directions[1]), self.game.destination(enemy, self.game.get_directions(enemy, pirate)[0]))
    
    return directions[0] if option1 < option2 else directions[1]

  def safe_islands(self):
    return filter(lambda island: len(self.opposition_around(island, 5.5)) < 4, self.game.not_my_islands())

  def abandoned_island(self, islands):
    enemies = self.game.enemy_pirates()
    for island in islands:
      if len(filter(lambda enemy: self.game.distance(enemy, island) < 20, enemies)) == 0:
        return island

  def safe_to_capture(self, island):
    if island.team_capturing != self.game.ME:
      return False
    enemies = self.game.enemy_pirates()
    if len(enemies) == 0:
      return True
    closest = self.closest_of(enemies, island)
    return ((self.game.distance(closest, island) - (island.capture_turns - island.turns_being_captured)) >= 6) and island.owner != self.game.ENEMY


