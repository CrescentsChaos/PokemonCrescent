import random
import discord
import sqlite3
import aiosqlite
import asyncio
import requests
import aiohttp
from pokemon import *
from movelist import *
from trainers import *
from pokemon import calcst
from typing import Optional,List, Tuple,TYPE_CHECKING,Set, Dict
from typematchup import *
from AI import *
from hiddenpower import *
megastones=("Heatranite","Zeraorite","Darkranite","Chimecite","Baxcaliburite","Floettite","Chandelurite","Scolipite","Falinksite","Pyroarite","Scraftinite","Drampanite","Eelektrossite","Dragalgite","Barbaracite","Clefablite","Starminite","Meganiumite","Excadrite","Emboarite","Froslassite","Feraligite","Skarmorite","Raichunite X","Raichunite Y","Greninjite","Delphoxite","Chesnaughtite","Malamarite","Hawluchanite","Victreebelite","Dragoninite","Gyaradosite","Venusaurite","Charizardite X","Charizardite Y","Abomasite","Absolite","Aerodactylite","Aggronite","Alakazite","Altarianite","Ampharosite","Audinite","Banettite","Beedrillite","Blastoisinite","Blazikenite","Camerupite","Diancite","Galladite","Garchompite","Gardevoirite","Gengarite","Glalitite","Heracronite","Houndoominite","Kangaskhanite","Latiasite","Latiosite","Lopunnite","Lucarionite","Manectite","Mawilite","Medichamite","Metagrossite","Mewtwonite X","Mewtwonite Y","Pidgeotite","Pinsirite","Sablenite","Salamencite","Sceptilite","Scizorite","Sharpedonite","Slowbronite","Steelixite","Seampertite","Tyranitarite")

async def pokeicon(nm):
    # FIX: Replace sqlite3.connect with aiosqlite.connect
    async with aiosqlite.connect("pokemondata.db") as db:
        
        # FIX: Use db.execute() followed by db.fetchone()
        # db.execute_fetchone() is not a method on the connection object.
        cursor = await db.execute("SELECT * FROM 'wild' WHERE name = ?", (nm,))
        row = await cursor.fetchone()
        
        # Assuming the icon is the 23rd column (index 22)
        return row[22] if row else None
    
async def lbskg(pounds):
    return round(pounds * 0.45359237, 2)

async def heightcon(meters):
    total_inches = meters * 39.37008 
    feet_part = int(total_inches // 12)
    inches_part = round(total_inches % 12)
    return f"{feet_part}'{inches_part}\""

async def usagerecord(team):
    db = sqlite3.connect("record.db")
    c = db.cursor()

    # --- FIX 1: Create the 'pokemons' table if it doesn't exist ---
    # Based on your INSERT statement, the table needs 6 columns.
    c.execute("""
        CREATE TABLE IF NOT EXISTS pokemons (
            name TEXT PRIMARY KEY,
            natures TEXT,
            items TEXT,
            abilities TEXT,
            total INTEGER,
            wins INTEGER
        )
    """)
    
    # --- FIX 2: Create the 'alltime' table and initialize it if it doesn't exist ---
    # This prevents an error when the function tries to select from it later.
    c.execute("""
        CREATE TABLE IF NOT EXISTS alltime (
            total INTEGER
        )
    """)
    # Initialize the total count if the table was just created or is empty
    c.execute(f"select * from `alltime`")
    if c.fetchone() is None:
        c.execute("INSERT INTO alltime (total) VALUES (0)")
    
    db.commit() # Commit the table creations/initializations

    # --- Existing Logic to Process Each Pokémon in the Team ---
    for i in team:
        c.execute(f"select * from `pokemons` where name='{i.name}'")
        v = c.fetchone()
        
        if v == None:
            # insert (v[4] is total, v[5] is wins)
            c.execute(f"""INSERT INTO `pokemons` VALUES (
                "{i.name}",
                "{i.nature} 1",
                "{(i.item.replace(' ','_')).replace('[Used]','')} 1",
                "{i.ability.replace(' ','_')} 1",
                1,
                0
            )""")
            db.commit() # Commit after each insert
        else:
            # update
            # ... (Existing update logic for natures, items, abilities, and total) ...
            
            # NOTE: Your original code doesn't update the WIN count (v[5]), 
            # only the TOTAL count (v[4]). I've kept this as-is.
            
            natures=await convert_items_string(v[1])
            items=await convert_items_string(v[2])
            abilities=await convert_items_string(v[3])
            
            if "Used" in i.item:
                i.item=i.item.replace('[Used]','')
                
            if i.nature in natures:
                natures[i.nature]=natures[i.nature]+1
                natures=await convert_dict_string(natures)
            elif i.nature not in natures:
                natures[i.nature]=1
                natures=await convert_dict_string(natures)
                
            if i.item.replace(' ','_') in items:
                items[i.item.replace(' ','_')]=items[i.item.replace(' ','_')]+1
                items=await convert_dict_string(items)
            elif i.item.replace(' ','_') not in items:
                items[i.item.replace(' ','_')]=1
                items=await convert_dict_string(items)
                
            if i.ability.replace(' ','_') in abilities:
                abilities[i.ability.replace(' ','_')]=abilities[i.ability.replace(' ','_')]+1
                abilities=await convert_dict_string(abilities)
            elif i.ability.replace(' ','_') not in abilities:
                abilities[i.ability.replace(' ','_')]=1
                abilities=await convert_dict_string(abilities)
                
            c.execute(f"""Update `pokemons` set natures="{natures}",items="{items}",abilities="{abilities}",total={v[4]+1} where name='{i.name}'""")
            db.commit() # Commit after each update

    # --- Existing Logic for All-Time Count ---
    c.execute(f"select * from `alltime`")
    tot = c.fetchone()
    # It must exist now due to the initialization above
    tot = tot[0] 
    c.execute(f"""Update `alltime` set total={tot+1}""")
    db.commit()
    
    # NOTE: You are missing db.close() at the end of the function!
    # It's good practice to close the synchronous connection.
    db.close()
    
async def convert_items_string(input_string):
    # Converting string to dictionary
    items_dict = {}
    
    items_list = input_string.split(',')
    for item in items_list:
        item_name, item_usage = item.split()
        items_dict[item_name] = int(item_usage)
    return {key:value for key, value in sorted(items_dict.items(),key=lambda item: item[1],reverse=True)}

async def convert_dict_string(input_dict):
    # Converting dictionary to string
    items_list = []
    for item_name, item_usage in input_dict.items():
        items_list.append(item_name + ' ' + str(item_usage))
    return ','.join(items_list)
async def sortbadge(normal_list):
    sample_list = [
        "Boulder Badge", "Cascade Badge", "Thunder Badge", "Rainbow Badge", "Soul Badge", "Marsh Badge", "Volcano Badge", "Earth Badge",
        "Zephyr Badge", "Hive Badge", "Plain Badge", "Fog Badge", "Storm Badge", "Mineral Badge", "Glacier Badge", "Rising Badge",
        "Stone Badge", "Knuckle Badge", "Dynamo Badge", "Heat Badge", "Balance Badge", "Feather Badge", "Mind Badge", "Rain Badge",
        "Coal Badge", "Forrest Badge", "Relic Badge", "Cobble Badge", "Fen Badge", "Mine Badge", "Beacon Badge",
        "Trio Badge", "Basic Badge", "Toxic Badge", "Insect Badge", "Bolt Badge", "Quake Badge", "Jet Badge", "Freeze Badge", "Wave Badge",
        "Legend Badge",
        "Bug Badge", "Cliff Badge", "Rumble Badge", "Plant Badge", "Pixie Badge", "Voltage Badge", "Psi Badge", "Iceberg Badge",
        "Grass Badge", "Water Badge", "Fighting Badge", "Fire Badge", "Ghost Badge", "Fairy Badge", "Rock Badge", "Ice Badge", "Dark Badge", "Dragon Badge",
        "Cortondo Badge", "Artazon Badge", "Levincia Badge", "Medali Badge", "Cascarrafa Badge", "Montenevera Badge", "Glaseado Badge", "Alfornada Badge",
        "Navi Badge", "Schedar Badge", "Ruchbah Badge", "Segin Badge", "Caph Badge",
        "Gold Knowledge Symbol", "Gold Tactics Symbol", "Gold Guts Symbol", "Gold Luck Symbol", "Gold Ability Symbol", "Gold Spirits Symbol", "Gold Brave Symbol",
        "Rocket Badge", "Aqua Badge", "Magma Badge", "Galactic Badge", "Plasma Badge"
    ]
    # Use a dictionary for faster lookups
    badge_order = {badge: i for i, badge in enumerate(sample_list)}
    # Sort using the dictionary as the key
    return sorted(normal_list, key=lambda x: badge_order.get(x, float('inf')))
async def findnum(ctx,row):
    mem=0
    try:
        mem=ctx.author.id
    except:    
        mem=ctx.user.id
    db=sqlite3.connect("owned.db")
    c=db.cursor()
    c.execute(f"select * from '{mem}'")
    allmon=c.fetchall()
    allmon=list(allmon)
    c.execute(f"select * from '{mem}' where rowid={row}")
    mon=c.fetchone()
    return allmon.index(mon)+1

async def pricetag(r):
    BASE_PRICES = {
        "Common": (100, 200),
        "Uncommon": (300, 400),
        "Rare": (500, 700),
        "Very Rare": (1000, 1500),
        "Common Legendary": (5000, 7500),
        "Legendary": (15000, 20000),
        "Mythical": (30000, 50000),
    }
    rarity = r[23]
    iv = round(sum(r[3:9]) / 186, 2)
    min_price, max_price = BASE_PRICES.get(rarity, (0, 0))
    base_price = random.randint(min_price, max_price)
    final_price = int(base_price * (1 + iv))
    return final_price         
    
async def row(ctx, index_num, c):
    """
    Translates a 1-based index (index_num) into the SQLite rowid 
    for the user's Pokémon at that position using the 'original' logic.
    'c' must be an aiosqlite.Cursor object.
    """
    try:
        user = ctx.author
    except:
        user = ctx.user
        
    # MUST USE AWAIT FOR AIOSQLITE CURSOR EXECUTION
    await c.execute(f"select *,rowid from '{user.id}'") 
    
    # MUST USE AWAIT FOR AIOSQLITE CURSOR FETCHALL
    hh = await c.fetchall()
    
    # Check if the list is long enough and access the rowid (index 27 in your original snippet)
    if 0 < index_num <= len(hh):
        # num is already being used as a 1-based index in the original code
        # The rowid is column 27 (index 27) in the result set
        rowid = hh[index_num - 1][27] 
        return rowid
        
    return None  

async def pokonvert(ctx, member, num: int = None):
    # Use asynchronous context managers for connection safety
    async with aiosqlite.connect("pokemondata.db") as wild_db, \
               aiosqlite.connect("owned.db") as owned_db:
        
        member_id_str = str(member.id)
        allmon_query = f"SELECT * FROM '{member_id_str}'"
        allmon = await owned_db.execute_fetchall(allmon_query)
        
        if num is None:
            # Check if there are any Pokémon
            if not allmon:
                 return None, []
                 
            # If num is None, we want the index of the latest Pokémon (len(allmon)).
            target_index = len(allmon)
            
            # We need an active cursor to call the row function
            async with owned_db.cursor() as cursor:
                # num will store the actual SQLite rowid after this call
                num = await row(ctx, target_index, cursor) # Pass the active cursor
                
            # If row returns None (shouldn't if allmon is > 0), use the last rowid in allmon
            if num is None:
                 num = allmon[-1][-1]
            
        num = int(num)
        owned_query = f"SELECT * FROM '{member_id_str}' WHERE rowid = ?"
        
        # --- FIX 1: Use a cursor to fetch the owned Pokémon data ---
        async with owned_db.cursor() as cursor:
            await cursor.execute(owned_query, (num,))
            n = await cursor.fetchone()
        
        if n is None:
            return None, allmon
        
        # --- FIX 2: Use a cursor to fetch the wild Pokémon data ---
        wild_query = "SELECT * FROM wild WHERE name = ?"
        async with wild_db.cursor() as cursor:
            await cursor.execute(wild_query, (n[0],))
            m = await cursor.fetchone()
        
        if m is None:
            return None, allmon
            
        # Create the Pokemon object (unchanged logic)
        p = Pokemon(
            name=m[0], nickname=n[1], primaryType=m[1], secondaryType=m[2],
            level=n[2], moves=n[22], ability=n[15], gender=n[19], tera=n[20], 
            item=n[18], shiny=n[17], nature=n[16], catchdate=n[24], icon=m[22], 
            sprite=m[12], weight=m[13], height=m[25], maxiv="Custom",
            hp=m[4], atk=m[5], defense=m[6], spatk=m[7], spdef=m[8], speed=m[9],
            hpiv=n[3], atkiv=n[4], defiv=n[5], spatkiv=n[6], spdefiv=n[7], speediv=n[8],
            hpev=n[9], atkev=n[10], defev=n[11], spatkev=n[12], spdefev=n[13], speedev=n[14],
        )
        return p, allmon
         
# async def pokonvert(ctx, member, num=None):
#     if num is not None:
#         num = int(num)
#     dt = sqlite3.connect("pokemondata.db")
#     db = sqlite3.connect("owned.db")
#     cx = dt.cursor()
#     c = db.cursor()
#     c.execute(f"SELECT * FROM '{member.id}'")
#     allmon=c.fetchall()
#     if num==None:
#         num=len(allmon)
#         num=await row(ctx,num,c)   
#     c.execute(f"SELECT * FROM '{member.id}' where rowid={num}")
#     n = c.fetchone()
#     cx.execute(f"SELECT * FROM 'wild' WHERE name=?", (n[0],))
#     m = cx.fetchall()[0]
#     p = Pokemon(
#         name=m[0],
#         nickname=n[1],
#         primaryType=m[1],
#         secondaryType=m[2],
#         level=n[2],
#         hp=m[4],
#         atk=m[5],
#         defense=m[6],
#         spatk=m[7],
#         spdef=m[8],
#         speed=m[9],
#         moves=n[22],
#         ability=n[15],
#         sprite=m[12],
#         gender=n[19],
#         tera=n[20],
#         maxiv="Custom",
#         item=n[18],
#         shiny=n[17],
#         nature=n[16],
#         hpiv=n[3],
#         atkiv=n[4],
#         defiv=n[5],
#         spatkiv=n[6],
#         spdefiv=n[7],
#         speediv=n[8],
#         hpev=n[9],
#         atkev=n[10],
#         defev=n[11],
#         spatkev=n[12],
#         spdefev=n[13],
#         speedev=n[14],
#         catchdate=n[24],
#         icon=m[22],
#         weight=m[13],
#         height=m[25]
        
#     )
#     return p,allmon


async def numberify(num):
    num = str(num)
    reversed_num = num[::-1]
    chunks = [reversed_num[i:i+3] for i in range(0, len(reversed_num), 3)]
    result = ','.join(chunks)[::-1]    
    return result

async def subl(num, original):
    start = (num - 1) * 10
    end = start + 10

    sub_list = original[start:end]

    return sub_list

async def gensub(num, original_dict):
    sub_dict = {}

    start = (num - 1) * 15
    end = start + 15

    keys = list(original_dict.keys())[start:end]
    values = list(original_dict.values())[start:end]

    sub_dict = dict(zip(keys, values))

    return sub_dict

async def listtodic(lst):
    dict_count = {}    
    for element in lst:
        if element in dict_count:
            dict_count[element] += 1
        else:
            dict_count[element] = 1
    return dict_count

async def movect(move):
    if move in typemoves.maxmovelist:
        return "<:dynamax:1104646304904257647>"
    elif move in typemoves.physicalmoves:
        return "<:physical:1127210535289634866>"
    elif move in typemoves.statusmove:
        return "<:status:1127210505275183156>"
    else:
        return "<:special:1127210563685077022>"
    
async def movetypeicon(x,move,field="Normal"):
    types=("Rock","Fire","Water","Grass","Electric","Ground","Flying","Fighting","Fairy","Dragon","Steel","Poison","Dark","Ghost","Normal","Bug","Ice","Psychic")
    res="Normal"
    for i in types:
        if move in eval(f"typemoves.{i.lower()}moves"):
            res=i
    typedic={
    "Normal":"<:normal:1127146220880674878>",
    "Bug":"<:bug:1127145792654802944>",
    "Dark":"<:dark:1127147091655938068>",
    "Dragon":"<:dragon:1127147065215029298>",
    "Electric":"<:electric:1127146987423289395>",
    "Fairy":"<:fairy:1127147120160411688>",
    "Fighting":"<:fighting:1127145305066971256>",
    "Fire":"<:fire:1127146792065183784>",
    "Flying":"<:flying:1127145341385457725>",
    "Ghost":"<:ghost:1127145829505966110>",
    "Grass":"<:grass:1127146939587235910>",
    "Ground":"<:ground:1127145407613517885>",
    "Ice":"<:ice:1127147039772381305>",
    "Poison":"<:poison:1127145374457536532>",
    "Psychic":"<:psychic:1127147015760007238>",
    "Rock":"<:rock:1127145761390473306>",
    "Steel":"<:steel:1127145866868830279>",
    "Water":"<:water:1127146821635027037>"
    }
    try:
        if move=="Hidden Power":
            dmg,res=await hidp(x.hpiv,x.atkiv,x.defiv,x.spatkiv,x.spdefiv,x.speediv) 
        elif x.ability=="Normalize":
            res="Normal"
        elif x.ability=="Liquid Voice" and move in typemoves.normalmoves:
            res="Water"
        elif x.ability=="Aerilate" and move in typemoves.normalmoves:
            res="Flying"
        elif x.ability=="Galvanize" and move in typemoves.normalmoves:
            res="Electric"
        elif x.ability=="Pixilate" and move in typemoves.normalmoves:
            res="Fairy"
        elif move in ["Revelation Dance","Multi-Attack","Judgment"]:
            res=x.primaryType
            if x.teraType!="???":
                res=x.teraType
        elif move=="Tera Blast" and x.teraType!="???":
            res=x.teraType     
        elif move=="Weather Ball":
            dict={
        "Rainy":"Water",
        "Sunny":"Fire",
        "Sandstorm":"Rock",
        "Hail":"Ice",
        "Snowstorm":"Ice"}
            if field!="Normal" and field.weather in dict:
                res=dict[field.weather]
            elif field=="Normal":
                res="Normal"
    except:
        pass        
    return typedic[res]

async def typeicon(type):
    typedic={
    "Normal":"<:normal:1127146220880674878>",
    "Bug":"<:bug:1127145792654802944>",
    "Dark":"<:dark:1127147091655938068>",
    "Dragon":"<:dragon:1127147065215029298>",
    "Electric":"<:electric:1127146987423289395>",
    "Fairy":"<:fairy:1127147120160411688>",
    "Fighting":"<:fighting:1127145305066971256>",
    "Fire":"<:fire:1127146792065183784>",
    "Flying":"<:flying:1127145341385457725>",
    "Ghost":"<:ghost:1127145829505966110>",
    "Grass":"<:grass:1127146939587235910>",
    "Ground":"<:ground:1127145407613517885>",
    "Ice":"<:ice:1127147039772381305>",
    "Poison":"<:poison:1127145374457536532>",
    "Psychic":"<:psychic:1127147015760007238>",
    "Rock":"<:rock:1127145761390473306>",
    "Steel":"<:steel:1127145866868830279>",
    "Water":"<:water:1127146821635027037>"
    }
    if type is None:
        return "<:normal:1127146220880674878>"
    else:
        return typedic[type]

async def teraicon(type):
    teradic={
    "Max":"<:dynamax:1104646304904257647>",
    "Normal":"<:normal1:1127150698623160430>",
    "Bug":"<:bug:1127151936366444615>",
    "Dark":"<:dark:1127152336301727784>",
    "Dragon":"<:dragon:1127152300549484544>",
    "Electric":"<:electric:1127152165333508116>",
    "Fairy":"<:fairy:1127152370854416385>",
    "Fighting":"<:fighting1:1127150829896482888>",
    "Fire":"<:fire:1127152044919226420>",
    "Flying":"<:flying1:1127150885324193812>",
    "Ghost":"<:ghost:1127151976531107860>",
    "Grass":"<:grass:1127152121846968390>",
    "Ground":"<:ground:1127151843617808485>",
    "Ice":"<:ice:1127152260686811146>",
    "Poison":"<:poison:1127151807655858227>",
    "Psychic":"<:psychic:1127152223537856584>",
    "Rock":"<:rock:1127151897355231284>",
    "Steel":"<:steel:1127152009733226558>",
    "Water":"<:water:1127152085159399475>",
    "Stellar":"<:stellartera:1187804319634964640>"
    }
    return teradic[type] 
   
async def entryeff(ctx, x, y, tr1, tr2, field, turn):
    entry = discord.Embed(title="Entry Effects:",color=0xffffff)
    em = None
    if y.ability!="Neutralizing Gas":
        if x.ability=="Download":
            entry.add_field(name=f"{x.icon} {x.name}'s {x.ability}!",value=f"{x.name} analyzing data from its opponent!")
            x.showability=True
            m=[a,b,c,d,e]=[y.atk,y.defense,y.spatk,y.spdef,y.speed]
            if tr2.reflect==True:
                m=[y.atk,y.defense/2,y.spatk,y.spdef,y.speed]
            if tr2.lightscreen==True:
                m=[y.atk,y.defense,y.spatk,y.spdef/2,y.speed]
            mn=min(m)
            mx=max(m)
            if mx==a:
                await defchange(entry,x,x,1)
            elif mn==b:
                await atkchange(entry,x,x,1)
            elif mx==c:
                await spdefchange(entry,x,x,1)
            elif mn==d:
                await spatkchange(entry,x,x,1)
            elif mx==e:
                await speedchange(entry,x,x,1)
        elif x.ability=="Intrepid Sword":
            entry.add_field(name=f"{x.icon} {x.name}'s {x.ability}!",value=f"{x.name}'s attack rose!")
            await atkchange(entry,x,x,1)
            x.showability=True
        elif x.ability=="Dauntless Shield":
            entry.add_field(name=f"{x.icon} {x.name}'s {x.ability}!",value=f"{x.name}'s defense rose!")
            await defchange(entry,x,x,1)
            x.showability=True
        elif x.ability=="Embody Aspect":
            x.showability=True
            if x.item=="Wellspring Mask":
                entry.add_field(name=f"{x.icon} {x.name}'s {x.ability}!",value=f"Wellspring Mask worn by {x.name} shone brilliantly, and {x.name}'s Special Defense rose!")
                await spdefchange(entry,x,x,1)
            elif x.item=="Hearthflame Mask":
                entry.add_field(name=f"{x.icon} {x.name}'s {x.ability}!",value=f"Hearthflame Mask worn by {x.name} shone brilliantly, and {x.name}'s Attack rose!")
                await atkchange(entry,x,x,1)
            elif x.item=="Cornerstone Mask":
                entry.add_field(name=f"{x.icon} {x.name}'s {x.ability}!",value=f"Cornerstone Mask worn by {x.name} shone brilliantly, and {x.name}'s Defense rose!")
                await defchange(entry,x,x,1)
            else:
                entry.add_field(name=f"{x.icon} {x.name}'s {x.ability}!",value=f"Teal Mask worn by {x.name} shone brilliantly, and {x.name}'s Speed rose!")
                await speedchange(entry,x,x,1)
                
        elif x.ability=="Vessel of Ruin":
            x.showability=True
            entry.add_field(name=f"<:vessel:1138386145194037258> {x.icon} {x.name}'s Vessel of Ruin!",value=f"{x.name} weakened the Special Attack of all surrounding Pokémon!")
        elif x.ability=="Sword of Ruin":
            x.showability=True
            entry.add_field(name=f"<:sword:1138386246348046336> {x.icon} {x.name}'s Sword of Ruin!",value=f"{x.name} weakened the Defense of all surrounding Pokémon!")
        elif x.ability=="Tablets of Ruin":
            x.showability=True
            entry.add_field(name=f"<:tablets:1138386311598837761> {x.icon} {x.name}'s Beads of Ruin!",value=f"{x.name} weakened the Attack of all surrounding Pokémon!")        
        elif x.ability=="Beads of Ruin":
            x.showability=True
            entry.add_field(name=f"<:beads:1138386205713633360> {x.icon} {x.name}'s Beads of Ruin!",value=f"{x.name} weakened the Special Defense of all surrounding Pokémon!")  
        elif x.ability=="Intimidate" and y.ability not in ["Inner Focus","Oblivious","Clear Body","Good as Gold"] and x.item not in ["Clear Amulet"]:
            x.showability=True
            entry.add_field(name="Intimidate:", value=f"{x.icon} {x.name}'s Intimidate!")
            entry.set_thumbnail(url=x.sprite)
            if y.ability!="Guard Dog":
                await atkchange(entry,y,x,-1)
            if y.ability=="Guard Dog":
                await atkchange(entry,y,x,1)            
            if y.item=="Adrenaline Orb":       
                await speedchange(entry,y,x,2)
        elif x.ability=="Majestic Moth":
            m=[a,b,c,d,e]=[y.atk,y.defense,y.spatk,y.spdef,y.speed]
            if tr2.reflect==True:
                m=[y.atk,y.defense/2,y.spatk,y.spdef,y.speed]
            if tr2.lightscreen==True:
                m=[y.atk,y.defense,y.spatk,y.spdef/2,y.speed]
            pp=max(m)
            if pp==a:
                await atkchange(em,y,y,1)
            elif pp==b:
                await defchange(em,y,y,1)
            elif pp==c:
                await spatkchange(em,y,y,1)
            elif pp==d:
                await spdefchange(em,y,y,1)
            elif pp==e:
                await speedchange(em,y,y,1)                
        elif x.ability == "Comatose":
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Comatose!", value=f"{x.name} is in a drowsy state.")
            x.status = "Drowsy"    
        elif x.ability == "Flower Gift" and field.weather in ["Sunny", "Extreme Sunlight"] and "Cherrim" in x.name and x.sprite != "https://play.pokemonshowdown.com/sprites/ani/cherrim-sunshine.gif" and y.ability!="Neutralizing Gas":
            entry.add_field(name=f"{x.icon} {x.name}'s Flower Gift!", value=f"{x.name} is reacting and absorbing sunlight!")
            x.sprite = "https://play.pokemonshowdown.com/sprites/ani/cherrim-sunshine.gif"
        elif x.ability == "Illusion":
            x.name = tr1.pokemons[-1].name
            x.nickname = tr1.pokemons[-1].nickname
            x.sprite = tr1.pokemons[-1].sprite
        elif x.ability == "Pressure" and y.ability not in ["Mold Breaker", "Teravolt", "Turboblaze", "Propeller Tail"]:
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Pressure!", value=f"{x.name} is exerting its pressure!")
        elif x.ability=="Supreme Overlord" and len(tr1.pokemons)!=0:
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Supreme Overlord!",value=f"{x.name} gained strength from the fallen!")  
        elif x.ability=="Frisk" and ("None" not in y.item and "Used" not in y.item):
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Frisk!",value=f"{y.name} is holding a {y.item}!")      
        elif x.ability in ["Air Lock","Cloud Nine"] and field.weather!="Clear":       
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Air Lock!",value=f"{x.name} nullified the effects of weather!")   
        elif x.ability=="Delta Stream" and field.weather!="Strong Winds":        
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Delta Stream!",value=f"Mysterious strong winds are protecting Flying-type Pokémon!")  
            field.weather="Strong Winds"
        elif x.ability=="Stakeout":
            x.atk*=2
            x.spatk*=2
        elif x.ability=="Trace" and y.ability not in ["As One","Battle Bond","Commander","Disguise","Forecast","Ice Face","Imposter","Illusion","Multitype","Power of Alchemy","Protosynthesis","Stance Change","Quark Drive","RKS System","Schooling","Trace","Zen Mode","Zero to Hero"] and y.item!="Ability Shield":
            entry.add_field(name=f"{x.icon} {x.name}'s Trace!",value=f"{x.name} gained {y.ability}!")
            x.ability=y.ability
            x.showability=True
            await entryeff(ctx,x,y,tr1,tr2,field,turn)   
        elif "Quark Drive" in x.ability and field.terrain=="Electric" and ("Booster Energy" not in x.item or "Used" in x.item):    
            x.showability=True    
            entry.add_field(name=f"{x.icon} {x.name}'s Quark Drive!",value=f"Electric Terrain activated {x.icon} {x.name}'s Quark Drive!")       
        elif "Protosynthesis" in x.ability and field.weather in ["Sunny","Extreme Sunlight"] and ("Booster Energy" not in x.item or "Used" in x.item) and y.ability!="Neutralizing Gas":    
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Protosynthesis!",value=f"Harsh sunlight activated {x.icon} {x.name}'s Protosynthesis!")  
        elif x.ability=="Costar":
            x.atkb=y.atkb
            x.defb=y.defb
            x.spatkb=y.spatkb
            x.spdefb=y.spdefb
            x.speedb=y.speedb   
            entry.add_field(name=f"{x.icon} {x.name}'s Costar!",value=f"{x.name} copied {y.icon} {y.name}'s stat boosts!")         
            x.showability=True
        elif x.ability=="Imposter" and y.dmax is False and y.item not in megastones:    
            entry.add_field(name=f"{x.icon} {x.name}'s Imposter!",value=f"{x.name} transformed into {y.name}!")
            x.hp=round(y.maxhp*(x.hp/x.maxhp))     
            x.sprite=y.sprite
            x.maxhp=y.maxhp
            x.maxatk=y.maxatk
            x.maxdef=y.maxdef
            x.maxspatk=y.maxspatk
            x.maxspdef=y.maxspdef
            x.maxspeed=y.maxspeed    
            x.atk=y.atk
            x.defense=y.defense
            x.spatk=y.spatk
            x.spdef=y.spdef
            x.speed=y.speed    
            x.atkb=y.atkb
            x.defb=y.defb
            x.spatkb=y.spatkb
            x.spdefb=y.spdefb
            x.speedb=y.speedb
            x.moves=y.moves
            x.primaryType=y.primaryType
            x.secondaryType=y.secondaryType
            x.ability=y.ability
            x.name=x.name+f"({y.name})"
        elif (x.ability == "Sand Stream" or (x.ability=="Forecast" and x.item=="Smooth Rock")) and field.weather not in ["Sandstorm","Heavy Rain","Extreme Sunlight"]:
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Sand Stream!",value=f"️{x.name} whipped up a sandstorm!")
            field.weather="Sandstorm" 
            field.sandturn=turn
            await sandend(field,x,y)   
        elif x.ability=="Primordial Sea" and field.weather!="Heavy Rain":
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Primordial Sea!",value=f"️A heavy rain began to fall!")
            field.weather="Heavy Rain"
        elif x.ability=="Desolate Land" and field.weather!="Extreme Sunlight":  
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Desolate Land!",value=f"️The sunlight turned extremely harsh!")
            field.weather="Extreme Sunlight"   
        elif x.ability=="Drought" and field.weather not in ["Sunny","Heavy Rain","Extreme Sunlight"]:
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Drought!",value=f"️{x.name} intensified the sun's rays!")
            field.weather="Sunny"  
            field.sunturn=turn
            await sunend(field,x,y)
        elif x.ability=="Orichalcum Pulse" and field.weather not in ["Sunny","Heavy Rain","Extreme Sunlight"]:
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Orichalcum Pulse!",value=f"️{x.name} turned the sunlight harsh, sending its ancient pulse into a frenzy!")
            field.weather="Sunny"  
            field.sunturn=turn
            await sunend(field,x,y)
        elif x.ability=="Drizzle" and field.weather not in ["Rainy","Heavy Rain","Extreme Sunlight"]:
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Drizzle!",value=f"️{x.name} made it rain!")
            field.weather="Rainy"  
            field.rainturn=turn
            await rainend(field,x,y)   
        elif x.ability=="Snow Warning" and field.weather not in ["Snowstorm","Heavy Rain","Extreme Sunlight"]:
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Snow Warning!",value=f"️{x.name} whipped up a snowstorm!")
            field.weather="Snowstorm"  
            field.snowturn=turn
            await snowend(field,x,y)  
        elif x.ability=="Electric Surge":
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Electric Surge!",value=f"️An electric current ran across the battlefield!")
            field.terrain="Electric"
            field.eleturn=turn
            field.eleend(x,y)  
        elif x.ability=="Hadron Engine":
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Hadron Engine!",value=f"️{x.name} summoned the Electric Terrain to energize its futuristic engine!")
            field.terrain="Electric"
            field.eleturn=turn
            field.eleend(x,y)       
        elif x.ability=="Misty Surge":
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Misty Surge!",value=f"️Mist swirled around the battlefield!")
            field.terrain="Misty"
            field.misturn=turn
            field.misend(x,y)     
        elif x.ability=="Grassy Surge":
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Grassy Surge!",value=f"️Grass grew to cover the battlefield!")
            field.terrain="Grassy"
            field.grassturn=turn
            field.grassend(x,y)   
        elif x.ability=="Psychic Surge":
            x.showability=True
            entry.add_field(name=f"{x.icon} {x.name}'s Psychic Surge!",value=f"️The battlefield got weird!")     
            field.terrain="Psychic"        
            field.psyturn=turn
            field.psyend(x,y)      
        elif x.ability=="North Wind":        
            x.showability=True
            tr1.auroraturn=turn
            tr1.auroraend(x,y)
            tr1.auroraveil=True  
            entry.add_field(name=f"{x.icon} {x.name}'s North Wind!",value="Aurora Veil will reduced your team's damage taken!")
    if x.item == "Blue Orb" and "Primal" not in x.name and x.name == "Kyogre":
        em = discord.Embed(title="Primal Reversion:", description=f"{x.name}'s Primal Reversion! It reverted to its primal form!")
        x.sprite = x.sprite.replace(".gif", "-primal.gif")
        x.name = "Primal Kyogre"
        per = x.hp / x.maxhp
        x.ability = "Primordial Sea"
        x.weight, x.hp, x.atk, x.defense, x.spatk, x.spdef, x.speed = 947.99, 100, 150, 90, 180, 160, 90
        calcst(x)
        x.hp = x.maxhp * per
        em.set_image(url=x.sprite)
        em.set_thumbnail(url="https://cdn.discordapp.com/attachments/1102579499989745764/1108653012680982568/Blue_Orb.png")    
    if x.item == "Red Orb" and "Primal" not in x.name and x.name == "Groudon":
        em = discord.Embed(title="Primal Reversion:", description=f"{x.name}'s Primal Reversion! It reverted to its primal form!")
        x.sprite = x.sprite.replace(".gif", "-primal.gif")
        x.name = "Primal Groudon"
        per = x.hp / x.maxhp
        x.ability = "Desolate Land"
        x.weight = 2203.96
        x.hp, x.atk, x.defense, x.spatk, x.spdef, x.speed = 100, 180, 160, 150, 90, 90
        calcst(x)
        x.hp = x.maxhp * per
        em.set_image(url=x.sprite)
        em.set_thumbnail(url="https://cdn.discordapp.com/attachments/1102579499989745764/1109011460601954364/Red_Orb.png")  
    
    if "Spikes" in tr1.hazard and x.ability not in ["Magic Guard","Levitate","Shield Dust"] and x.item not in ["Heavy-Duty Boots","Air Balloon"]:
        entry.add_field(name=f"Spikes!",value=f"️{x.name} was hurt by the Spikes!")
        
        spikes_count = tr1.hazard.count("Spikes")
        if spikes_count == 3:
            damage_fraction = 4  # 1/4
        elif spikes_count == 2:
            damage_fraction = 6  # 1/6
        elif spikes_count == 1:
            damage_fraction = 8  # 1/8
        if spikes_count >= 1:
            x.hp -= (x.maxhp / damage_fraction)  
                  
    is_affected = x.ability not in ["Magic Guard","Levitate","Shield Dust"] and \
              x.item not in ["Heavy-Duty Boots","Air Balloon"] and \
              "Steel" not in (x.primaryType,x.secondaryType,x.teraType) and \
              x.status == "Alive"

    if "Toxic Spikes" in tr1.hazard and is_affected:
        is_poison_type = "Poison" in (x.primaryType,x.secondaryType,x.teraType)

        if is_poison_type:
            # Poison-types absorb the hazard
            tr1.hazard.remove("Toxic Spikes")
            entry.add_field(name=f"{x.name} is a part Poison-type!",value=f"️{x.name} absorbed the Toxic Spikes!")
        else:
            # Non-Poison/Steel types get status
            ts_count = tr1.hazard.count("Toxic Spikes")
            
            entry.add_field(name=f"Toxic Spikes!",value=f"️{x.name} was {'badly ' if ts_count >= 2 else ''}poisoned by toxic spikes!")

            # Apply status: Badly Poisoned for 2+ layers, Poisoned for 1 layer
            x.status = "Badly Poisoned" if ts_count >= 2 else "Poisoned" 
                      
    if "Sticky Web" in tr1.hazard and x.ability not in ["Magic Guard","Levitate","Shield Dust"] and x.item not in ["Heavy-Duty Boots","Air Balloon"]:
        entry.add_field(name=f"Sticky Web!",value=f"️{x.name} fell into the sticky web!")
        await speedchange(entry,x,y,-0.5)   
            
    rock_steel_exclusion = x.ability not in ["Magic Guard","Levitate","Shield Dust","Mountaineer"] and x.item not in ["Heavy-Duty Boots","Air Balloon"]
    ## Stealth Rock
    if "Stealth Rock" in tr1.hazard and rock_steel_exclusion:
        # Rock is super-effective against Flying, Bug, Fire, Ice
        stealth_rock_weak_types = ["Flying", "Bug", "Fire", "Ice"]
        buff = await calculate_hazard_buff(x, stealth_rock_weak_types)
        
        # Damage calculation: 1 + (Max HP * 0.0625 * buff) where 0.0625 is 1/16
        x.hp -= (1 + (x.maxhp * 0.0625 * buff))
        entry.add_field(name=f"Stealth Rock!",value=f"️Pointed stones dug into {x.name}!")

    ## Steel Spikes
    if "Steel Spikes" in tr1.hazard and rock_steel_exclusion:
        # Steel is super-effective against Fairy, Rock, Ice
        steel_spikes_weak_types = ["Fairy", "Rock", "Ice"]
        buff = await calculate_hazard_buff(x, steel_spikes_weak_types)
        
        # Damage calculation: 1 + (Max HP * 0.0625 * buff) where 0.0625 is 1/16
        x.hp -= (1 + (x.maxhp * 0.0625 * buff))
        entry.add_field(name=f"Steel Spikes!",value=f"️Pointed steel spikes dug into {x.name}!")     
    await prebuff(ctx,x,y,tr1,tr2,turn,field)
    if len(entry.fields)!=0:
        await ctx.send(embed=entry)    
        
async def maxendturn(x,turn):
    if x.dmax is True:
       x.maxend=turn+2         
       
async def ulttrans(ctx, x, y, tr1, tr2, field, turn):
    hp_percent = x.hp / x.maxhp
    x.name = "Ultra Necrozma"
    x.ability = "Neuroforce"
    is_shiny = "shiny" if x.shiny == "Yes" else ""
    x.sprite = f"http://play.pokemonshowdown.com/sprites/ani{'-'+is_shiny if is_shiny else ''}/necrozma-ultra.gif"
    x.hp = 97
    x.atk = 167
    x.defense = 97
    x.spatk = 167
    x.spdef = 97
    x.speed = 129
    calcst(x) 
    x.hp = int(x.maxhp * hp_percent) 
    em = discord.Embed(
        title=f"✨ {x.name}'s Ultra Burst! ✨",
        description=f"{x.name} regained its true power through Ultra Burst!"
    )
    em.set_image(url=x.sprite)
    await ctx.send(embed=em)
    await entryeff(ctx, x, y, tr1, tr2, field, turn)
    
async def maxtrans(ctx,x,tr1,turn):
    x.dmax=True
    tr1.canmax=False
    x.choiced=False
    tr1.sub="None"
    x.choicedmove="None"
    x.nickname+=" <:dynamax:1104646304904257647>"
    em=discord.Embed(title=f"{tr1.name} dynamaxed {x.name}!")   
    em.set_thumbnail(url="https://cdn.discordapp.com/attachments/1102579499989745764/1106824399983751248/Dynamax.png")
    if x.name in ("Charizard","Pikachu","Butterfree","Snorlax","Machamp","Gengar","Kingler","Lapras","Garbodor","Melmetal","Corviknight","Orbeetle","Drednaw","Coalossal","Copperajah","Flapple","Appletun","Sandaconda","Grimmsnarl","Hatterene","Toxtricity","Centiskorch","Alcremie","Duraludon","Single Strike Urshifu","Centiskorch","Meowth"):
        x.gsprite=x.sprite.replace(".gif","-gmax.gif")
    elif x.name=="Rapid Strike Urshifu":
        x.gsprite="https://pporg-cdn.nullcontent.net/monthly_2021_01/large.urshifu-rapid-strike-gigantamax.gif.4cb27a830aa200f328d5159491cf37d1.gif"    
    elif x.name=="Single Strike Urshifu":
        x.gsprite="https://pporg-cdn.nullcontent.net/monthly_2021_01/large.urshifu-gigantamax_002.gif.c5c2375142cfcf0d0fe6f53d8923a748.gif"       
    elif x.name=="Cinderace":
        x.gsprite="https://pporg-cdn.nullcontent.net/monthly_2021_01/large.815Cinderace-Gigantamax.png.115853e2114a6c98dd5909b7df2a9562.png"
    elif x.name=="Rillaboom":
        x.gsprite="https://cdn.discordapp.com/attachments/1102579499989745764/1120161218154475551/large.rillaboom-gigantamax.gif.8436bd055644be30e97a252e42166f26.gif"
    elif x.name=="Inteleon":
        x.gsprite="https://pporg-cdn.nullcontent.net/monthly_2021_01/large.poke_capture_0818_000_mf_g_00000000_f_r.png.61ed306f900ef5065e5cdfe4655300c1.png"
    elif x.name=="Venusaur":
        x.gsprite="https://pporg-cdn.nullcontent.net/monthly_2021_01/large.003Venusaur-Gigantamax.png.55d8fc03bb6f1a021deaf82dd16b7315.png"
    elif x.name=="Blastoise":
        x.gsprite="https://pporg-cdn.nullcontent.net/monthly_2021_01/large.009Blastoise-Gigantamax.png.d708478f1a8a467addd0944977d17bf6.png"        
    em.set_image(url=x.sprite)
    if x.gsprite!="None":
        em.set_image(url=x.gsprite)
    await maxendturn(x,turn)
    x.hp*=2
    x.maxhp*=2
    return x,em

OGERPON_MASKS = {
    "Cornerstone Mask": {
        "stat_change": "Defense", "func": "defchange", "sprite": "https://cdn.discordapp.com/attachments/1102579499989745764/1151387710855057518/IMG_20230913_112226.jpg", "gif": "https://cdn.discordapp.com/attachments/1102579499989745764/1152291696017670174/image0.gif"
    },
    "Wellspring Mask": {
        "stat_change": "Special Defense", "func": "spdefchange", "sprite": "https://cdn.discordapp.com/attachments/1102579499989745764/1151387700117643316/IMG_20230913_112215.jpg", "gif": "https://cdn.discordapp.com/attachments/1102579499989745764/1152291615709347960/image0.gif"
    },
    "Hearthflame Mask": {
        "stat_change": "Attack", "func": "atkchange", "sprite": "https://cdn.discordapp.com/attachments/1102579499989745764/1151387689338277928/IMG_20230913_112203.jpg", "gif": "https://cdn.discordapp.com/attachments/1102579499989745764/1152292963758641152/image0.gif"
    },
    # Default case (Teal Mask)
    "default": {
        "stat_change": "Speed", "func": "speedchange", "sprite": "https://cdn.discordapp.com/attachments/1102579499989745764/1151387771164971048/IMG_20230913_112147.jpg", "gif": "https://cdn.discordapp.com/attachments/1102579499989745764/1152290298345562132/image0.gif"
    }
}

async def teratrans(ctx, x, tr1, field):
    x.teraType = x.tera
    tr1.cantera = False
    x.nickname += f" {await teraicon(x.tera)}"
    
    em = discord.Embed(
        title="Terastallization:",
        description=f"{tr1.name} terastallized {x.name} into {x.teraType}-Type!"
    ) 
    em.set_thumbnail(url=f"https://play.pokemonshowdown.com/sprites/types/Tera{x.teraType}.png")
    if x.name == "Terapagos" and x.ability == "Tera Shell":
        x.ability = "Teraform Zero"
        field.weather = 'Clear'
        field.terrain = 'Normal'
        hp_percent = x.hp / x.maxhp
        x.hp, x.atk, x.defense, x.spatk, x.spdef, x.speed = 160, 105, 110, 130, 110, 85
        calcst(x) 
        x.hp = int(x.maxhp * hp_percent) 
        x.sprite = "https://cdn.discordapp.com/attachments/1102579499989745764/1184947676018647152/1024-s.png"
        em.add_field(name=f"{x.icon} {x.name}'s {x.ability}!", value="Terapagos transformed into its Stellar form!")
        em.set_image(url="https://cdn.discordapp.com/attachments/1102579499989745764/1184950556100411403/image0.gif")
    elif x.name == "Ogerpon":
        x.ability = "Embody Aspect"
        mask_data = OGERPON_MASKS.get(x.item, OGERPON_MASKS["default"])
        x.sprite = mask_data["sprite"]
        stat_name = mask_data["stat_change"]
        em.add_field(
            name=f"{x.icon} {x.name}'s {x.ability}!",
            value=f"{x.item} worn by {x.name} shone brilliantly, and {x.name}'s {stat_name} rose!"
        )
        em.set_image(url=mask_data["gif"])
        if mask_data["func"] == "defchange":
            await defchange(em, x, x, 1)
        elif mask_data["func"] == "spdefchange":
            await spdefchange(em, x, x, 1)
        elif mask_data["func"] == "atkchange":
            await atkchange(em, x, x, 1)
        else: 
            await speedchange(em, x, x, 1)
    
    else:
        em.set_image(url=x.gsprite if x.gsprite != "None" else x.sprite)
        
    return x, em
TRANSFORM_DATA = {
    "Wishiwashi-School": {
        "name": "School Wishiwashi", "ability": "Schooling", 
        "stats": (55, 140, 130, 140, 135, 30),
        "sprite_base": "https://play.pokemonshowdown.com/sprites/ani/wishiwashi-school.gif"
    },
    "Terapagos-Shell": {
        "name": "Terapagos", "ability": "Tera Shell", 
        "stats": (95, 95, 110, 105, 110, 85),
        "sprite_base": "https://cdn.discordapp.com/attachments/1102579499989745764/1150127557245681765/ezgif.com-resize_9.gif"
    },
    "Darmanitan-Zen": {
        "nickname_suffix": "-Zen", "ability": "Zen Mode", 
        "types": ("Fire", "Psychic"),
        "stats": (105, 30, 105, 140, 105, 55),
        "sprite_base": "https://play.pokemonshowdown.com/sprites/ani/darmanitan-zen.gif"
    },
    "Darmanitan-Galarian-Zen": {
        "nickname_suffix": "-Zen", "ability": "Zen Mode", 
        "types": ("Ice", "Fire"),
        "stats": (105, 160, 55, 30, 55, 135),
        "sprite_base": "https://play.pokemonshowdown.com/sprites/ani/darmanitan-galarzen.gif"
    },
    "Castform-Normal": {"type": "Normal", "sprite_base": "https://play.pokemonshowdown.com/sprites/ani/castform.gif"},
    "Castform-Snowy": {"type": "Ice", "sprite_base": "https://play.pokemonshowdown.com/sprites/ani/castform-snowy.gif"},
    "Castform-Rainy": {"type": "Water", "sprite_base": "https://play.pokemonshowdown.com/sprites/ani/castform-rainy.gif"},
    "Castform-Sunny": {"type": "Fire", "sprite_base": "https://play.pokemonshowdown.com/sprites/ani/castform-sunny.gif"}
}

# Mapping of Ruin Abilities to the stat they suppress on opponents
RUIN_ABILITIES = {
    "Vessel of Ruin": "spatkbuff",
    "Tablets of Ruin": "atkbuff",
    "Sword of Ruin": "defbuff",
    "Beads of Ruin": "spdefbuff"
}

def _apply_stats_and_hp(pokemon, data_key):
    """Handles stat changes, recalculates final stats, and restores HP percentage."""
    data = TRANSFORM_DATA[data_key]
    hp, atk, defense, spatk, spdef, speed = data["stats"]
    
    hp_percent = pokemon.hp / pokemon.maxhp
    
    pokemon.hp, pokemon.atk, pokemon.defense, pokemon.spatk, pokemon.spdef, pokemon.speed = \
        hp, atk, defense, spatk, spdef, speed
    
    # Recalculate max stats (assumed to be done by calcst)
    calcst(pokemon) 
    
    # Restore current HP based on percentage
    pokemon.hp = int(pokemon.maxhp * hp_percent)

def _get_max_stat_modifier(pokemon, tr1):
    """Determines which stat gets boosted by Protosynthesis/Quark Drive."""
    stats = [pokemon.atk, pokemon.defense, pokemon.spatk, pokemon.spdef, pokemon.speed]
    
    # Apply screen multipliers for Defense and Sp. Defense
    # Note: This is simplified, usually the buff is applied to the final stat after calculation
    # but here we follow the original logic of applying it to base/max stat before comparison.
    if tr1.reflect:
        stats[1] /= 2
    if tr1.lightscreen:
        stats[3] /= 2
        
    max_val = max(stats)
    
    # The original logic compares the max value to the un-multiplied max-stat variables (a, b, c, d, e)
    # which is flawed if the stats have different max values but end up equal after screen division.
    # We will prioritize the index of the max value in the modified list for better reliability.
    
    max_index = stats.index(max_val)
    
    if max_index == 0: return "atkbuff", "Attack", 1.3
    if max_index == 1: return "defbuff", "Defense", 1.3
    if max_index == 2: return "spatkbuff", "Sp. Attack", 1.3
    if max_index == 3: return "spdefbuff", "Sp. Defense", 1.3
    if max_index == 4: return "speedbuff", "Speed", 1.5
    
async def prebuff(ctx, x, y, tr1, tr2, turn, field):
    """Applies pre-move buffs, debuffs, and form changes to the active Pokémon (x)."""
    
    # Initialize buff multipliers
    buffs = {
        "atkbuff": 1.0, "defbuff": 1.0, "spatkbuff": 1.0, 
        "spdefbuff": 1.0, "speedbuff": 1.0
    }
    
    pre_embed = discord.Embed(title="Pre-move buffs:")

    # --- 1. Form Changes (Wishiwashi, Terapagos, Zen Mode) ---
    # Wishiwashi (Schooling)
    if x.ability == "Schooling" and "School" not in x.name and x.hp > (x.maxhp * 0.25):
        pre_embed.add_field(name=f"{x.icon} {x.name}'s Schooling!", value="Wishiwashi formed a school!")
        x.sprite = TRANSFORM_DATA["Wishiwashi-School"]["sprite_base"].replace("/ani/", "/ani-shiny/") if x.shiny == "Yes" else TRANSFORM_DATA["Wishiwashi-School"]["sprite_base"]
        _apply_stats_and_hp(x, "Wishiwashi-School")

    # Terapagos (Tera Shift)
    if x.ability == "Tera Shift":
        pre_embed.add_field(name=f"{x.icon} {x.name}'s Tera Shift!", value="Terapagos transformed!")
        _apply_stats_and_hp(x, "Terapagos-Shell")
        x.ability = "Tera Shell" # Update ability after stat application

    # Darmanitan (Zen Mode)
    if x.ability == "Zen Mode":
        if "Zen" not in x.name:
            if ("Galarian" in x.name and x.hp <= (x.maxhp / 2)): # Check for Galarian and HP threshold
                data_key = "Darmanitan-Galarian-Zen"
                pre_embed.add_field(name=f"{x.icon} {x.name}'s Zen Mode!", value=f"{x.name} transformed!")
                _apply_stats_and_hp(x, data_key)
                x.nickname += TRANSFORM_DATA[data_key]["nickname_suffix"]
                x.primaryType, x.secondaryType = TRANSFORM_DATA[data_key]["types"]
                x.sprite = TRANSFORM_DATA[data_key]["sprite_base"]
            elif "Galarian" not in x.name and x.hp <= (x.maxhp / 2): # Check for Regular and HP threshold
                data_key = "Darmanitan-Zen"
                pre_embed.add_field(name=f"{x.icon} {x.name}'s Zen Mode!", value=f"{x.name} transformed!")
                _apply_stats_and_hp(x, data_key)
                x.nickname += TRANSFORM_DATA[data_key]["nickname_suffix"]
                x.primaryType, x.secondaryType = TRANSFORM_DATA[data_key]["types"]
                x.sprite = TRANSFORM_DATA[data_key]["sprite_base"]

    # --- 2. Terrain/Weather Form Changes and Fades (Castform, Flower Gift, Delta Stream) ---
    
    # Castform (Forecast)
    if x.ability == "Forecast":
        weather_map = {"Clear": "Normal", "Snowstorm": "Ice", "Rainy": "Water", "Sunny": "Fire"}
        type_key = weather_map.get(field.weather)
        if type_key:
            data_key = f"Castform-{weather_map.get(field.weather)}"
            x.primaryType = TRANSFORM_DATA[data_key]["type"]
            x.sprite = TRANSFORM_DATA[data_key]["sprite_base"]

    # Delta Stream Fade
    if field.weather == "Strong Winds" and "Delta Stream" not in (x.ability, y.ability):
        pre_embed.add_field(name="Delta Stream Faded!", value="The mysterious strong winds have dissipated!")
        field.weather = "Clear"
    
    # --- 3. Trainer Screens and Field Effects ---

    if y.ability == "Screen Cleaner":
        tr1.lightscreen = tr1.reflect = tr1.auroraveil = False
    
    if tr1.auroraveil and y.ability != "Infiltrator":
        buffs["defbuff"] *= 2; buffs["spdefbuff"] *= 2
    if tr1.reflect and y.ability != "Infiltrator":
        buffs["defbuff"] *= 2
    if tr1.lightscreen and y.ability != "Infiltrator":
        buffs["spdefbuff"] *= 2
    if tr1.tailwind:
        buffs["speedbuff"] *= 2
    if x.ability == "Grass Pelt" and field.terrain == "Grassy":
        buffs["defbuff"] *= 1.5
    if field.weather == "Snowstorm" and any(t in (x.primaryType, x.secondaryType, x.teraType) for t in ["Ice"]):
        buffs["defbuff"] *= 1.5
    elif field.weather == "Sandstorm" and any(t in (x.primaryType, x.secondaryType, x.teraType) for t in ["Rock"]) and y.ability != "Cloud Nine":
        buffs["spdefbuff"] *= 1.5

    # --- 4. Item Buffs/Debuffs ---
    
    ITEM_BUFFS = {
        "Thick Club": lambda mon: ("Marowak" in mon.name and buffs.update({"atkbuff": buffs["atkbuff"] * 2})),
        "Float Stone": lambda mon: buffs.update({"defbuff": buffs["defbuff"] * 0.5, "spdefbuff": buffs["spdefbuff"] * 0.5}),
        "Iron Ball": lambda mon: buffs.update({"speedbuff": buffs["speedbuff"] * 0.5}),
        "Wise Glasses": lambda mon: buffs.update({"spatkbuff": buffs["spatkbuff"] * 1.1}),
        "Muscle Band": lambda mon: buffs.update({"atkbuff": buffs["atkbuff"] * 1.1}),
        "Choice Band": lambda mon: (not mon.dmax and buffs.update({"atkbuff": buffs["atkbuff"] * 1.5})),
        "Choice Specs": lambda mon: (not mon.dmax and buffs.update({"spatkbuff": buffs["spatkbuff"] * 1.5})),
        "Choice Scarf": lambda mon: (not mon.dmax and buffs.update({"speedbuff": buffs["speedbuff"] * 1.5})),
        "Assault Vest": lambda mon: buffs.update({"spdefbuff": buffs["spdefbuff"] * 1.5}),
        "Life Orb": lambda mon: buffs.update({"atkbuff": buffs["atkbuff"] * 1.3, "spatkbuff": buffs["spatkbuff"] * 1.3}),
        "Eviolite": lambda mon: buffs.update({"defbuff": buffs["defbuff"] * 1.5, "spdefbuff": buffs["spdefbuff"] * 1.5}),
        "Light Ball": lambda mon: ("Pikachu" in mon.name and buffs.update({"atkbuff": buffs["atkbuff"] * 2, "spatkbuff": buffs["spatkbuff"] * 2}))
    }
    
    # Iterate through all item buffs
    ITEM_BUFFS.get(x.item, lambda mon: None)(x)


    # --- 5. Ability Buffs/Debuffs ---
    
    ABILITY_BUFFS = {
        "Flower Gift": lambda mon: (field.weather in ["Sunny", "Extreme Sunlight"] and buffs.update({"speedbuff": buffs["speedbuff"] * 1.5, "atkbuff": buffs["atkbuff"] * 1.5})),
        "Illusion": lambda mon: ("Zoroark" not in mon.name and buffs.update({"atkbuff": buffs["atkbuff"] * 1.3, "spatkbuff": buffs["spatkbuff"] * 1.3})),
        "Quick Feet": lambda mon: (mon.status != "Alive" and buffs.update({"speedbuff": buffs["speedbuff"] * 2})),
        "Unburden": lambda mon: (mon.item == "None" or "Used" in mon.item and buffs.update({"speedbuff": buffs["speedbuff"] * 2})),
        "Defeatist": lambda mon: (mon.hp <= (mon.maxhp / 3) and buffs.update({"atkbuff": buffs["atkbuff"] * 0.5, "spatkbuff": buffs["spatkbuff"] * 0.5})),
        "Toxic Boost": lambda mon: ("Poison" in mon.status and buffs.update({"atkbuff": buffs["atkbuff"] * 1.5})),
        "Orichalcum Pulse": lambda mon: (field.weather in ["Sunny", "Extreme Sunlight"] and buffs.update({"atkbuff": buffs["atkbuff"] * 1.34})),
        "Hadron Engine": lambda mon: (field.terrain == "Electric" and buffs.update({"spatkbuff": buffs["spatkbuff"] * 1.34})),
        "Guts": lambda mon: (mon.status != "Alive" and buffs.update({"atkbuff": buffs["atkbuff"] * 1.5})),
        "Feline Prowess": lambda mon: buffs.update({"spatkbuff": buffs["spatkbuff"] * 2}),
        "Surge Surfer": lambda mon: (field.terrain == "Electric" and buffs.update({"speedbuff": buffs["speedbuff"] * 2})),
        "Marvel Scale": lambda mon: (mon.status != "Alive" and buffs.update({"defbuff": buffs["defbuff"] * 1.5})),
        "Hustle": lambda mon: buffs.update({"atkbuff": buffs["atkbuff"] * 1.5}),
        "Flare Boost": lambda mon: (mon.status == "Burned" and buffs.update({"spatkbuff": buffs["spatkbuff"] * 1.5})),
        "Swift Swim": lambda mon: (field.weather in ["Rainy", "Heavy Rain"] and y.ability != "Cloud Nine" and buffs.update({"speedbuff": buffs["speedbuff"] * 2})),
        "Chlorophyll": lambda mon: (field.weather in ["Sunny", "Extreme Sunlight"] and y.ability != "Cloud Nine" and buffs.update({"speedbuff": buffs["speedbuff"] * 2})),
        "Big Leaves": lambda mon: (field.weather in ["Sunny", "Extreme Sunlight"] and y.ability != "Cloud Nine" and buffs.update({"speedbuff": buffs["speedbuff"] * 2})),
        "Sand Rush": lambda mon: (field.weather in ["Sandstorm"] and y.ability != "Cloud Nine" and buffs.update({"speedbuff": buffs["speedbuff"] * 2})),
        "Slush Rush": lambda mon: (field.weather in ["Hail", "Snowstorm"] and y.ability != "Cloud Nine" and buffs.update({"speedbuff": buffs["speedbuff"] * 2})),
        "Fur Coat": lambda mon: buffs.update({"atkbuff": buffs["atkbuff"] * 0.5}), # Note: This is an opposing Pokémon debuff
        "Ice Scales": lambda mon: buffs.update({"spdefbuff": buffs["spdefbuff"] * 2}),
        "Sage Power": lambda mon: buffs.update({"spatkbuff": buffs["spatkbuff"] * 1.5}),
        "Majestic Bird": lambda mon: buffs.update({"spatkbuff": buffs["spatkbuff"] * 1.5}),
        "Gorilla Tactics": lambda mon: buffs.update({"atkbuff": buffs["atkbuff"] * 1.5}),
        "Huge Power": lambda mon: buffs.update({"atkbuff": buffs["atkbuff"] * 2}),
        "Pure Power": lambda mon: buffs.update({"atkbuff": buffs["atkbuff"] * 2})
    }
    
    # Iterate through all ability buffs
    ABILITY_BUFFS.get(x.ability, lambda mon: None)(x)
    
    # Special: Supreme Overlord
    if x.ability == "Supreme Overlord":
        multiplier = 1 + 0.1 * (6 - len(tr1.pokemons))
        buffs["atkbuff"] *= multiplier
        buffs["spatkbuff"] *= multiplier
        
    # Special: Typeless
    if x.ability == "Typeless":
        x.primaryType = x.atktype

    # Special: Bull Rush/Quill Rush (needs to be reset)
    if x.ability in ["Bull Rush", "Quill Rush"] and x.bullrush == True:
        buffs["speedbuff"] *= 1.5
        buffs["atkbuff"] *= 1.2
        x.bullrush = False

    # --- 6. Opposing Ability Debuffs (Ruins) ---
    
    # Apply Ruin abilities
    if y.ability in RUIN_ABILITIES:
        ruin_buff_key = RUIN_ABILITIES[y.ability]
        buffs[ruin_buff_key] *= 0.75
    
    # --- 7. Status Debuffs ---

    if x.status == "Paralyzed" and x.ability != "Quick Feet":
        buffs["speedbuff"] *= 0.5
    if x.status == "Frostbite":
        buffs["spatkbuff"] *= 0.5
    if x.status == "Burned" and x.ability != "Guts":
        buffs["atkbuff"] *= 0.5
        
    # --- 8. Protosynthesis and Quark Drive ---
    
    # Protosynthesis
    is_proto_active = ("Protosynthesis" in x.ability and (field.weather in ["Sunny", "Extreme Sunlight"] or x.item == "Booster Energy")) or "[Attack" in x.ability or "[Defense" in x.ability or "[Sp. Attack" in x.ability or "[Sp. Defense" in x.ability or "[Speed" in x.ability
    
    if is_proto_active:
        is_booster_used = field.weather not in ["Sunny", "Extreme Sunlight"] and "[" not in x.ability
        if is_booster_used:
            pre_embed.add_field(name=f"{x.icon} {x.name}'s {await itemicon(x.item)} {x.item}!", value=f"{x.name} used its Booster Energy to activate Protosynthesis!")
            x.item += "[Used]"
            
        buff_key, stat_name, multiplier = _get_max_stat_modifier(x, tr1)
        buffs[buff_key] *= multiplier
        x.ability = f"Protosynthesis [{stat_name}]"

    # Quark Drive
    is_quark_active = ("Quark Drive" in x.ability and (field.terrain == "Electric" or x.item == "Booster Energy")) or "[Attack" in x.ability or "[Defense" in x.ability or "[Sp. Attack" in x.ability or "[Sp. Defense" in x.ability or "[Speed" in x.ability

    if is_quark_active:
        is_booster_used = field.terrain != "Electric" and "[" not in x.ability
        if is_booster_used:
            pre_embed.add_field(name=f"{x.icon} {x.name}'s {await itemicon(x.item)} {x.item}!", value=f"{x.name} used its Booster Energy to activate Quark Drive!")
            x.item += "[Used]"
            
        buff_key, stat_name, multiplier = _get_max_stat_modifier(x, tr1)
        buffs[buff_key] *= multiplier
        x.ability = f"Quark Drive [{stat_name}]"
    
    # --- 9. Final Stat Calculation ---

    # Base formula from the original code: x.stat = x.maxstat * buff_multiplier * stage_multiplier
    muldict = {1: 1.5, 2: 2, 3: 2.5, 4: 3, 5: 3.5, 6: 4, 0: 1, -1: 0.66, -2: 0.5, -3: 0.4, -4: 0.33, -5: 0.29, -6: 0.25}
    
    x.atk = x.maxatk * buffs["atkbuff"] * muldict[x.atkb]
    x.defense = x.maxdef * buffs["defbuff"] * muldict[x.defb]
    x.spatk = x.maxspatk * buffs["spatkbuff"] * muldict[x.spatkb]
    x.spdef = x.maxspdef * buffs["spdefbuff"] * muldict[x.spdefb]
    x.speed = x.maxspeed * buffs["speedbuff"] * muldict[x.speedb]
    
    # Send embed if any field was added
    if pre_embed.fields:
        await ctx.send(embed=pre_embed)

    return x, y, tr1, tr2, field    
    
def _is_trapped(user_mon, opp_mon):
    """Checks if the user's Pokémon (user_mon) is prevented from switching."""
    # Check for Arena Trap (if opponent has it and user is grounded/not holding Shed Shell)
    arena_trap = (opp_mon.ability == "Arena Trap" and user_mon.ability != "Levitate" and user_mon.item != "Shed Shell")
    
    # Check for Shadow Tag (if opponent has it and user isn't Ghost/holding Shed Shell)
    shadow_tag = (opp_mon.ability == "Shadow Tag" and "Ghost" not in (user_mon.primaryType, user_mon.secondaryType, user_mon.teraType) and user_mon.item != "Shed Shell")

    # Check for Magnet Pull (if opponent has it and user is Steel-type)
    magnet_pull = (opp_mon.ability == "Magnet Pull" and "Steel" in (user_mon.primaryType, user_mon.secondaryType, user_mon.teraType))
    
    # Check for trapping move effects
    move_trap = any([user_mon.firespin, user_mon.infestation, user_mon.sandtomb, user_mon.whirlpool])

    # Check for custom trainer/battle trap flags (y.trap == x or y.trap == y)
    custom_trap = (opp_mon.trap == user_mon or opp_mon.trap == opp_mon)
    
    return custom_trap or arena_trap or shadow_tag or magnet_pull or move_trap
    
class PlayerActionView(discord.ui.View):
    def __init__(self, tr1: 'Trainer', available_actions: Set[int], action_descriptions: Dict[int, str]):
        super().__init__(timeout=120.0)
        self.tr1 = tr1
        self.action_descriptions = action_descriptions
        self.selected_action: Optional[int] = None
        
        # Define base button styles and emojis using only standard colors
        styles = {
            1: (discord.ButtonStyle.secondary, "💥", "Fight"),        # Success
            2: (discord.ButtonStyle.secondary, "🔁", "Switch"),      # Primary
            3: (discord.ButtonStyle.secondary, "🚫", "Forfeit"),         # Danger
            
            # Use 'blurple' or 'gray' to replace 'gold' and 'dark_teal'
            5: (discord.ButtonStyle.secondary, "<:zmove:1140788256577949717>", "Z-Move"), 
            6: (discord.ButtonStyle.secondary, "<:megaevolve:1104646688951500850>", "Mega Evolve"), 
            7: (discord.ButtonStyle.secondary, "🌟", "Ultra Burst"),
            8: (discord.ButtonStyle.secondary, "<:dynamax:1104646304904257647>", "Dynamax"), 
            
            # Use 'blurple' or 'gray' to replace 'fuchsia'
            9: (discord.ButtonStyle.secondary, f"✨", "Terastallize"),
        }

        # Add buttons based on available_actions set
        for action_num in sorted(available_actions):
            if action_num in styles:
                style, emoji, label = styles[action_num]
                
                # Use a partial function to pass the action_num to the callback
                button = discord.ui.Button(
                    label=f"{label}",
                    style=style,
                    emoji=emoji,
                    custom_id=f"action_{action_num}"
                )
                button.callback = self.create_action_callback(action_num)
                self.add_item(button)

    def create_action_callback(self, action_num: int):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.tr1.member.id:
                await interaction.response.send_message("This action menu is not for you.", ephemeral=True)
                return

            self.selected_action = action_num
            await interaction.response.defer() # Defer before stopping
            self.stop()
            
        return callback

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Check moved into the button callbacks for personalized error
        return True

    async def on_timeout(self):
        # On timeout, the action defaults to 3 (Forfeit) handled in _get_player_action
        pass

# --- Helper to process available actions and descriptions ---

async def get_action_data(tr1, x):
    """Processes Pokemon state to determine available actions."""
    
    action_descriptions = {
        1: "Fight", 2: "Switch", 3: "Forfeit"
    }
    available_actions = {1, 2, 3}
    
    # Check Z-Move (5)
    if "m-Z" in x.item and tr1.canz and x.zuse:
        available_actions.add(5)
        action_descriptions[5] = "Z-Move"
        
    # Check Mega Evolve (6)
    if tr1.canmega and not x.dmax and (x.item in megastones or "Dragon Ascent" in x.moves) and x.teraType == "???":
        available_actions.add(6)
        action_descriptions[6] = "Mega Evolve"
        
    # Check Ultra Burst (7)
    if not x.dmax and x.item == "Ultranecrozium-Z" and "Ultra" not in x.name:
        available_actions.add(7)
        action_descriptions[7] = "Ultra Burst"
        
    # Check Dynamax/Gigantamax (8)
    if tr1.canmax and not x.dmax and x.item not in megastones and x.teraType == "???" and "m-Z" not in x.item:
        available_actions.add(8)
        action_descriptions[8] = "Dynamax/Gigantamax"
        
    # Check Terastallize (9)
    if tr1.cantera and not x.dmax and x.item not in megastones and x.teraType == "???" and "m-Z" not in x.item and x.tera != "Max":
        available_actions.add(9)
        action_descriptions[9] = f"Terastallize {await teraicon(x.tera)}"
        
    return available_actions, action_descriptions   
async def _get_player_action(bot, ctx, tr1, x, tr2):
    """Handles the user input using buttons and returns the validated action number."""
    
    # 1. Determine Available Actions (Replaces original description building)
    available_actions, action_descriptions = await get_action_data(tr1, x)

    # 2. Get Input Target and Channel
    # Human vs Human (DM) or Human vs AI (Channel)
    if not tr2.ai:
        channel = tr1.member.dm_channel or await tr1.member.create_dm()
    else:
        channel = ctx.channel
    
    # 3. Create and Send View
    view = PlayerActionView(tr1, available_actions, action_descriptions)
    
    # Build the description string for the embed
    des_list = [f"#{num} {action_descriptions.get(num, 'Action')}" for num in sorted(available_actions)]
    des = "\n".join(des_list)

    em = discord.Embed(
        title=f"{tr1.name}, what do you wanna do?", 
        description=des
    )
    em.set_footer(text="Select your action using the buttons below.")
    
    # Send the embed with the buttons
    msg = await channel.send(embed=em, view=view)
    
    # 4. Wait for the button press (or timeout)
    try:
        await view.wait()
        
        # Clean up the message after selection
        try:
            await msg.edit(view=None)
        except:
            pass
            
        # Return the selected action number
        return view.selected_action if view.selected_action is not None else 3 # Default to Forfeit on miss
        
    except asyncio.TimeoutError:
        # Clean up the message on timeout
        try:
            await msg.edit(content="Action timed out. Forfeiting battle.", embed=None, view=None)
        except:
            pass
            
        # Explicitly catch timeout and return 3 (Forfeit)
        return 3             
async def action(bot, ctx, tr1, tr2, x, y):
    """
    Determines the action (move, switch, transform) for a trainer (tr1), 
    either by AI or by user input.
    """
    
    # --- AI Logic (tr1.ai == True) ---
    if tr1.ai:
        # Check for transformation priority (order matters)
        
        # 1. Mega Evolve (Highest priority)
        if x.item in megastones and tr1.canmega:
            # 10:1 chance for Mega vs Fight
            return random.choices([1, 6], weights=[1, 10], k=1)[0] 
        
        # 2. Z-Move
        if "m-Z" in x.item and tr1.canz and x.zuse:
            move = 5
        
        # 3. Terastallize
        elif x.tera not in ["???", "Max"] and tr1.cantera and x.item not in megastones and x.teraType == "???" and \
             (x.name == "Ogerpon" or x.name == "Terapagos" or x.tera not in (x.primaryType, x.secondaryType)):
            move = 9
            
        # 4. Dynamax/Gigantamax
        elif x.item not in megastones and tr1.canmax and x.teraType == "???" and "m-Z" not in x.item:
            # Check for the Max form on a team member (from the original logic)
            new = [i.tera for i in tr1.pokemons]
            if x.tera == "Max" or "Max" not in new:
                # 1/6 chance to Dynamax
                max_choice = random.randint(1, 6)
                move = 8 if max_choice == 1 else 1
            else:
                move = 1 # Fight if another mon is Dynamaxed/no Max form selected
        
        # 5. Default Action: 10:1 chance for Fight vs Switch
        else:
            move = random.choices([1, 2], weights=[10, 1], k=1)[0]

        # 6. Final Trapping Check
        if move == 2 and _is_trapped(x, y):
            return 1  # Force Fight if trapped
        else:
            return move
        
    # --- Player Logic (tr1.ai == False) ---
    else:
        action_num = await _get_player_action(bot, ctx, tr1, x, tr2)
        
        # Final Trapping Check
        if action_num == 2 and _is_trapped(x, y):
            return 1  # Force Fight if trapped
        
        return action_num
        
async def spartyup(tr1,x):
    di={

    "Male":"<:male:1140875825693085757>",

    "Female":"<:female:1140875954193956944>",

    "Genderless":"<:genderless:1140875679383175250>",

    "Sleep":"<:asleep:1140745217193021511>",

    "Burned":"<:burned:1140744974514782369>",

    "Poisoned":"<:poisoned:1140745045805379604>",

    "Badly Poisoned":"<:poisoned:1140745045805379604>",

    "Frozen":"<:frozen:1140745102889857045>",

    "Paralyzed":"<:paralyzed:1140745164231544954>",

    "Alive":"<:healthy:1140746496657080420>",

    "Drowsy":"<:asleep:1140745217193021511>",

    "Frostbite":"<:frozen:1140745102889857045>",

    "Fainted":"<:fainted:1142928844421070849>"

    }

    tr1.sparty[tr1.party.index(x.icon)]=di[x.status]
    return tr1.sparty

async def score(ctx, x, y, tr1, tr2, turn, bg):
    
    # 1. Create a list of all potential awaitable coroutines (including those that are None)
    awaitables = [
        typeicon(x.primaryType),
        typeicon(x.secondaryType) if x.secondaryType != "???" else None,
        spartyup(tr1, x),
        itemicon(x.item) if x.showitem else None,
        statusicon(x.status),
        bufficon(x.atkb),
        bufficon(x.defb),
        bufficon(x.spatkb),
        bufficon(x.spdefb),
        bufficon(x.speedb)
    ]
    
    # 2. Filter out all 'None' values
    coroutines_to_run = [c for c in awaitables if c is not None]

    # 3. Run only the valid coroutines
    results = await asyncio.gather(*coroutines_to_run)
    
    # --- Mapping Results Back ---
    # This part gets tricky because the number of 'results' is variable.
    # To maintain the original structure and make sure 'results' aligns with the original 10 items, 
    # you need a different approach.
    
    # The better approach is to wrap the None value in an awaitable:
    
    # ------------------------------------------------
    # 2. Use an Awaitable to Return None (Alternative Fix)
    # ------------------------------------------------
    
    # Helper to return None as an awaitable
    async def return_none():
        return None
        
    results = await asyncio.gather(
        typeicon(x.primaryType),
        typeicon(x.secondaryType) if x.secondaryType != "???" else return_none(), # <- Fix 1
        spartyup(tr1, x),
        itemicon(x.item) if x.showitem else return_none(),                     # <- Fix 2
        statusicon(x.status),
        bufficon(x.atkb),
        bufficon(x.defb),
        bufficon(x.spatkb),
        bufficon(x.spdefb),
        bufficon(x.speedb)
    )

    p_type_icon, s_type_icon, tr1.sparty, item_icon, status_icon_val, atkb_icon, defb_icon, spatkb_icon, spdefb_icon, speedb_icon = results

    # Reconstruct the 'types' string
    types = p_type_icon
    if x.secondaryType != "???":
        types = f"{p_type_icon}{s_type_icon}"

    team = " ".join(tr1.party)
    steam = " ".join(tr1.sparty)
    
    # --- HP Bar Construction (No change needed, it's efficient) ---
    hp_ratio = x.hp / x.maxhp
    hpbar_base = "<:HP:1107296292243255356>"
    hpbar_end = "<:END:1107296362988580907>"
    fill_count = int(hp_ratio * 10)
    grey_count = 10 - fill_count
    grey_fill = "<:GREY:1107331848360689747>" * grey_count

    status_icons = {
        "Frostbite": "<:FBT:1107340620097404948>",
        "Frozen": "<:FZN:1107340597980827668>",
        "Sleep": "<:SLP:1107340641882603601>",
        "Drowsy": "<:SLP:1107340641882603601>",
        "Paralyzed": "<:YELLOW:1107331825929556111>",
        "Burned": "<:BRN:1107340533518573671>",
        "Poisoned": "<:PSN:1107340504762437723>",
        "Badly Poisoned": "<:PSN:1107340504762437723>"
    }

    fill_emoji = ""
    if x.dmax:
        fill_emoji = "<:dynamax:1141227784958652547>"
    elif x.status in status_icons:
        fill_emoji = status_icons[x.status]
    elif x.status == "Alive":
        if 0.6 < hp_ratio <= 1:
            fill_emoji = "<:GREEN:1107296335780139113>"
        elif 0.3 < hp_ratio <= 0.6:
            fill_emoji = "<:YELLOW:1107331825929556111>"
        elif 0 < hp_ratio <= 0.3:
            fill_emoji = "<:RED:1107331787480379543>"
            
    hpbar = f"{hpbar_base}{fill_emoji * fill_count}{grey_fill}{hpbar_end}"
    
    # --- Optimization 2: Field Effects (Fixing the logic bug) ---
    rflct = ""
    ls = ""
    av = ""
    tw = ""

    if tr1.reflect:
        rflct = f"\n<:reflect:1142009182095163422> Reflect"
    if tr1.lightscreen:
        ls = f"\n<:lightscreen:1142009225741082657> Light Screen"
    if tr1.auroraveil:
        av = f"\n<:auroraveil:1142009279705006102> Aurora Veil"
    if tr1.tailwind:
        tw = f"\n<:tailwind:1142043322064572446> Tailwind"

    # --- Ability and Item (No change needed) ---
    abl = f"\n**Ability:** {x.ability}" if x.showability else ""
    itm = ""
    if x.showitem:
        it = x.item
        if "Used" in x.item:
            it = "None"
        itm = f"\n**Held Item:** {item_icon} {it}"

    # --- Embed Construction (No change needed) ---
    em = discord.Embed(
        title=f"{tr1.name}:",
        description=f"{team}\n{steam}",
        color=bg,
    )

    em.add_field(
        name="Stats:", 
        value=(
            f"{types} **{x.nickname}** Lv. {x.level}\n"
            f"**HP:** {round(x.hp)}/{x.maxhp} ({round(hp_ratio*100, 2)}%){abl}{itm}\n"
            f"**ATK:** {atkb_icon} **DEF:** {defb_icon} **SPA:** {spatkb_icon} **SPD:** {spdefb_icon} **SPE:** {speedb_icon}"
            f"{rflct}{ls}{av}{tw}"
        )
    )
    em.add_field(name="HP Bar:", value=f"{hpbar}{status_icon_val}")

    # --- Hazards Field (No change needed) ---
    if tr1.hazard != []:
        hazard = ""
        # Using string methods for cleaner hazard creation
        if "Stealth Rock" in tr1.hazard:
            hazard += "\n<:stealthrock:1154507457763233823> Stealth Rock"
        hazard += f"\n<:spikes:1154509457976459380> Spikes x{tr1.hazard.count('Spikes')}" if "Spikes" in tr1.hazard else ""
        hazard += f"\n<:toxicspikes:1154509769168662648> Toxic Spikes x{tr1.hazard.count('Toxic Spikes')}" if "Toxic Spikes" in tr1.hazard else ""
        hazard += f"\n<:steelspikes:1154509599467118694> Steel Spikes x{tr1.hazard.count('Steel Spikes')}" if "Steel Spikes" in tr1.hazard else ""
        if "Sticky Web" in tr1.hazard:
            hazard += "\n<:stickyweb:1154510037067255808> Sticky Web"
        
        # Remove the leading '\n' if present
        em.add_field(name="Hazards:", value=hazard.lstrip('\n'), inline=False)
        
    em.set_image(url=x.sprite)
    em.set_footer(text=f"ATK: {x.atkb} DEF: {x.defb} SPA: {x.spatkb} SPD: {x.spdefb} SPE: {x.speedb}")
    
    if tr1.sub != "None":
        em.set_image(url="https://play.pokemonshowdown.com/sprites/substitutes/gen5/substitute.png")
    if x.gsprite != "None":
        em.set_image(url=x.gsprite)
    await ctx.send(embed=em)
    
async def statusicon(s):
    di={
    "Male":"<:male:1140875825693085757>",
    "Female":"<:female:1140875954193956944>",
    "Genderless":"<:genderless:1140875679383175250>",
    "Sleep":"<:asleep:1140745217193021511>",
    "Burned":"<:burned:1140744974514782369>",
    "Poisoned":"<:poisoned:1140745045805379604>",
    "Badly Poisoned":"<:poisoned:1140745045805379604>",
    "Frozen":"<:frozen:1140745102889857045>",
    "Paralyzed":"<:paralyzed:1140745164231544954>",
    "Alive":"<:healthy:1140746496657080420>",
    "Drowsy":"<:asleep:1140745217193021511>",
    "Frostbite":"<:frozen:1140745102889857045>",
    "Fainted":"<:fainted:1142928844421070849>"
    }
    return di[s]
async def advscore(ctx, x, y, tr1, tr2, turn, field, bg):
    types=await typeicon(x.primaryType)
    if x.secondaryType!="???":
        types=f"{await typeicon(x.primaryType)}{await typeicon(x.secondaryType)}"
    team = " ".join(tr1.party)
    tr1.sparty = await spartyup(tr1, x)
    steam = " ".join(tr1.sparty)
    
    hpbar = "<:HP:1107296292243255356>" + "<:GREY:1107331848360689747>" * 10 + "<:END:1107296362988580907>"
    
    status_icons = {
        "Frostbite": "<:FBT:1107340620097404948>",
        "Frozen": "<:FZN:1107340597980827668>",
        "Sleep": "<:SLP:1107340641882603601>",
        "Drowsy": "<:SLP:1107340641882603601>",
        "Paralyzed": "<:YELLOW:1107331825929556111>",
        "Burned": "<:BRN:1107340533518573671>",
        "Poisoned": "<:PSN:1107340504762437723>",
        "Badly Poisoned": "<:PSN:1107340504762437723>"
    }
    
    if x.dmax == True:
        hpbar = "<:HP:1107296292243255356>" + "<:dynamax:1141227784958652547>" * int((x.hp / x.maxhp) * 10) + "<:GREY:1107331848360689747>" * (10 - int((x.hp / x.maxhp) * 10)) + "<:END:1107296362988580907>"
    elif x.status in status_icons:
        hpbar = "<:HP:1107296292243255356>" + status_icons[x.status] * int((x.hp / x.maxhp) * 10) + "<:GREY:1107331848360689747>" * (10 - int((x.hp / x.maxhp) * 10)) + "<:END:1107296362988580907>"
    elif x.status == "Alive":
        if 0.6 < (x.hp / x.maxhp) <= 1:
            hpbar = "<:HP:1107296292243255356>" + "<:GREEN:1107296335780139113>" * int((x.hp / x.maxhp) * 10) + "<:GREY:1107331848360689747>" * (10 - int((x.hp / x.maxhp) * 10)) + "<:END:1107296362988580907>"
        if 0.3 < (x.hp / x.maxhp) <= 0.6:
            hpbar = "<:HP:1107296292243255356>" + "<:YELLOW:1107331825929556111>" * int((x.hp / x.maxhp) * 10) + "<:GREY:1107331848360689747>" * (10 - int((x.hp / x.maxhp) * 10)) + "<:END:1107296362988580907>"
        if 0 < (x.hp / x.maxhp) <= 0.3:
            hpbar = "<:HP:1107296292243255356>" + "<:RED:1107331787480379543>" * int((x.hp / x.maxhp) * 10) + "<:GREY:1107331848360689747>" * (10 - int((x.hp / x.maxhp) * 10)) + "<:END:1107296362988580907>"
    
    itm = x.item
    if "Used" in itm:
        itm = "None"
    
    rflct = ""
    if tr1.reflect == True:
        rflct = f"\n<:reflect:1142009182095163422> Reflect ({tr1.rfendturn-turn} turns left)"
    
    ls = ""
    if tr1.lightscreen == True:
        rflct = f"\n<:lightscreen:1142009225741082657> Light Screen ({tr1.screenend-turn} turns left)"     
   
    av = ""          
    if tr1.auroraveil == True:
        av = f"\n<:auroraveil:1142009279705006102> Aurora Veil ({tr1.avendturn-turn} turns left)"
    
    tw = ""   
    if tr1.tailwind == True:
        av = f"\n<:tailwind:1142043322064572446> Tailwind ({tr1.twendturn-turn} turns left)"        
    
    em = discord.Embed(
        title=f"{tr1.name}:",
        description=f"{team}\n{steam}",
        color=bg
    )
    
    em.add_field(name="Stats:", value=f"{types} **{x.nickname}** {await statusicon(x.gender)} Lv. {x.level}\n**HP:** {round(x.hp)}/{x.maxhp} ({round((x.hp/x.maxhp)*100,2)}%)\n**Ability:** {x.ability}\n**Held Item:** {await itemicon(x.item)} {itm}\n**ATK:** {round(x.atk)}{await bufficon(x.atkb)} **DEF:** {round(x.defense)}{await bufficon(x.defb)} **SPA:** {round(x.spatk)}{await bufficon(x.spatkb)} **SPD:** {round(x.spdef)}{await bufficon(x.spdefb)} **SPE:** {round(x.speed)}{await bufficon(x.speedb)}{rflct}{ls}{av}{tw}")
    em.add_field(name="HP Bar:", value=f"{hpbar}{await statusicon(x.status)}")
    if tr1.hazard!=[]:
        hazard=""
        if "Stealth Rock" in tr1.hazard:
            hazard+="\n<:stealthrock:1154507457763233823> Stealth Rock"
        if "Spikes" in tr1.hazard:
            hazard+=f"\n<:spikes:1154509457976459380> Spikes x{tr1.hazard.count('Spikes')}"
        if "Toxic Spikes" in tr1.hazard:
            hazard+=f"\n<:toxicspikes:1154509769168662648> Toxic Spikes x{tr1.hazard.count('Toxic Spikes')}"
        if "Steel Spikes" in tr1.hazard:
            hazard+=f"\n<:steelspikes:1154509599467118694> Steel Spikes x{tr1.hazard.count('Steel Spikes')}"
        if "Sticky Web" in tr1.hazard:
            hazard+="\n<:stickyweb:1154510037067255808> Sticky Web"
        em.add_field(name="Hazards:",value=f"{hazard}",inline=False)
    em.set_image(url=x.sprite)
    em.set_footer(text=f"ATK: {x.atkb} DEF: {x.defb} SPA: {x.spatkb} SPD: {x.spdefb} SPE: {x.speedb}")
    
    if tr1.sub != "None":
        em.set_image(url="https://cdn.discordapp.com/attachments/1102579499989745764/1139438981445062719/20230811_120335.png")
    
    if x.gsprite != "None":
        em.set_image(url=x.gsprite)
    
    if tr2.ai == False:
        await tr1.member.send(embed=em)
        
    if tr2.ai == True:
        await ctx.send(embed=em)
async def bufficon(s,base=0):
    if s==base:
        return "<:base:1140755497323081789>"
    elif s<base:
        return "<:low:1140755454071418910>"
    elif s>base:
        return "<:high:1140755420533772389>"  
class MoveChoiceView(discord.ui.View):
    def __init__(self, x: 'Pokemon', tr1: 'Trainer', tr2, field, move_data: List[Tuple[str, str, str, str, int]]):
        super().__init__(timeout=120.0)
        self.x = x
        self.tr1 = tr1
        self.tr2 = tr2
        self.field = field
        self.move_data = move_data # (Move Name, Type Icon, Ct Icon, PP Left)
        self.selected_move: Optional[str] = None

        # Create buttons for each move
        for i, (m_name, t_icon, ct_icon, pp_text, pp_left) in enumerate(move_data):
            # Move index is 0-indexed here
            move_index = i
            
            # Disable if PP is zero
            is_disabled = (pp_left <= 0)
            
            # Use 'red' if PP is 0, 'green' otherwise
            button_style = discord.ButtonStyle.secondary if is_disabled else discord.ButtonStyle.secondary
            
            button = discord.ui.Button(
                label=f"{m_name}",
                style=button_style,
                custom_id=f"move_{move_index}",
                disabled=is_disabled
            )
            button.callback = self.create_move_callback(move_index, m_name)
            self.add_item(button)

    def create_move_callback(self, move_index: int, move_name: str):
        async def callback(interaction: discord.Interaction):
            # Check if the correct user pressed the button
            if interaction.user.id != self.tr1.member.id:
                await interaction.response.send_message("This move menu is not for you.", ephemeral=True)
                return

            # Acknowledge the interaction
            await interaction.response.defer()
            
            # --- Perform immediate validation checks here (e.g., Assault Vest, Choice Lock) ---
            
            current_move_list = self.x.maxmoves if self.x.dmax else self.x.moves
            selected_move = current_move_list[move_index]
            
            # 1. Assault Vest Check
            # NOTE: Assuming typemoves.statusmove is accessible, otherwise this check needs data
            if "Assault Vest" in self.x.item:
                 # Check if the selected_move is a status move
                 if selected_move in typemoves.statusmove: # Requires typemoves
                    await interaction.followup.send("Cannot use status moves while holding Assault Vest.", ephemeral=True)
                    return # Keep view alive
            
            # 2. Choice Item Lock Check (Only checks if *another* move was selected)
            if "Choice" in self.x.item and self.x.choiced != "None":
                if selected_move != self.x.choicedmove:
                    # User clicked wrong move, force the correct one
                    try:
                        # Find the index of the locked move
                        lock_index = current_move_list.index(self.x.choicedmove)
                        
                        # Return the locked move, but send feedback to the user
                        self.selected_move = self.x.choicedmove
                        await interaction.followup.send(f"Locked into {self.x.choicedmove} by Choice Item!", ephemeral=True)
                        self.stop()
                        return
                    except ValueError:
                        # Locked move is gone (e.g., PP exhausted, deleted)
                        self.selected_move = "Struggle"
                        self.stop()
                        return
            
            # 3. Default Choice / First Choice Item Lock
            if "Choice" in self.x.item and self.x.choiced == "None":
                self.x.choiced = True
                self.x.choicedmove = selected_move
            
            # Final valid move selection
            self.selected_move = selected_move
            self.stop()
            
        return callback

    async def on_timeout(self):
        # On timeout, the move defaults to Struggle handled in fchoice
        pass
        
async def movelist(ctx, x, tr1, tr2, field):
    """
    Prepares and returns the list of moves and their data for the view.
    Does NOT send an embed.
    """
    move_data = [] # Stores (Move Name, Type Icon, Ct Icon, PP Text, PP Left)
    
    # Define which moves and PP list to use
    moves = x.maxmoves if x.dmax else x.moves
    pp_list = x.pplist
    
    # --- Z-Move Logic (Override the entire list) ---
    if x.zuse and tr1.canz:
        # Z-Move is unique and only one option, usually handled outside the move list selection
        # For simplicity with buttons, we'll keep Z-Move selection separate from the 4 moves.
        # However, since your Z-Move logic uses fchoice, we'll return an empty list
        # and handle the Z-Move return directly in fchoice.
        return []

    # --- Dynamax or Normal Moves logic ---
    if not moves:
        return [] # No moves left
        
    awaitables = []
    # Create a list of all movetypeicon and movect calls
    for m in moves:
        awaitables.append(movetypeicon(x, m, field))
        awaitables.append(movect(m))
        
    # Run all awaits concurrently
    if awaitables:
        results = await asyncio.gather(*awaitables)
        
        # Map results back to move_data
        for i, m in enumerate(moves):
            type_icon = results[i * 2]
            move_ct = results[i * 2 + 1]
            
            # Get the correct PP index (Dynamax moves map to the original move's PP index)
            try:
                if x.dmax:
                    # Find the corresponding original move index for maxmove (complex lookup needed)
                    # For simplicity, we assume maxmoves is in the same order as x.moves
                    pp_index = i
                else:
                    pp_index = x.moves.index(m)
                
                pp_left = pp_list[pp_index]
            except (IndexError, ValueError):
                pp_left = 0 # Safety catch

            pp_text = f"PP:{pp_left}"
            
            # Store data as a tuple: (Move Name, Type Icon, Ct Icon, PP Text, PP Left)
            move_data.append((m, type_icon, move_ct, pp_text, pp_left))

    return move_data
       
async def fchoice(ctx, bot, x, y, tr1, tr2, field):
    # --- AI Trainer Logic (Direct Return) ---
    if tr1.ai:
        choice = await moveAI(x, y, tr1, tr2, field)
        return choice[0]

    # --- Human Trainer Logic (Button View) ---
    
    # 1. Z-Move Check (If Z-Move is available, it's the only immediate option)
    if x.zuse and tr1.canz:
        x.zuse = False
        tr1.canz = False
        # Send a brief message confirming Z-Move selection (optional)
        # await tr1.member.send(f"{x.name} is preparing to use {x.zmove}!")
        return x.zmove

    # 2. Get Move Data
    move_data = await movelist(ctx, x, tr1, tr2, field)
    
    if not move_data:
        return "Struggle"
    
    # 3. Determine Channel
    if not tr2.ai: # Human vs Human: DM
        channel = tr1.member.dm_channel or await tr1.member.create_dm()
    else: # Human vs AI: Channel
        channel = ctx.channel

    # 4. Create and Send View
    view = MoveChoiceView(x, tr1, tr2, field, move_data)
    
    # Create the embed description from the move_data for display
    des_list = []
    for i, (m_name, t_icon, ct_icon, pp_text, pp_left) in enumerate(move_data):
        des_list.append(f"#{i+1} {t_icon} {m_name} {ct_icon} {pp_text}")
    
    embed = discord.Embed(
        title=f"What will {x.name} use? (Select a Move)",
        description="\n".join(des_list),
        color=discord.Color.red()
    )

    msg = await channel.send(embed=embed, view=view)
    
    # 5. Wait for selection
    try:
        await view.wait()
        
        # Clean up the message
        try:
            await msg.edit(view=None)
        except:
            pass
            
        # Return the selected move (already validated for most conditions within the view)
        if view.selected_move:
            return view.selected_move
        else:
            return "Struggle" # Should only happen on timeout
            
    except asyncio.TimeoutError:
        # Clean up the message and return Struggle
        try:
            await msg.edit(content="Move selection timed out. Using Struggle.", embed=None, view=None)
        except:
            pass
        return "Struggle"
                      
async def megatrans(ctx,x,y,tr1,tr2,field,turn):
    des=f"{x.icon} {x.name}'s {x.item} is reacting to {tr1.name}'s Keystone!\n{x.name} has Mega Evolved into Mega {x.name}!"
    x.nickname=f"Mega {x.name}"
    if x.name not in ["Mewtwo","Charizard","Raichu"]:
        x.sprite=x.sprite.replace(".gif","-mega.gif")
    elif x.name not in ["Mewtwo","Charizard","Raichu"]:
        x.nickname=f"Mega {x.name} {x.item[-1]}"
    if "Rayquaza" in x.name:
        des=f"{tr1.name}'s fervent wish has reached {x.name}!\nRayquaza Mega evolved into Mega Rayquaza!"
    em=discord.Embed(title="Mega Evolution:",description=des) 
    em.set_thumbnail(url="https://cdn.discordapp.com/attachments/1102579499989745764/1108284098641940521/Mega.png")
    tr1.canmega=False
    if True:
        if x.item=="Zygardite" and "Zygarde" in x.name and x.hp<=x.maxhp:
            per=x.hp/x.maxhp
            x.weight=1344.82
            x.hp=216
            x.atk=70
            x.defense=91
            x.spatk=216
            x.spdef=85
            x.speed=100
            calcst(x)
            x.sprite="https://archives.bulbagarden.net/media/upload/thumb/2/2e/Mega_Zygarde_aiming_its_cannon.jpg/214px-Mega_Zygarde_aiming_its_cannon.jpg"
            x.hp=x.maxhp*per
        if x.item=="Heatranite" and "Heatran" in x.name:
            per=x.hp/x.maxhp
            x.weight=4300
            x.hp=91
            x.atk=120
            x.defense=106
            x.spatk=175
            x.spdef=141
            x.speed=67
            calcst(x)
            x.sprite="https://i.postimg.cc/9fM83CX8/Mega-Heatran.png"
            x.hp=x.maxhp*per    
        if x.item=="Zeraorite" and "Zeraora" in x.name:
            per=x.hp/x.maxhp
            x.weight=445
            x.hp=88
            x.atk=157
            x.defense=75
            x.spatk=147
            x.spdef=80
            x.speed=153
            calcst(x)
            x.sprite="https://i.postimg.cc/7L6svwPt/Mega-Zeraora.png"
            x.hp=x.maxhp*per
        if x.item=="Darkranite" and "Darkrai" in x.name:
            per=x.hp/x.maxhp
            x.weight=505
            x.hp=70
            x.atk=120
            x.defense=130
            x.spatk=165
            x.spdef=130
            x.speed=85
            calcst(x)
            x.sprite="https://i.postimg.cc/N0MJhBGN/Mega-Darkrai.png"
            x.hp=x.maxhp*per
        if x.item=="Baxcaliburite" and "Baxcalibur" in x.name:
            per=x.hp/x.maxhp
            x.weight=445
            x.hp=115
            x.atk=185
            x.defense=112
            x.spatk=65
            x.spdef=96
            x.speed=102
            calcst(x)
            x.sprite="https://i.postimg.cc/pV8WjtQ8/Mega-Baxcalibur.png"
            x.hp=x.maxhp*per
        if x.item=="Chimecite" and "Chimecho" in x.name:
            x.secondaryType="Steel"
            per=x.hp/x.maxhp
            x.weight=445
            x.hp=75
            x.atk=60
            x.defense=100
            x.spatk=145
            x.spdef=120
            x.speed=95
            calcst(x)
            x.sprite="https://i.postimg.cc/h4xDmq8T/Mega-Chingling.png"
            x.hp=x.maxhp*per
        if x.item=="Feraligite" and "Feraligatr" in x.name:
            x.ability="Strong Jaw"
            x.secondaryType="Dragon"
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=85
            x.atk=160
            x.defense=125
            x.spatk=89
            x.spdef=93
            x.speed=78
            calcst(x)
            x.sprite="https://i.postimg.cc/SNB9LFtP/mega-fetaligatr.png"
            x.hp=x.maxhp*per
        if x.item=="Chandelurite" and "Chandelure" in x.name:
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=60
            x.atk=75
            x.defense=110
            x.spatk=175
            x.spdef=110
            x.speed=90
            x.sprite="https://i.postimg.cc/NFcpF2vY/mega-chandelure.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Froslassite" and "Froslass" in x.name:
            x.ability="Intimidate"
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=70
            x.atk=80
            x.defense=70
            x.spatk=140
            x.spdef=100
            x.speed=120
            x.sprite="https://i.postimg.cc/MTqpnk1L/mega-froslass.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Scolipite" and "Scolipede" in x.name:
            x.ability="Tinted Lens"
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=60
            x.atk=130
            x.defense=109
            x.spatk=65
            x.spdef=995
            x.speed=122
            x.sprite="https://pbs.twimg.com/media/G0ghgGtXUAE1XSd.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Emboarite" and "Emboar" in x.name:
            x.ability="Supreme Overlord"
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=110
            x.atk=148
            x.defense=75
            x.spatk=110
            x.spdef=110
            x.speed=75
            x.sprite="https://i.postimg.cc/1RV857vP/mega-emboar.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Excadrite" and "Excadrill" in x.name:
            x.ability="Tough Claws"
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=110
            x.atk=165
            x.defense=100
            x.spatk=65
            x.spdef=65
            x.speed=103
            x.sprite="https://i.postimg.cc/NFB55BJq/mega-excadrill.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Falinksite" and "Falinks" in x.name:
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=65
            x.atk=135
            x.defense=135
            x.spatk=70
            x.spdef=65
            x.speed=100
            x.sprite="https://i.postimg.cc/x1pkdrV6/mega-falinks.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Meganiumite" and "Meganium" in x.name:
            x.ability="Natural Cure"
            x.secondaryType="Fairy"
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=80
            x.atk=92
            x.defense=115
            x.spatk=143
            x.spdef=115
            x.speed=80
            x.sprite="https://i.postimg.cc/rmjFWh9n/mega-meganium.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Pyroarite" and "Pyroar" in x.name:
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=86
            x.atk=88
            x.defense=92
            x.spatk=129
            x.spdef=86
            x.speed=126
            x.sprite="https://i.postimg.cc/VkZSNyPZ/mega-pyroar.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Starmite" and "Starmie" in x.name:
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=60
            x.atk=140
            x.defense=105
            x.spatk=130
            x.spdef=105
            x.speed=120
            x.sprite="https://i.postimg.cc/ydjY9fTG/mega-starmie.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Clefablite" and "Clefable" in x.name:
            x.ability="Aerialate"
            x.secondaryType="Flying"
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=95
            x.atk=80
            x.defense=93
            x.spatk=135
            x.spdef=110
            x.speed=70
            x.sprite="https://i.postimg.cc/5yjYtdMS/mega-clefable.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Scolipedite" and "Scolipede" in x.name:
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=60
            x.atk=140
            x.defense=149
            x.spatk=75
            x.spdef=99
            x.speed=62
            x.sprite="https://i.postimg.cc/fbxbWWSx/mega-scolipede.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Scraftinite" and "Scrafty" in x.name:
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=60
            x.atk=130
            x.defense=135
            x.spatk=55
            x.spdef=135
            x.speed=68
            x.sprite="https://i.postimg.cc/TPrP225g/mega-scrafty.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Skarmorite" and "Skarmory" in x.name:
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=65
            x.atk=140
            x.defense=110
            x.spatk=40
            x.spdef=100
            x.speed=110
            x.sprite="https://i.postimg.cc/85Nz78Lq/mega-skarmory.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Malamarite" and "Malamar" in x.name:
            x.ability="Contrary"
            per=x.hp/x.maxhp
            x.weight=153.41
            x.hp=86
            x.atk=102
            x.defense=88
            x.spatk=98
            x.spdef=120
            x.speed=88
            x.sprite="https://i.postimg.cc/XvTDL3s2/mega-malamar.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Dragoninite" and "Dragonite" in x.name:
            x.ability="Aerilate"
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=91
            x.atk=124
            x.defense=115
            x.spatk=145
            x.spdef=125
            x.speed=100
            x.sprite="https://i.postimg.cc/KYLZhCZs/mega-dragonite.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Drampanite" and "Drampa" in x.name:
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=78
            x.atk=85
            x.defense=110
            x.spatk=160
            x.spdef=116
            x.speed=36
            x.sprite="https://i.postimg.cc/fR9CcvWk/mega-drampa.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Eelektrossite" and "Eelektross" in x.name:
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=85
            x.atk=145
            x.defense=80
            x.spatk=135
            x.spdef=90
            x.speed=80
            x.sprite="https://i.postimg.cc/tghgRRns/mega-eelektross.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Victreebelite" and "Victreebel" in x.name:
            x.ability="Corrosion"
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=80
            x.atk=125
            x.defense=85
            x.spatk=135
            x.spdef=95
            x.speed=70
            x.sprite="https://i.postimg.cc/c4ByJKXj/mega-victreebel.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Greninjite" and "Greninja" in x.name:
            x.ability="Techician"
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=72
            x.atk=125
            x.defense=77
            x.spatk=133
            x.spdef=81
            x.speed=142
            x.sprite="https://i.postimg.cc/63tp8sCr/mega-greninja.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Floettite" and "Eternal Floette" in x.name:
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=74
            x.atk=85
            x.defense=87
            x.spatk=155
            x.spdef=148
            x.speed=102
            x.sprite="https://i.postimg.cc/8zXFC8gy/mega-foette.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Delphoxite" and "Delphox" in x.name:
            x.ability="Levitate"
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=75
            x.atk=69
            x.defense=72
            x.spatk=159
            x.spdef=125
            x.speed=134
            x.sprite="https://i.postimg.cc/HxdkrGb7/mega-delphox.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Dragalgite" and "Dragalge" in x.name:
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=65
            x.atk=85
            x.defense=105
            x.spatk=132
            x.spdef=163
            x.speed=44
            x.sprite="https://i.postimg.cc/JzYyhwC6/mega-dragalge.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Chesnaughtite" and "Chesnaught" in x.name:
            x.ability="Stamina"
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=88
            x.atk=137
            x.defense=172
            x.spatk=74
            x.spdef=115
            x.speed=44
            x.sprite="https://i.postimg.cc/PxT5CG1b/mega-chesnaught.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Hawluchanite" and "Hawlucha" in x.name:
            x.ability="Defiant"
            per=x.hp/x.maxhp
            x.weight=72.41
            x.hp=78
            x.atk=137
            x.defense=100
            x.spatk=74
            x.spdef=93
            x.speed=118
            x.sprite="https://i.postimg.cc/5ymd2MTt/mega-hawlucha.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Barbaracite" and "Barabaracle" in x.name:
            x.secondaryType="Fighting"
            per=x.hp/x.maxhp
            x.weight=72.41
            x.hp=72
            x.atk=140
            x.defense=130
            x.spatk=64
            x.spdef=106
            x.speed=88
            x.sprite="https://i.postimg.cc/8cPhJRct/mega-barbaracle.png"
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Gyaradosite" and "Gyarados" in x.name:
            x.secondaryType="Dark"
            x.ability="Mold Breaker"
            per=x.hp/x.maxhp
            x.weight=672.41
            x.hp=95
            x.atk=155
            x.defense=109
            x.spatk=130
            x.spdef=130
            x.speed=81
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Venusaurite" and "Venusaur" in x.name:
            if x.ability=="Chlorophyll":
                x.ability=="Big Leaves"
            else:
                x.ability="Thick Fat"
            x.weight=342.82
            per=x.hp/x.maxhp
            x.hp=80
            x.atk=100
            x.defense=123
            x.spatk=122
            x.spdef=120
            x.speed=80
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Charizardite X" and "Charizard" in x.name:
            x.ability="Tough Claws"
            x.secondaryType="Dragon"
            x.weight=243.61
            x.sprite=x.sprite.replace(".gif","-megax.gif")
            per=x.hp/x.maxhp
            x.hp=78
            x.atk=130
            x.defense=111
            x.spatk=130
            x.spdef=85
            x.speed=100
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Raichunite X" and "Raichu" in x.name:
            x.ability="Reckless"
            x.weight=243.61
            x.sprite="https://i.postimg.cc/FKjKFFkb/mega-raichu-x.png"
            per=x.hp/x.maxhp
            x.hp=60
            x.atk=130
            x.defense=85
            x.spatk=110
            x.spdef=95
            x.speed=150
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Raichunite Y" and "Raichu" in x.name:
            x.ability="Static"
            x.weight=243.61
            x.sprite="https://i.postimg.cc/hG9G44QV/mega-raichu-y.png"
            per=x.hp/x.maxhp
            x.hp=60
            x.atk=85
            x.defense=85
            x.spatk=155
            x.spdef=105
            x.speed=140
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Charizardite Y" and "Charizard" in x.name:
            x.ability="Drought"
            x.weight=221.56
            per=x.hp/x.maxhp
            x.sprite=x.sprite.replace(".gif","-megay.gif")
            x.hp=78
            x.atk=104
            x.defense=78
            x.spatk=159
            x.spdef=115
            x.speed=100
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Blastoisinite" and "Blastoise" in x.name:
            x.ability="Mega Launcher"
            x.secondaryType="Steel"
            x.weight=222.89
            per=x.hp/x.maxhp
            x.hp=79
            x.atk=103
            x.defense=120
            x.spatk=135
            x.spdef=115
            x.speed=78
            calcst(x)
            x.hp=x.maxhp*per    
        elif x.item=="Beedrillite" and "Beedrill" in x.name:
            x.ability="Adaptability"
            x.weight=89.29
            per=x.hp/x.maxhp
            x.hp=65
            x.atk=160
            x.defense=70
            x.spatk=15
            x.spdef=90
            x.speed=175
            calcst(x)
            x.hp=x.maxhp*per      
        elif x.item=="Pidgeotite" and "Pidgeot" in x.name:
            x.ability="No Guard"
            x.weight=111.33
            per=x.hp/x.maxhp
            x.hp=83
            x.atk=80
            x.defense=95
            x.spatk=135
            x.spdef=80
            x.speed=121
            calcst(x)
            x.hp=x.maxhp*per     
        elif x.item=="Alakazite" and "Alakazam" in x.name:
            x.ability="Trace"
            x.weight=105.82
            per=x.hp/x.maxhp
            x.hp=55
            x.atk=50
            x.defense=65
            x.spatk=175
            x.spdef=105
            x.speed=150
            calcst(x)
            x.hp=x.maxhp*per  
        elif x.item=="Slowbronite" and "Slowbro" in x.name:
            x.ability="Regenerator"
            x.weight=264.55
            per=x.hp/x.maxhp
            x.hp=95
            x.atk=75
            x.defense=180
            x.spatk=130
            x.spdef=80
            x.speed=30
            calcst(x)
            x.hp=x.maxhp*per 
        elif x.item=="Gengarite" and "Gengar" in x.name:
            x.ability="Shadow Tag"
            x.weight=89.29
            per=x.hp/x.maxhp
            x.hp=60
            x.atk=140
            x.defense=80
            x.spatk=170
            x.spdef=95
            x.speed=130
            calcst(x)
            x.hp=x.maxhp*per       
        elif x.item=="Kangaskhanite" and "Kangaskhan" in x.name:
            x.ability="Parental Bond"
            x.weight=220.46
            per=x.hp/x.maxhp
            x.hp=105
            x.atk=125
            x.defense=100
            x.spatk=60
            x.spdef=100
            x.speed=100
            calcst(x)
            x.hp=x.maxhp*per       
        elif x.item=="Pinsirite" and "Pinsir" in x.name:
            x.ability="Aerilate"
            x.secondaryType="Flying"
            x.weight=130.07
            per=x.hp/x.maxhp
            x.hp=65
            x.atk=155
            x.defense=130
            x.spatk=65
            x.spdef=90
            x.speed=105
            calcst(x)
            x.hp=x.maxhp*per         
        elif x.item=="Aerodactylite" and "Aerodactyl" in x.name:
            x.ability="Tough Claws"
            x.weight=174.17
            per=x.hp/x.maxhp
            x.hp=80
            x.atk=135
            x.defense=85
            x.spatk=70
            x.spdef=95
            x.speed=150
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Mewtwonite X" and "Mewtwo" in x.name:
            x.ability="Steadfast"
            x.secondaryType="Fighting"
            x.weight=279.99
            x.sprite=x.sprite.replace(".gif","-megax.gif")
            per=x.hp/x.maxhp
            x.hp=106
            x.atk=190
            x.defense=100
            x.spatk=154
            x.spdef=100
            x.speed=130
            calcst(x)
            x.hp=x.maxhp*per    
        elif x.item=="Mewtwonite Y" and "Mewtwo" in x.name:
            x.ability="Insomnia"
            x.sprite=x.sprite.replace(".gif","-megay.gif")
            x.weight=72.75
            per=x.hp/x.maxhp
            x.hp=106
            x.atk=150
            x.defense=70
            x.spatk=194
            x.spdef=120
            x.speed=140
            calcst(x)
            x.hp=x.maxhp*per     
        elif x.item=="Ampharosite":
            x.ability="Transistor"
            x.secondaryType="Dragon"
            x.weight=135.58
            per=x.hp/x.maxhp
            x.hp=110
            x.atk=95
            x.defense=105
            x.spatk=165
            x.spdef=110
            x.speed=45
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Steelixite":
            x.ability="Primal Armor"
            x.weight=1631.42
            per=x.hp/x.maxhp
            x.hp=75
            x.atk=145
            x.defense=230
            x.spatk=55
            x.spdef=105
            x.speed=20
            calcst(x)
            x.hp=x.maxhp*per   
        elif x.item=="Scizorite":
            x.ability="Technician"
            x.weight=275.58
            per=x.hp/x.maxhp
            x.hp=70
            x.atk=150
            x.defense=140
            x.spatk=65
            x.spdef=100
            x.speed=75
            calcst(x)
            x.hp=x.maxhp*per  
        elif x.item=="Heracronite":
            x.ability="Skill Link"
            x.weight=137.79
            per=x.hp/x.maxhp
            x.hp=80
            x.atk=185
            x.defense=115
            x.spatk=40
            x.spdef=105
            x.speed=75
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Houndoominite":
            x.ability="Solar Power"
            x.weight=109.13
            per=x.hp/x.maxhp
            x.hp=75
            x.atk=120
            x.defense=90
            x.spatk=140
            x.spdef=90
            x.speed=115
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Tyranitarite":
            x.ability="Primal Armor"
            x.weight=562.18
            per=x.hp/x.maxhp
            x.hp=100
            x.atk=164
            x.defense=150
            x.spatk=95
            x.spdef=120
            x.speed=71
            calcst(x)
            x.hp=x.maxhp*per    
        elif x.item=="Sceptilite":
            x.ability="Technician"
            x.secondaryType="Dragon"
            x.weight=121.7
            per=x.hp/x.maxhp
            x.hp=70
            x.atk=145
            x.defense=75
            x.spatk=110
            x.spdef=85
            x.speed=145
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Blazikenite":
            x.ability="Speed Boost"
            x.weight=114.64
            per=x.hp/x.maxhp
            x.hp=80
            x.atk=160
            x.defense=80
            x.spatk=130
            x.spdef=80
            x.speed=100
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Swampertite":
            x.ability="Swift Swim"
            x.weight=224.87
            per=x.hp/x.maxhp
            x.hp=100
            x.atk=150
            x.defense=110
            x.spatk=95
            x.spdef=110
            x.speed=70
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Gardevoirite":
            x.ability="Pixilate"
            x.weight=106.7
            per=x.hp/x.maxhp
            x.hp=68
            x.atk=85
            x.defense=80
            x.spatk=165
            x.spdef=135
            x.speed=100
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Sablenite":
            x.ability="Magic Bounce"
            x.weight=354.94
            per=x.hp/x.maxhp
            x.hp=70
            x.atk=85
            x.defense=130
            x.spatk=85
            x.spdef=120
            x.speed=20
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Mawilite":
            x.ability="Huge Power"
            x.weight=51.81
            per=x.hp/x.maxhp
            x.hp=70
            x.atk=105
            x.defense=130
            x.spatk=55
            x.spdef=100
            x.speed=50
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Aggronite":
            x.ability="Primal Armor"
            x.secondaryType="None"
            x.weight=870.83
            per=x.hp/x.maxhp
            x.hp=70
            x.atk=140
            x.defense=230
            x.spatk=60
            x.spdef=80
            x.speed=50
            calcst(x)
            x.hp=x.maxhp*per    
        elif x.item=="Medichamite":
            x.ability="Pure Power"
            x.weight=69.45
            per=x.hp/x.maxhp
            x.hp=60
            x.atk=100
            x.defense=85
            x.spatk=80
            x.spdef=85
            x.speed=100
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Manectite":
            x.ability="Intimidate"
            x.weight=97
            per=x.hp/x.maxhp
            x.hp=70
            x.atk=110
            x.defense=90
            x.spatk=135
            x.spdef=90
            x.speed=135
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Sharpedonite":
            x.ability="Strong Jaw"
            x.weight=287.26
            per=x.hp/x.maxhp
            x.hp=70
            x.atk=150
            x.defense=70
            x.spatk=120
            x.spdef=65
            x.speed=115
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Camerupite":
            x.ability="Drought"
            x.weight=706.58
            per=x.hp/x.maxhp
            x.hp=90
            x.atk=100
            x.defense=110
            x.spatk=145
            x.spdef=115
            x.speed=20
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Altarianite":
            x.ability="Pixilate"
            x.secondaryType="Fairy"
            x.weight=45.42
            per=x.hp/x.maxhp
            x.hp=85
            x.atk=110
            x.defense=110
            x.spatk=110
            x.spdef=105
            x.speed=100
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Banettite":
            x.ability="Prankster"
            x.secondaryType="Normal"
            x.weight=28.66
            per=x.hp/x.maxhp
            x.hp=84
            x.atk=165
            x.defense=105
            x.spatk=75
            x.spdef=103
            x.speed=103
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Absolite":
            x.ability="Dark Aura"
            x.secondaryType="Fairy"
            x.weight=108.03
            per=x.hp/x.maxhp
            x.hp=65
            x.atk=160
            x.defense=60
            x.spatk=125
            x.spdef=60
            x.speed=115
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Glalitite":
            x.ability="Refrigerate"
            x.weight=772.06
            per=x.hp/x.maxhp
            x.hp=80
            x.atk=135
            x.defense=80
            x.spatk=105
            x.spdef=80
            x.speed=110
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Salamencite":
            x.ability="Aerilate"
            x.weight=248.24
            per=x.hp/x.maxhp
            x.hp=95
            x.atk=145
            x.defense=130
            x.spatk=120
            x.spdef=90
            x.speed=120
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Metagrossite":
            x.ability="Tough Claws"
            x.weight=2078.74
            per=x.hp/x.maxhp
            x.hp=80
            x.atk=145
            x.defense=150
            x.spatk=105
            x.spdef=110
            x.speed=110
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Latiasite":
            per=x.hp/x.maxhp
            x.weight=114.64
            x.hp=80
            x.atk=100
            x.defense=120
            x.spatk=140
            x.spdef=150
            x.speed=110
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Latiosite":
            per=x.hp/x.maxhp
            x.weight=154.32
            x.hp=80
            x.atk=139
            x.defense=100
            x.spatk=160
            x.spdef=120
            x.speed=110
            calcst(x)
            x.hp=x.maxhp*per
        elif "Dragon Ascent" in x.moves:
            x.ability="Delta Stream"
            per=x.hp/x.maxhp
            x.weight=864.21
            x.hp=105
            x.atk=180
            x.defense=100
            x.spatk=180
            x.spdef=100
            x.speed=115
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Garchompite":
            x.ability="Sand Force"
            x.weight=209.44
            per=x.hp/x.maxhp
            x.hp=108
            x.atk=170
            x.defense=110
            x.spatk=120
            x.spdef=90
            x.speed=102
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Lucarionite":
            x.ability="Adaptability"
            x.weight=126.77
            per=x.hp/x.maxhp
            x.hp=70
            x.atk=145
            x.defense=88
            x.spatk=140
            x.spdef=70
            x.speed=112
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Abomasite":
            x.ability="Slush Rush"
            x.weight=407.86
            per=x.hp/x.maxhp
            x.hp=90
            x.atk=142
            x.defense=105
            x.spatk=142
            x.spdef=105
            x.speed=60
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Lopunnite":
            x.ability="Scrappy"
            per=x.hp/x.maxhp
            x.weight=62.9
            x.hp=80
            x.atk=146
            x.defense=74
            x.spatk=64
            x.spdef=96
            x.speed=135
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Galladite":
            x.ability="Sharpness"
            x.weight=124.34
            per=x.hp/x.maxhp
            x.hp=68
            x.atk=155
            x.defense=95
            x.spatk=65
            x.spdef=125
            x.speed=115
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Audinite":
            x.ability="Regenerator"
            x.secondaryType="Fairy"
            color="yellow"
            x.weight=70.55
            per=x.hp/x.maxhp
            x.hp=103
            x.atk=60
            x.defense=126
            x.spatk=120
            x.spdef=126
            x.speed=50
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Diancite":
            x.ability="Magic Bounce"
            x.weight=61.29
            per=x.hp/x.maxhp
            x.hp=50
            x.atk=160
            x.defense=110
            x.spatk=160
            x.spdef=110
            x.speed=110
            calcst(x)
            x.hp=x.maxhp*per
        elif x.item=="Poliwrathite":
            x.ability="No Guard"
            x.weight=61.29
            per=x.hp/x.maxhp
            x.hp=90
            x.atk=155
            x.defense=120
            x.spatk=70
            x.spdef=105
            x.speed=70
            calcst(x)
            x.hp=x.maxhp*per      
            x.sprite="https://cdn.discordapp.com/attachments/1102579499989745764/1148175796431753216/20230904_144035.png"
        em.set_image(url=x.sprite)            
        await entryeff(ctx,x,y,tr1,tr2,field,turn)
    return x,em                                           


async def faint(ctx, bot, x, y, tr1, tr2, field, turn):
    
    # Initialize the primary log embed for Dynamax End / Standard Faint
    # We set a placeholder embed, its contents will be determined later.
    em = discord.Embed(color=discord.Color.default()) 
    
    # 1. Dynamax End Check (Occurs regardless of HP, based on turn count)
    if x.dmax == True and turn >= x.maxend:
        x.dmax = False
        x.gsprite = "None"
        # Revert HP and Max HP from the +50% Dynamax state back to base stats.
        # Note: Your code *halves* current and max HP, which is unusual for Dynamax end, 
        # but kept here to match your original structure.
        x.hp = round(x.hp / 2)
        x.maxhp = round(x.maxhp / 2)
        
        # Build the Dynamax end message onto the initialized 'em'
        em.add_field(name="Dynamax End:", value=f"{x.name} returned to it's normal state!")
        x.nickname = x.nickname.replace(" <:dynamax:1104646304904257647>", "")
        if "gmax" in x.sprite:
            x.sprite = x.sprite.replace("-gmax.gif", ".gif")
    
    # Check for faint/revival abilities. These are major events that send their own message.
    # They use 'elif' because a Pokemon can only have one ability.
    
    # 2. Eternamax
    if x.hp <= 0 and x.ability == "Eternamax":
        x.ability = "Levitate"
        x.name = "Eternamax Eternatus"
        x.sprite = "https://cdn.discordapp.com/attachments/1102579499989745764/1142037644470124656/image0.gif"
        x.weight = 9999.99
        x.hp = 255
        x.atk = 115
        x.defense = 250
        x.spatk = 125
        x.spdef = 250
        x.speed = 130
        calcst(x)    
        x.hp = x.maxhp
        
        # Dedicated embed for the transformation
        em_eternamax = discord.Embed(title="Eternatus's Eternamax!", description="Eternamax Eternamaxed itself and regained its true form.", color=0x8fd5f7)
        em_eternamax.set_thumbnail(url="https://cdn.discordapp.com/attachments/1102579499989745764/1106824399983751248/Dynamax.png")
        em_eternamax.set_image(url="https://cdn.discordapp.com/attachments/1102579499989745764/1142037751101915207/image0.gif")
        await ctx.send(embed=em_eternamax)
        return x # Pokemon revived, exit faint check

    # 3. Therian Reincarnation (Thundurus)
    elif x.hp <= 0 and x.ability == "Therian Reincarnation" and x.name == "Thundurus":
        x.dmax = False
        x.name = "Therian Thundurus"
        x.ability = "Volt Absorb"
        x.sprite = "http://play.pokemonshowdown.com/sprites/ani/thundurus-therian.gif"
        x.weight = 134.48
        x.hp = 79
        x.atk = 105
        x.defense = 70
        x.spatk = 145
        x.spdef = 80
        x.speed = 101
        calcst(x)    
        x.hp = x.maxhp
        
        em_therian = discord.Embed(title="Thundurus's Therian Reincarnation!", description="Thundurus transformed into it's therian forme after touching its <:revealglass:1140992335593885746> Reveal Glass.", color=0x8fd5f7)
        await atkchange(em_therian, x, x, 1)
        await defchange(em_therian, x, x, 1)
        await spatkchange(em_therian, x, x, 1)
        await spdefchange(em_therian, x, x, 1)
        await speedchange(em_therian, x, x, 1)
        em_therian.set_image(url=x.sprite)
        await ctx.send(embed=em_therian)
        return x # Pokemon revived, exit faint check

    # 4. Therian Reincarnation (Enamorus)
    elif x.hp <= 0 and x.ability == "Therian Reincarnation" and x.name == "Enamorus":
        x.dmax = False
        x.name = "Therian Enamorus"
        x.ability = "Overcoat"
        x.sprite = "https://cdn.discordapp.com/attachments/1102535204968599592/1141004828911353967/image_search_1692107000875.gif"
        x.weight = 105.8
        x.hp = 74
        x.atk = 115
        x.defense = 110
        x.spatk = 135
        x.spdef = 100
        x.speed = 46
        calcst(x)    
        x.hp = x.maxhp
        
        em_therian = discord.Embed(title="Enamorus's Therian Reincarnation!", description="Enamorus transformed into it's therian forme after touching its <:revealglass:1140992335593885746> Reveal Glass.", color=0xe9749c)
        await atkchange(em_therian, x, x, 1)
        await defchange(em_therian, x, x, 1)
        await spatkchange(em_therian, x, x, 1)
        await spdefchange(em_therian, x, x, 1)
        await speedchange(em_therian, x, x, 1)
        em_therian.set_image(url=x.sprite)
        await ctx.send(embed=em_therian) 
        return x # Pokemon revived, exit faint check
    
    # 5. Therian Reincarnation (Tornadus)
    elif x.hp <= 0 and x.ability == "Therian Reincarnation" and x.name == "Tornadus":
        x.dmax = False
        x.name = "Therian Tornadus"
        x.ability = "Regenerator"
        x.sprite = "http://play.pokemonshowdown.com/sprites/ani/tornadus-therian.gif"
        x.weight = 138.89
        x.hp = 79
        x.atk = 100
        x.defense = 80
        x.spatk = 110
        x.spdef = 90
        x.speed = 121
        calcst(x)    
        x.hp = x.maxhp
        
        em_therian = discord.Embed(title="Tornadus's Therian Reincarnation!", description="Tornadus transformed into it's therian forme after touching its <:revealglass:1140992335593885746> Reveal Glass.", color=0x78b867)
        await atkchange(em_therian, x, x, 1)
        await defchange(em_therian, x, x, 1)
        await spatkchange(em_therian, x, x, 1)
        await spdefchange(em_therian, x, x, 1)
        await speedchange(em_therian, x, x, 1)
        em_therian.set_image(url=x.sprite)
        await ctx.send(embed=em_therian) 
        return x # Pokemon revived, exit faint check
        
    # 6. Therian Reincarnation (Landorus)
    elif x.hp <= 0 and x.ability == "Therian Reincarnation" and x.name == "Landorus":
        x.dmax = False
        x.name = "Therian Landorus"
        x.ability = "Intimidate"
        x.sprite = "http://play.pokemonshowdown.com/sprites/ani/landorus-therian.gif"
        x.weight = 149.91
        x.hp = 89
        x.atk = 145
        x.defense = 90
        x.spatk = 105
        x.spdef = 80
        x.speed = 91
        calcst(x)    
        x.hp = x.maxhp
        
        em_therian = discord.Embed(title="Landorus's Therian Reincarnation!", description="Landorus transformed into it's therian forme after touching its <:revealglass:1140992335593885746> Reveal Glass.", color=0xfea458)
        await atkchange(em_therian, x, x, 1)
        await defchange(em_therian, x, x, 1)
        await spatkchange(em_therian, x, x, 1)
        await spdefchange(em_therian, x, x, 1)
        await speedchange(em_therian, x, x, 1)
        em_therian.set_image(url=x.sprite)
        await ctx.send(embed=em_therian)
        return x # Pokemon revived, exit faint check
        
    # 7. Mirage Metamorphosis (Hoopa)
    elif x.hp <= 0 and x.ability == "Mirage Metamorphosis":
        x.dmax = False
        x.name = "Hoopa Unbound"
        x.ability = "Magician"
        x.sprite = "http://play.pokemonshowdown.com/sprites/ani/hoopa-unbound.gif"
        x.weight = 1080.27
        x.hp = 80
        x.atk = 160
        x.defense = 60
        x.spatk = 170
        x.spdef = 130
        x.speed = 80
        calcst(x)    
        x.hp = x.maxhp
        
        em_hoopa = discord.Embed(title="Hoopa's Mirage Metamorphosis!", description="Hoopa transformed into it's unbound forme after absorbing its lost power from the <:prisonbottle:1138429051929907390> Prison Bottle.", color=0xab427a)
        await atkchange(em_hoopa, x, x, 1)
        await defchange(em_hoopa, x, x, 1)
        await spatkchange(em_hoopa, x, x, 1)
        await spdefchange(em_hoopa, x, x, 1)
        await speedchange(em_hoopa, x, x, 1)
        em_hoopa.set_image(url=x.sprite)
        await ctx.send(embed=em_hoopa)
        return x # Pokemon revived, exit faint check
        
    # 8. Distorted Resurgence (Giratina)
    elif x.hp <= 0 and x.ability == "Distorted Resurgence":
        x.dmax = False
        x.name = "Origin Giratina"
        x.ability = "Levitate"
        x.sprite = "http://play.pokemonshowdown.com/sprites/ani/giratina-origin.gif"
        x.weight = 1433
        x.hp = 150
        x.atk = 120
        x.defense = 100
        x.spatk = 120
        x.spdef = 100
        x.speed = 90
        calcst(x)    
        x.hp = x.maxhp
        
        em_giratina = discord.Embed(title="Giratina's Distorted Resurgence!", description="Giratina transformed into it's origin forme after falling to the abyss.", color=0xfcf491)
        await atkchange(em_giratina, x, x, 1)
        await defchange(em_giratina, x, x, 1)
        await spatkchange(em_giratina, x, x, 1)
        await spdefchange(em_giratina, x, x, 1)
        await speedchange(em_giratina, x, x, 1)
        em_giratina.set_image(url=x.sprite)
        await ctx.send(embed=em_giratina)
        return x # Pokemon revived, exit faint check
        
    # 9. Standard Faint Logic
    elif x.hp <= 0:
        x.status = "Fainted"
        
        # Re-define 'em' for the standard faint message
        em = discord.Embed(title=f"{x.name} fainted!")
        em.set_image(url=x.sprite)

        tr1.sparty = await spartyup(tr1, x)
        
        # Mega Evolution Reversion
        if " <:megaevolve:1104646688951500850>" in x.name and x.name not in ["Charizard", "Mewtwo"]:
            x.sprite = x.sprite.replace("-mega", "")
            x.nickname = x.nickname.replace(" <:megaevolve:1104646688951500850>", "")
        elif " <:megaevolve:1104646688951500850>" in x.name and x.name in ["Charizard", "Mewtwo"]:
            x.sprite = x.sprite.replace("-megax", "")
            x.sprite = x.sprite.replace("-megay", "")
            x.nickname = x.nickname.replace(" <:megaevolve:1104646688951500850>", "")
        
        # Opponent's Ability Checks (y)
        if y.ability in ["Moxie", "Chilling Neigh"]:
            em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!", value=f"Knocking Out {x.name} made {y.name} go on a rampage!")
            await atkchange(em, y, y, 1)
        elif y.ability in ["Soul-Heart", "Grim Neigh"]:
            em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!", value=f"Knocking Out {x.name} made {y.name} go on a rampage!")
            await spatkchange(em, y, y, 1)
        elif y.ability == "As One":
            if "Shadow" in y.name:
                await spatkchange(em, y, y, 1)
            elif "Ice" in y.name:
                await atkchange(em, y, y, 1)
        elif y.ability == "Beast Boost":
            em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!", value=f"Knocking Out {x.name} made {y.name} go on a rampage!")
            # Determine highest stat to boost
            # Note: The way 'm' is defined and then using 'pp' as a variable name is confusing, 
            # but kept here to match your original variable use.
            m = [y.atk, y.defense, y.spatk, y.spdef, y.speed]
            if tr2.reflect == True:
                # The division by 2 here is likely wrong; this should be based on base stats or stage, 
                # but kept to match your original logic.
                m = [y.atk, y.defense / 2, y.spatk, y.spdef, y.speed]
            if tr2.lightscreen == True:
                m = [y.atk, y.defense, y.spatk, y.spdef / 2, y.speed]
                
            pp = max(m)
            # Find the stat that matches the maximum value and boost it
            if pp == y.atk:
                await atkchange(em, y, y, 1)
            elif pp == y.defense:
                await defchange(em, y, y, 1)
            elif pp == y.spatk:
                await spatkchange(em, y, y, 1)
            elif pp == y.spdef:
                await spdefchange(em, y, y, 1)
            elif pp == y.speed:
                await speedchange(em, y, y, 1)
                
        # Battle Bond Transformation
        elif y.ability == "Battle Bond" and "Ash" not in y.name:
            per = y.hp / y.maxhp
            y.weight = 88.18
            y.sprite = "http://play.pokemonshowdown.com/sprites/ani/greninja-ash.gif"
            y.name = "Ash Greninja"
            y.hp = 72
            y.atk = 145
            y.defense = 67
            y.spatk = 153
            y.spdef = 71
            y.speed = 132
            calcst(y)
            y.hp = y.maxhp * per
            
            bb = discord.Embed(title=f"{y.icon} {y.name}'s Battle Bond!", description=f"{y.name} transformed into Ash-Greninja!")
            bb.set_image(url="https://cdn.discordapp.com/attachments/1102579499989745764/1125023366278029402/image0.gif")
            await ctx.send(embed=bb)
            
        # Fainting Ability Damage/Heal
        if x.ability == "Aftermath":
            y.hp -= (y.maxhp / 4)
        if y.ability in ["Looter", "Predator", "Scavenger"]:
            y.hp += (y.maxhp / 4)  
            if y.hp > y.maxhp:
                y.hp = y.maxhp
                
        # Remove fainted Pokemon from team
        try:    
            tr1.faintedmon.append(x)
            tr1.pokemons.remove(x)
        except:
            pass  
            
        # Send faint message and handle switch
        if len(tr1.pokemons) == 0:
            await ctx.send(embed=em)
        if len(tr1.pokemons) != 0 and len(tr2.pokemons) != 0:
            await ctx.send(embed=em)
            x = await switch(ctx, bot, x, y, tr1, tr2, field, turn)
            
            # Loop check for immediate successive faints (e.g., from entry hazards on switch-in)
            while len(tr1.pokemons) > 1:
                if x.hp <= 0:
                    # Recursive call for a second faint
                    x = await faint(ctx, bot, x, y, tr1, tr2, field, turn)  
                    return x    
                if x.hp > 0:
                    return x  
            return x
            
    # Final return for cases where the loop finished or if only Dynamax End occurred
    return x               
async def addmoney(ctx,member,price):
    db=sqlite3.connect("playerdata.db")
    c=db.cursor()
    c.execute(f"select * from '{member.id}'")
    m=c.fetchone()
    money=m[0]+price
    try:
        if price<0 and member.id!=1084473178400755772:
            c.execute(f"select * from '1084473178400755772'")
            mow=c.fetchone()
            moey=mow[0]-price
            c.execute(f"update '1084473178400755772' set balance={moey}")
            db.commit()
    except:
        pass           
    c.execute(f"update '{member.id}' set balance={money}")
    db.commit()
    if price>0:
        pass
        #await ctx.send(f"{member.display_name} {await numberify(price)} <:pokecoin:1134595078892044369> added to your balance!")
    if price<0:
        price=-price
        #await ctx.send(f"{member.display_name} {await numberify(price)} <:pokecoin:1134595078892044369> was deducted from your balance!")
    await ctx.channel.send(f"{member.display_name}'s New Balance: {await numberify(money)}<:pokecoin:1134595078892044369>")
#freeze
async def freeze(em,x,y,ch):
    miss=100-ch
    if x.ability=="Serene Grace":
        miss/=2
    chance=random.randint(1,100)
    if y.name!="Substitute" and chance>=miss and "Ice" not in (y.secondaryType,y.primaryType,y.teraType) and y.ability not in ["Ice Body","Magic Bounce","Leaf Guard","Comatose","Ice Scales","Snow Cloak","Snow Warning"] and y.status=="Alive" and x.ability!="Sheer Force" and y.hp>0:
        if y.item!="Covert Cloak" or y.ability not in ["Shield Dust"]:
            y.status="Frozen"
            em.add_field(name="Status:",value=f"{y.name} is frozen solid!")
    if chance>=miss and y.status=="Frozen" and y.ability in ["Synchronize"] and x.status=="Alive":
        x.status="Frozen"
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} is frozen solid!")
    if chance>=miss and y.ability in ["Magic Bounce"] and x.status=="Alive" and y.status!="Frozen":
        x.status="Frozen"
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} is frozen solid!")
#burn
async def burn(em,x,y,ch):
    if x.ability=="Serene Grace":
        ch*=2
    elif x.ability=="Pyromancy":
        ch*=5
    miss=100-ch
    chance=random.randint(1,100)
    if y.name!="Substitute" and chance>=miss and "Fire" not in (y.secondaryType,y.primaryType,y.teraType) and y.ability not in ["Flash Fire","Magic Bounce","Leaf Guard","Comatose","Thermal Exchange","Magma Armor","Water Veil"] and y.status=="Alive" and x.ability!="Sheer Force" and y.hp>0:
        if y.item!="Covert Cloak" or y.ability not in ["Shield Dust"]:
            y.status="Burned"
            em.add_field(name="Status:",value=f"{y.name} was burned.")
    if chance>=miss and y.status=="Burned" and y.ability in ["Synchronize"] and x.status=="Alive":
        x.status="Burned"
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} was burned.")     
    if chance>=miss and y.ability in ["Magic Bounce"] and x.status=="Alive" and y.status!="Burned":
        x.status="Burned"
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} was burned.")            
#paralyze
async def paralyze(em,x,y,ch):
    miss=100-ch
    if x.ability=="Serene Grace":
        miss/=2
    chance=random.randint(1,100)
    if y.name!="Substitute" and chance>=miss and (((("Electric" not in (y.secondaryType,y.primaryType,y.teraType) and "Ground" not in (y.secondaryType,y.primaryType,y.teraType) or y.use in ["Body Slam","Force Plam","Glare","Lightning Rod","Volt Absorb","Juggernaut"] and y.ability not in ["Limber","Leaf Guard","Comatose","Magic Bounce"])) and y.status=="Alive" and x.ability!="Sheer Force") and y.hp>0):
        if y.item!="Covert Cloak" or y.ability not in ["Shield Dust"]:
            y.status="Paralyzed"
            em.add_field(name="Status:",value=f"{y.name} was paralyzed!")
    if chance>=miss and y.status=="Paralyzed" and y.ability in ["Synchronize"] and x.status=="Alive":
        x.status="Paralyzed"
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} was paralayzed.")     
    if chance>=miss and y.ability in ["Magic Bounce"] and x.status=="Alive" and y.status!="Paralyzed":
        x.status="Paralyzed"
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} was paralayzed.")       
#poison
async def poison(em,x,y,ch):
    miss=100-ch
    if x.ability=="Serene Grace":
        miss/=2
    chance=random.randint(1,100)
    if y.name!="Substitute" and (chance>=miss and ("Steel" not in (y.secondaryType,y.primaryType,y.teraType) and "Poison"  not in (y.secondaryType,y.primaryType,y.teraType) or x.ability=="Corrosion") and y.ability not in ["Immunity","Magic Bounce","Leaf Guard","Comatose","Pastel Veil"] and y.status=="Alive" and x.ability!="Sheer Force") and y.hp>0:
        if y.item!="Covert Cloak" or y.ability not in ["Shield Dust"]:
            y.status="Badly Poisoned"
            em.add_field(name="Status:",value=f"{y.name} was badly poisoned.")
    if chance>=miss and y.status=="Badly Poisoned" and y.ability in ["Synchronize"] and x.status=="Alive":
        x.status="Badly Poisoned"
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} was badly poisoned!")
    if chance>=miss and y.ability in ["Magic Bounce"] and x.status=="Alive" and y.status!="Badly Poisoned":
        x.status="Badly Poisoned"      
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} was badly poisoned!") 
#sleep
async def sleep(em,x,y,ch):
    miss=100-ch
    if x.ability=="Serene Grace":
        miss/=2
    chance=random.randint(1,100)
    if y.name!="Substitute" and chance>=miss and y.ability not in ["Magic Bounce","Leaf Guard","Comatose","Vital Spirit","Insomnia"] and y.status=="Alive" and x.ability!="Sheer Force" and y.hp>0:
        if y.item!="Covert Cloak" or y.ability not in ["Shield Dust"]:
            y.status="Sleep"
            em.add_field(name="Status:",value=f"{y.name} fell asleep!")
            if y.ability=="Early Bird":
                y.sleepturn=random.randint(2,3)
            elif y.ability!="Early Bird":
                y.sleepturn=random.randint(2,5)
    if chance>=miss and y.status=="Sleep" and y.ability in ["Synchronize"] and x.status=="Alive":
        x.status="Sleep"
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} fell asleep!")
        if x.ability=="Early Bird":
            x.sleepturn=random.randint(2,3)
        elif x.ability!="Early Bird":
            x.sleepturn=random.randint(2,5)   
    if chance>=miss and y.ability in ["Magic Bounce"] and x.status=="Alive" and y.status!="Sleep":
        x.status="Sleep"
        em.add_field(name=f"{y.icon} {y.name}'s {y.ability}!",value=f"{x.name} fell asleep!")
        if x.ability=="Early Bird":
            x.sleependturn=random.randint(2,3)
        elif x.ability!="Early Bird":
            x.sleependturn=random.randint(2,5)
#confusion
async def confuse(em,x,y,ch):
    miss=100-ch
    if x.ability=="Serene Grace":
        miss/=2
    chance=random.randint(1,100)
    if y.name!="Substitute" and chance>=miss and y.confused is False and x.ability!="Sheer Force" and y.ability not in ["Own Tempo"] and y.status!="Sleep":
        em.add_field(name="Status:",value=f"{y.name} became confused!")
        y.confused=True
        y.confuseendturn=random.randint(2,5)            
#flinch
async def flinch(em, x, y, ch):
    # Pokémon with Substitute cannot flinch, nor can a fainted Pokémon.
    if y.name == "Substitute" or y.hp <= 0:
        return
    # Calculate the flinch miss chance, accounting for Serene Grace.
    miss_chance = 100 - ch
    if x.ability == "Serene Grace":
        miss_chance /= 2
    # Check for abilities that prevent flinching.
    if y.ability in ["Inner Focus", "Shield Dust"]:
        return
    # Check for items that prevent flinching.
    if y.item == "Covert Cloak":
        return
    # A Pokémon with the Sheer Force ability cannot cause flinching.
    if x.ability == "Sheer Force":
        return
    # Roll the dice to see if the flinch succeeds.
    if random.randint(1, 100) > miss_chance:
        y.flinched = True  
                   
async def winner(ctx,tr1,tr2):
    if tr2.ai==False:
        await usagerecord(tr2.fullteam)
    if tr1.ai==False:
        db=sqlite3.connect("record.db")
        c=db.cursor()
        await usagerecord(tr1.fullteam)
        for i in tr1.fullteam:
            c.execute(f"select * from `pokemons` where name='{i.name}'")
            v=c.fetchone()
            c.execute(f"""Update `pokemons` set wins={v[5]+1} where name='{i.name}'""")
            db.commit()
    db=sqlite3.connect("playerdata.db")
    c=db.cursor()
    c.execute(f"select * from '{ctx.author.id}'")
    pl=c.fetchone()
    winner=tr1
    em=discord.Embed(title=f"{winner.name} won the battle!")
    em.set_image(url=tr1.sprite)
    if tr1.name!=ctx.author.display_name:
        c.execute(f"""Update `{ctx.author.id}` set winstreak=0""")
        db.commit()
    elif tr1.name==ctx.author.display_name:
        am=0
        streak=pl[4]+1
        c.execute(f"""Update `{ctx.author.id}` set winstreak={streak}""")
        db.commit()
        dt=sqlite3.connect("pokemondata.db")
        ct=dt.cursor()
        nm=tr2.name.split("> ")[-1]
        ct.execute(f"select * from 'Trainers' where name='{nm}'")
        bdg=ct.fetchone()
        if bdg!=None:
            if pl[6]=="None":
                c.execute(f"""Update `{ctx.author.id}`set badges='{bdg[1]}'""")
                em.add_field(name="1st badge obtained!",value=f"{bdg[2]} Congratulations! You received a {bdg[1]} from {tr2.name}.")
                db.commit()
            elif pl[6]!="None":
                if bdg[1] not in pl[6]:
                    new=pl[6]+","+bdg[1]
                    c.execute(f"""Update `{ctx.author.id}`set badges='{new}'""")
                    em.add_field(name="New badge obtained!",value=f"{bdg[2]} Congratulations! You received a {bdg[1]} from {tr2.name}.")
                    db.commit()
        if pl[5]<streak:
            c.execute(f"""Update `{ctx.author.id}` set highstreak={streak}""")
            db.commit()
        if "Pokemon Trainer" in tr2.name:
            am=1000
        elif "Gym Leader" in tr2.name:
            am=2000
        elif "Elite Four" in tr2.name:
            am=5000
        elif "Champion" in tr2.name:
            am=10000
        else:
             am=1000
        await addmoney(ctx,ctx.author,am)
    await ctx.send(embed=em)        
        
#Effects    
async def effects(ctx,x,y,tr1,field,turn):
    if 0 in x.pplist:
        if x.dmax is False and x.use in x.moves:
            x.lostmoves.append(x.moves[x.pplist.index(0)])
            x.moves.remove(x.moves[x.pplist.index(0)])
            x.pplist.remove(0) 
        elif x.dmax is True and x.use in x.maxmoves:
            x.moves.remove(x.moves[x.pplist.index(0)])
            x.maxmoves.remove(x.maxmoves[x.pplist.index(0)])
            x.pplist.remove(0) 
    em=discord.Embed(title="Effects:")
    x.flinched=False
    x.canfakeout=False
    if tr1.doom!=0 and tr1.doom==turn:
        em.add_field(name=f"Doom Desire:",value=f"{x.name} took the Doom Desire attack!")   
        x.hp-=tr1.ftmul
        tr1.doom=0
        tr1.ftmul=0
    if tr1.future!=0 and tr1.future==turn:
        em.add_field(name="Future Sight:",value=f"{x.name} took the Future Sight attack!")   
        x.hp-=tr1.ftmul
        tr1.future=0
        tr1.ftmul=0
    if x.yawn is not True and x.yawn=="Sleep" and x.status=="Alive" and field.terrain!="Electric":
        x.status="Sleep"
        x.sleependturn=random.randint(2,5)
        x.yawn=False
    if x.status!="Alive" and (x.ability in ["Purifying Salt","Good as Gold"] or field.terrain=="Misty"):
        x.status="Alive"   
        if x.ability in ["Purifying Salt","Good as Gold"]:
            x.showability=True
    if x.taunted==True:
        x.taunturn-=1
        if x.taunturn<=0:
            x.taunted=False
            em.add_field(name="Taunt:",value=f"{x.name} got rid of taunt.")
    if x.encore==True:
        x.encendturn-=1
        if encendturn<=0:
            x.encore=False
            em.add_field(name="Encore:",value=f"{x.name} got rid of encore.")
    if field.trickroom is True:
        if turn==field.troomendturn:
            field.trickroom=False
            em.add_field(name=f"Trick Room:",value="The dimensions returned to normal!")         
    if tr1.auroraveil is True:
        if turn==tr1.avendturn:
            tr1.auroraveil=False
            em.add_field(name=f"Aurora Veil:",value="The Aurora Veil wore off!") 
    if tr1.tailwind is True:        
        if turn==tr1.twendturn:
            tr1.tailwind=False
            em.add_field(name="Tailwind:",value="The Tailwind petered out!")
    if tr1.reflect is True:
        if turn==tr1.rfendturn:
            tr1.reflect=False
            em.add_field(name=f"Reflect:",value="The Reflect wore off!")
    if tr1.lightscreen is True:
        if turn==tr1.screenend:
            tr1.lightscreen=False
            em.add_field(name=f"Light Screen:",value="The Light Screen wore off!")
    if field.terrain=="Misty":
        if turn>=field.misendturn:
            em.add_field(name="Terrain:",value="The battlefield turned normal.")
            field.terrain="Normal"
    elif field.terrain=="Psychic":
        if turn>=field.psyendturn:
            em.add_field(name="Terrain:",value="The battlefield turned normal.")
            field.terrain="Normal"
    elif field.terrain=="Electric":
        if turn>=field.eleendturn:
            em.add_field(name="Terrain:",value="The battlefield turned normal.")
            field.terrain="Normal"
    elif field.terrain=="Grassy":
        if turn>=field.grassendturn:
            em.add_field(name="Terrain:",value="The battlefield turned normal.")
            field.terrain="Normal"
    if field.weather=="Snowstorm":
        if turn>=field.snowendturn:
            em.add_field(name="Weather:",value="The snowstorm stopped.")
            field.weather="Cloudy"            
    elif field.weather=="Hail":
        if turn>=field.hailendturn:
            em.add_field(name="Weather:",value="The hail stopped.")
            field.weather="Cloudy"
    elif field.weather=="Sandstorm":
        if turn>=field.sandendturn:
            em.add_field(name="Weather:",value="The sandstorm subsided.")
            field.weather="Clear"
    elif field.weather=="Sunny":
        if turn>=field.sunendturn:
            em.add_field(name="Weather:",value="The harsh sunlight faded.")
            field.weather="Clear"
    elif field.weather=="Rainy":
        if turn>=field.rainendturn:
            em.add_field(name="Weather:",value="The rain stopped.")
            field.weather="Cloudy"        
    elif field.weather=="Heavy Rain" and "Primordial Sea" not in (x.ability,y.ability) and "Marine" not in field.location:
        field.weather="Clear"
        em.add_field(name="Weather:",value="The heavy rainfall stopped.")
    elif field.weather=="Extreme Sunlight" and "Desolate Land" not in (x.ability,y.ability) and "Terra" not in field.location:
        field.weather="Clear"
        em.add_field(name="Weather:",value="The extreme sunlight fade away.")          
    #Dynamax Reset
    if x.dmax==True and turn>=x.maxend:
        x.dmax=False
        x.gsprite="None"
        x.hp=round(x.hp/2)
        x.maxhp=round(x.maxhp/2)
        em.add_field(name="Dynamax End:",value=f"{x.name} returned to it's normal state!")
        x.nickname=x.nickname.replace(" <:dynamax:1104646304904257647>","")
        if "gmax" in x.sprite:
            x.sprite=x.sprite.replace("-gmax.gif",".gif")
    if x.fmove==True:
        x.fmoveturn-=1
        if x.fmoveturn==0:
            x.fmove=False
            await confuse(em,x,x,100)            
    #Perish            
    if x.perishturn!=0:
        x.perishturn-=1
        em.add_field(name="Perish Count:",value=f"{x.icon} {x.name}'s perish count fell to {x.perishturn}!")
        if x.perishturn==0:
            x.hp=0
            em.add_field(name="Perish End:",value=f"{x.name} perished away!")    
    #Flame Orb            
    if x.item=="Flame Orb" and x.status=="Alive" and x.hp>0:
        x.status="Burned"
        em.add_field(name=f"{x.icon} {x.name}'s {await itemicon(x.item)} {x.item}!",value=f"{x.name} was burned by its {x.item}!")
    #Toxic Orb        
    elif x.item=="Toxic Orb" and x.status=="Alive" and x.hp>0:
        x.status="Badly Poisoned"
        em.add_field(name=f"{x.icon} {x.name}'s {await itemicon(x.item)} {x.item}!",value=f"{x.name} was badly poisoned by its {x.item}!")          
    #BAD DREAMS
    if y!= None and y.ability == "Bad Dreams" and x.status == "Sleep" and x.hp > 0:
        y.showability=True
        dmg=round(x.maxhp/8)
        if dmg<1:
            dmg=1
        x.hp-=dmg
        em.add_field(name="{y.icon} {y.name}'s Bad Dreams!",value=f"{x.name} is tormented.")
    #LEECH SEED
    if x.seeded==True and x.hp>0 and y.hp>0:
        em.add_field(name="Leech Seed:",value=f"The opposing {x.icon} {x.name}'s health is sapped by leech seed!")
        dmg=round(x.maxhp/16)
        if dmg<1:
            dmg=1
        x.hp-=dmg
        if y.hp<=(y.maxhp-y.maxhp/16):
            y.hp+=round(y.maxhp/16)    
    #HAIL DAMAGE
    if field.weather=="Hail" and x.ability not in ["Snow Cloak","Ice Body","Overcoat","Slush Rush"] and x.item!="Safety Googles" and x.hp>0:     
        if x.primaryType!="Ice" and x.secondaryType!="Ice" and x.teraType!="Ice" and x.ability!="Magic Guard":
            dmg=round(x.maxhp/16)
            if dmg<1:
                dmg=1
            x.hp-=dmg
            em.add_field(name="<:hail:1141090300501176511> Hail:",value=f"{x.name} is pelted by the hail!")      
    #SAND DAMAGE
    elif field.weather =="Sandstorm" and x.ability not in ["Sand Veil","Sand Force","Overcoat","Sand Rush"] and x.item!="Safety Googles" and x.hp>0:
        if x.primaryType not in ["Rock","Ground","Steel"] and x.secondaryType not in ["Rock","Ground","Steel"] and x.teraType not in ["Rock","Ground","Steel"] and x.ability!="Magic Guard":
            dmg=round(x.maxhp/8)
            if dmg<1:
                dmg=1
            x.hp-=dmg
            em.add_field(name="<:sandstorm:1141088700047048744> Sandstorm:",value=f"{x.name} is buffeted by the sandstorm!")
    if x.gravendturn==turn:
        x.grav=False
    if x.vlendturn==turn:
        x.vldmg=False
    if x.cntendturn==turn:
        x.cntdmg=False
    if x.cnendturn==turn:
        x.cndmg=False
    if x.wfendturn==turn:
        x.wfdmg=False
    if x.magmaendturn==turn:
        x.magmadmg=False
    #Badly Poisoned            
    if x.status=="Badly Poisoned" and x.ability not in ["Magic Guard","Poison Heal","Toxic Boost","Immunity"] and x.hp>0:
        x.hp-=(1+(x.maxhp*x.toxicCounter/16))
        x.toxicCounter+=1
        em.add_field(name="<:poisoned:1140745045805379604> Badly Poisoned:",value=f"{x.name} was hurt by fatal poison!")
    #Burned        
    if x.status=="Burned" and x.ability!="Magic Guard" and x.hp>0:
        em.add_field(name="<:burned:1140744974514782369> Burn:",value=f"{x.name} was hurt by burn!")
        dmg=round(x.maxhp/16)
        if dmg<1:
            dmg=1
        x.hp-=dmg
    #poisoned
    if x.status=="Poisoned" and x.ability!="Magic Guard" and x.hp>0:
        em.add_field(name="<:poisoned:1140745045805379604> Poisoned:",value=f"{x.name} was hurt by poison!")
        dmg=round(x.maxhp/8)
        if dmg<1:
            dmg=1
        x.hp-=dmg
    #Infestation end       
    if x.infestation==turn or (x.infestation!=False and "Infestation" not in y.moves):
        x.infestation=False
        em.add_field(name="Infestation:",value=f"{x.name} is freed from the infestation.")        
    #Sand Tomb free        
    if x.sandtomb==turn or (x.sandtomb!=False and "Sand Tomb" not in y.moves):
        x.sandtomb=False
        em.add_field(name="Sand Tomb:",value=f"{x.name} is freed from the sand tomb.")
    #Whirlpool free       
    if x.whirlpool==turn or (x.whirlpool!=False and "Whirlpool" not in y.moves):
        x.whirlpool=False
        em.add_field(name="Whirlpool:",value=f"{x.name} is freed from the whirlpool.")
    #Fire spin free        
    if x.firespin==turn or (x.firespin!=False and "Fire Spin" not in y.moves):
        x.firespin=False
        em.add_field(name="Fire Spin:",value=f"{x.name} is freed from the vortex of fire.")  
    if x.syrup!=False:
        x.syrup-=1
        await speedchange(em,x,x,-1)
        if x.syrup<=0:
            x.syrup=False              
    #Speed Boost        
    if x.ability=="Speed Boost" and x.hp>0:
        await speedchange(em,x,y,1)       
        x.showability=True 
    #Trap damage        
    if x.wfdmg==True and x.hp>0 and x.ability!="Magic Guard":
        em.add_field(name="G-Max Wildfire:",value=f"{x.name} is hurt by G-Max Wildlife’s flames!")
        dmg=round(x.maxhp/6)
        if dmg<1:
            dmg=1
        x.hp-=dmg
    if tr1.vcdmg==True and x.hp>0 and x.ability!="Magic Guard":
        em.add_field(name="G-Max Volcalith:",value=f"{x.name} is hurt by the rocks thrown out by G-Max Volcalith!")
        dmg=round(x.maxhp/6)
        if dmg<1:
            dmg=1
        x.hp-=dmg      
    if x.vldmg==True and x.hp>0 and x.ability!="Magic Guard":
        em.add_field(name="G-Max Vine Lash:",value=f"{x.name} is hurt by G-Max Vine Lash’s ferocious beating!")
        dmg=round(x.maxhp/6)
        if dmg<1:
            dmg=1
        x.hp-=dmg
    if x.cntdmg==True and x.hp>0 and x.ability!="Magic Guard":
        em.add_field(name="G-Max Centiferno:",value=f"{x.name} is hurt by G-Max Centiferno’s vortex!")
        dmg=round(x.maxhp/6)
        if dmg<1:
            dmg=1
        x.hp-=dmg
    if x.cndmg==True and x.hp>0 and x.ability!="Magic Guard":
        em.add_field(name="G-Max Cannonade:",value=f"{x.name} is hurt by G-Max Cannonade’s vortex!")
        dmg=round(x.maxhp/6)
        if dmg<1:
            dmg=1
        x.hp-=dmg
    if x.magmadmg==True and x.hp>0 and "Magma Storm" in y.moves and x.ability!="Magic Guard":
        em.add_field(name="Magma Storm:",value=f"{x.name} was hurt by Magma Storm!")
        if y.item!="Binding Band":
            dmg=round(x.maxhp/8)
            if dmg<1:
                dmg=1
            x.hp-=dmg
        elif y.item=="Binding Band":
            dmg=round(x.maxhp/6)
            if dmg<1:
                dmg=1
            x.hp-=dmg           
    if x.salty==True and x.hp>0 and x.ability!="Magic Guard":      
        em.add_field(name="Salt Cure:",value=f"{x.name} is hurt by the salt cure!")
        if "Steel" in (x.primaryType,x.secondaryType,x.teraType) or "Water" in (x.primaryType,x.secondaryType,x.teraType):
            x.hp-=(x.maxhp/4)
        else:
            x.hp-=(x.maxhp/8)
    if x.infestation!=0 and x.hp>0 and x.ability!="Magic Guard":
        em.add_field(name="Infestation:",value=f"{x.name} is hurt by the infestation!")
        dmg=round(x.maxhp/16)
        if dmg<1:
            dmg=1
        x.hp-=dmg 
    if x.sandtomb!=0 and x.hp>0 and x.ability!="Magic Guard":
        em.add_field(name="Sand Tomb:",value=f"{x.name} is hurt by the sand tomb!")
        dmg=round(x.maxhp/16)
        if dmg<1:
            dmg=1
        x.hp-=dmg  
    if x.whirlpool!=0 and x.hp>0 and x.ability!="Magic Guard":
        em.add_field(name="Whirlpool:",value=f"{x.name} is hurt by the whirlpool!")
        dmg=round(x.maxhp/16)
        if dmg<1:
            dmg=1
        x.hp-=dmg
    if x.firespin!=0 and x.hp>0 and x.ability!="Magic Guard":
        em.add_field(name="Fire Spin:",value=f"{x.name} is hurt by the vortex of fire!")
        dmg=round(x.maxhp/16)
        if dmg<1:
            dmg=1
        x.hp-=dmg
    if tr1.wishhp!=False:
        if isinstance(tr1.wishhp,str):
            tr1.wishhp=int(tr1.wishhp)
        else:
            x.hp+=tr1.wishhp
            tr1.wishhp=False
            em.add_field(name="Wish:",value=f"{x.name}'s wish came true!")
            if x.hp>x.maxhp:
                x.hp=x.maxhp
    #Leftovers       
    if x.hp>0 and x.hp<x.maxhp and x.item=="Leftovers":
        em.add_field(name=f"{x.icon} {x.name}'s {await itemicon(x.item)} {x.item}!",value=f"{x.name} restored a little HP using its Leftovers.")
        x.showitem=True
        x.hp+=round(x.maxhp/16) 
        if x.hp>x.maxhp:
            x.hp=x.maxhp
    #Ice Body
    if x.hp>0 and x.hp<x.maxhp and field.weather in ["Snowstorm","Hail"] and x.ability=="Ice Body":
        em.add_field(name=f"<:snowstorm:1141089242731266180> {x.icon} {x.name}'s Ice Body!",value=f"{x.name} restored a little HP using its Ice Body.")
        x.showability=True
        x.hp+=round(x.maxhp/8)    
        if x.hp>x.maxhp:
            x.hp=x.maxhp     
    #Poison Heal
    if x.hp>0 and x.hp<x.maxhp and x.ability=="Poison Heal" and "Poisoned" in x.status:
        em.add_field(name=f"{x.icon} {x.name}'s Poison Heal!",value=f"{x.name} restored a little HP using its Poison Heal.")
        x.showability=True
        x.hp+=round(x.maxhp/8)       
        if x.hp>x.maxhp:
            x.hp=x.maxhp 
    #Black Sludge
    if x.hp>0 and x.hp<x.maxhp and x.item=="Black Sludge":
        if "Poison" in (x.primaryType,x.secondaryType,x.teraType):
            em.add_field(name=f"{x.icon} {x.name}'s {await itemicon(x.item)} {x.item}!",value=f"{x.name} restored a little HP using its Black Sludge.")
            x.showitem=True
            x.hp+=round(x.maxhp/16)   
            if x.hp>x.maxhp:
                x.hp=x.maxhp   
        else:  
            em.add_field(name=f"{x.icon} {x.name}'s {await itemicon(x.item)} {x.item}!",value=f"{x.name} lost a little HP using its Black Sludge.")
            dmg=round(x.maxhp/16)
            if dmg<1:
                dmg=1
            x.hp-=dmg
    #Aqua Ring        
    if x.hp>0 and x.hp<x.maxhp and x.aring is True:
        em.add_field(name="Aqua Ring:",value=f"{x.name} restored a little HP using its Aqua Ring.")
        if x.item=="Big Root":
            x.hp+=round((x.maxhp/16)*1.3)
            if x.hp>x.maxhp:
                x.hp=x.maxhp
        else:
            x.hp+=round(x.maxhp/16)      
            if x.hp>x.maxhp:
                x.hp=x.maxhp    
    #Grassy Terrain            
    if x.hp>0 and field.terrain =="Grassy" and x.hp<x.maxhp and (x.ability not in ["Levitate"] and "Flying" not in (x.primaryType,x.secondaryType,x.teraType) or x.grav is True):
        em.add_field(name="<:grassy:1141090982788603985> Grassy Terrain:",value=f"{x.icon} {x.name}'s HP was restored.")
        x.hp+=round(x.maxhp/16)
        if x.hp>x.maxhp:
            x.hp=x.maxhp
    if x.hp<0:
        x.hp=0
    if len(em.fields)!=0:
        await ctx.send(embed=em)
#Weather    
async def weather(ctx, field, bg):
    weather_messages = {
        "Extreme Sunlight": "The sunlight is extremely harsh.",
        "Heavy Rain": "Heavy rain continues to fall.",
        "Snowstorm": "Snow continues to fall.",
        "Rainy": "Rain continues to fall.",
        "Sandstorm": "The sandstorm is raging!",
        "Hail": "Hail continues to fall.",
        "Sunny": "The sunlight is strong."
    }
    
    em = discord.Embed(title="Weather Update!", color=bg)
    if field.weather in weather_messages:
        em.add_field(name="Weather:", value=weather_messages[field.weather])
    elif field.weather not in ["Normal", "Cloudy", "Clear"]:
        await ctx.send(embed=em)

async def partyup(tr1,new):
    if new.icon not in tr1.party:
        tr1.party[tr1.party.index("<:ball:1127196564948009052>")]=new.icon
    return tr1.party

async def send_switch_message(ctx, tr1, new):
    """Handles the creation and sending of the 'sent out' embed."""
    em = discord.Embed(title=f"{tr1.name} sent out {new.name}!")
    em.set_thumbnail(url=tr1.sprite)
    em.set_image(url=new.sprite)
    await ctx.send(embed=em)

async def apply_illusion_effect(tr1, new):
    """Applies the Illusion ability's sprite and nickname change."""
    # Find the last pokemon (highest index) in the party for Illusion
    last_pokemon = tr1.pokemons[-1]
    
    # Check if the new pokemon is the last one; if so, Illusion doesn't trigger
    if new != last_pokemon:
        new.nickname = last_pokemon.nickname
        new.sprite = last_pokemon.sprite
        # Note: The original code sets nickname twice, which is redundant but preserved if needed elsewhere.
        # new.nickname = last_pokemon.nickname
class PokemonSwitchSelect(discord.ui.Select):
    def __init__(self, tr1: 'Trainer', current_pokemon: 'Pokemon'):
        self.tr1 = tr1
        self.current_pokemon = current_pokemon
        self.selected_index = -1
        
        options = []
        for i, p in enumerate(tr1.pokemons):
            # --- FIX: REMOVE 'disabled=is_disabled' ---
            is_fainted_or_active = (p.hp <= 0 or p == current_pokemon)
            hp_status = "KO" if p.hp <= 0 else f"{int(p.hp)}/{int(p.maxhp)} HP"
            
            options.append(
                discord.SelectOption(
                    label=f"#{i+1} {p.name} ({hp_status})",
                    # Append a warning to the description instead of disabling
                    description=f"Ability: {p.ability}" if not is_fainted_or_active else "Cannot switch (Active)",
                    value=str(i),
                    emoji=p.icon,
                    # NO 'disabled' ARGUMENT HERE
                )
            )

        super().__init__(
            placeholder="Choose a Pokémon to switch into...", 
            min_values=1, max_values=1, options=options
        )

    async def callback(self, interaction: discord.Interaction):
        index = int(self.values[0])
        selected_pokemon = self.tr1.pokemons[index]
        
        # --- NEW VALIDATION LOGIC ---
        if selected_pokemon.hp <= 0 or selected_pokemon == self.current_pokemon:
            # Send an error message, but keep the view alive so they can pick again.
            await interaction.response.send_message(
                f"{selected_pokemon.name} cannot be chosen! Select a different Pokémon.", 
                ephemeral=True
            )
            return
        
        # If valid, proceed with the original logic:
        self.selected_index = index
        
        # Acknowledge and stop the view
        await interaction.response.defer() 
        self.view.stop()

class PokemonSwitchView(discord.ui.View):
    def __init__(self, tr1: 'Trainer', current_pokemon: 'Pokemon', send_target):
        super().__init__(timeout=60.0)
        self.tr1 = tr1
        self.current_pokemon = current_pokemon
        self.send_target = send_target
        self.switch_select = PokemonSwitchSelect(tr1, current_pokemon)
        self.add_item(self.switch_select)
        self.chosen_pokemon: Optional['Pokemon'] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only the player controlling the switch can use the view
        if interaction.user.id != self.tr1.member.id:
            await interaction.response.send_message("This switch menu is not for you.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        # Notify the user on timeout if they haven't made a choice
        if self.chosen_pokemon is None:
            await self.send_target.send("Switch choice timed out. The battle has ended.", embed=None, view=None)

    # A button to re-send the switch menu if the user loses the message
    @discord.ui.button(label="Re-send Menu", style=discord.ButtonStyle.gray, row=1)
    async def resend_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Acknowledge the interaction
        await interaction.response.send_message("Re-sending the switch menu.", ephemeral=True)
        # Send a new copy of the full menu
        em = await self.tr1.get_party_embed(self.current_pokemon) # Assuming you have a helper for this
        await self.send_target.send(embed=em, view=self)

    async def wait_for_switch(self) -> Optional['Pokemon']:
        # Wait for the view to stop (either by selection or timeout)
        await self.wait() 
        
        if self.switch_select.selected_index != -1:
            # A selection was made
            return self.tr1.pokemons[self.switch_select.selected_index]
        return None
                           
async def switch(ctx, bot, x, y, tr1, tr2, field, turn):
    # --- 1. Cleanup Active Pokémon (x) State ---
    
    # Dynamax Cleanup
    if x.dmax:
        x.gsprite = x.sprite
        x.name = x.name.replace(" <:dynamax:1104646304904257647>", "")
        x.hp /= 2
        x.maxhp /= 2
        x.dmax = False
    
    # Protean/Libero Cleanup (Reset to original base types)
    type_assignments = {
        "Kecleon": ("Normal", "Ghost"),
        "Meowscarada": ("Grass", "Dark"),
        "Cinderace": ("Fire", "???"),
        "Greninja": ("Water", "Dark")
    }
    if x.ability in ["Protean", "Libero"] and x.name in type_assignments:
        x.primaryType, x.secondaryType = type_assignments[x.name]
        
    # Ability-specific Cleanup
    if "Disguise" in x.ability:
        x.ability = "Disguise"
        x.sprite = "http://play.pokemonshowdown.com/sprites/ani/mimikyu.gif"
    if "Quark Drive" in x.ability: x.ability = "Quark Drive"
    if "Protosynthesis" in x.ability: x.ability = "Protosynthesis"
    if "Ditto" in x.name:
        x.ability = "Imposter"
        x.name = "Ditto"
        x.sprite = "sprites/Ditto.png"
        
    # Reset Stat Stages and Status Effects
    x.atkb = x.defb = x.spatkb = x.spdefb = x.speedb = 0
    x.atk, x.speed, x.spatk, x.spdef, x.defense = x.maxatk, x.maxspeed, x.maxspatk, x.maxspdef, x.maxdef
    x.accuracy = x.evasion = 100
    x.toxicCounter = 1
    x.perishturn = 0
    x.canfakeout = True 
    x.choicedmove = "None"
    
    # Reset various boolean flags
    x.priority = x.recharge = x.seeded = x.flinched = x.protect = y.protect = x.shelltrap = x.choiced = x.dbond = x.salty = x.flashfire = x.taunted = x.confused = x.encore = x.cursed = x.yawn = x.aring = False
    
    # Substitute removal
    if tr1.sub != "None" and "Shed Tail" not in x.moves:
        tr1.sub = "None"
        
    # --- 2. AI Switch Logic ---
    if tr1.ai:
        new = None
        # Select a random Pokémon that is not currently in battle (x)
        while new is None or new == x:
            new = random.choice(tr1.pokemons)

        # Apply Withdrawal Effect and Illusion
        await withdraweff(ctx, x, tr1, y)
        if new.ability == "Illusion":
            await apply_illusion_effect(tr1, new)
            
        await send_switch_message(ctx, tr1, new)
        await entryeff(ctx, new, y, tr1, tr2, field, turn)
        tr1.party = await partyup(tr1, new)
        return new

    # --- 3. Human Switch Logic (Combined) ---
    else:
        new = None
        
        # Determine where to send the switch menu (Channel vs. DM)
        if tr2.ai: # Human vs AI: input in main channel
            send_target = ctx.channel 
            send_feedback = lambda msg: ctx.send(msg)
        else: # Human vs Human: input in DM
            send_target = tr1.member 
            send_feedback = lambda msg: tr1.member.send(msg)

        # Build the initial embed for the user (optional, but good for context)
        pklist = ""
        for i, p in enumerate(tr1.pokemons):
            hp_status = "KO" if p.hp <= 0 else f"{int(p.hp)}/{int(p.maxhp)} HP"
            pklist += f"#{i+1} {p.icon} {p.name} ({hp_status})\n"
            
        em = discord.Embed(title="Choose your pokémon!", description=pklist)

        # Initialize and send the view
        switch_view = PokemonSwitchView(tr1, x, send_target)
        msg = await send_target.send(embed=em, view=switch_view)
        
        # Wait for the selection
        new = await switch_view.wait_for_switch()
        
        # Clean up the message after selection or timeout
        try:
            await msg.edit(view=None)
        except:
            pass
        
        # --- Switch Execution ---
        if new:
            # Only run withdraweff if the current Pokémon (x) was active (i.e., not a forced switch after faint)
            if x in tr1.pokemons:
                await withdraweff(ctx, x, tr1, y)
            
            # Apply Illusion
            if new.ability == "Illusion":
                await apply_illusion_effect(tr1, new)

            # Apply Entry Effects and Update Party
            await entryeff(ctx, new, y, tr1, tr2, field, turn)
            await send_switch_message(ctx, tr1, new)
            tr1.party = await partyup(tr1, new)
            
            return new
        else:
            # Timeout/Cancellation handled by the view
            return None
        
async def withdraweff(ctx, x, tr1, y):
    # Determine if Neutralizing Gas is active on the opponent's side (y)
    neutralizing_gas_active = y.ability == "Neutralizing Gas"
    
    # Initialize the list of fields to add to the embed
    fields_to_add = []

    # --- 1. Zero to Hero (Palafin) Transformation ---
    # Simplified conditions and logic flow
    if (x.ability == "Zero to Hero" and 
        "Hero" not in x.name and 
        x.hp > 0 and 
        not x.dmax and 
        not neutralizing_gas_active):
        
        x.showability = True
        fields_to_add.append({
            "name": f"{x.icon} {x.name}'s Zero to Hero!",
            "value": f"{x.name} underwent a heroic transformation!"
        })
        
        # Store current HP percentage before stat change
        per = x.hp / x.maxhp
        
        # Apply Hero Form Base Stats (Palafin-Hero)
        x.nickname = "Hero Palafin"
        x.sprite = "http://play.pokemonshowdown.com/sprites/ani/palafin-hero.gif"
        x.weight = 214.73
        
        # Directly assign base HP/stats for Hero Form
        x.hp = 100 
        x.atk = 160
        x.defense = 97
        x.spatk = 106
        x.spdef = 87
        x.speed = 100
        
        # Re-calculate max stats based on new base stats (calcst must be synchronous)
        calcst(x) 
        
        # Restore HP based on percentage
        x.hp = x.maxhp * per


    # --- 2. Illusion Cleanup ---
    # This must run regardless of Neutralizing Gas, as it's a visual state reset.
    if x.ability == "Illusion":
        # Access last element directly using index -1 for cleaner code
        last_pokemon = tr1.pokemons[-1] 
        x.name = last_pokemon.name
        x.sprite = last_pokemon.sprite
        x.nickname = last_pokemon.nickname

    # --- 3. Natural Cure Status Healing ---
    if (x.ability == "Natural Cure" and 
        x.status not in ["Alive", "Fainted"] and 
        not neutralizing_gas_active):
        
        x.showability = True
        fields_to_add.append({
            "name": f"{x.icon} {x.name}'s Natural Cure!",
            "value": f"{x.name}'s status condition was cured!"
        })
        x.status = "Alive"

    # --- 4. Regenerator Health Recovery ---
    if (x.ability == "Regenerator" and 
        0 < x.hp < x.maxhp and 
        x.status != "Fainted" and 
        not neutralizing_gas_active):
        
        x.showability = True
        fields_to_add.append({
            "name": f"{x.icon} {x.name}'s Regenerator!",
            "value": f"{x.name} regenerated a bit of its health!"
        })
        
        # Calculate and apply recovery
        recovery = round(x.maxhp / 3)
        x.hp += recovery
        
        # Cap HP at maxhp (simplified check)
        if x.hp > x.maxhp:
            x.hp = x.maxhp

    # --- 5. Send Embed if Effects Occurred ---
    if fields_to_add:
        em = discord.Embed(title="Withdraw Effect:")
        for field in fields_to_add:
            em.add_field(name=field["name"], value=field["value"])
        await ctx.send(embed=em)                  

async def rankedbuild(team):
    new=[]
    while len(new)!=6:
        mon=random.choice(team)
        if mon not in new:
            new.append(mon)  
    return new         

async def teambuild(team):
    new=[]
    if len(team)>6:
        while len(new)!=5:
            mon=random.choice(team)
            if mon not in new and mon!=team[5]:
                new.append(mon)
        new.append(team[5])        
        return new         
    else:
        return team    
           
async def gamemonvert(tr, m, lev):
    # --- Variable Setup (Same as optimized synchronous version) ---
    NAME_INDEX = 0
    NICKNAME_INDEX = 1
    # ... define other indices if necessary to improve clarity
    
    pokemon_name = m[NAME_INDEX]
    nickname = m[NICKNAME_INDEX]
    ability_str = m[8]
    item_str = m[11]
    moves_str = m[14]
    tera_type_str = m[13]

    final_name = pokemon_name
    
    # Conditional Name/Form Assignment (Non-Blocking Logic)
    if pokemon_name == "Zacian" and item_str == "Rusted Sword":
        final_name = "Crowned Zacian"
    elif pokemon_name == "Zamazenta" and item_str == "Rusted Shield":
        final_name = "Crowned Zamazenta"
    elif pokemon_name == "Palkia" and item_str == "Lustrous Globe":
        final_name = "Origin Palkia"
    elif pokemon_name == "Dialga" and item_str == "Adamant Crystal":
        final_name = "Origin Dialga"
    elif pokemon_name == "Giratina" and item_str == "Griseous Core":
        final_name = "Origin Giratina"
        
    if nickname is None or nickname == pokemon_name:
        nickname = pokemon_name

    # --- Awaitable Database Access (The Core Optimization) ---
    try:
        # Use async with for connection and cursor for non-blocking I/O
        async with aiosqlite.connect("pokemondata.db") as db:
            async with db.cursor() as cx:
                # Use parameter substitution for safety (f-strings can be risky with user input)
                await cx.execute("SELECT * FROM 'wild' WHERE name=?", (final_name,))
                db_data = await cx.fetchall()
                
                if not db_data:
                    # Handle case where the Pokémon name is not found
                    # You might raise an exception or log an error here.
                    raise ValueError(f"Pokémon '{final_name}' not found in database.")

                n = db_data[0]
                
    except Exception as e:
        print(f"Database error in gamemonvert: {e}")
        return None # Return None or raise error as appropriate for your game flow

    # --- Item, Moves, Ability, Tera Assignment (Non-Blocking Logic) ---
    
    itm = "None"
    db_item_str = n[24] # Assuming n[24] is the index for DB item list
    
    if item_str != "None":
        if "," in item_str:
            itm = random.choice(item_str.split(","))
        else:
            itm = item_str
    elif db_item_str is not None:
        if "," in db_item_str:
            itm = random.choice(db_item_str.split(","))
        else:
            itm = db_item_str

    if moves_str == "A,B,C,D":
        moves_str = n[10] # Use DB moves

    if ability_str == "None":
        ability_str = n[11] # Use DB ability

    tera_type = tera_type_str
    if tera_type_str != "???" and "," in tera_type_str:
        tera_type = random.choice(tera_type_str.split(","))

    # --- Pokemon Object Creation ---
    p = Pokemon(
        name=pokemon_name,
        nickname=nickname,
        hpev=m[2],
        atkev=m[3],
        defev=m[4],
        spatkev=m[5],
        spdefev=m[6],
        speedev=m[7],
        ability=random.choice(ability_str.split(",")),
        nature=random.choice(m[9].split(",")),
        shiny=m[10],
        item=itm,
        gender=m[12],
        tera=tera_type,
        moves=moves_str,
        maxiv="Yes",
        primaryType=n[1],
        secondaryType=n[2],
        level=lev,
        hp=n[4],
        atk=n[5],
        defense=n[6],
        spatk=n[7],
        spdef=n[8],
        speed=n[9],
        sprite=n[12],
        icon=n[22],
        weight=n[13]
    )
    
    return p

async def evspread():
    # Define constants for clarity
    MAX_EV_SUM = 508
    MAX_STAT_EV = 252
    NUM_STATS = 6

    # 1. Generate 5 random EVs within the range [0, 252]
    # We generate 5 because the 6th will be determined by the sum.
    evs = []
    
    # Use a constructive approach:
    # Generate 6 random numbers that sum to 508, then clamp them to 252.
    # A simpler approach is to generate 5, and force the 6th to be the remainder,
    # then iterate to fix the 6th if it's out of bounds.

    while True:
        lst = [random.randint(0, MAX_STAT_EV) for _ in range(NUM_STATS - 1)]
        current_sum = sum(lst)
        remainder = MAX_EV_SUM - current_sum
        if 0 <= remainder <= MAX_STAT_EV:
            lst.append(remainder)
            random.shuffle(lst) # Shuffle to randomize which stat gets the remainder EV
            return lst       

async def rankedmonvert(tr, m):
    # --- 1. Initial Variable Setup and Item Assignment ---
    
    # Use indices from the input list 'm' for clarity
    NAME_INDEX = 0
    ITEM_LIST_INDEX = 24
    
    pokemon_name = m[NAME_INDEX]
    
    # 1a. Determine Held Item
    item = "None"
    if m[ITEM_LIST_INDEX] is not None:
        item = random.choice(m[ITEM_LIST_INDEX].split(","))
        
    final_name = pokemon_name
    newname = pokemon_name
    ability = m[11]
    
    # 1b. Conditional Name/Form Assignment based on Item
    if pokemon_name == "Zacian" and item == "Rusted Sword":
        final_name = "Crowned Zacian"
    elif pokemon_name == "Zamazenta" and item == "Rusted Shield":
        final_name = "Crowned Zamazenta"
    elif pokemon_name == "Palkia" and item == "Lustrous Globe":
        final_name = "Origin Palkia"
    elif pokemon_name == "Dialga" and item == "Adamant Crystal":
        final_name = "Origin Dialga"
    elif pokemon_name == "Giratina" and item == "Griseous Core":
        final_name = "Origin Giratina"
        ability = "Levitate" # Giratina-Origin form ability

    # --- 2. Concurrent Awaitables (EVs and DB Fetch) ---

    # PRE-FETCH: Get the custom EV spread concurrently with the DB query
    # The evspread function is now called *outside* the random.choices list.
    custom_evs_coro = evspread()

    # The DB fetch is now non-blocking
    try:
        async with aiosqlite.connect("pokemondata.db") as db:
            async with db.cursor() as cx:
                # Use parameterized query for safety
                await cx.execute("SELECT * FROM 'wild' WHERE name=?", (final_name,))
                db_data = await cx.fetchall()
                if not db_data:
                    raise ValueError(f"Pokémon '{final_name}' not found in database.")
                n = db_data[0] # n holds the database row (base stats, types, etc.)

    except Exception as e:
        print(f"Database error in rankedmonvert: {e}")
        return None 
    
    # RESOLVE AWAITABLES: Get the custom EV spread result
    custom_evs = await custom_evs_coro

    # --- 3. EV Spread Selection (Non-Blocking) ---
    
    # Fixed EV spread: 252/252/4 spread, randomly shuffled
    fixed_evs = [0, 0, 0, 4, 252, 252]
    random.shuffle(fixed_evs) 
    
    # Use random.choices to select the final spread: 90% fixed, 10% custom
    ev_choices = [fixed_evs, custom_evs]
    ev = random.choices(ev_choices, weights=[10, 1], k=1)[0]
    
    # --- 4. Pokemon Object Creation (Consolidated) ---
    
    # Simplified Nature choices (Original list was large and contained duplicates)
    all_natures = ["Hardy", "Lonely", "Adamant", "Naughty", "Brave", "Bold", 'Docile', 
                   'Impish', 'Lax', 'Relaxed', 'Modest', 'Mild', 'Bashful', 'Rash', 
                   'Quiet', 'Calm', 'Gentle', 'Careful', 'Quirky', 'Sassy', 'Timid', 
                   'Hasty', 'Jolly', 'Naive', 'Serious']

    p = Pokemon(
        name=pokemon_name,
        nickname=newname,
        hpev=ev[0], atkev=ev[1], defev=ev[2],
        spatkev=ev[3], spdefev=ev[4], speedev=ev[5],
        
        # Random Selections
        ability=random.choice(ability.split(",")),
        nature=random.choice(all_natures),
        shiny=random.choices(["Yes", "No"], weights=[1, 100], k=1)[0],
        gender=random.choice(m[15].split(",")),
        
        # Simple Assignments
        item=item,
        tera="???", # Tera is always '???' as per original logic
        moves=m[10],
        maxiv="Yes",
        
        # Data from Input (m)
        primaryType=m[1], secondaryType=m[2],
        level=m[3],
        
        # Data from DB (n)
        hp=n[4], atk=n[5], defense=n[6], spatk=n[7], spdef=n[8], speed=n[9],
        sprite=n[12], icon=n[22], weight=n[13]
    )
    
    return p

async def checkname(name):
    # A dictionary mapping keywords to their corresponding Discord icon strings
    icons = {
        "Gym Leader": "<:gym:1134404587432980611>",
        "Elite Four": "<:e4:1134407225222377474>",
        "Galactic": "<:galactic:1134373093457022996>",
        "Rocket": "<:rocket:1134396195394039968>",
        "Aqua": "<:aqua:1134377659342798849>",
        "Magma": "<:magma:1134377889287110681>",
        "Plasma": "<:plasma:1134394632004968448>",
    }

    for keyword, icon in icons.items():
        if keyword in name:
            return f"{icon} {name}"

    return name

async def calculate_hazard_buff(pokemon, weak_types):
    """Calculates the damage buff based on type weaknesses (base 2, doubles for each weak type)."""
    buff = 2
    
    # Check primary type, only if not Terastallized
    if pokemon.primaryType in weak_types and pokemon.teraType == "???":
        buff *= 2
        
    # Check secondary type, only if not Terastallized
    if pokemon.secondaryType in weak_types and pokemon.teraType == "???":
        buff *= 2
        
    # Check Tera type
    if pokemon.teraType in weak_types:
        buff *= 2
        
    return buff

async def rankedteam(ctx):
    # Initialize name and sprite with fallback values outside the 'try' block
    name = "Mysterious Trainer"
    sprite = "https://play.pokemonshowdown.com/sprites/trainers/unknown.png"
    
    # --- 1. Asynchronous API Call using aiohttp ---
    try:
        async with aiohttp.ClientSession() as session:
            # The 'await' makes this an non-blocking operation
            async with session.get('https://randomuser.me/api/') as response:
                if response.status == 200:
                    data = await response.json()
                    results = data['results'][0]
                    name = f"{results['name']['first']} {results['name']['last']}"
                    sprite = f"{results['picture']['large']}"
                else:
                    # Log error if API call fails
                    print(f"Random User API failed with status: {response.status}")
    except aiohttp.ClientConnectorError as e:
        # Handle connection errors (e.g., DNS resolution failure)
        print(f"Error connecting to Random User API: {e}")
    except Exception as e:
        # Catch any other unexpected errors during the API call
        print(f"An unexpected error occurred during API call: {e}")


    # --- 2. Database Operations (Assuming pokemondata.db exists on Render) ---
    team = []
    names = []
    try:
        # Use a 'with' statement for clean resource management
        with sqlite3.connect("pokemondata.db") as db:
            c = db.cursor()
            c.execute("SELECT * FROM wild") # Changed f-string for safety, assuming 'wild' is literal
            mons = c.fetchall()
            
            # --- 3. Team Generation ---
            for i in mons:
                # i[0] is the Pokémon name, i[14] is the rarity/type
                # Ensure i[14] is cast to string or handle potential type errors
                rarity = str(i[14]) 
                valid_rarities = {"Common","Uncommon","Rare","Very Rare","Common Legendary","Ultra Beasts","Fusion","Legendary","Mythical"}
                
                if i[0] not in names and rarity in valid_rarities:
                    # Assuming rankedmonvert is an async function
                    p = await rankedmonvert(name, i) 
                    team.append(p)
                    names.append(i[0])
                    
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        # If the database access fails, the function will return a trainer with an empty team
        
        
    # --- 4. Final Trainer Object Creation ---
    # Assuming rankedbuild is an async function
    final_mons = await rankedbuild(team)
    
    # Pass the collected name and sprite (either real or fallback)
    tr1 = Trainer(name, final_mons, "Earth", sprite=sprite, ai=True)
    return tr1

async def gameteam(ctx, num=0, p1team=None):
    """
    Creates a CPU Trainer with a team of Pokémon.
    """

    # --- 1. Trainer Selection ---
    players = ("Pokemon Trainer Ludlow","Pokemon Trainer Liko","Pokemon Trainer Roy","Pokemon Trainer Dot","Pokemon Trainer Ult",
        "Explorers Chalce","Explorers Lucius","Explorers Coral","Explorers Sidian","Flare Nouveau Grisham","Flare Nouveau Griselle",
        "SBC Lebanne","SBC Jacinthe","Detective Emma","Fist of Justice Gwynn","Fist of Justice Ivor",
        "Quasartico Vinnie","DYN4MO Tarragon","DYN4MO Canari","Rust Syndicate Corbeau",
        "Rust Syndicate Philippe","Pokemon Trainer Taunie","Pokemon Trainer Naveen","Pokemon Trainer Lida",
        "World Champion Ash","Professor Oak","Researcher Gary Oak","Team Rocket James",
        "Team Rocket Jessie","Pokemon Breeder Brock","Gym Leader Brock","Tomboyish Mermaid Misty",
        "Gym Leader Misty","Gym Leader Lt.Surge","Gym Leader Erika","Gym Leader Janine",
        "Gym Leader Sabrina","Gym Leader Blaine","Gym Leader Blue","Elite Four Lorelei",
        "Champion Lorelei(Rain)","Champion Lorelei(Hail)","Elite Four Bruno","Elite Four Agatha",
        "Kanto Champion Lance","Pokemon Trainer Green","Pokemon Trainer Trace","Kanto Champion Red",
        "Rocket Boss Giovanni","Pokemon Trainer Silver","Gym Leader Falkner","Gym Leader Bugsy",
        "Gym Leader Morty","Gym Leader Chuck","Gym Leader Jasmine","Gym Leader Pryce",
        "Gym Leader Clair","Elite Four Will","Elite Four Koga","Elite Four Karen",
        "Rocket Admin Archer","Rocket Admin Ariana","Pokemon Trainer Harrison","Pokemon Trainer May",
        "Gym Leader Roxanne","Gym Leader Brawly","Gym Leader Wattson","Gym Leader Flannery",
        "Gym Leader Norman","Gym Leader Winona","Gym Leader Tate","Gym Leader Liza",
        "Gym Leader Juan","Elite Four Sidney","Elite Four Phoebe","Elite Four Glacia",
        "Elite Four Drake","Hoenn Champion Steven","Hoenn Champion Wallace","Aqua Leader Archie",
        "Magma Admin Courtney","Magma Leader Maxie","Factory Head Noland","Arena Tycoon Greta",
        "Dome Ace Tucker","Palace Maven Spenser","Pike Queen Lucy","Salon Maiden Anabel",
        "Pyramid King Brandon","Pokemon Trainer Paul","Pokemon Trainer Barry","Pokemon Trainer Conway",
        "Gym Leader Roark","Gym Leader Gardenia","Gym Leader Maylene","Gym Leader Crasher Wake",
        "Gym Leader Fantina","Gym Leader Byron","Gym Leader Candice","Gym Leader Volkner",
        "Elite Four Aaron","Elite Four Bertha","Elite Four Flint","Elite Four Lucian",
        "Sinnoh Champion Cynthia","Pokemon Trainer Tobias","Galactic Commander Mars",
        "Galactic Commander Jupiter","Galactic Commander Saturn","Galactic Leader Cyrus",
        "Pokemon Trainer Riley","Pokemon Trainer Cheryl","Pokemon Trainer Marley","Pokemon Trainer Mira",
        "Pokemon Trainer Buck","Factory Head Thorton","Battle Arcade Dahlia","Castle Velvet Darach",
        "Hall Matron Argenta","Tower Tycoon Palmer","Pokemon Trainer Trip","Pokemon Trainer Cameron",
        "Pokemon Trainer Stephan","Gym Leader Cilan","Gym Leader Cress","Gym Leader Chili",
        "Pokemon Trainer Cheren","Pokemon Trainer Bianca","Gym Leader Lenora","Gym Leader Roxie",
        "Gym Leader Burgh","Gym Leader Elesa","Gym Leader Clay","Gym Leader Skyla",
        "Gym Leader Brycen","Gym Leader Marlon","Gym Leader Drayden","Gym Leader Marlon",
        "Elite Four Marshal","Elite Four Shauntal","Elite Four Grimsley","Elite Four Caitlin",
        "Unova Champion Alder","Unova Champion Iris","Pokemon Trainer Hugh",
        "Plasma Admin Colress","Natural Harmonia Gropius","Plasma Leader Ghetsis",
        "Boss Trainer Benga","Subway Boss Ingo","Subway Boss Emmet","Pokemon Trainer Sawyer",
        "Pokemon Trainer Trevor","Pokemon Trainer Tierno","Pokemon Trainer Shauna",
        "Gym Leader Viola","Gym Leader Grant","Gym Leader Korrina","Gym Leader Ramos",
        "Gym Leader Clemont","Gym Leader Valerie","Gym Leader Olympia","Gym Leader Wulfric",
        "Elite Four Siebold","Elite Four Wikstrom","Elite Four Malva","Elite Four Drasna",
        "Pokemon Trainer Alain","Kalos Champion Diantha","Flare Boss Lysandre",
        "Pokemon Trainer Gladion","Trial Captain Kiawe","Trial Captain Lana","Trial Captain Lillie",
        "Trial Captain Mallow","Island Kahuna Ilima","Trial Captain Nanu","Elite Four Hala",
        "Elite Four Olivia","Elite Four Molayne","Professor Kukui","Skull Admin Plumeria",
        "Skull Leader Guzma","Aether Foundation Faba","Aether President Lusamine",
        "Gym Leader Milo","Gym Leader Nessa","Gym Leader Kabu","Gym Leader Bede",
        "Gym Leader Bea","Gym Leader Allister","Gym Leader Opal","Gym Leader Gordie",
        "Gym Leader Marnie","Gym Leader Piers","Gym Leader Raihan","Pokemon Trainer Hop",
        "Galar Champion Peony","Galar Champion Leon","Chairman Rose","Galar Champion Mustard",
        "Instructor Jacq","Instructor Miriam","Instructor Tyme","Instructor Dendra",
        "Gym Leader Katy","Gym Leader Brassius","Gym Leader Iono","Gym Leader Kofu",
        "Gym Leader Ryme","Gym Leader Tulip","Gym Leader Grusha","Team Star Giacomo",
        "Team Star Mela","Team Star Atticus","Team Star Ortega","Team Star Eri",
        "Star Leader Penny","Elite Four Rika","Elite Four Poppy","Elite Four Larry",
        "Elite Four Hassel","Paldea Champion Geeta","Paldea Champion Nemona",
        "Pokemon Trainer Carmine","Elite Four Crispin","Elite Four Amarys",
        "Elite Four Lacey","Elite Four Drayton","Pokemon Trainer Keiran",
        "Academy Director Cyrano","Director Clavell","Professor Sada","Professor Turo",
        "Elite Four Acerola","Pokemon Trainer Drew","Battle Chatelaine Evelyn",
        "Island Kahuna Hapu","Fusion Creator Darwin","Elite Four Kahili",
        "Coordinator Kenny","Gym Leader Klara","Aqua Admin Matt","Battle Chatelaine Nita",
        "Pokemon Wielder Volo","Nurse Joy","Evil Trainer Crescent","CrescentUwU",
        "Cipher Head Evice",'Gym Leader Jessica','Gym Leader Esmeralda','Gym Leader Lucas',
        'Gym Leader Thomas','Gym Leader Atlur','Gym Leader Rayner','Gym Leader Sophia',
        'Gym Leader Wesley','Elite Four Aisey','Elite Four Triton','Elite Four Rukia',
        'Elite Four Elizabeth','Zhery Champion Kaohri'
    )

    if num == 0:
        trainer_name = random.choice(players)
    elif 1 <= num <= len(players):
        # Adjust for 0-based index
        trainer_name = players[num - 1]
    else:
        # Fallback if an invalid num is provided (outside the list range)
        trainer_name = random.choice(players)

    # Get the trainer's sprite
    trainer_sprite = await trsprite(trainer_name)

    # --- 2. Determine Max Pokémon Level ---
    if p1team is None:
        # Default to level 100 if no opponent team is provided
        max_level = 100
    else:
        # Find the max level of the opponent's team and subtract 2
        opponent_levels = [mon.level for mon in p1team if mon is not None]
        max_level = max(opponent_levels) - 2

    # --- 3. Retrieve Trainer's Base Team from Database ---
    try:
        # Use 'with' statement for safer resource management (connecting/closing db)
        with sqlite3.connect("pokemondata.db") as db:
            c = db.cursor()
            # Note: Parameterized query is safer, but assuming trainer_name is clean
            # as it comes from a fixed tuple.
            c.execute(f"SELECT * FROM '{trainer_name}'")
            base_pokemon_data = c.fetchall()
    except sqlite3.Error as e:
        print(f"Database error for trainer {trainer_name}: {e}")
        return None # Return None or raise an error if team fetching fails

    # --- 4. Build the Pokémon Team ---
    team = []
    # Clean/format the name before using it for Pokémon-specific logic
    formatted_name = await checkname(trainer_name)

    for pokemon_data in base_pokemon_data:
        # Convert database row to a usable Pokemon object, setting the level
        p = await gamemonvert(formatted_name, pokemon_data, max_level)

        # Apply specific sprite logic for certain trainers/Pokémon (e.g., Ash's Pikachu)
        if p.name == "Pikachu":
            if formatted_name == "Kanto Champion Red":
                p.sprite = "https://play.pokemonshowdown.com/sprites/ani/pikachu-starter.gif"
            elif formatted_name == "World Champion Ash":
                ash_pikachu_sprites = [
                    '-partner', '', '-alola', '-hoenn', '-kalos', '-sinnoh', '-unova', '-original'
                ]
                p.sprite = f"https://play.pokemonshowdown.com/sprites/ani/pikachu{random.choice(ash_pikachu_sprites)}.gif"

        team.append(p)

    # Finalize the team (e.g., set items, abilities, moves)
    final_team = await teambuild(team)

    # --- 5. Create and Return the Trainer Object ---
    # The region is hardcoded as "Unknown" in the original code, retaining that
    tr1=Trainer(trainer_name,final_team,"Unknown",sprite=trainer_sprite,ai=True)
    return tr1

async def trsprite(name):
    spritelist={
    "Pokemon Trainer Ludlow":"https://archives.bulbagarden.net/media/upload/thumb/d/d7/Ludlow_anime_2.png/200px-Ludlow_anime_2.png",
    "Pokemon Trainer Ult":"https://archives.bulbagarden.net/media/upload/thumb/1/1a/Ult_anime.png/130px-Ult_anime.png",
    "Pokemon Trainer Dot":"https://archives.bulbagarden.net/media/upload/thumb/3/3a/Dot_anime_5.png/150px-Dot_anime_5.png",
    "Pokemon Trainer Liko":"https://archives.bulbagarden.net/media/upload/thumb/8/8b/Liko_anime_8.png/180px-Liko_anime_8.png",
    "Pokemon Trainer Roy":"https://archives.bulbagarden.net/media/upload/thumb/9/98/Roy_anime_3.png/120px-Roy_anime_3.png",
    "Explorers Chalce":"https://archives.bulbagarden.net/media/upload/thumb/2/23/Chalce_anime_2.png/200px-Chalce_anime_2.png",
    "Explorers Sidian":"https://archives.bulbagarden.net/media/upload/thumb/1/11/Sidian_anime_2.png/150px-Sidian_anime_2.png",
    "Explorers Coral":"https://archives.bulbagarden.net/media/upload/thumb/2/2e/Coral_anime_2.png/150px-Coral_anime_2.png",
    "Explorers Lucius":"https://archives.bulbagarden.net/media/upload/thumb/4/4b/Lucius_2.png/200px-Lucius_2.png",
    "Flare Nouveau Grisham":"https://archives.bulbagarden.net/media/upload/thumb/d/d3/ZA_Grisham.png/300px-ZA_Grisham.png",
    "Flare Nouveau Griselle":"https://archives.bulbagarden.net/media/upload/thumb/2/22/ZA_Griselle.png/450px-ZA_Griselle.png",
    "SBC Lebanne":"https://archives.bulbagarden.net/media/upload/thumb/b/b9/ZA_Lebanne.png/300px-ZA_Lebanne.png",
    "SBC Jacinthe":"https://archives.bulbagarden.net/media/upload/thumb/9/93/ZA_Jacinthe.png/300px-ZA_Jacinthe.png",
    "Detective Emma":"https://archives.bulbagarden.net/media/upload/thumb/f/f5/ZA_Emma.png/120px-ZA_Emma.png",
    "Fist of Justice Gwynn":"https://archives.bulbagarden.net/media/upload/thumb/e/ef/ZA_Gwynn.png/300px-ZA_Gwynn.png",
    "Fist of Justice Ivor":"https://archives.bulbagarden.net/media/upload/thumb/5/55/ZA_Ivor.png/300px-ZA_Ivor.png",
    "Quasartico Vinnie":"https://archives.bulbagarden.net/media/upload/thumb/4/4a/ZA_Vinnie.png/120px-ZA_Vinnie.png",
    "DYN4MO Tarragon":"https://archives.bulbagarden.net/media/upload/5/5a/ZA_Tarragon.png",
    "DYN4MO Canari":"https://archives.bulbagarden.net/media/upload/thumb/7/72/ZA_Canari.png/350px-ZA_Canari.png",
    "Rust Syndicate Corbeau":"https://archives.bulbagarden.net/media/upload/thumb/3/36/ZA_Corbeau.png/180px-ZA_Corbeau.png",
    "Rust Syndicate Philippe":"https://archives.bulbagarden.net/media/upload/thumb/e/e6/ZA_Philippe.png/300px-ZA_Philippe.png",
    "Pokemon Trainer Taunie":"https://archives.bulbagarden.net/media/upload/thumb/7/75/ZA_Taunie.png/148px-ZA_Taunie.png",
    "Pokemon Trainer Naveen":"https://archives.bulbagarden.net/media/upload/thumb/1/18/ZA_Naveen.png/140px-ZA_Naveen.png",
    "Pokemon Trainer Lida":"https://archives.bulbagarden.net/media/upload/thumb/4/4c/ZA_Lida.png/180px-ZA_Lida.png",    
    "Zhery Champion Kaohri":"https://cdn.discordapp.com/attachments/1102579499989745764/1193467672097202256/20240107_141321.png",    
    'Elite Four Elizabeth':'https://cdn.discordapp.com/attachments/1102579499989745764/1193467671883296788/20240107_141305.png',
    'Elite Four Rukia':'https://cdn.discordapp.com/attachments/1102579499989745764/1193467671656800266/20240107_141242.png',
    'Elite Four Triton':'https://cdn.discordapp.com/attachments/1102579499989745764/1193467671421923359/20240107_141225.png',
    'Elite Four Aisey':'https://cdn.discordapp.com/attachments/1102579499989745764/1193465662010556467/20240107_140445.png',
    'Gym Leader Wesley':'https://cdn.discordapp.com/attachments/1102579499989745764/1193465661654061056/1704614621962.png',   
    'Gym Leader Sophia':'https://cdn.discordapp.com/attachments/1102579499989745764/1193465661452718190/1704614593948.png',   
    'Gym Leader Rayner':'https://cdn.discordapp.com/attachments/1102579499989745764/1193465661263970345/1704614566112.png',   
    'Gym Leader Atlur':'https://cdn.discordapp.com/attachments/1102579499989745764/1193465661066858526/1704614544936.png',   
    'Gym Leader Thomas':'https://cdn.discordapp.com/attachments/1102579499989745764/1193465660873904178/1704614516571.png',   
    'Gym Leader Lucas':'https://cdn.discordapp.com/attachments/1102579499989745764/1193465660676767844/1704614490107.png',   
    'Gym Leader Esmeralda':'https://cdn.discordapp.com/attachments/1102579499989745764/1193464081374527600/1704614399126.png',   
    'Gym Leader Jessica':'https://cdn.discordapp.com/attachments/1102579499989745764/1193463642235093105/1704614284030.png',   
    "Director Clavell":"https://cdn.discordapp.com/attachments/1102579499989745764/1185853231373496431/ezgif.com-resize_1.png",
    "Academy Director Cyrano":"https://cdn.discordapp.com/attachments/1102579499989745764/1185848826154713179/ezgif.com-resize.png",
    "Elite Four Crispin":"https://cdn.discordapp.com/attachments/1102579499989745764/1184945696734986360/ezgif.com-resize_2.png",
    "Elite Four Amarys":"https://cdn.discordapp.com/attachments/1102579499989745764/1184945696940503110/ezgif.com-resize_3.png",
    "Elite Four Lacey":"https://cdn.discordapp.com/attachments/1102579499989745764/1184945695745122364/ezgif.com-resize_1.png",
    "Elite Four Drayton":"https://cdn.discordapp.com/attachments/1102579499989745764/1184944755327635567/ezgif.com-resize.png",
    "CrescentUwU":"https://cdn.discordapp.com/attachments/1102579499989745764/1152888429068177438/20230917_144646.png",
    "Pokemon Trainer Carmine":"https://cdn.discordapp.com/attachments/1102579499989745764/1151461386073948210/ezgif.com-resize_5.png",
    "Pokemon Trainer Keiran":"https://cdn.discordapp.com/attachments/1102579499989745764/1151461394273816596/ezgif.com-resize_6.png",
    "Instructor Dendra":"https://play.pokemonshowdown.com/sprites/trainers/dendra.png",
    "Instructor Tyme":"https://play.pokemonshowdown.com/sprites/trainers/tyme.png",
    "Instructor Jacq":"https://play.pokemonshowdown.com/sprites/trainers/jacq.png",
    "Instructor Miriam":"https://play.pokemonshowdown.com/sprites/trainers/miriam.png",
    "Pokemon Trainer Hugh":"https://play.pokemonshowdown.com/sprites/trainers/hugh.png",
    "Cipher Head Evice":"https://cdn.discordapp.com/attachments/1102579499989745764/1143884401780990012/20230823_182800.png",
    "Pokemon Trainer Harrison":"https://cdn.discordapp.com/attachments/1102579499989745764/1143763951184785408/20230823_102906.png",
    "Gym Leader Chili":"https://play.pokemonshowdown.com/sprites/trainers/chili.png",
    "Gym Leader Cress":"https://play.pokemonshowdown.com/sprites/trainers/cress.png",
    "Pokemon Trainer Bianca":"https://play.pokemonshowdown.com/sprites/trainers/bianca.png",
    "Pokemon Trainer Stephan":"https://cdn.discordapp.com/attachments/1102579499989745764/1143754567297806517/20230823_095207.png",
    "Pokemon Trainer Trip":"https://cdn.discordapp.com/attachments/1102579499989745764/1143597556773949520/20230822_232813.png",
    "Pokemon Trainer Cameron":"https://cdn.discordapp.com/attachments/1102579499989745764/1143595948983988294/20230822_232150.png",
    "Pokemon Trainer Silver":"https://cdn.discordapp.com/attachments/1102579499989745764/1143486243842314340/20230822_160554.png",
    "Pokemon Trainer Trace":"https://cdn.discordapp.com/attachments/1102579499989745764/1143485651145203762/20230822_160305.png",
    "Pokemon Trainer Green":"https://cdn.discordapp.com/attachments/1102579499989745764/1143485660976660570/20230822_160335.png",
    "Pokemon Trainer Shauna":"https://play.pokemonshowdown.com/sprites/trainers/shauna.png",
    "Pokemon Trainer Tierno":"https://play.pokemonshowdown.com/sprites/trainers/tierno.png",
    "Pokemon Trainer Trevor":"https://play.pokemonshowdown.com/sprites/trainers/trevor.png",
    "Pokemon Trainer Sawyer":"https://cdn.discordapp.com/attachments/1102579499989745764/1143377840205733928/20230822_085457.png",
    "Nurse Joy":"https://cdn.discordapp.com/attachments/1102579499989745764/1142455980181954590/20230819_195155.png",
    "Gym Leader Valerie":"https://play.pokemonshowdown.com/sprites/trainers/valerie.png",
    "Gym Leader Cilan":"https://play.pokemonshowdown.com/sprites/trainers/cilan.png",
    "Gym Leader Viola":"https://play.pokemonshowdown.com/sprites/trainers/viola.png",
    "Team Star Eri":"https://play.pokemonshowdown.com/sprites/trainers/eri.png",
    "Team Star Mela":"https://play.pokemonshowdown.com/sprites/trainers/mela.png",
    "Team Star Giacomo":"https://play.pokemonshowdown.com/sprites/trainers/giacomo.png",
    "Team Star Atticus":"https://play.pokemonshowdown.com/sprites/trainers/atticus.png",
    "Hall Matron Argenta":"https://cdn.discordapp.com/attachments/1102579499989745764/1140512276017840168/KatePlatinum.gif",
    "Gym Leader Wulfric":"https://cdn.discordapp.com/attachments/1102579499989745764/1140300033028259910/image_search_1691939087769.png",
    "Elite Four Will":"https://cdn.discordapp.com/attachments/1102579499989745764/1138413461248950403/Spr_HGSS_Will.png",
    "Pokemon Wielder Volo":"https://play.pokemonshowdown.com/sprites/trainers/volo.png",
    "Gym Leader Volkner":"https://cdn.discordapp.com/attachments/1102579499989745764/1138361906139242527/Spr_B2W2_Volkner.png",
    "Gym Leader Tulip":"https://cdn.discordapp.com/attachments/1102579499989745764/1137992736453177365/20230807_121640.png",
    "Elite Four Sidney":"https://play.pokemonshowdown.com/sprites/trainers/sidney.png",
    "World Champion Ash":random.choice(["https://play.pokemonshowdown.com/sprites/trainers/ash-alola.png","https://play.pokemonshowdown.com/sprites/trainers/ash-capbackward.png","https://play.pokemonshowdown.com/sprites/trainers/ash-hoenn.png","https://play.pokemonshowdown.com/sprites/trainers/ash-johto.png","https://play.pokemonshowdown.com/sprites/trainers/ash-kalos.png","https://play.pokemonshowdown.com/sprites/trainers/ash-sinnoh.png","https://play.pokemonshowdown.com/sprites/trainers/ash-unova.png","https://play.pokemonshowdown.com/sprites/trainers/ash.png"]),
    "Elite Four Shauntal":"https://cdn.discordapp.com/attachments/1102579499989745764/1136917784996089906/Spr_B2W2_Shauntal.png",
    "Pokemon Trainer Tobias":"https://cdn.discordapp.com/attachments/1102579499989745764/1136904651510394943/1691129578488.png",
    "Professor Turo":"https://play.pokemonshowdown.com/sprites/trainers/turo.png",
    "Professor Sada":"https://play.pokemonshowdown.com/sprites/trainers/sada.png",
    "Dome Ace Tucker":"https://cdn.discordapp.com/attachments/1102579499989745764/1136899891789045780/Spr_E_Tucker.png",
    "Palace Maven Spenser":"https://cdn.discordapp.com/attachments/1102579499989745764/1136898826507137104/Spr_E_Spenser.png",
    "Gym Leader Janine":"https://cdn.discordapp.com/attachments/1102579499989745764/1140291026578321478/JanineHGSSSprite.gif",
    "Gym Leader Skyla":"https://cdn.discordapp.com/attachments/1102579499989745764/1136898405508063252/Spr_B2W2_Skyla.png",
    "Galactic Commander Saturn":"https://cdn.discordapp.com/attachments/1102579499989745764/1136897817684754494/Spr_DP_Saturn.png",
    "Factory Head Thorton":"https://cdn.discordapp.com/attachments/1102579499989745764/1140296434642604112/NejikiPlatinum.gif",
    "Hoenn Champion Wallace":"https://cdn.discordapp.com/attachments/1102579499989745764/1140288579105460224/WallaceB2W2sprite.gif",
    "Gym Leader Tate":"https://cdn.discordapp.com/attachments/1102579499989745764/1136897295825240104/Spr_B2W2_Tate.png",
    "Gym Leader Winona":"https://cdn.discordapp.com/attachments/1102579499989745764/1136615608037941360/image_search_1691060615276.png",
    "Gym Leader Wattson":"https://cdn.discordapp.com/attachments/1102579499989745764/1136615607631106078/image_search_1691060604914.png",
    "Elite Four Siebold":"https://play.pokemonshowdown.com/sprites/trainers/siebold.png",
    "Elite Four Wikstrom":"https://cdn.discordapp.com/attachments/1102579499989745764/1136901309019205662/image_search_1691128774978.png",
    "Pokemon Trainer Cheryl":"https://cdn.discordapp.com/attachments/1102579499989745764/1126801413515780146/Cheryl.png",
    "Pokemon Trainer Buck":"https://cdn.discordapp.com/attachments/1102579499989745764/1126801176525029396/Buck.png",
    "Gym Leader Ryme":"https://play.pokemonshowdown.com/sprites/trainers/ryme.png",
    "Gym Leader Roxie":"https://cdn.discordapp.com/attachments/1102579499989745764/1126792580957487194/Roxie.png",
    "Gym Leader Roxanne":"https://cdn.discordapp.com/attachments/1102579499989745764/1126792580739379200/Roxanne.png",
    "Chairman Rose":"https://cdn.discordapp.com/attachments/1102579499989745764/1126792580470935562/Rose.png",
    "Gym Leader Roark":"https://cdn.discordapp.com/attachments/1102579499989745764/1126792580257038336/Roark.png",
    "Pokemon Trainer Riley":"https://cdn.discordapp.com/attachments/1102579499989745764/1126792580030541964/Riley.png",
    "Elite Four Rika":"https://play.pokemonshowdown.com/sprites/trainers/rika.png",
    "Kanto Champion Red":"https://cdn.discordapp.com/attachments/1102579499989745764/1126792579544006806/Red.png",
    "Gym Leader Ramos":"https://cdn.discordapp.com/attachments/1102579499989745764/1126792579309121536/Ramos.png",
    "Gym Leader Raihan":"https://cdn.discordapp.com/attachments/1102579499989745764/1126792579057455124/Raihan.png",
    "Gym Leader Pryce":"https://cdn.discordapp.com/attachments/1102579499989745764/1126767579650871366/Pryce.png",
    "Elite Four Poppy":"https://cdn.discordapp.com/attachments/1102579499989745764/1126767579415982110/Poppy.png",
    "Skull Admin Plumeria":"https://cdn.discordapp.com/attachments/1102579499989745764/1126767579172716614/Plumeria.png",
    "Gym Leader Piers":"https://cdn.discordapp.com/attachments/1102579499989745764/1126767578904285254/Piers.png",
    "Elite Four Phoebe":"https://play.pokemonshowdown.com/sprites/trainers/phoebe-gen6.png",
    "Galar Champion Peony":"https://play.pokemonshowdown.com/sprites/trainers/peony.png",
    "Star Leader Penny":"https://play.pokemonshowdown.com/sprites/trainers/penny.png",
    "Pokemon Trainer Paul":"https://cdn.discordapp.com/attachments/1102579499989745764/1126767577742458930/Paul.png",
    "Tower Tycoon Palmer":"https://cdn.discordapp.com/attachments/1102579499989745764/1140296432981639168/PalmerPlatinum.gif",
    "Team Star Ortega":"https://play.pokemonshowdown.com/sprites/trainers/ortega.png",
    "Gym Leader Opal":"https://cdn.discordapp.com/attachments/1102579499989745764/1126759237054382100/Opal.png",
    "Gym Leader Olympia":"https://play.pokemonshowdown.com/sprites/trainers/olympia.png",
    "Elite Four Olivia":"https://cdn.discordapp.com/attachments/1102579499989745764/1126759236274237510/Olivia.png",
    "Professor Oak":"https://play.pokemonshowdown.com/sprites/trainers/oak.png",
    "Gym Leader Norman":"https://cdn.discordapp.com/attachments/1102579499989745764/1126759235586371644/Norman.png",
    "Factory Head Noland":"https://play.pokemonshowdown.com/sprites/trainers/noland.png",
    "Battle Chatelaine Nita":"https://cdn.discordapp.com/attachments/1102579499989745764/1126759235032715334/Nita.png",
    "Gym Leader Nessa":"https://cdn.discordapp.com/attachments/1102579499989745764/1126759234751709254/Nessa.png",
    "Paldea Champion Nemona":"https://play.pokemonshowdown.com/sprites/trainers/nemona-v.png",
    "Trial Captain Nanu":"https://cdn.discordapp.com/attachments/1102579499989745764/1126759234122563654/Nanu.png",
    "Natural Harmonia Gropius":"https://cdn.discordapp.com/attachments/1102579499989745764/1126712947134177370/N.png",
    "Galar Champion Mustard":"https://play.pokemonshowdown.com/sprites/trainers/mustard-master.png",
    "Gym Leader Morty":"https://cdn.discordapp.com/attachments/1102579499989745764/1126712946685394964/Morty.png",
    "Elite Four Molayne":"https://cdn.discordapp.com/attachments/1102579499989745764/1126712946479865886/Molayne.png",
    "Pokemon Trainer Mira":"https://cdn.discordapp.com/attachments/1102579499989745764/1126712946203045898/Mira.png",
    "Pokemon Trainer Mina":"https://cdn.discordapp.com/attachments/1102579499989745764/1126712945942994965/Mina.png",
    "Gym Leader Milo":"https://cdn.discordapp.com/attachments/1102579499989745764/1126712945636814919/Milo.png",
    "Gym Leader Maylene":"https://cdn.discordapp.com/attachments/1102579499989745764/1126712944982503524/Maylene.png",
    "Fusion Creator Darwin":"https://play.pokemonshowdown.com/sprites/trainers/unknown.png",
    "Pokemon Trainer May":"https://cdn.discordapp.com/attachments/1102579499989745764/1120587242423992350/May.png",
    "Magma Leader Maxie":"https://cdn.discordapp.com/attachments/1102579499989745764/1120587242084237423/Maxie.png",
    "Aqua Admin Matt":"https://play.pokemonshowdown.com/sprites/trainers/matt.png",
    "Elite Four Marshal":"https://cdn.discordapp.com/attachments/1102579499989745764/1120587241442512916/Marshal.png",
    "Galactic Commander Mars":"https://cdn.discordapp.com/attachments/1102579499989745764/1120587241077620796/Mars.png",
    "Gym Leader Marnie":"https://cdn.discordapp.com/attachments/1102579499989745764/1120587240830140496/Marnie.png",
    "Gym Leader Marlon":"https://cdn.discordapp.com/attachments/1102579499989745764/1120587240557514792/Marlon.png",
    "Pokemon Trainer Marley":"https://cdn.discordapp.com/attachments/1102579499989745764/1120587240200994847/Marley.png",
    "Elite Four Malva":"https://cdn.discordapp.com/attachments/1102579499989745764/1120587239886426205/Malva.png",
    "Trial Captain Mallow":"https://cdn.discordapp.com/attachments/1102579499989745764/1120587239634780170/Mallow.png",
    "Flare Boss Lysandre":"https://play.pokemonshowdown.com/sprites/trainers/lysandre.png",
    "Aether President Lusamine":"https://cdn.discordapp.com/attachments/1102579499989745764/1120578905494003773/Lusamine.png",
    "Pike Queen Lucy":"https://play.pokemonshowdown.com/sprites/trainers/lucy.png",
    "Elite Four Lucian":"https://cdn.discordapp.com/attachments/1102579499989745764/1120578905003274261/Lucian.png",
    "Champion Lorelei(Hail)":"https://cdn.discordapp.com/attachments/1102579499989745764/1138762073552195594/1691572419426.png",
    "Champion Lorelei(Rain)":"https://cdn.discordapp.com/attachments/1102579499989745764/1138762073552195594/1691572419426.png",
    "Elite Four Lorelei":"https://cdn.discordapp.com/attachments/1102579499989745764/1120578904743223387/Lorelei.png",
    "Gym Leader Liza":"https://cdn.discordapp.com/attachments/1102579499989745764/1120578904478986280/Liza.png",
    "Trial Captain Lillie":"https://cdn.discordapp.com/attachments/1102579499989745764/1120578904252489798/Lillie.png",
    "Galar Champion Leon":"https://play.pokemonshowdown.com/sprites/trainers/leon.png",
    "Gym Leader Lenora":"https://cdn.discordapp.com/attachments/1102579499989745764/1120578903749177436/Lenora.png",
    "Elite Four Larry":"https://cdn.discordapp.com/attachments/1102579499989745764/1120578903463960647/Larry.png",
    "Kanto Champion Lance":"https://cdn.discordapp.com/attachments/1102579499989745764/1120571178516492379/Lance.png",
    "Trial Captain Lana":"https://cdn.discordapp.com/attachments/1102579499989745764/1120571178222887003/Lana.png",
    "Professor Kukui":"https://cdn.discordapp.com/attachments/1102579499989745764/1120571178013180055/Kukui.png",
    "Gym Leader Korrina":"https://cdn.discordapp.com/attachments/1102579499989745764/1120571177732153495/Korrina.png",
    "Elite Four Koga":"https://cdn.discordapp.com/attachments/1102579499989745764/1140291025651372154/KogaHGSS.gif",
    "Gym Leader Kofu":"https://cdn.discordapp.com/attachments/1102579499989745764/1120571177212063805/Kofu.png",
    "Gym Leader Klara":"https://cdn.discordapp.com/attachments/1102579499989745764/1120571176998150244/Klara.png",
    "Trial Captain Kiawe":"https://cdn.discordapp.com/attachments/1102579499989745764/1120571176771666030/Kiawe.png",
    "Coordinator Kenny":"https://cdn.discordapp.com/attachments/1102579499989745764/1120571176532586598/Kenny.png",
    "Gym Leader Katy":"https://cdn.discordapp.com/attachments/1102579499989745764/1120571176322867210/Katy.png",
    "Island Kahuna Ilima":"https://cdn.discordapp.com/attachments/1102579499989745764/1112283056624119858/Ilima.png",
    "Subway Boss Ingo":"https://cdn.discordapp.com/attachments/1102579499989745764/1112283056850608228/Ingo.png",
    "Elite Four Karen":"https://cdn.discordapp.com/attachments/1102579499989745764/1115999806100357140/Karen.png",
    "Gym Leader Kabu":"https://cdn.discordapp.com/attachments/1102579499989745764/1115999805869666314/Kabu.png",
    "Elite Four Kahili":"https://cdn.discordapp.com/attachments/1102579499989745764/1115999805601239110/Kahili.png",
    "Galactic Commander Jupiter":"https://cdn.discordapp.com/attachments/1102579499989745764/1115999805349576834/Jupiter.png",
    "Team Rocket Jessie":"https://cdn.discordapp.com/attachments/1102579499989745764/1115999804837875752/Jessie.png",
    "Gym Leader Juan":"https://cdn.discordapp.com/attachments/1102579499989745764/1115999805076942962/Juan.png",
    "Gym Leader Jasmine":"https://cdn.discordapp.com/attachments/1102579499989745764/1115999804535881758/Jasmine.png",
    "Team Rocket James":"https://cdn.discordapp.com/attachments/1102579499989745764/1115999804280025169/James.png",
    "Unova Champion Iris":"https://cdn.discordapp.com/attachments/1102579499989745764/1140295347105714298/Champion_Iris.gif",
    "Gym Leader Iono":"https://cdn.discordapp.com/attachments/1102579499989745764/1115999803806072852/Iono.png",
    "Elite Four Bruno":random.choice(["https://cdn.discordapp.com/attachments/1102579499989745764/1115998773781475368/Bruno.png","https://cdn.discordapp.com/attachments/1102579499989745764/1140293031187206195/BrunoHGSS.gif"]),
    "Pokemon Trainer Hop":"https://cdn.discordapp.com/attachments/1102579499989745764/1112283056359866469/Hop.png",
    "Pokemon Trainer Hau":"https://cdn.discordapp.com/attachments/1102579499989745764/1112283056133382204/Hau.png",
    "Elite Four Hassel":"https://cdn.discordapp.com/attachments/1102579499989745764/1112283055927865435/Hassel.png",
    "Island Kahuna Hapu":"https://cdn.discordapp.com/attachments/1102579499989745764/1112283055705554994/Hapu.png",
    "Elite Four Hala":"https://cdn.discordapp.com/attachments/1102579499989745764/1112258206861889566/Hala.png",
    "Skull Leader Guzma":"https://cdn.discordapp.com/attachments/1102579499989745764/1112258206614438008/Guzma.png",
    "Gym Leader Grusha":"https://play.pokemonshowdown.com/sprites/trainers/grusha.png",
    "Elite Four Grimsley":"https://cdn.discordapp.com/attachments/1102579499989745764/1112258205993668628/Grimsley.png",
    "Arena Tycoon Greta":"https://cdn.discordapp.com/attachments/1102579499989745764/1112258205628776528/Greta.png",
    "Gym Leader Grant":"https://play.pokemonshowdown.com/sprites/trainers/grant.png",
    "Gym Leader Gordie":"https://play.pokemonshowdown.com/sprites/trainers/gordie.png",
    "Pokemon Trainer Gladion":"https://cdn.discordapp.com/attachments/1102579499989745764/1112020338079973416/Gladion.png",
    "Elite Four Glacia":"https://play.pokemonshowdown.com/sprites/trainers/glacia.png",
    "Rocket Boss Giovanni":"https://cdn.discordapp.com/attachments/1102579499989745764/1140297675254796348/GiovanniHGSS.gif",
    "Plasma Leader Ghetsis":random.choice(["https://play.pokemonshowdown.com/sprites/trainers/ghetsis.png","https://play.pokemonshowdown.com/sprites/trainers/ghetsis-gen5bw.png"]),
    "Paldea Champion Geeta":"https://play.pokemonshowdown.com/sprites/trainers/geeta.png",
    "Researcher Gary Oak":"https://cdn.discordapp.com/attachments/1102579499989745764/1111943226698514492/Gary2.png",
    "Gym Leader Gardenia":"https://cdn.discordapp.com/attachments/1102579499989745764/1111943226476208159/Gardenia.png",
    "Elite Four Flint":"https://cdn.discordapp.com/attachments/1102579499989745764/1111943226245517382/Flint.png",
    "Gym Leader Flannery":"https://cdn.discordapp.com/attachments/1102579499989745764/1111943226027425904/Flannery.png",
    "Gym Leader Fantina":"https://cdn.discordapp.com/attachments/1102579499989745764/1111897876314996816/Fantina.png",
    "Gym Leader Falkner":"https://cdn.discordapp.com/attachments/1102579499989745764/1140291027006136340/FalknerHGSSSprite.gif",
    "Aether Foundation Faba":"https://cdn.discordapp.com/attachments/1102579499989745764/1111897875903942706/Faba.png",
    "Battle Chatelaine Evelyn":"https://cdn.discordapp.com/attachments/1102579499989745764/1111897875702628362/Evelyn.png",
    "Subway Boss Emmet":"https://cdn.discordapp.com/attachments/1102579499989745764/1111897875484520468/Emmet.png",
    "Gym Leader Elesa":"https://cdn.discordapp.com/attachments/1102579499989745764/1111897704201736202/Elesa1.png",
    "Pokemon Trainer Drew":"https://cdn.discordapp.com/attachments/1102579499989745764/1111163495371771934/Drew.png",
    "Gym Leader Drayden":"https://cdn.discordapp.com/attachments/1102579499989745764/1140295347848093776/DraydenBWsprite.gif",
    "Elite Four Drasna":"https://cdn.discordapp.com/attachments/1102579499989745764/1111163494876860476/Drasna.png",
    "Elite Four Drake":"https://cdn.discordapp.com/attachments/1102579499989745764/1111163494662942791/Drake.png",
    "Kalos Champion Diantha":"https://play.pokemonshowdown.com/sprites/trainers/diantha.png",
    "Castle Velvet Darach":"https://cdn.discordapp.com/attachments/1102579499989745764/1140296433464004698/KochraneCattleyaPlatinum.gif",
    "Battle Arcade Dahlia":"https://cdn.discordapp.com/attachments/1102579499989745764/1140296433858256977/Dahlia.gif",
    "Galactic Leader Cyrus":"https://cdn.discordapp.com/attachments/1102579499989745764/1140297304201506906/CyrusPlatinum.gif",
    "Gym Leader Crasher Wake":"https://cdn.discordapp.com/attachments/1102579499989745764/1111144174755000380/Crasher_Wake.png",
    "Magma Admin Courtney":"https://cdn.discordapp.com/attachments/1102579499989745764/1111144174503350334/Courtney.png",
    "Pokemon Trainer Conway":"https://cdn.discordapp.com/attachments/1102579499989745764/1111144174289436672/Conway.png",
    "Plasma Admin Colress":"https://cdn.discordapp.com/attachments/1102579499989745764/1111127415071199272/Colress.png",
    "Gym Leader Clemont":"https://cdn.discordapp.com/attachments/1102579499989745764/1111127414836314162/Clemont.png",
    "Gym Leader Clay":"https://cdn.discordapp.com/attachments/1102579499989745764/1111127414546903040/Clay.png",
    "Gym Leader Clair":"https://cdn.discordapp.com/attachments/1102579499989745764/1111127414240727092/Clair.png",
    "Gym Leader Chuck":"https://cdn.discordapp.com/attachments/1102579499989745764/1111127413951316037/Chuck.png",
    "Pokemon Trainer Cheren":"https://cdn.discordapp.com/attachments/1102579499989745764/1111127413481558167/Cheren.png",
    "Gym Leader Candice":"https://cdn.discordapp.com/attachments/1102579499989745764/1111114704904003685/Candice.png",
    "Elite Four Caitlin":"https://cdn.discordapp.com/attachments/1102579499989745764/1140296434256707695/Caitlin.gif",
    "Gym Leader Byron":"https://cdn.discordapp.com/attachments/1102579499989745764/1111114704451010661/Byron.png",
    "Gym Leader Burgh":"https://cdn.discordapp.com/attachments/1102579499989745764/1111114704144834662/Burgh.png",
    "Gym Leader Bugsy":"https://cdn.discordapp.com/attachments/1102579499989745764/1140292531888869449/BugsyHGSSSprite.gif",
    "Gym Leader Brycen":"https://cdn.discordapp.com/attachments/1102579499989745764/1111114703641522226/Brycen.png",
    "Gym Leader Brawly":"https://cdn.discordapp.com/attachments/1102579499989745764/1111112061213216788/Brawly.png",
    "Gym Leader Brassius":"https://cdn.discordapp.com/attachments/1102579499989745764/1111112060919632012/Brassius.png",
    "Pyramid King Brandon":"https://cdn.discordapp.com/attachments/1102579499989745764/1111112060684738601/Brandon.png",
    "Aqua Leader Archie":"https://cdn.discordapp.com/attachments/1102579499989745764/1109681004983107714/Archie.png",
    "Sinnoh Champion Cynthia":random.choice(["https://cdn.discordapp.com/attachments/1102579499989745764/1140294182708195328/CynthiaPlatinum.gif","https://cdn.discordapp.com/attachments/1102579499989745764/1140294183165378670/Champion_Cynthia.gif"]),
    "Gym Leader Brock":"https://cdn.discordapp.com/attachments/1102579499989745764/1140289187719950386/Brock_gameHGSS.gif",
    "Pokemon Breeder Brock":"https://cdn.discordapp.com/attachments/1102579499989745764/1140289187719950386/Brock_gameHGSS.gif",
    "Gym Leader Misty":"https://cdn.discordapp.com/attachments/1102579499989745764/1140289438115696690/MistyHGSS.gif",
    "Tomboyish Mermaid Misty":"https://cdn.discordapp.com/attachments/1102579499989745764/1140289438115696690/MistyHGSS.gif",
    "Gym Leader Lt.Surge":"https://cdn.discordapp.com/attachments/1102579499989745764/1140289772473036902/Lt._SurgeHGSS.gif",
    "Gym Leader Erika":"https://cdn.discordapp.com/attachments/1102579499989745764/1140289772837949611/ErikaHGSS.gif",
    "Gym Leader Sabrina":"https://cdn.discordapp.com/attachments/1102579499989745764/1140291025223565322/SabrinaHGSS.gif",
    "Gym Leader Blaine":"https://cdn.discordapp.com/attachments/1102579499989745764/1140291026142118009/BlaineHGSS.gif",
    "Gym Leader Blue":"https://cdn.discordapp.com/attachments/1102579499989745764/1140292117814579401/BlueHGSS.gif",
    "Hoenn Champion Steven":"https://cdn.discordapp.com/attachments/1102579499989745764/1140288579571036210/StevenB2W2sprite.gif",
    "Elite Four Aaron":"https://cdn.discordapp.com/attachments/1102579499989745764/1109598046653788231/Aaron.png",
    "Elite Four Acerola":"https://cdn.discordapp.com/attachments/1102579499989745764/1109598930997620938/Acerola.png",
    "Elite Four Agatha":"https://cdn.discordapp.com/attachments/1102579499989745764/1109599848900083863/Agatha.png",
    "Pokemon Trainer Alain":"https://play.pokemonshowdown.com/sprites/trainers/alain.png",
    "Unova Champion Alder":"https://cdn.discordapp.com/attachments/1102579499989745764/1140295347441250427/AlderBWsprite.gif",
    "Gym Leader Allister":"https://cdn.discordapp.com/attachments/1102579499989745764/1109611947713892362/Allister.png",
    "Salon Maiden Anabel":random.choice(["https://cdn.discordapp.com/attachments/1102579499989745764/1109681004442046505/Anabel.png","https://play.pokemonshowdown.com/sprites/trainers/anabel.png"]),
    "Rocket Admin Archer":"https://cdn.discordapp.com/attachments/1102579499989745764/1109681004727246958/Archer.png",
    "Rocket Admin Ariana":"https://cdn.discordapp.com/attachments/1102579499989745764/1136897549467394078/Spr_HGSS_Ariana.png",
    "Pokemon Trainer Barry":"https://media.tenor.com/M0jtKgsWg-4AAAAi/barry-dance.gif",
    "Gym Leader Bea":"https://cdn.discordapp.com/attachments/1102579499989745764/1111029602874294355/Bea.png",
    "Gym Leader Bede":random.choice(["https://play.pokemonshowdown.com/sprites/trainers/bede.png","https://play.pokemonshowdown.com/sprites/trainers/bede-leader.png"]),
    "Boss Trainer Benga":"https://cdn.discordapp.com/attachments/1102579499989745764/1111031362300952747/Benga.png",
    "Elite Four Bertha":"https://cdn.discordapp.com/attachments/1102579499989745764/1111037750297243848/Bertha.png"
    }
    if name in spritelist:
        sprite=spritelist[name]
    else:
        sprite="https://play.pokemonshowdown.com/sprites/trainers/unknown.png"
    return sprite 
     
async def typesheet(t1,t2):
    typechart={
    "Fire": {"Weakness": ["Ground","Rock","Water"],
    "Resistance":["Bug","Steel","Fire","Grass","Ice","Fairy"],
    "Immunity":[]},
    "Water": {"Weakness": ["Grass","Electric"],
    "Resistance":["Steel","Fire","Water","Ice"],
    "Immunity":[]},
    "Normal": {"Weakness": ["Fighting"],
    "Resistance":[],
    "Immunity":["Ghost"]},
    "Fighting": {"Weakness": ["Flying","Fairy","Psychic"],
    "Resistance":["Rock","Bug","Dark"],
    "Immunity":[]},
    "Flying": {"Weakness": ["Rock","Electric","Ice"],
    "Resistance":["Fighting","Bug","Grass"],
    "Immunity":["Ground"]},
    "Poison": {"Weakness": ["Ground","Psychic"],
    "Resistance":["Fighting","Bug","Grass","Poison","Fairy"],
    "Immunity":[]},
    "Ground": {"Weakness": ["Water","Grass","Ice"],
    "Resistance":["Poison","Rock"],
    "Immunity":["Electric"]},
    "Rock": {"Weakness": ["Fighting","Ground","Steel","Water","Grass"],
    "Resistance":["Normal","Flying","Poison","Fire"],
    "Immunity":[]},
    "Bug": {"Weakness": ["Rock","Fire","Flying"],
    "Resistance":["Fighting","Ground","Grass"],
    "Immunity":[]},
    "Ghost": {"Weakness": ["Ghost","Dark"],
    "Resistance":["Poison","Bug"],
    "Immunity":["Normal","Fighting"]},
    "Steel": {"Weakness": ["Fighting","Ground","Fire"],
    "Resistance":["Normal","Bug","Grass","Flying","Rock","Steel","Psychic","Ice","Dragon","Fairy"],
    "Immunity":["Poison"]},
    "Grass": {"Weakness": ["Flying","Fire","Ice","Bug","Poison"],
    "Resistance":["Water","Ground","Grass","Electric"],
    "Immunity":[]},
    "Electric": {"Weakness": ["Ground"],
    "Resistance":["Flying","Steel","Electric"],
    "Immunity":[]},
    "Psychic": {"Weakness": ["Bug","Ghost","Dark"],
    "Resistance":["Fighting","Psychic"],
    "Immunity":[]},
    "Ice": {"Weakness": ["Fighting","Rock","Steel","Fire"],
    "Resistance":["Ice"],
    "Immunity":[]},
    "Dragon": {"Weakness": ["Dragon","Fairy","Ice"],
    "Resistance":["Fire","Water","Grass","Electric"],
    "Immunity":[]},
    "Dark": {"Weakness": ["Fighting","Bug","Fairy"],
    "Resistance":["Ghost","Dark"],
    "Immunity":["Psychic"]},
    "Fairy": {"Weakness": ["Poison","Steel"],
    "Resistance":["Fighting","Bug","Dark"],
    "Immunity":["Dragon"]},
    "???": {"Weakness": [],
    "Resistance":[],
    "Immunity":[]}
    }
    W4=list(set(typechart[t1]["Weakness"]).intersection(set(typechart[t2]["Weakness"])))
    
    W2=list((set(typechart[t1]["Weakness"]).union(set(typechart[t2]["Weakness"])).difference(set(typechart[t1]["Resistance"]).union(set(typechart[t2]["Resistance"]).union(set(typechart[t2]["Immunity"]))))).difference(set(typechart[t1]["Weakness"]).intersection(set(typechart[t2]["Weakness"]))))
    
    IM=list(set(set(typechart[t1]["Immunity"]).union(set(typechart[t2]["Immunity"]))))
    
    R4=list(set(typechart[t1]["Resistance"]).intersection(set(typechart[t2]["Resistance"])))
    
    R2=list((set(typechart[t1]["Resistance"]).union(set(typechart[t2]["Resistance"]))).difference(set(typechart[t1]["Weakness"]).union(set(typechart[t2]["Weakness"]).union(set(R4).union(set(IM))))))
    return W2,W4,IM,R2,R4
async def movecolor(u,field=None,x=None):
    c=int("FFFFFF",16)
    try:
        if u in typemoves.normalmoves:
            if x.ability=="Galvanize":
                c=int("FECD07",16)
            elif x.ability=="Liquid Voice":
                c=int("2196F3",16)
            elif x.ability=="Aerilate":
                c=int("9E87E1",16)
            elif x.ability=="Liquid Voice":
                c=int("2196F3",16)
            else:
                c=int("BFB97F",16)
    except:
        pass            
    if u in typemoves.fightingmoves:
        c=int("D32F2E",16)
    elif u in typemoves.flyingmoves:
        c=int("9E87E1",16)
    elif u in typemoves.poisonmoves:
        c=int("AA47BC",16)
    elif u in typemoves.groundmoves:
        c=int("DFB352",16)
    elif u in typemoves.rockmoves:
        c=int("BDA537",16)
    elif u in typemoves.bugmoves:
        c=int("98B92E",16)
    elif u in typemoves.ghostmoves:
        c=int("7556A4",16)
    elif u in typemoves.steelmoves:
        c=int("B4B4CC",16)
    elif u in typemoves.firemoves:
        c=int("E86513",16)
    elif u in typemoves.watermoves:
        c=int("2196F3",16)
    elif u in typemoves.grassmoves:
        c=int("4CB050",16)
    elif u in typemoves.electricmoves:
        c=int("FECD07",16)
    elif u in typemoves.psychicmoves:
        c=int("EC407A",16)
    elif u in typemoves.icemoves:
        c=int("80DEEA",16)
    elif u in typemoves.fairymoves:
        c=int("F483BB",16)
    elif u in typemoves.darkmoves:
        c=int("5C4038",16)
    elif u in typemoves.dragonmoves:
        c=int("673BB7",16)
    try:    
        if u=="Weather Ball":
            if field.weather in ("Rainy","Heavy Rain"):
                c=int("2196F3",16)
            elif field.weather=="Sandstorm":
                c=int("BDA537",16)
            elif field.weather=="Snowstorm":
                c=int("80DEEA",16)
            elif field.weather in ("Sunny","Extreme Sunlight"):
                c=int("E86513",16)
            else:
                c=int("BFB97F",16)
    except:
        pass            
    try:        
        if x.ability=="Normalize":
            c=int("BFB97F",16)    
        elif x.name=="Ogerpon" and u=="Ivy Cudgel":
            if x.item=="Cornerstone Mask":
                c=int("BDA537",16)
            elif x.item=="Wellspring Mask":
                c=int("2196F3",16)
            elif x.item=="Hearthflame Mask":
                c=int("E86513",16)
    except:
        pass            
               
    return c
