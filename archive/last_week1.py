ghosters = []#the list of individual missions of the ghost_pirates(mission is the islands id)
missions = []#list of team missions(currently empty)
up_down = ""
right_left = ""
pirates_per_island = [] #a list of counters for number of pirates aiming for each island(island 0 in [0])
ignored_pirates=[]

def start_point(game):
    """
    puts in the up_down global 'n' or 's' in which map part the safe zone is
    puts in the right_left global 'e' or 'w' in which map part the safe zone is
    """
    global up_down
    global right_left
    pirate = game.all_my_pirates()[0]
    loc = pirate.initial_loc
    rows = game.rows
    cols = game.cols
    if loc[0] < rows / 2:
        up_down = 'n'
    else:
        up_down = 's'
    if loc[1] > cols / 2:
        right_left = 'e'
    else:
        right_left = 'w'


def pirates_islands():
    """
    puts in the pirates_per_island global the counters as for now
    """
    global pirates_per_island
    for i in range(len(pirates_per_island)):
        pirates_per_island[i] = 0
    for mission in ghosters:
        if mission != None:
            pirates_per_island[mission] = pirates_per_island[mission] + 1

def arrival_in_time(game,pirate,island):
    if game.distance(island, pirate) - 2 < island.capture_turns - island.turns_being_captured:
        return True
    return False

def find_ideal_island(game,team):
    global pirates_per_island
    global ghosters
    optional_islands = []
    for island in game.islands():
        if island.team_capturing == game.ENEMY:
            optional_islands.append(island)
    final_islands=[]
    for island in optional_islands:
        team=closest_pirates(game,island,team)
        game.debug("team %s"%team)
        size,group = size_of_group(game,island)
        if (size == len(team) or (size==len(team)-1 and len(team)>2)) and arrival_in_time(game,team[0],island) \
            and (pirates_per_island[island.id]==0 \
            or ghosters[team[0].id]==island.id):
            final_islands.append(island)
    return final_islands

def ideal_attack(game,pirate):
    global ghosters
    global ignored_pirates
    team=my_team(game,pirate)
    ideal_islands=find_ideal_island(game,team)
    if ideal_islands == []:
        team=[pirate]
        ideal_islands=find_ideal_island(game,team)
        if ideal_islands == []:
            return False
        best_island=get_closest_island(pirate,game,ideal_islands)
        ghosters[pirate.id]=best_island.id
    best_island=get_closest_island(pirate,game,ideal_islands)
    for p in team:
        ghosters[p.id]=best_island.id
        ignored_pirates.append(p)
    return True

def abandoned_island(game):
    islands = game.not_my_islands()
    enemies = game.enemy_pirates()
    bool1 = True
    for island in islands:
        for enemy in enemies:
            if game.distance(enemy, island) < 20:
                bool1 = False
        if bool1:
            return island
        bool1 = True
    return None
def same_mission_team(team):
    global ghosters
    mission=ghosters[team[0].id]
    team1=team[:]
    for pirate in team1:
        if ghosters[pirate.id]!=mission:
            return False
    return True

import random
def best_island_twos(game,pirate):
    global ghosters
    team=my_team(game,pirate)
    counter=0
    is_mission_modified=False
    if len(team)<=2 and not same_mission_team(team):
        return is_mission_modified
    one,two,three,four=find_attack(game)
    for island in two:
        if ghosters[pirate.id]!=island.id :
            if (pirates_per_island[island.id] >= 3 and island.owner!=game.ME )\
                or (pirates_per_island[island.id] >= 2 and island.owner==game.ME):
                game.debug("remove %s"%island.id)
                continue
        size, group = size_of_group(game, island)
        if game.distance(island, pirate) - 2 < island.capture_turns - island.turns_being_captured and size==2:
            for pirate1 in team:
                if counter < 3 and not game.is_capturing(pirate1):
                    game.debug("done")
                    ghosters[pirate1.id]=island.id
                    is_mission_modified=True
                    ignored_pirates.append(pirate1.id)
    return is_mission_modified


def best_island_indiv(game, pirate):
    global pirates_per_island
    """
    tried to find a best island for one man.
    if found and moved towards there return true
    else it returns false
    """
    global ghosters
    one, two, three, more = find_attack(game)
    for island in one:
        if ghosters[pirate.id]!=island.id :
            if (pirates_per_island[island.id] >= 2 and island.owner!=game.ME )\
                or (pirates_per_island[island.id] >= 1 and island.owner==game.ME):
                game.debug("remove %s"%island.id)
                continue
        size, group = size_of_group(game, island)
        game.debug(size)
        if game.distance(island, pirate) - 2 < island.capture_turns - island.turns_being_captured and size == 1 and \
                not game.is_capturing(pirate):
            if run(game, pirate):
                return True
            game.debug("11")
            direction = new_direction(game,pirate,game.get_directions(pirate, island))
            ghosters[pirate.id] = island.id
            if game.distance(pirate, island) < 2 and pirate.is_cloaked and island.team_capturing!=game.ME:
                game.reveal(pirate)
            else:
                game.set_sail(pirate, direction[0])
            game.debug("go")
            return True
    return False


def is_good(game, pirate, directions):
    """
    get a pirate and the list of direction and returns True if
    the next direction is available to pass through or False if not
    """
    dest = game.destination(pirate, directions[0])
    closest=get_closest_island(pirate,game,game.islands())
    if (not game.is_passable(dest)) and game.distance(pirate,closest)>2:
        game.debug("direction not good")
        return False
    return True

def not_trapped(game,position):
    counter=0
    for direction in ['n','s','e','w']:
        new_pos=game.destination(position,direction)
        if not game.is_passable(new_pos):
            counter+=1
    if counter>=2:
        return False
    return True

def to_the_future(game,pirate,direction):
    position1=game.destination(pirate,direction)
    game.debug(not_trapped(game,position1))
    return not_trapped(game,position1)

def alternative_direction(game,pirate):
    for direction in ['e','n','w','s']:
                if is_good(game,pirate,[direction]) and to_the_future(game,pirate,direction):
                    game.debug("new direction %s"%direction)
                    return [direction]

def new_direction(game,pirate,directions):
    if directions==[] or directions==['-']:
        game.debug("1")
        return directions
    if not is_good(game,pirate,directions):
        game.debug("2")
        directions.remove(directions[0])
        if directions==[]:
            game.debug("3")
            return alternative_direction(game,pirate)

        if is_good(game,pirate,directions) and to_the_future(game,pirate,directions[0]):
            game.debug("4")
            return directions
        else:
            game.debug("5")
            return alternative_direction(game,pirate)
    if to_the_future(game,pirate,directions[0]):
        game.debug("6")
        #random.shuffle(directions)
        return directions
    else:
        game.debug("7")
        directions.remove(directions[0])
        if directions==[]:
            return alternative_direction(game,pirate)

        if is_good(game,pirate,directions) and to_the_future(game,pirate,directions[0]):
            return directions

        else:
            return alternative_direction(game,pirate)

    return alternative_direction(game,pirate)

def ghost_creation(game, pirates):
    """
    creates the ghost mission list and the pirates_per_island list according
    to the current map
    """
    global ghosters
    global pirates_per_island
    for pirate in pirates:
        ghosters.append(None)
    for island in game.islands():
        pirates_per_island.append(0)


def my_defence(game, my_pirate):
    """
    get a pirate and returns the power of him and his ratio ally pirates,
    the defence is based of attack capable pirates(not ghost)
    """
    defence = 1
    pirates = game.my_pirates()
    if my_pirate in pirates:
        pirates.remove(my_pirate)
    if game.is_capturing(my_pirate) or my_pirate.is_cloaked:
        defence = 0
    for pirate in game.my_pirates():
        if game.in_range(pirate, my_pirate) and not game.is_capturing(pirate) \
                and not pirate.is_cloaked:
            defence = defence + 1
    return defence


def enemy_defence(game, enemy_pirate):
    """
    same as my_defence but with enemy_pirate
    """
    defence = 1
    if game.is_capturing(enemy_pirate):
        defence = 0
    for pirate in game.enemy_pirates():
        if game.in_range(pirate, enemy_pirate) and pirate != enemy_pirate and not game.is_capturing(pirate):
            defence = defence + 1
    return defence

def my_team(game,pirate):
    team=[pirate]
    for pirate1 in game.my_pirates():
        current_target=game.get_island(ghosters[pirate1.id])
        #bool1=current_target in safe_capture(game,game.islands())
        #bool2=current_target!=None and current_target.owner == game.ME and game.distance(pirate1,current_target)>7
        if game.in_range(pirate,pirate1) and pirate!=pirate1 and not game.is_capturing(pirate1) and len(team)<=2:
            if pirate1.is_cloaked:
                game.reveal(pirate1)
            if pirate.is_cloaked:
                game.reveal(pirate1)
            team.append(pirate1)
    return team

def avoid_tackle(game, pirate):
    """
    not finished, supposed to avoid friendly or ghost tackles
    """
    enemies = game.enemy_pirates()
    avoid_en = None
    for enemy in enemies:
        if game.distance(enemy, pirate) < 3:
            avoid_en = enemy
            break


def ghost_routine(game, ghost_pirate):
    """
    ghost pirate main function
    gives the pirate his best mission or command in ghosters
    """
    global cloak
    global missions
    global ghosters
    global pirates_per_island
    global ignored_pirates
    pirates_islands()
    if run(game,ghost_pirate):
        return
    if ghost_pirate.is_cloaked and ghosters[ghost_pirate.id]!=None and game.distance(ghost_pirate,game.get_island(ghosters[ghost_pirate.id]))<3 and len(my_team(game,ghost_pirate))==1 and not enemy_team_threat(game,[ghost_pirate]):
            game.reveal(ghost_pirate)
            return
    if ghost_pirate.id in ignored_pirates:
        if ghost_pirate.is_cloaked:
            game.reveal(ghost_pirate)
            return
        directions=new_direction(game,ghost_pirate,game.get_directions(ghost_pirate,game.get_island(ghosters[ghost_pirate.id])))
        game.set_sail(ghost_pirate,directions[0])
        return
    if ghost_pirate.is_lost:
        ghosters[ghost_pirate.id] = None
        return
    all_mine = False
    if game.not_my_islands() == []:
        all_mine = True
        for island in game.islands():
            if island.team_capturing == game.ENEMY or run(game, ghost_pirate):
                all_mine = False
    if ghost_pirate.is_lost:
        ghosters[ghost_pirate.id] = None
        return
    if all_mine:
        run(game, ghost_pirate)
        for island in game.my_islands():
            if island.location == ghost_pirate.location:
                game.set_sail(ghost_pirate, 'e')
    

    if ideal_attack(game,ghost_pirate):
        if ghost_pirate.is_cloaked and len(my_team(game,ghost_pirate))>1:
            game.reveal(ghost_pirate)
            return
        if game.can_cloak() and ghost_pirate.is_cloaked == False and not game.is_capturing(ghost_pirate) and \
            (enemy_team_threat(game, [ghost_pirate]) or game.enemy_pirates() == []) and \
                    len(my_team(game,ghost_pirate)) == 1 and game.distance(ghost_pirate,game.get_island(ghosters[ghost_pirate.id]))<8:
            game.cloak(ghost_pirate)
            return
        directions=new_direction(game,ghost_pirate,game.get_directions(ghost_pirate,game.get_island(ghosters[ghost_pirate.id])))
        game.set_sail(ghost_pirate,directions[0])
        return
    if ghost_pirate.is_cloaked and ghosters[ghost_pirate.id]!=None and game.distance(ghost_pirate,game.get_island(ghosters[ghost_pirate.id]))<3 and my_defence(game,ghost_pirate)>1:
            game.reveal(ghost_pirate)
    elif ghost_pirate.is_cloaked:
        islands = game.not_my_islands()
        for mission in ghosters:
            island=game.get_island(mission)
            if island in islands and ((mission != ghosters[ghost_pirate.id] \
                    and pirates_per_island[mission]>=3) or (island in safe_capture(game,game.islands()) and game.get_pirate_on(island)!=ghost_pirate)):
                # game.debug("removed island number:%s"%mission)
                islands.remove(game.get_island(mission))
        if islands != []:
            closest=get_closest_island(ghost_pirate, game, islands)
            target = closest
            if abandoned_island(game) in islands and game.distance(ghost_pirate,abandoned_island(game))-game.distance(ghost_pirate,closest)<game.rows/2 \
            and pirates_per_island[abandoned_island(game).id]<2:
                target = abandoned_island(game)
            ghosters[ghost_pirate.id] = target.id
        else:
            islands_alt = game.not_my_islands()
            game.debug("a %s"%safe_capture(game,game.islands()))
            for island in islands_alt:
                if (pirates_per_island[island.id] >= 3 and ghosters[ghost_pirate.id] != island.id)\
                        or (island in safe_capture(game,game.islands()) and game.get_pirate_on(island)!=ghost_pirate):
                    islands_alt.remove(island)
            target = get_closest_island(ghost_pirate, game, islands_alt)
            ghosters[ghost_pirate.id] = target.id

        if game.distance(ghost_pirate, target) > 2:
            directions = new_direction(game,ghost_pirate,game.get_directions(ghost_pirate, target))
            game.set_sail(ghost_pirate, directions[0])
        elif not enemy_team_threat(game, [ghost_pirate]):
            if ghost_pirate.is_cloaked:
                if run(game, ghost_pirate):
                    return
                if target.team_capturing!=game.ME:
                    game.reveal(ghost_pirate)
                else:
                    return
            else:
                directions = new_direction(game,ghost_pirate,game.get_directions(ghost_pirate, target))
                game.set_sail(ghost_pirate, directions[0])
        else:
            if run(game, ghost_pirate):
                game.debug('run %s' % ghost_pirate)
                return
            return
    elif not ghost_pirate.is_cloaked:
        a = run(game, ghost_pirate)
        if a:
            if a:
                game.debug('run %s' % ghost_pirate)
            return
        islands = game.not_my_islands()
        for mission in ghosters:
           island=game.get_island(mission)
           if island in islands and ((mission != ghosters[ghost_pirate.id] \
                    and pirates_per_island[mission]>=3) or (island in safe_capture(game,game.islands()) and game.get_pirate_on(island)!=ghost_pirate)):
                # game.debug("pirate %s removed island number:%s"%(ghost_pirate,mission))
                islands.remove(game.get_island(mission))
        if islands != []:
            closest=get_closest_island(ghost_pirate, game, islands)
            target = closest
            if abandoned_island(game) in islands and game.distance(ghost_pirate,abandoned_island(game))-game.distance(ghost_pirate,closest)<game.rows/2 \
            and pirates_per_island[abandoned_island(game).id]<2:
                target = abandoned_island(game)
            ghosters[ghost_pirate.id] = target.id
        else:
            islands_alt = game.not_my_islands()
            game.debug("a %s"%safe_capture(game,game.islands()))
            for island in islands_alt:
                if (pirates_per_island[island.id] >= 3 and ghosters[ghost_pirate.id] != island.id)\
                        or (island in safe_capture(game,game.islands()) and game.get_pirate_on(island)!=ghost_pirate):
                    islands_alt.remove(island)
            target = get_closest_island(ghost_pirate, game, islands_alt)
        directions = new_direction(game,ghost_pirate,game.get_directions(ghost_pirate, target))
        game.set_sail(ghost_pirate, directions[0])
        ghosters[ghost_pirate.id] = target.id
    else:
        return

def safe_capture(game,islands):
    global ghosters
    safe_islands=[]
    for island in islands:
        if island.team_capturing==game.ME:
            enemy_pirates=game.enemy_pirates()
            if len(enemy_pirates)==0:
                return safe_islands
            enemy_pirates=closest_pirates(game,island,enemy_pirates)
            if game.distance(enemy_pirates[0],island)>island.capture_turns-island.turns_being_captured+5 and island.owner!=game.ENEMY:
                safe_islands.append(island)
    return safe_islands

def run_direction(game, pirate, enemy_pirate):
    """
    gets a pirate and an enemy pirate to run from and returns
    the ideal run direction(char)
    """
    global up_down
    global right_left
    if right_left == 'e':
        other = 'w'
    else:
        other = 'e'
    if up_down == 'n':
        other1 = 's'
    else:
        other1 = 'n'
    dist1 = game.distance(enemy_pirate, game.destination(pirate, right_left))
    dist2 = game.distance(enemy_pirate, game.destination(pirate, other))
    dist3 = game.distance(enemy_pirate, game.destination(pirate, up_down))
    dist4 = game.distance(enemy_pirate, game.destination(pirate, other1))
    lst = [dist1, dist2, dist3, dist4]
    lst.sort()
    best_run_dir = lst[3]
    if best_run_dir == dist1 and (not game.in_range(enemy_pirate,game.destination(pirate, right_left)) or pirate.is_cloaked):
        if not game.is_passable(game.destination(pirate, right_left)):
            return up_down
        return right_left
    if best_run_dir == dist3 and (not game.in_range(enemy_pirate,game.destination(pirate, up_down)) or pirate.is_cloaked):
        if not game.is_passable(game.destination(pirate, up_down)):
            if best_run_dir == dist1:
                return right_left
            else:
                return other
        return up_down
    if best_run_dir == dist2 and (not game.in_range(enemy_pirate,game.destination(pirate, other))or pirate.is_cloaked):
        if not game.is_passable(game.destination(pirate, other)):
            return up_down
        return right_left
    if best_run_dir == dist4 and (not game.in_range(enemy_pirate,game.destination(pirate, other1)) or pirate.is_cloaked):
        if not game.is_passable(game.destination(pirate, other1)):
            if best_run_dir == dist1:
                return right_left
            else:
                return other
        return other1
    return right_left


def run(game, pirate):
    """
    if running is necessary it runs and returns True
    otherwise it return False and do nothing
    """
    global ghosters
    power = my_defence(game, pirate)
    enemies = game.enemy_pirates()
    for enemy in enemies:
        anti_power = enemy_defence(game, enemy)
        if (game.distance(pirate, enemy) < 7 and not game.is_capturing(enemy) and (power < anti_power or (len(my_team(game,pirate))==1 and ghosters[pirate.id] != None and\
         game.get_island(ghosters[pirate.id]).team_capturing!=game.ME and not game.is_capturing(pirate) and power<=anti_power)))\
        or(pirate.is_cloaked and game.distance(pirate, enemy) < 2 and enemy_defence(game,enemy)>1 ):
            if anti_power==1 and power==1 and ghosters[pirate.id] != None and game.get_island(ghosters[pirate.id]).team_capturing!=game.ME and   game.distance(pirate, game.get_island(ghosters[pirate.id]))\
            and not pirate.is_cloaked and game.can_cloak():
                game.cloak(pirate)
                return
            game.set_sail(pirate, run_direction(game, pirate, enemy))
            if ghosters[pirate.id] != None:
                if game.distance(pirate, game.get_island(ghosters[pirate.id])) > 10:
                    ghosters[pirate.id] = None
            game.debug("run %s"%pirate)
            return True
    return False


def closest_pirates(game, island, pirates):
    """
    recv an island and available pirates and return a list of them from
    the closest to the farest one from the island
    """
    pirate_lst = []
    dist_lst = []
    for pirate in pirates:
        distance = game.distance(pirate, island)
        dist_lst.append((distance, pirate))
    dist_lst = sorted(dist_lst, key=lambda dist: dist[0])
    for tuple in dist_lst:
        pirate_lst.append(tuple[1])
    return pirate_lst


def find_attack(game):
    """
    this function returns 4 lists:
    islands that one ship is capturing them
    islands where two ships are capturing them
    islands where three ships are capturing them
    islands where more than three ships are capturing them
    """
    attack_islands1 = []
    attack_islands2 = []
    attack_island3 = []
    attack_big_islands = []
    islands = game.islands()
    counter1 = 1
    for island in islands:
        if ((island in game.my_islands() or island in game.neutral_islands()) ) and game.get_pirate_on(island) != None:
            enemy_pirate = game.get_pirate_on(island)
            if enemy_pirate.owner == game.ENEMY:
                for enemy in game.enemy_pirates():
                    if enemy != enemy_pirate:
                        if game.distance(enemy_pirate, enemy) < 5:
                            counter1 = counter1 + 1
                if counter1 == 1:
                    attack_islands1.append(island)
                    counter1 = 1
                elif counter1 == 2:
                    attack_islands2.append(island)
                    counter1 = 1
                elif counter1 == 3:
                    attack_island3.append(island)
                    counter1 = 1
                else:
                    attack_big_islands.append(island)
                    counter1 = 1
    #game.debug("special island 1")
    #game.debug(attack_islands1)
    game.debug("special island 2")
    game.debug(attack_islands2)
    return (attack_islands1, attack_islands2, attack_island3, attack_big_islands)


def get_closest_island(pirate, game, islands):
    """
    get a pirate and a list of islands and returns
    the closest island
    """
    lis_d = []
    islands1 = islands
    if islands == []:
        islands1 = game.my_islands()
    for island in islands1:
        lis_d.append(game.distance(pirate, island))
    min_value_index = lis_d.index(min(lis_d))
    return islands1[min_value_index]


def size_of_group(game, island):
    """
    get an island and returns a tuple of size of an enemy group
    near that island(int) and the list of enemy pirates
    """
    enemies = game.enemy_pirates()
    group = []
    ignoreEnemies = []

    for enemy in enemies:
        if enemy not in ignoreEnemies:
            otherEnemies = enemies[:]
            otherEnemies.remove(enemy)
            group = [enemy]
            for otherEnemy in otherEnemies:
                if game.distance(otherEnemy, enemy) < 5 and (otherEnemy not in group) and (
                            otherEnemy not in ignoreEnemies):
                    ignoreEnemies.append(otherEnemy)
                    enemy = otherEnemy
                    group.append(otherEnemy)
                    ignoreEnemies.append(otherEnemy)

            if game.distance(group[0], island) < 5:
                return len(group), group
    return 0, []


def enemy_team_threat(game, my_team1):
    """
    if a group of enemies is near my team it returns
    true otherwise it returns false
    """
    enemies = game.enemy_pirates()
    groups = []
    ignoreEnemies = []

    for enemy in enemies:
        if enemy not in ignoreEnemies:
            otherEnemies = enemies[:]
            otherEnemies.remove(enemy)
            group = [enemy]

            for otherEnemy in otherEnemies:
                if game.distance(otherEnemy, enemy) < 5 and (otherEnemy not in group) and (
                            otherEnemy not in ignoreEnemies):
                    enemy = otherEnemy
                    group.append(otherEnemy)
                    ignoreEnemies.append(otherEnemy)
            if len(group) >= my_defence(game, my_team1[0]):
                clos = get_closest_island(group[0], game, game.islands())
                group = closest_pirates(game, clos, group)
                if game.distance(group[0], my_team1[0]) < 10 and \
                        (game.distance(group[0], clos) > 1 and (
                                        len(group) == len(my_team1) or len(group) > len(my_team1))):
                    game.debug("threat: my %s %s" % (my_team1[0], group[0]))
                    return True
    return False


def do_turn(game):
    """
    performs the turn
    """
    global ignored_pirates
    global ghosters
    if game.get_turn() == 1:
        start_point(game)
    ghost_creation(game, game.all_my_pirates())
    ignored_pirates=[]
    for pirate in game.all_my_pirates():
        ghost_routine(game, pirate)
    for i in range(len(ghosters)):
        if ghosters[i] != None:
            game.debug("%s missions %s" % (i, ghosters[i]))
