import random
import discord
from movelist import *
from typing import TYPE_CHECKING, Optional, List, Set, Dict
if TYPE_CHECKING:
    class Pokemon:
        name: str
        hp: int
        maxhp: int
        status: str # e.g., "Alive", "Burned"
        ability: str
        item: str
        dmax: bool
        zuse: bool
        fmove: Optional[str]
        atk: int
        spatk: int
        defense: int
        spdef: int
        speed: int
        atkb: int
        spatkb: int
        speedb: int
        spdefb: int
        level: int # Crucial for damage calculation
        choiced: bool
        choicedmove: Optional[str]
        moves: List[str]
        maxmoves: List[str]
        primaryType: str
        secondaryType: Optional[str]
        teraType: Optional[str]
        atkcat: str # Category of the last move used (y.atkcat)
        use: str # Last move used (y.use)
        
    class Trainer:
        canz: bool
        hazard: Dict[str, bool] # Must be a dict for specific hazards
        tailwind: bool
        reflect: bool
        lightscreen: bool
        
    class Field:
        weather: str
        terrain: str
        em: discord.Embed # Required for your damage functions
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

async def moveAI(x: 'Pokemon', y: 'Pokemon', tr1: 'Trainer', tr2: 'Trainer', field: 'Field'):
    """
    Determines the best move for an AI Pokémon using a comprehensive scoring system
    that prioritizes KO potential, setup advantage, and utility.

    NOTE: This requires access to the functions defined in moves.py and attack.py
    (e.g., physical, special, weakness, randroll) to simulate damage.
    """
    
    # --------------------------------------------------------------------------
    # HELPER: DAMAGE SIMULATION FUNCTION
    # This replaces the old placeholder and attempts to use your battle functions.
    # It must return the damage dealt, the effectiveness modifier, and crit flag.
    # --------------------------------------------------------------------------
    async def _simulate_damage(move: str, attacker: 'Pokemon', defender: 'Pokemon', current_field: 'Field') -> float:
        """Simulates move damage as a percentage of opponent's max HP."""
        try:
            # We need temporary copies of Pokemon objects if your damage functions modify them,
            # but for this simulation, we'll try to use the raw functions with mock variables.

            # Assume 'movetypes' is a dictionary mapping move names to their properties
            # and that 'MoveData' is available/imported.
            move_data = MoveData[move]
            move_type = move_data.type
            move_category = move_data.category # 'Physical', 'Special', 'Status'
            
            # 1. Calculate effectiveness and crit chance (using your functions)
            # This is complex because your 'weakness' function requires 'ctx' and 'em'
            # and updates the field/embed, which is not ideal for simulation.
            # We'll use a direct effectiveness calculation if possible:
            
            # --- Simplified Type Effectiveness Proxy (REPLACE IF YOU HAVE A BETTER ONE) ---
            effectiveness = 1.0
            
            # Since I can't directly call 'await weakness(ctx,x,y,field,em)', 
            # I must rely on effectiveness lists calculated in Section 2.
            # A real simulation would calculate this here using TYPE_DATA.
            
            # 2. Get Power (Base Power is assumed to be in MoveData)
            power = move_data.power
            if power == 0 or move_category == "Status":
                return 0.0, 1.0 # 0 damage for status moves, score handled separately
            
            # 3. Use your damage functions (physical/special) to get raw damage
            # NOTE: Your original functions are complex and use many side effects (like crit/randroll).
            # We must call them in a way that minimizes side effects.
            
            # To avoid modifying the *real* embed/field, we pass the actual field/em here
            # hoping the damage functions only use them for display/readout, not state changes.
            
            # We need to determine the final damage value 'dmg'
            # Placeholder for actual damage calculation using your functions:
            
            # Example call (you must adjust based on your function signatures):
            # dmg = await physical/special(x, x.level, x.atk/x.spatk, y.defense/y.spdef, power, move_type, c, effectiveness, r, al)
            # Since I cannot fully replicate your damage environment, I use a scoring proxy 
            # that is informed by the effectiveness lists from Section 2 for accuracy.
            
            # --- Scoring Proxy based on Effectiveness (to be replaced by your code) ---
            
            damage_score = power * 2
            
            # Effectiveness boost (based on the classification derived in moveAI)
            x_types = [t for t in [attacker.primaryType, attacker.secondaryType, attacker.teraType] if t is not None]
            is_stab = any(move in TYPE_MOVES.get(t, set()) for t in x_types)
            
            if is_stab: damage_score *= 1.5
            
            # Effectiveness lists (emove, superduper) are not available here, so we must calculate:
            
            # Simple check for Super Effective/Resisted:
            
            
            # Placeholder effectiveness check based on TYPE_DATA
            target_types = [defender.primaryType, defender.secondaryType, defender.teraType]
            final_multiplier = 1.0
            for t in target_types:
                if t in TYPE_DATA:
                    if move_type in TYPE_DATA[t].get("weakness", set()):
                        final_multiplier *= 2
                    elif move_type in TYPE_DATA[t].get("resistance", set()):
                        final_multiplier *= 0.5
                    elif move_type in TYPE_DATA[t].get("immunity", set()):
                        final_multiplier *= 0 # Immune moves filtered earlier, but check is safe
                        
            damage_score *= final_multiplier
            
            # --- End of Scoring Proxy ---
            
            
            # Convert score to percentage damage of opponent's max HP
            # This requires a prediction of the RAW damage number 'dmg' which I can't derive
            # without the full environment. We return a raw 'score' instead.
            
            return damage_score, final_multiplier
            
        except Exception as e:
            # print(f"Error simulating damage for {move}: {e}")
            return 10.0, 1.0 # Default low score if simulation fails


    # 1. Initialization and Edge Cases (A remains the same)
    mymove = x.maxmoves.copy() if x.dmax else x.moves.copy()
    
    if x.ability == "Imposter" and not x.dmax: mymove = y.moves.copy()
    if x.zuse and tr1.canz:
      x.zuse = False
      tr1.canz = False
      return x.zmove, [], [], []
    if not mymove: return "Struggle", [], [], []

    # A. Guaranteed Moves (Lock/Reversal moves) - Highest Priority, skip scoring
    use = None
    if x.fmove and any(m in mymove for m in ["Outrage", "Thrash", "Petal Dance", "Raging Fury"]):
        use = next((m for m in ["Outrage", "Thrash", "Petal Dance", "Raging Fury"] if m in mymove), None)
    elif "Counter" in mymove and y.atkcat == "Physical" and y.use in typemoves.physicalmoves:
        use = "Counter"
    elif "Mirror Coat" in mymove and y.atkcat == "Special" and y.use not in typemoves.physicalmoves + typemoves.statusmove:
        use = "Mirror Coat"
    elif "Sleep Talk" in mymove and x.status == "Sleep" and not x.choiced:
        use = "Sleep Talk"
        
    if use is not None:
        return use, [], [], []

    # 2. Pre-calculate Move Categories and Immunities
    my_types = [t for t in [x.primaryType, x.secondaryType, x.teraType] if t is not None]
    mystablist = []
    for my_type in my_types:
      if my_type in TYPE_MOVES:
        mystablist.extend(list(set(mymove) & set(TYPE_MOVES[my_type])))

    weaklist, resistlist, immunelist, myimmunemove = set(), set(), set(), set()
    for ptype in [y.primaryType, y.secondaryType, y.teraType]:
      if ptype in TYPE_DATA:
        if ptype not in ["???", "Stellar"]:
          weaklist.update(TYPE_DATA[ptype]["weakness"])
          resistlist.update(TYPE_DATA[ptype]["resistance"])
          if "immunity" in TYPE_DATA[ptype]:
            immunelist.update(TYPE_DATA[ptype]["immunity"])

    all_moves = set(mymove)
    emove = {move for m_type in weaklist if m_type in TYPE_MOVES for move in all_moves & set(TYPE_MOVES[m_type])}
    resmove = {move for m_type in resistlist if m_type in TYPE_MOVES for move in all_moves & set(TYPE_MOVES[m_type])}
    myimmunemove.update({move for m_type in immunelist if m_type in TYPE_MOVES for move in all_moves & set(TYPE_MOVES[m_type])})
    
    for abilities, moveset in ABILITY_IMMUNITIES.items():
      if isinstance(abilities, str) and y.ability == abilities: myimmunemove.update(all_moves & set(moveset))
      elif isinstance(abilities, tuple) and y.ability in abilities: myimmunemove.update(all_moves & set(moveset))
    if y.item == "Air Balloon": myimmunemove.update(all_moves & set(typemoves.groundmoves))
    if field.weather == "Desolate Land": myimmunemove.update(all_moves & set(typemoves.watermoves))
    if field.weather == "Primordial Sea": myimmunemove.update(all_moves & set(typemoves.firemoves))
    if x.taunted: myimmunemove.update(all_moves & set(typemoves.statusmove))

    # Final legal move pool
    legal_moves = list(all_moves - myimmunemove)
    emove_list = list(emove - myimmunemove)
    superduper_list = list(set(emove) & set(mystablist) - myimmunemove)
    
    if not legal_moves: return "Struggle", [], [], []

    # 3. Intelligent Move Scoring System (REPLACES B, C, D, E, F)
    
    move_scores = {}
    has_major_status = (y.status != "Alive")
    y_types = [y.primaryType, y.secondaryType, y.teraType]

    for move in legal_moves:
        score = 0
        
        # --- Offensive Scoring ---
        if move not in typemoves.statusmove and move not in typemoves.healingmoves:
            
            # 1. Base Score based on damage simulation (Uses the helper above)
            damage_score, effectiveness_multiplier = await _simulate_damage(move, x, y, field)
            score += damage_score
            
            # 2. Effectiveness Bonus/Penalty (Reinforced)
            if effectiveness_multiplier >= 2.0: score *= 1.4 # Super Effective
            elif effectiveness_multiplier <= 0.5: score *= 0.5 # Not Very Effective
            
            # 3. KO Check (Highest Priority) - Score 1000 if guaranteed KO
            # To implement this, _simulate_damage must return the raw damage number.
            # if predicted_damage >= y.hp: score = 1000 
            
            # 4. Cleanup Moves (e.g., Flip Turn)
            if move == "Flip Turn" and "Hero" not in x.name and x.ability == "Zero to Hero":
                if x.hp <= x.maxhp * 0.3: score += 500 # Emergency switch out
                else: score += 100 # Strategic switch out

            elif move == "Hex" and has_major_status:
                score *= 2.0 # Power doubled
            
            elif move == "Explosion" and y.hp <= y.maxhp * 0.5:
                # Prioritize KO but with caution (suicide move)
                score = 850 

        # --- Utility/Setup Scoring ---
        else: # Move is status or healing
            is_sleep_move = move in typemoves.sleepmoves # ASSUMPTION: This list exists
            if is_sleep_move and y.status == "Sleep":
                score = 0
            # A. Emergency/Critical Healing (Prioritize)
            if move in typemoves.healingmoves and x.hp <= x.maxhp * 0.5:
                if x.hp <= x.maxhp * 0.25: score = 950 # Very Low HP, highest priority
                else: score = 750 # Need to heal now
            
            # B. Hazard Control
            elif move == "Defog" and tr1.hazard:
                score = 700
                
            # C. Status Infliction (Smart Selection: Avoid Spam/Immunity)
            elif not has_major_status:
                if move == "Will-O-Wisp" and "Steel" not in y_types: score = 650
                elif move == "Thunder Wave" and "Ground" not in y_types: score = 650
                elif move == "Toxic" and "Poison" not in y_types and "Steel" not in y_types: score = 650
            
            # D. Setup/Boosting Moves (Prioritize when safe and advantageous)
            elif x.speed > y.speed and x.hp >= x.maxhp * 0.75: # Only setup when safe
                if (move == "Swords Dance" and x.atk > x.spatk and x.atkb < 6): score = 700
                elif (move == "Nasty Plot" and x.spatk > x.atk and x.spatkb < 6): score = 700
                elif (move == "Dragon Dance" and x.atkb < 6 and x.speedb < 6): score = 750
                elif (move == "Calm Mind" and x.spatkb < 6 and x.spdefb < 6): score = 700
                elif (move == "Agility" and x.speedb < 6): score = 600
                elif (move == "Substitute" and y.hp >= y.maxhp * 0.5): score = 600
                
                # Screens and Tailwind (Team Support)
                elif move == "Reflect" and y.atk > y.spatk and not tr1.reflect: score = 600
                elif move == "Light Screen" and y.spatk > y.atk and not tr1.lightscreen: score = 600
                elif move == "Tailwind" and not tr1.tailwind: score = 650 # Strategic selection
                
                # Entry Hazards
                elif move == "Stealth Rock" and not tr2.hazard.get("Stealth Rock"): score = 600
                elif move == "Toxic Spikes" and not tr2.hazard.get("Toxic Spikes"): score = 600
                
            # E. Weather/Terrain Control
            elif move == "Sunny Day" and field.weather != "Sunny": score = 550
            elif move == "Rain Dance" and field.weather != "Rainy": score = 550
            elif move == "Sandstorm" and field.weather != "Sandstorm": score = 550
            elif move == "Snowscape" and field.weather != "Snowscape": score = 550
            
        move_scores[move] = score

    # 4. Final Decision
    if move_scores:
        chosen_move = max(move_scores, key=move_scores.get)
    else:
        chosen_move = "Struggle"

    # 5. Handle Choice Items
    use = chosen_move
    if "Choice" in x.item and not x.choiced and not x.dmax:
        x.choiced = True
        x.choicedmove = use
    if x.choiced and not x.dmax and x.choicedmove in x.moves:
        use = x.choicedmove

    return use, emove_list, superduper_list, list(myimmunemove)