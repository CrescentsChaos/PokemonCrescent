import random
import discord
from movelist import *
from typing import TYPE_CHECKING, Optional, List, Set, Dict
async def movetype(move): 
    types=("Rock","Fire","Water","Grass","Electric","Ground","Flying","Fighting","Fairy","Dragon","Steel","Poison","Dark","Ghost","Normal","Bug","Ice","Psychic")
    res="Normal"
    for i in types:
        if move in eval(f"typemoves.{i.lower()}moves"):
            res=i
    return res  
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
    # --------------------------------------------------------------------------
    async def _simulate_damage(move: str, attacker: 'Pokemon', defender: 'Pokemon', current_field: 'Field') -> float:
        """Simulates move damage as a percentage of opponent's max HP."""
        try:
            effectiveness = 1.0
            
            move_type = await movetype(move)
            #damage_score = power * 2
            damage_score=10
            # Effectiveness boost (based on the classification derived in moveAI)
            x_types = [t for t in [attacker.primaryType, attacker.secondaryType, attacker.teraType] if t is not None]
            is_stab = any(move in TYPE_MOVES.get(t, set()) for t in x_types)
            
            if is_stab: 
                damage_score *= 1.5
            
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
        if move not in typemoves.statusmove:
            
            # 1. Base Score based on damage simulation (Uses the helper above)

            score = 1
            
            if move == "Counter" and x.hp>=(x.maxhp*0.25) and y.atk>y.spatk:
                score=5
            elif move == "Mirror Coat" and x.hp>=(x.maxhp*0.25) and y.spatk>y.atk:
                score=5
            elif move in typemoves.prioritymove and field.terrain=="Psychic":
                score=0
            # 4. Cleanup Moves (e.g., Flip Turn)
            elif move == "Flip Turn" and "Hero" not in x.name and x.ability == "Zero to Hero":
                score==500 # Strategic switch out
            elif move == "Hex" and has_major_status:
                score *= 2.0 # Power doubled
            elif move == "Rapid Spin" and len(tr1.hazard)!=0:
                score = 7
            elif move == "Final Gambit" and (x.hp == x.maxhp) and (x.hp >= y.hp) and (y.hp>=y.maxhp * 0.25):
                score = 85
            elif move in typemoves.priorityatkmoves and (y.hp <=y.maxhp * 0.10):
                score=100
            elif move in ["Explosion","Self Destruct","Misty Explosion"] and (x.hp >= x.maxhp * 0.5):
                # Prioritize KO but with caution (suicide move)
                score = 0 
            elif move == "Explosion" and (x.hp <= x.maxhp * 0.25):
                # Prioritize KO but with caution (suicide move)
                score = 85

        # --- Utility/Setup Scoring ---
        else: # Move is status or healing
            is_sleep_move = move in typemoves.sleepmoves # ASSUMPTION: This list exists
            if is_sleep_move and y.status == "Sleep" and y.ability in ["Insomnia","Vital Spirit","Early Bird"]:
                score = 0
            elif move=="Stealth Rock" and "Stealth Rock" not in tr2.hazard and (y.hp >= y.maxhp * 0.75):
                score=50
            elif move in typemoves.atkboost and x.atkb<1 and (x.hp >= x.maxhp * 0.75):
                score=50
                print(f"{tr1.name} will boost")
            elif move in typemoves.spatkboost and x.spatkb<1 and (x.hp >= x.maxhp * 0.75):
                score=50
                print(f"{tr1.name} will boost")
            elif move in typemoves.protectmoves and x.protect:
                score=0
            elif move == "Sleep Talk" and y.status=="Sleep":
                score=100
            elif move=="Taunt" and y.use in typemoves.statusmove and not y.taunted:
                score=70
            elif move in ["Toxic","Thunder Wave","Poison Powder","Spore","Will-O-Wisp"] and (y.status != "Alive" or y.ability in ["Magic Bounce","Comatose"] or field.terrain=="Misty"):
                score=0
            elif move == "Tailwind" and tr1.tailwind:
                score=0
                print(f"{tr1.name} will avoid using Tailwind")
            elif move == "Grassy Terrain" and field.terrain=="Grassy":
                score=0
                print(f"{tr1.name} will avoid using Grassy Terrain")
            elif move == "Misty Terrain" and field.terrain=="Misty":
                score=0
                print(f"{tr1.name} will avoid using Misty Terrain")
            elif move == "Electric Terrain" and field.terrain=="Electric":
                score=0
                print(f"{tr1.name} will avoid using Electric Terrain")
            elif move == "Psychic Terrain" and field.terrain=="Psychic":
                score=0
                print(f"{tr1.name} will avoid using Psychic Terrain")
            elif move=="Reflect" == tr1.reflect:
                score=0
                print(f"{tr1.name} will avoid using Reflect")
            elif move=="Light Screen" == tr1.lightscreen:
                score=0
                print(f"{tr1.name} will avoid using Light Screen")
            elif move=="Trick Room" and field.trickroom and x.speed<y.speed:
                score=0
                print(f"{tr1.name} will avoid using Trick Room")
            elif move=="Trick Room" and field.trickroom and x.speed>y.speed:
                score=50
                print(f"{tr1.name} will use Trick Room")
            if move in typemoves.healingmoves and x.hp <= x.maxhp * 0.5:
                if x.hp <= x.maxhp * 0.25: 
                    score = 950 # Very Low HP, highest priority
                    print(f"{tr1.name} will definitely heal")
                else: 
                    score = 400 # Need to heal now
                    print(f"{tr1.name} might heal")
            
            # B. Hazard Control
            elif move == "Defog" and len(tr1.hazard)!=0:
                score = 70
            elif move in typemoves.protectmoves and x.used in typemoves.protectmoves:
                score =  0    
            # C. Status Infliction (Smart Selection: Avoid Spam/Immunity)
            elif not has_major_status:
                if move == "Will-O-Wisp":
                    if "Fire" not in y_types and y.atk>y.spatk: 
                        score = 65
                elif move == "Thunder Wave":
                    if "Ground" not in y_types and "Electric" not in y_types and y.speed>x.speed:
                        score = 65
                elif move == "Toxic":
                    if "Poison" not in y_types and "Steel" not in y_types:
                        score = 50
            
            # D. Setup/Boosting Moves (Prioritize when safe and advantageous)
            elif x.speed > y.speed and x.hp >= x.maxhp * 0.75: # Only setup when safe
                if (move == "Agility" and x.speedb < 6): score = 600
                elif (move == "Substitute" and y.hp >= y.maxhp * 0.5): score = 600
                
                # Screens and Tailwind (Team Support)
                elif move == "Reflect" and y.atk > y.spatk and not tr1.reflect: score = 600
                elif move == "Light Screen" and y.spatk > y.atk and not tr1.lightscreen: score = 600
                elif move == "Tailwind" and not tr1.tailwind: score = 650 # Strategic selection
                
        damage_score, effectiveness_multiplier = await _simulate_damage(move, x, y, field)
        if effectiveness_multiplier >= 2.0: score *= 2 # Super Effective
        elif effectiveness_multiplier <= 0.5: score *= 0.5   
        if move not in typemoves.statusmove:
            score*=damage_score 
        move_scores[move] = score
    print(move_scores)
    # 4. Final Decision
    if move_scores:
        max_score = max(move_scores.values())
        best_moves = [
            move for move, score in move_scores.items() if score == max_score
        ]
        chosen_move = random.choice(best_moves)
    else:
        chosen_move = "Struggle"

    # 5. Handle Choice Items
    use = chosen_move
    if "Choice" in x.item and not x.choiced and not x.dmax:
        x.choiced = True
        x.choicedmove = use
    if x.choiced and not x.dmax and x.choicedmove in x.moves:
        use = x.choicedmove
        print("choice")
    x.used=use
    return use, emove_list, superduper_list, list(myimmunemove)