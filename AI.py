import random
from movelist import *

# Pre-computation of data for efficiency and clarity
# These should ideally be defined at a module level outside the function
# to avoid re-creation on every call.

TYPE_DATA = {
  "Bug": {"weakness": ["Rock", "Flying", "Fire"], "resistance": ["Grass", "Fighting", "Ground"]},
  "Water": {"weakness": ["Grass", "Electric"], "resistance": ["Water", "Ice", "Fire", "Steel"]},
  "Ghost": {"weakness": ["Dark", "Ghost"], "resistance": ["Poison", "Bug"], "immunity": ["Normal"]},
  "Electric": {"weakness": ["Ground"], "resistance": ["Flying", "Electric", "Steel"]},
  "Psychic": {"weakness": ["Bug", "Ghost", "Dark"], "resistance": ["Fighting", "Psychic"]},
  "Ice": {"weakness": ["Steel", "Fire", "Fighting", "Rock"], "resistance": ["Ice"]},
  "Dragon": {"weakness": ["Ice", "Dragon", "Fairy"], "resistance": ["Fire", "Water", "Grass", "Electric"]},
  "Fairy": {"weakness": ["Poison", "Steel"], "resistance": ["Fighting", "Bug", "Dark"], "immunity": ["Dragon"]},
  "Dark": {"weakness": ["Fighting", "Bug", "Fairy"], "resistance": ["Ghost", "Psychic"], "immunity": ["Psychic"]},
  "Steel": {"weakness": ["Fire", "Fighting", "Ground"], "resistance": ["Rock", "Ice", "Fairy", "Normal", "Flying", "Grass", "Psychic", "Bug", "Steel", "Dragon"], "immunity": ["Poison"]},
  "Grass": {"weakness": ["Flying", "Poison", "Bug", "Ice", "Fire"], "resistance": ["Ground", "Electric", "Grass", "Water"]},
  "Fire": {"weakness": ["Rock", "Ground", "Water"], "resistance": ["Bug", "Steel", "Grass", "Ice", "Fairy", "Fire"]},
  "Poison": {"weakness": ["Psychic", "Ground"], "resistance": ["Grass", "Fairy", "Bug", "Poison", "Fighting"]},
  "Flying": {"weakness": ["Rock", "Ice", "Electric"], "resistance": ["Fighting", "Bug", "Grass"], "immunity": ["Ground"]},
  "Rock": {"weakness": ["Fighting", "Ground", "Steel", "Grass", "Water"], "resistance": ["Flying", "Normal", "Fire", "Poison"]},
  "Normal": {"weakness": ["Fighting"], "resistance": [], "immunity": ["Ghost"]},
  "Fighting": {"weakness": ["Flying", "Psychic", "Fairy"], "resistance": ["Bug", "Rock", "Dark"]},
  "Ground": {"weakness": ["Water", "Grass", "Ice"], "resistance": ["Poison", "Rock"], "immunity": ["Flying"]}
}

TYPE_MOVES = {
  "Water": typemoves.watermoves, "Fire": typemoves.firemoves, "Grass": typemoves.grassmoves,
  "Electric": typemoves.electricmoves, "Rock": typemoves.rockmoves, "Ground": typemoves.groundmoves,
  "Ghost": typemoves.ghostmoves, "Normal": typemoves.normalmoves, "Dark": typemoves.darkmoves,
  "Psychic": typemoves.psychicmoves, "Bug": typemoves.bugmoves, "Flying": typemoves.flyingmoves,
  "Fighting": typemoves.fightingmoves, "Fairy": typemoves.fairymoves, "Steel": typemoves.steelmoves,
  "Poison": typemoves.poisonmoves, "Ice": typemoves.icemoves, "Dragon": typemoves.dragonmoves
}

# Consolidated ability and weather immunities
ABILITY_IMMUNITIES = {
  "taunted": typemoves.statusmove,
  ("Dazzling", "Queenly Majesty", "Armor Tail"): typemoves.prioritymove,
  ("Water Absorb", "Water Compaction", "Storm Drain", "Dry Skin"): typemoves.watermoves,
  ("Volt Absorb", "Motor Drive", "Lightning Rod"): typemoves.electricmoves,
  ("Flash Fire", "Well-baked Body"): typemoves.firemoves,
  ("Levitate", "Earth Eater"): typemoves.groundmoves,
  "Sap Sipper": typemoves.grassmoves,
  "Mountaineer": typemoves.rockmoves,
  "Immunity": typemoves.poisonmoves,
  "Dark Mind": typemoves.psychicmoves,
  "Purifying Salt": typemoves.ghostmoves
}

async def moveAI(x, y, tr1, tr2, field):
  """
  Determines the best move for an AI Pokémon.

  Args:
    x (object): The AI's Pokémon.
    y (object): The opponent's Pokémon.
    tr1 (object): The AI trainer's state.
    tr2 (object): The opponent trainer's state.
    field (object): The battlefield state.

  Returns:
    tuple: (chosen_move, effective_moves, super_effective_STAB_moves, immune_moves)
  """
  
  # 1. Initialize move pool
  mymove = x.maxmoves.copy() if x.dmax else x.moves.copy()
  
  # Handle edge cases with highest priority
  if x.ability == "Imposter" and not y.dmax:
    mymove = y.moves.copy()
  if x.zuse and tr1.canz:
    x.zuse = False
    tr1.canz = False
    return x.zmove, [], [], []
  if not mymove:
    return "Struggle", [], [], []
  
  # 2. Pre-calculate move categories
  my_types = [t for t in [x.primaryType, x.secondaryType, x.teraType] if t is not None]
  
  mystablist = [] # Changed from dict to list
  for my_type in my_types:
    if my_type in TYPE_MOVES:
      # Corrected: Use .extend() to add the elements of the set
      mystablist.extend(list(set(mymove) & set(TYPE_MOVES[my_type])))

  # 3. Determine move effectiveness and immunities
  weaklist, resistlist, immunelist, myimmunemove = set(), set(), set(), set()
  
  for ptype in [y.primaryType, y.secondaryType, y.teraType]:
    if ptype in TYPE_DATA:
      if ptype not in ["???", "Stellar"]:
        weaklist.update(TYPE_DATA[ptype]["weakness"])
        resistlist.update(TYPE_DATA[ptype]["resistance"])
        if "immunity" in TYPE_DATA[ptype]:
          immunelist.update(TYPE_DATA[ptype]["immunity"])

  # Calculate moves the AI's Pokémon has that are effective, resisted, or immune
  all_moves = set(mymove)
  emove = {move for m_type in weaklist if m_type in TYPE_MOVES for move in all_moves & set(TYPE_MOVES[m_type])}
  resmove = {move for m_type in resistlist if m_type in TYPE_MOVES for move in all_moves & set(TYPE_MOVES[m_type])}
  
  # Calculate moves the opponent is immune to
  myimmunemove.update({move for m_type in immunelist if m_type in TYPE_MOVES for move in all_moves & set(TYPE_MOVES[m_type])})
  
  # Check for ability-based immunities
  for abilities, moveset in ABILITY_IMMUNITIES.items():
    if isinstance(abilities, str) and y.ability == abilities:
      myimmunemove.update(all_moves & set(moveset))
    elif isinstance(abilities, tuple) and y.ability in abilities:
      myimmunemove.update(all_moves & set(moveset))
  
  # Check for other immunities
  if y.item == "Air Balloon": myimmunemove.update(all_moves & set(typemoves.groundmoves))
  if field.weather == "Desolate Land": myimmunemove.update(all_moves & set(typemoves.watermoves))
  if field.weather == "Primordial Sea": myimmunemove.update(all_moves & set(typemoves.firemoves))
  if x.taunted: myimmunemove.update(all_moves & set(typemoves.statusmove))

  # Remove all immune moves from the available pool
  mymove = list(all_moves - myimmunemove)
  emove = list(emove - myimmunemove)
  resmove = list(resmove - myimmunemove)
  
  # 4. Implement AI decision-making hierarchy
  use = None
  # Corrected: Now that mystablist is a list, you can use sets for intersection
  superduper = list(set(emove) & set(mystablist))

  # A. Guaranteed Moves (Highest Priority)
  if x.fmove and any(m in mymove for m in ["Outrage", "Thrash", "Petal Dance", "Raging Fury"]):
    use = next((m for m in ["Outrage", "Thrash", "Petal Dance", "Raging Fury"] if m in mymove), None)
  elif "Counter" in mymove and y.atkcat == "Physical" and y.use in typemoves.physicalmoves:
    use = "Counter"
  elif "Mirror Coat" in mymove and y.atkcat == "Special" and y.use not in typemoves.physicalmoves + typemoves.statusmove:
    use = "Mirror Coat"
  elif "Sleep Talk" in mymove and x.status == "Sleep" and not x.choiced:
    use = "Sleep Talk"

  # B. High-Impact Moves (Conditional Priority)
  if use is None:
    # Emergency healing
    if "Healing Wish" in mymove and x.hp <= x.maxhp * 0.25:
      use = "Healing Wish"
    elif x.hp <= x.maxhp / 3 and list(all_moves & set(typemoves.healingmoves)):
      use = random.choice(list(all_moves & set(typemoves.healingmoves)))
    
    # Hazard Control
    elif tr1.hazard and "Defog" in mymove:
      use = "Defog"
    
    # Status infliction
    elif "Will-O-Wisp" in mymove and "Burned" not in y.status and "Steel" not in [y.primaryType, y.secondaryType, y.teraType]:
      use = "Will-O-Wisp"
    elif "Thunder Wave" in mymove and "Paralyzed" not in y.status and "Ground" not in [y.primaryType, y.secondaryType, y.teraType]:
      use = "Thunder Wave"
    elif "Toxic" in mymove and "Poisoned" not in y.status:
      use = "Toxic"
  
  # C. Attacking Moves (Based on Effectiveness and STAB)
  if use is None:
    if superduper:
      use = random.choice(superduper)
    elif emove:
      use = random.choice(list(emove)) # emove is a set so it must be cast to a list
    elif list(all_moves & set(mystablist)):
      use = random.choice(list(all_moves & set(mystablist)))
      
  # Filter out redundant status/field moves
  if "Sunny" in field.weather and "Sunny Day" in mymove:
    mymove.remove("Sunny Day")
  if "Rainy" in field.weather and "Rain Dance" in mymove:
    mymove.remove("Rain Dance")
  if "Sandstorm" in field.weather and "Sandstorm" in mymove:
    mymove.remove("Sandstorm")
  if "Snowscape" in field.weather and "Snowscape" in mymove:
    mymove.remove("Snowscape")
  if field.terrain != "Normal" and set(mymove) & set(typemoves.terrainmove):
    for move in list(set(mymove) & set(typemoves.terrainmove)):
      mymove.remove(move)
  if tr1.tailwind and "Tailwind" in mymove:
    mymove.remove("Tailwind")
  if tr1.reflect and "Reflect" in mymove:
    mymove.remove("Reflect")
  if tr1.lightscreen and "Light Screen" in mymove:
    mymove.remove("Light Screen")
    
  # D. Setup/Support Moves (When the AI has an advantage)
  if use is None and x.speed > y.speed and x.hp >= x.maxhp * 0.75:
    if "Swords Dance" in mymove and x.atk > x.spatk and x.atkb < 6:
      use = "Swords Dance"
    elif "Nasty Plot" in mymove and x.spatk > x.atk and x.spatkb < 6:
      use = "Nasty Plot"
    elif "Dragon Dance" in mymove and x.atkb < 6 and x.speedb < 6:
      use = "Dragon Dance"
    elif "Calm Mind" in mymove and x.spatkb < 6 and x.spdefb < 6:
      use = "Calm Mind"
    elif "Agility" in mymove and x.speedb < 6:
      use = "Agility"
    elif "Substitute" in mymove and y.hp >= y.maxhp * 0.5:
      use = "Substitute"
    elif "Reflect" in mymove and y.atk > y.spatk and not tr1.reflect:
      use = "Reflect"
    elif "Light Screen" in mymove and y.spatk > y.atk and not tr1.lightscreen:
      use = "Light Screen"
    elif "Stealth Rock" in mymove and not tr2.hazard.get("Stealth Rock"):
      use = "Stealth Rock"
    elif "Toxic Spikes" in mymove and not tr2.hazard.get("Toxic Spikes"):
      use = "Toxic Spikes"

  # E. Last Resort / Fallback Moves
  if use is None:
    if "Flip Turn" in mymove and "Hero" not in x.name and x.ability == "Zero to Hero":
      use = "Flip Turn"
    elif "Hex" in mymove and y.status != "Alive":
      use = "Hex"
    elif "Explosion" in mymove and y.hp <= y.maxhp * 0.5:
      use = "Explosion"

  # F. Final Fallback (If no strategic move is found)
  if use is None:
    if mymove:
      use = random.choice(mymove)
    else:
      use = "Struggle"
  
  # 5. Handle Choice Items
  if "Choice" in x.item and not x.choiced and not x.dmax:
    x.choiced = True
    x.choicedmove = use
  if x.choiced and not x.dmax and x.choicedmove in x.moves:
    use = x.choicedmove

  return use, list(emove), list(superduper), list(myimmunemove)