from intro import *
@bot.tree.command(name="createhuman",description="Creates random human.")
async def createhuman(ctx:discord.Interaction):
    response = requests.get('https://randomuser.me/api/')
    if response.status_code == 200:
        data = response.json()
        results = data['results'][0]
        
        name = f"{results['name']['first']} {results['name']['last']}"
        email = results['email']
        username = results['login']['username']
        dob = results['dob']['date']
        gender = results['gender']
        
        user_info = {
            'Name': name,
            'Email': email,
            'Username': username,
            'Date of Birth': dob,
            'Gender': gender
        }
        em=discord.Embed(title=name,description=f"Email: {email.replace('example','gmail')}\nUsername: {username}\nDate of Birth: {dob}\nSex: {gender}\nLocation: {results['location']['street']['number']} {results['location']['street']['name']}, {results['location']['city']}, {results['location']['state']} {results['location']['postcode']}, {results['location']['country']}")
        em.set_thumbnail(url=f"{results['picture']['large']}")
        await ctx.response.send_message(embed=em,ephemeral=True)
    else:
        await ctx.response.send_message("Invalid.")
@bot.tree.command(name="release",description="Release following pokémons.")
@app_commands.describe(mons="Pokémons that you wanna release!")
async def release(ctx:discord.Interaction,mons:str):
    db=sqlite3.connect("owned.db")
    c=db.cursor()
    mons=mons.split(" ")
    rel=[]
    txt="Are you sure you want to release these pokemon(s)? Write (yes/confirm) to release!"
    for i in mons:
        rel.append(await row(ctx,int(i),c))
    for i in rel:
        c.execute(f"select * from '{ctx.user.id}' where rowid={i}")
        mon=c.fetchone()
        txt+=f"\n**{mon[0]}** - {mon[25]}%"
    em=discord.Embed(title="Release:",description=txt,color=0xff0000)
    em.set_image(url="https://cdn.discordapp.com/attachments/1102579499989745764/1142222584159674569/image_search_1692397466636.png")
    await ctx.response.send_message(embed=em)
    rsponse = await bot.wait_for('message', check=lambda message: message.author == ctx.user)
    if rsponse.content.lower() in ["yes","confirm"]:
        for i in rel:
            c.execute(f"delete from '{ctx.user.id}' where rowid={i}")
            db.commit()
        await ctx.channel.send(f"Released {len(rel)} pokémon(s) successfully!")
    else:
        await ctx.channel.send("Release cancelled!")  
        
@bot.tree.command(name="abilityinfo",description="Shows ability description.")
@app_commands.describe(ability="Name of the ability.")
async def abilityinfo(ctx:discord.Interaction,ability:str):
    ability=ability.title()
    d=await abilitydesc(ability)
    em=discord.Embed(title=f"{ability}:",description=d,color=0x00ff00)
    await ctx.response.send_message(embed=em,ephemeral=True)
    
@bot.tree.command(name="withdraw",description="Withdraws pokémon from market.")
async def withdraw(ctx:discord.Interaction,code:str):    
    db=sqlite3.connect("market.db")
    c=db.cursor()
    dt=sqlite3.connect("pokemondata.db")
    ct=dt.cursor()
    dx=sqlite3.connect("owned.db")
    cx=dx.cursor()
    c.execute(f"select * from 'market' where serialno='{code}'")
    n=c.fetchone()
    ct.execute(f"SELECT * FROM 'wild' WHERE name='{n[0]}'")
    m=ct.fetchone()
    p = Pokemon(
        name=m[0],
        nickname=n[1],
        primaryType=m[1],
        secondaryType=m[2],
        level=m[3],
        hp=m[4],
        atk=m[5],
        defense=m[6],
        spatk=m[7],
        spdef=m[8],
        speed=m[9],
        moves=n[22],
        ability=n[15],
        sprite=m[12],
        gender=n[19],
        tera=n[20],
        maxiv="Custom",
        item=n[18],
        shiny=n[17],
        nature=n[16],
        hpiv=n[3],
        atkiv=n[4],
        defiv=n[5],
        spatkiv=n[6],
        spdefiv=n[7],
        speediv=n[8],
        hpev=n[9],
        atkev=n[10],
        defev=n[11],
        spatkev=n[12],
        spdefev=n[13],
        speedev=n[14],
        catchdate=n[24],
        icon=m[22],
        weight=m[13]
    )
    p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
    if n[27]==ctx.user.id:
        cx.execute(f"""INSERT INTO "{ctx.user.id}" VALUES (
                    "{p.name}",
                    "{p.nickname}",
                    "{p.level}",
                    "{p.hpiv}",
                    "{p.atkiv}",
                    "{p.defiv}",
                    "{p.spatkiv}",
                    "{p.spdefiv}",
                    "{p.speediv}",
                    "{p.hpev}",
                    "{p.atkev}",
                    "{p.defev}",
                    "{p.spatkev}",
                    "{p.spdefev}",
                    "{p.speedev}",
                    "{p.ability}",
                    "{p.nature}",
                    "{p.shiny}",
                    "{p.item}",
                    "{p.gender}",
                    "{p.tera}",
                    "Custom",
                    "{p.moves}",
                    "{m[14]}",
                    "{p.catchdate}",
                    "{p.totaliv}",
                    "{m[18]}")""")
        dx.commit()
        c.execute(f"delete from 'market' where serialno='{code}'")    
        db.commit()          
        await ctx.response.send_message("Withdraw successfully!")
    else:
        await ctx.response.send_message("You cannot withdraw others pokémon.") 
        
@bot.tree.command(name="purchase",description="Purchase pokémon from market.")
async def purchase(ctx:discord.Interaction,code:str):
    db=sqlite3.connect("market.db")
    c=db.cursor()
    dt=sqlite3.connect("pokemondata.db")
    ct=dt.cursor()
    dx=sqlite3.connect("owned.db")
    cx=dx.cursor()
    dm=sqlite3.connect("playerdata.db")
    cm=dm.cursor()
    c.execute(f"select * from 'market' where serialno='{code}'")
    n=c.fetchone()
    ct.execute(f"SELECT * FROM 'wild' WHERE name='{n[0]}'")
    m=ct.fetchone()
    cm.execute(f"select * from '{ctx.user.id}'")
    ply=cm.fetchone()
    money=ply[0]
    price=n[26]
    p = Pokemon(
        name=m[0],
        nickname=n[1],
        primaryType=m[1],
        secondaryType=m[2],
        level=m[3],
        hp=m[4],
        atk=m[5],
        defense=m[6],
        spatk=m[7],
        spdef=m[8],
        speed=m[9],
        moves=n[22],
        ability=n[15],
        sprite=m[12],
        gender=n[19],
        tera=n[20],
        maxiv="Custom",
        item=n[18],
        shiny=n[17],
        nature=n[16],
        hpiv=n[3],
        atkiv=n[4],
        defiv=n[5],
        spatkiv=n[6],
        spdefiv=n[7],
        speediv=n[8],
        hpev=n[9],
        atkev=n[10],
        defev=n[11],
        spatkev=n[12],
        spdefev=n[13],
        speedev=n[14],
        catchdate=n[24],
        icon=m[22],
        weight=m[13]
    )
    p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
    if n[27]!=ctx.user.id and price<money:
        cx.execute(f"""INSERT INTO "{ctx.user.id}" VALUES (
                    "{p.name}",
                    "{p.nickname}",
                    "{p.level}",
                    "{p.hpiv}",
                    "{p.atkiv}",
                    "{p.defiv}",
                    "{p.spatkiv}",
                    "{p.spdefiv}",
                    "{p.speediv}",
                    "{p.hpev}",
                    "{p.atkev}",
                    "{p.defev}",
                    "{p.spatkev}",
                    "{p.spdefev}",
                    "{p.speedev}",
                    "{p.ability}",
                    "{p.nature}",
                    "{p.shiny}",
                    "{p.item}",
                    "{p.gender}",
                    "{p.tera}",
                    "Custom",
                    "{p.moves}",
                    "{m[14]}",
                    "{p.catchdate}",
                    "{p.totaliv}",
                    "{m[18]}")""")
        dx.commit()
        c.execute(f"delete from 'market' where serialno='{code}'")    
        db.commit()        
        await addmoney(ctx,ctx.user,-price)  
        await ctx.response.send_message("Purchased successfully!")
    else:
        await ctx.response.send_message("You don't have enough pokécoins.")    
          
@bot.tree.command(name="compare", description="Compare two pokémons.")
async def compare(ctx: discord.Interaction, num1: int, num2: int):
    # Use 'async with' for connection to ensure it's closed properly
    async with aiosqlite.connect("owned.db") as db:
        c = await db.cursor()

        # Assuming 'row' and 'pokonvert' are defined elsewhere and are 'async' functions.
        # If 'row' is a wrapper for a simple database query, it must now use 'aiosqlite' methods.
        nm1 = await row(ctx, num1, c)
        nm2 = await row(ctx, num2, c)

        p, allmon, mon, spc = await pokonvert(ctx, ctx.user, nm1)
        q, allmon, mon, spc = await pokonvert(ctx, ctx.user, nm2)

    # --- Embed Creation (Remains the same) ---
    com = discord.Embed(
        title=f"#{num1} {p.name} {p.icon} vs {q.icon} {q.name} #{num2}",
        description="Sample comparison between these two pokemons are shown below!"
    )
    
    # Attributes Field
    com.add_field(
        name="Attributes:",
        value=(
            f"**HP:** {await bufficon(p.hp, q.hp)}{p.hp} - {q.hp}{await bufficon(q.hp, p.hp)}\n"
            f"**ATK:** {await bufficon(p.atk, q.atk)}{p.atk} - {q.atk}{await bufficon(q.atk, p.atk)}\n"
            f"**DEF:** {await bufficon(p.defense, q.defense)}{p.defense} - {q.defense}{await bufficon(q.defense, p.defense)}\n"
            f"**SPA:** {await bufficon(p.spatk, q.spatk)}{p.spatk} - {q.spatk}{await bufficon(q.spatk, p.spatk)}\n"
            f"**SPD:** {await bufficon(p.spdef, q.spdef)}{p.spdef} - {q.spdef}{await bufficon(q.spdef, p.spdef)}\n"
            f"**SPE:** {await bufficon(p.speed, q.speed)}{p.speed} - {q.speed}{await bufficon(q.speed, p.speed)}"
        )
    )

    # IVs Field
    com.add_field(
        name="IVs:",
        value=(
            f"**HP IV:** {await bufficon(p.hpiv, q.hpiv)}{p.hpiv} - {q.hpiv}{await bufficon(q.hpiv, p.hpiv)}\n"
            f"**ATK IV:** {await bufficon(p.atkiv, q.atkiv)}{p.atkiv} - {q.atkiv}{await bufficon(q.atkiv, p.atkiv)}\n"
            f"**DEF IV:** {await bufficon(p.defiv, q.defiv)}{p.defiv} - {q.defiv}{await bufficon(q.defiv, p.defiv)}\n"
            f"**SPA IV:** {await bufficon(p.spatkiv, q.spatkiv)}{p.spatkiv} - {q.spatkiv}{await bufficon(q.spatkiv, p.spatkiv)}\n"
            f"**SPD IV:** {await bufficon(p.spdefiv, q.spdefiv)}{p.spdefiv} - {q.spdefiv}{await bufficon(q.spdefiv, p.spdefiv)}\n"
            f"**SPE IV:** {await bufficon(p.speediv, q.speediv)}{p.speediv} - {q.speediv}{await bufficon(q.speediv, p.speediv)}"
        )
    )

    # EVs Field
    com.add_field(
        name="EVs:",
        value=(
            f"**HP EV:** {await bufficon(p.hpev, q.hpev)}{p.hpev} - {q.hpev}{await bufficon(q.hpev, p.hpev)}\n"
            f"**ATK EV:** {await bufficon(p.atkev, q.atkev)}{p.atkev} - {q.atkev}{await bufficon(q.atkev, p.atkev)}\n"
            f"**DEF EV:** {await bufficon(p.defev, q.defev)}{p.defev} - {q.defev}{await bufficon(q.defev, p.defev)}\n"
            f"**SPA EV:** {await bufficon(p.spatkev, q.spatkev)}{p.spatkev} - {q.spatkev}{await bufficon(q.spatkev, p.spatkev)}\n"
            f"**SPD EV:** {await bufficon(p.spdefev, q.spdefev)}{p.spdefev} - {q.spdefev}{await bufficon(q.spdefev, p.spdefev)}\n"
            f"**SPE EV:** {await bufficon(p.speedev, q.speedev)}{p.speedev} - {q.speedev}{await bufficon(q.speedev, p.speedev)}"
        )
    )
    
    await ctx.response.send_message(embed=com)

@bot.tree.command(name="coinflip",description="Flips a coin to 2x the amount or lose it.")
async def coinflip(ctx:discord.Interaction,choice:str,amount:int):    
    db=sqlite3.connect("playerdata.db")
    c=db.cursor()
    c.execute(f"select * from '{ctx.user.id}'")
    man=c.fetchone()
    if amount<=man[0]:
        choice=choice.title()
        x=random.choice(["Heads","Tails"])
        if choice==x:
            em=discord.Embed(title=f"It's {x}! You Won!",color=0x00ff00)
            em.set_thumbnail(url="https://i.gifer.com/Fw3P.gif")
            await ctx.response.send_message(embed=em)
            await addmoney(ctx,ctx.user,amount)
        if choice!=x and choice in ["Heads","Tails"]:
            em=discord.Embed(title=f"It's {x}! You Lost!",color=0xff0000)
            em.set_thumbnail(url="https://i.gifer.com/Fw3P.gif")
            await ctx.response.send_message(embed=em)
            await addmoney(ctx,ctx.user,-amount)
    else:
        ctx.reply("You don't have enough balance!")
        
async def moncolor(u):
    colors = {
        "Normal": "BFB97F",
        "Fighting": "D32F2E",
        "Flying": "9E87E1",
        "Poison": "AA47BC",
        "Ground": "DFB352",
        "Rock": "BDA537",
        "Bug": "98B92E",
        "Ghost": "7556A4",
        "Steel": "B4B4CC",
        "Fire": "E86513",
        "Water": "2196F3",
        "Grass": "4CB050",
        "Electric": "FECD07",
        "Psychic": "EC407A",
        "Ice": "80DEEA",
        "Fairy": "F483BB",
        "Dark": "5C4038",
        "Dragon": "673BB7"
    }

    if u in colors:
        return int(colors[u], 16)
    else:
        return int("FFFFFF", 16)
    
@bot.tree.command(name="pokedex",description="Shows pokédex entry and infos.")
async def pokedex(ctx:discord.Interaction,name:str):
    await ctx.response.defer(thinking=True)
    shiny=""
    name=name.title()
    if "Shiny " in name:
        name=name.replace("Shiny ","")
        shiny="Yes"
    db=sqlite3.connect("pokemondata.db")
    c=db.cursor()   
    dt=sqlite3.connect("owned.db")
    cx=dt.cursor()
    c.execute(f"select * from 'wild' where Name='{name}'")
    p=c.fetchone() 
    cx.execute(f"select * from '{ctx.user.id}' where name='{name}'")
    ch=cx.fetchall()
    text=""
    if len(ch)==0:
        text=f"<:cross:1133677258398257193> You haven't caught any {name} yet!"
    if len(ch)>0:
        text=f"<:tick:1133677303407325286> You have caught {len(ch)} {name}!"
    if p: 
        total=p[4]+p[5]+p[6]+p[7]+p[8]+p[9]
        sprite=p[12]
        if shiny=="Yes":
            sprite=sprite.replace("http://play.pokemonshowdown.com/sprites/ani/","http://play.pokemonshowdown.com/sprites/ani-shiny/")
        name=p[0]
        rare=p[14]
        types=await typeicon(p[1])
        clr=await moncolor(p[1])
        ht=p[25]
        ft="0'00\""
        if ht!=None:
            ft=await heightcon(ht)
        if p[2]!="???":
            types=f"{await typeicon(p[1])}{await typeicon(p[2])}"
            clr=await moncolor(random.choice([p[1],p[2]]))
        m=await typesheet(p[1],p[2])
        W2 = "".join([await typeicon(i) for i in m[0]])
        W4 = "".join([await typeicon(i) for i in m[1]])
        IM = "".join([await typeicon(i) for i in m[2]])   
        R2 = "".join([await typeicon(i) for i in m[3]])   
        R4 = "".join([await typeicon(i) for i in m[4]])    
        data=discord.Embed(title=f"{p[22]} {name}",description=f"{p[23]} Pokémon", color=clr)
        data.add_field(name="__Infos:__",value=f"**__Types:__** {types}\n**__Abilities:__** {p[11].replace(',','/')}\n**__Rarity:__** {rare}\n**__Weight:__** {p[13]} lbs ({await lbskg(p[13])} kg)\n**__Height:__** {ft} ({ht} m)\n**__Region:__** {p[16]}\n**__Egg Group:__** {p[18]}")
        data.add_field(name=f"__Base Stats:__ {total}",value=f"""**__HP:__** {p[4]}\n**__Attack:__** {p[5]}\n**__Defense:__** {p[6]}\n**__Sp. Atk:__** {p[7]}\n**__Sp. Def:__** {p[8]}\n**__Speed:__** {p[9]}""")
        data.set_thumbnail(url="https://cdn.discordapp.com/attachments/1127110331408318496/1127136147156500580/1688800580902.png")
        if p[20]!="None" and '-' in p[20]:
            data.add_field(name="__Evolution:__",value=f"Evolves into {await pokeicon(p[20].split('-')[0])} {p[20].split('-')[0]} after reaching Lv.{p[20].split('-')[1]}",inline=False)
        if p[19]!="None":
            data.add_field(name="__Dex Entry:__",value=p[19],inline=False)
        if len(W4)>0:    
            data.add_field(name="4x Weakness:",value=f"{W4}",inline=False)  
        if len(W2)>0:    
            data.add_field(name="2x Weakness:",value=f"{W2}",inline=False)
        if len(R2)>0:    
            data.add_field(name="2x Resistance:",value=f"{R2}",inline=False)
        if len(R4)>0:    
            data.add_field(name="4x Resistance:",value=f"{R4}",inline=False)  
        if len(IM)>0:    
            data.add_field(name="Immune to:",value=f"{IM}",inline=False)                  
        data.add_field(name="__Entry:__",value=text)   
        data.set_image(url=sprite) 
        await ctx.followup.send(embed=data)
        
@bot.tree.command(name="movedex", description="Shows move infos.")
async def movedex(ctx: discord.Interaction, name: str):
    # Standardize the name input for database lookup
    name = name.title()

    # Use async with for connection and cursor
    async with aiosqlite.connect("pokemondata.db") as db:
        # Aiosqlite allows executing SQL directly on the connection object (db)
        # Use a parameterized query to prevent SQL injection (better practice)
        
        # Use .fetchone() directly from the connection object for a simple query
        cursor = await db.execute("SELECT * FROM moves WHERE Name=?", (name,))

        # Use fetchone() on the Cursor object to get the single row
        p = await cursor.fetchone()

    # Check if a move was found
    if p:
        # p is a tuple (MoveName, Description, Power, PP, Accuracy, ...)
        
        # Assuming the external functions are defined asynchronously:
        move_name = p[0]
        description = p[1]
        power = p[2]
        pp = p[3]
        accuracy = p[4]

        # Fetch external values
        clr = await movecolor(move_name)
        type_icon = await movetypeicon(None, move_name) # Assuming this function takes 'None' or the Type string
        category = await movect(move_name)
        
        # Create and send the embed
        data = discord.Embed(
            title=move_name,
            description=description,
            color=clr
        )
        
        # Add fields
        data.add_field(name='Power:', value=power, inline=False)
        data.add_field(name='PP:', value=pp, inline=False)
        data.add_field(name='Accuracy:', value=accuracy, inline=False)
        data.add_field(name='Type:', value=type_icon, inline=False)
        data.add_field(name='Category:', value=category, inline=False)
        
        await ctx.response.send_message(embed=data)
    else:
        # Handle case where the move is not found
        await ctx.response.send_message(f"❌ Move **{name}** not found in the MoveDex.", ephemeral=True) 
              
@bot.tree.command(name="spawn",description="Spawns a pokémon.")   
async def spawn(ctx:discord.Interaction):
    dn=sqlite3.connect("playerdata.db")
    cn=dn.cursor()
    cn.execute(f"select * from '{ctx.user.id}'")
    mmm=cn.fetchone()
    money=mmm[0]
    if money>=500:
        await addmoney(ctx,ctx.user,-500)
        dx=sqlite3.connect("playerdata.db")
        ct=dx.cursor()
        ct.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{ctx.user.id}' ")
        if ct.fetchone():
            db=sqlite3.connect("pokemondata.db")
            dt=sqlite3.connect("owned.db")
            cx=dt.cursor()
            c=db.cursor()
            select=random.choices(["Common","Uncommon","Rare","Very Rare","Common Legendary","Ultra Beasts","Legendary","Mythical"],weights=[1500,500,150,50,5,10,1,3],k=1)[0]
            c.execute(f"select * from 'wild' where Rarity='{select}'")
            x=c.fetchall()
            m=random.choice(x)
            tch=random.randint(1,25)
            ach=random.randint(1,50)
            tera="???"
            extra=""
            turl=""
            shinyodd=random.randint(1,1024)
            shiny="No"
            maxiv="No"
            item="None"
            itemodd=random.randint(1,100)
            if itemodd<25:
                item=random.choice(m[17].split(","))
            if shinyodd==7:
                shiny="Yes"
            if ach==7 and select not in ("Common Legendary","Legendary","Mythical"):
                maxiv="Alpha"
                turl="https://cdn.discordapp.com/attachments/1102579499989745764/1103318414795219024/20230503_195314.png"
                extra=" This pokémon seems larger than usual!"
            if tch==7:
                tera=random.choice(("Rock","Fire","Water","Grass","Electric","Ground","Flying","Fighting","Fairy","Dragon","Steel","Poison","Dark","Ghost","Normal","Bug","Ice","Psychic","Stellar"))
                if 'Terapagos' in m[0]:
                    tera='Stellar'
                if tera not in (m[1],m[2]):
                    extra=" Seems like it has a different Tera-Type!"
                    if tera!='Stellar':
                        turl=f"https://play.pokemonshowdown.com/sprites/types/Tera{tera}.png"
                    elif tera=='Stellar':
                        turl='https://cdn.discordapp.com/attachments/1151371872815034370/1187805155249373215/20231222_230941.png'
            p=Pokemon(name=m[0],primaryType=m[1],secondaryType=m[2],level=100,hp=m[4],atk=m[5],defense=m[6],spatk=m[7],spdef=m[8],speed=m[9],moves=m[10], ability=m[11],sprite=m[12],gender=m[15],tera=tera,shiny=shiny,maxiv=maxiv,item=item)
            #level=random.randint(1,m[3])
            types=p.primaryType
            if p.secondaryType!="???":
                types=f"{p.primaryType}/{p.secondaryType}"
            p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
            p.totalev=(p.hpev+p.atkev+p.defev+p.spatkev+p.spdefev+p.speedev)    
            wild=discord.Embed(title=f"A wild pokémon has appeared!{extra}")
            if (tch<10 and tera not in (m[1],m[2])) or "Alpha" in p.nickname:
                wild.set_thumbnail(url=f"{turl}")
            try:
                wild.set_image(url=p.sprite)
            except:
                wild.add_field(name="Network Error!",value=f"Answer: {p.name}")
            wild.set_footer(text="Guess it's full name to capture it!")
            flee=discord.Embed(title=f"The wild {p.name} fled!")
            flee.set_image(url=p.sprite)
            flee.set_footer(text="Try again later!")
            await ctx.response.send_message(embed=wild)
            try:
                while True:
                    guess = await bot.wait_for('message',timeout=60)
                    if "hint" in guess.content:
                        ch=random.randint(1,5)
                        hint=p.name
                        if ch==4:
                            hint=p.ability
                        elif ch==3:
                            hint=p.secondaryType
                        elif ch==2:
                            hint=p.primaryType
                        elif ch==1:
                            n=list(p.name.lower())
                            random.shuffle(n)
                            hint="".join(n)
                        await ctx.channel.send(f" Hint: {hint}")
                    if p.name.lower().split()[-1] in guess.content.lower():
                        p.moves=f"{p.moves}"
                        cx.execute(f"""CREATE TABLE IF NOT EXISTS [{guess.author.id}] (
                    Name text,
                    Nickname text,
                    Level integer,
                    hpiv integer,
                    atkiv integer,
                    defiv integer,
                    spatkiv integer,
                    spdefiv integer,
                    speediv integer,
                    hpev integer,
                    atkev integer,
                    defev integer,
                    spatkev integer,
                    spdefev integer,
                    speedev integer,
                    ability text,
                    nature text,
                    shiny text,
                    item text,
                    gender text,
                    teratype text,
                    maxiv text,
                    moves text,
                    rarity text,
                    time text,
                    totaliv integer,
                    egg text)""")
                        clk=datetime.datetime.now()
                        catchtime=clk.strftime("%Y-%m-%d %H:%M:%S")
                        if p.shiny=="Yes" or m[14] in ["Ultra Beasts","Common Legendary","Legendary","Mythical"]:
                            dt.commit()
                            cx.execute(f"""INSERT INTO "1084473178400755772" VALUES (
                    "{p.name}",
                    "{p.nickname}",
                    "{p.level}",
                    "{p.hpiv}",
                    "{p.atkiv}",
                    "{p.defiv}",
                    "{p.spatkiv}",
                    "{p.spdefiv}",
                    "{p.speediv}",
                    "{p.hpev}",
                    "{p.atkev}",
                    "{p.defev}",
                    "{p.spatkev}",
                    "{p.spdefev}",
                    "{p.speedev}",
                    "{p.ability}",
                    "{p.nature}",
                    "{p.shiny}",
                    "{p.item}",
                    "{p.gender}",
                    "{p.tera}",
                    "Custom",
                    "{p.moves}",
                    "{m[14]}",
                    "{catchtime}",
                    "{p.totaliv}",
                    "{m[18]}")""")
                            dt.commit()                    
                        cx.execute(f"""INSERT INTO "{guess.author.id}" VALUES (
                    "{p.name}",
                    "{p.nickname}",
                    "{p.level}",
                    "{p.hpiv}",
                    "{p.atkiv}",
                    "{p.defiv}",
                    "{p.spatkiv}",
                    "{p.spdefiv}",
                    "{p.speediv}",
                    "{p.hpev}",
                    "{p.atkev}",
                    "{p.defev}",
                    "{p.spatkev}",
                    "{p.spdefev}",
                    "{p.speedev}",
                    "{p.ability}",
                    "{p.nature}",
                    "{p.shiny}",
                    "{p.item}",
                    "{p.gender}",
                    "{p.tera}",
                    "Custom",
                    "{p.moves}",
                    "{m[14]}",
                    "{catchtime}",
                    "{p.totaliv}",
                    "{m[18]}")""")
                        dt.commit()
                        db.commit()
                        catch="caught"
                        if ctx.user!=guess.author:
                            catch="sniped"
                        await guess.reply(f"{guess.author.display_name} {catch} a level {p.level} {p.nickname} (IV: {p.totaliv}%)!")
                        if p.item!="None":
                            await ctx.channel.send(f"{p.name} is holding a {p.item}!")
                        if guess.author==ctx.user:
                            await addmoney(ctx,ctx.user,250)
                        if guess.author!=ctx.user:
                            await addmoney(ctx,guess.author,-750)
                        break                             
            except:             
                await ctx.channel.send(embed=flee)
        else:
            await ctx.channel.send("You don't have an account. Type `/start` to create an account.")              
    else:
        await ctx.channel.send("You don't have enough money.") 
                
@bot.tree.command(name="cheat", description="Enter a secret code (if you have one).")
@app_commands.describe(code="The secret cheat code to enter.")
async def cheat_slash(interaction: discord.Interaction, code: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    if code == "tsilverw7":
        # Pass None for the 'ctx' argument to prevent addmoney from sending a public message
        await addmoney(None, interaction.user, 1000000) 
        await interaction.followup.send("💰 Success! You received 1,000,000 Pokécoins!", ephemeral=True)
    else:
        await interaction.followup.send("❌ Invalid code. Better luck next time!", ephemeral=True)
               
async def sortbadge(bdg_list: List[str]) -> List[str]:
    # Placeholder for your badge sorting logic
    return sorted(bdg_list)

# --- View Class for Pagination ---

class BadgesView(discord.ui.View):
    def __init__(self, user_id: int, bdg_list: List[str], max_per_page: int = 10):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.bdg_list = bdg_list
        self.max_per_page = max_per_page
        self.current_page = 1
        
        # Calculate total pages
        self.total_pages = (len(bdg_list) + max_per_page - 1) // max_per_page
        
        # Disable buttons if only one page exists
        if self.total_pages <= 1:
            self.children[0].disabled = True  # Previous
            self.children[1].disabled = True  # Next

    # --- Pagination Logic ---
    def get_page_content(self) -> discord.Embed:
        # Re-establish DB connection for each page generation (safer in async callbacks)
        dt = sqlite3.connect("pokemondata.db")
        ct = dt.cursor()
        
        tex = ""
        start = (self.current_page - 1) * self.max_per_page
        end = min(self.current_page * self.max_per_page, len(self.bdg_list))
        
        # If the page is valid but empty (shouldn't happen if logic is correct)
        if start >= len(self.bdg_list):
            self.current_page = 1
            return self.get_page_content() # Recursively call page 1

        for i in range(start, end):
            # bdg_list[i] is the symbolname
            ct.execute(f"select symbolname, icon, name from 'Trainers' where symbolname='{self.bdg_list[i]}'")
            # Assuming jj[2] is icon, jj[1] is name in your original code
            jj = ct.fetchone() 
            if jj:
                 # Check if the structure is jj[2]=icon and jj[1]=name
                tex += f"{jj[1]} {jj[2]}\n"  # Adjust indexing based on your DB columns
        
        dt.close()
        
        # Update button states
        self.children[0].disabled = (self.current_page == 1)      # Previous button
        self.children[1].disabled = (self.current_page == self.total_pages) # Next button

        # Create the embed
        bd = discord.Embed(
            title=f"Badges: {len(self.bdg_list)} Total",
            description=tex if tex else "No badges found on this page."
        )
        bd.set_footer(text=f"Page {self.current_page} of {self.total_pages}")
        
        return bd

    # --- Button Callbacks ---

    @discord.ui.button(label="<", style=discord.ButtonStyle.blurple, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            embed = self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label=">", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages:
            self.current_page += 1
            embed = self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only the user who ran the command can use the buttons
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This badge viewer is not for you!", ephemeral=True)
            return False
        return True
        
@bot.tree.command(name="badges", description="Shows the badges you have collected.")
async def badges(ctx: discord.Interaction): # Removed page argument as it's handled by the view
    db = sqlite3.connect("playerdata.db")
    c = db.cursor()
    c.execute(f"select data_column_for_badges from '{ctx.user.id}'")
    dat = c.fetchone()
    db.close() # Close connection immediately

    # dat[6] is assumed to be the column index for the comma-separated badge string
    badge_data = dat[6] if dat and len(dat) > 6 else "None" # Safe indexing

    if badge_data == "None" or not badge_data.strip():
        await ctx.response.send_message("You haven't collected any badges yet! 🏅", ephemeral=True)
        return

    bdg = badge_data.split(",")
    # You MUST await your sortbadge function
    bdg = await sortbadge(bdg) 

    # Initialize the View
    view = BadgesView(ctx.user.id, bdg)
    
    # Get the content for the first page
    initial_embed = view.get_page_content()

    # Send the initial response with the buttons
    await ctx.response.send_message(embed=initial_embed, view=view)
        
@bot.tree.command(name="start",description="Start the game.")
async def start(ctx:discord.Interaction):
    "Starts the game for you and creates your account."
    dt=sqlite3.connect("playerdata.db")
    ct=dt.cursor()
    ct.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{ctx.user.id}' ")
    if ct.fetchone():
        await ctx.response.send_message("You already have an account!")
    else:
        ct.execute(f"""CREATE TABLE IF NOT EXISTS [{ctx.user.id}] (
        Balance integer,
        Squad text,
        Items text,
        creationdate text,
        winstreak integer,
        highstreak integer,
        badges text
        )""")
        clk=datetime.datetime.now()
        ca=clk.strftime("%Y-%m-%d %H:%M:%S")
        ct.execute(f"""INSERT INTO "{ctx.user.id}" VALUES (
        10000,
        "0,0,0,0,0,0",
        "[]",
        "{ca}",
        0,
        0,
        "None")""")
        dt.commit()
        await ctx.response.send_message("Account created successfully.")
        db=sqlite3.connect("pokemondata.db")
        dx=sqlite3.connect("owned.db")
        c=db.cursor()
        cx=dx.cursor()
        ann=discord.Embed(title="Choose your starter:", description="Enter the fullname of the starter to claim it.")
        ann.add_field(name="Kanto",value="<:venusaur:1127115228660903946> Venusaur\n<:charizard:1127547984893186208> Charizard\n<:blastoise:1127191979768430653> Blastoise")
        ann.add_field(name="Johto",value="<:meganium:1129640030177087650> Meganium\n<:typh:1132296209302831154> Typhlosion\n<:feraligatr:1129262800267661353> Feraligatr")
        ann.add_field(name="Hoenn",value="<:sceptile:1129989351422574662> Sceptile\n<:blaziken:1127192016783163442> Blaziken\n<:swampert:1130780356166037504> Swampert")
        ann.add_field(name="Sinnoh",value="<:torterra:1131074386431066122> Torterra\n<:infernape:1129334188286427166> Infernape\n<:empoleon:1127922322012123157> Empoleon")
        ann.add_field(name="Unova",value="<:serperior:1130286563025240094> Serperior\n<:emboar:1127922180395634710> Emboar\n<:samurott:1129985096628326421> Samurott")
        ann.add_field(name="Kalos",value="<:chesnaught:1127548059014938665> Chesnaught\n<:delphox:1127709319815766076> Delphox\n<:greninja:1129305368271540335> Greninja")
        ann.add_field(name="Alola",value="<:decidueye:1127709077821214781> Decidueye\n<:incineroar:1129334128370798673> Incineroar\n<:primarina:1129742315305566270> Primarina")
        ann.add_field(name="Galar",value="<:rillaboom:1129959201792327821> Rillaboom\n<:cinderace:1127549451075059812> Cinderace\n<:inteleon:1129334218829353012> Inteleon")
        ann.add_field(name="Paldea",value="<:meowscarada:1129640128940363826> Meowscarada\n<:skeledirge:1130708795522289674> Skeledirge\n<:quaquaval:1129744913072930816> Quaquaval")
        ann.set_footer(text="You have to enter the full name to claim your starter.")
        await ctx.channel.send(embed=ann)
        while True:
            guess=await bot.wait_for('message',check=lambda message: message.author==ctx.user)
            nam=guess.content.strip().title()
            if nam in "Venusaur\nCharizard\nBlastoiseMeganium\nTyphlosion\nFeraligatrSceptile\nBlaziken\nSwampertTorterra\nInfernape\nEmpoleonSerperior\nEmboar\nSamurottChesnaught\nDelphox\nGreninjaDecidueye\nIncineroar\nPrimarinaRillaboom\nCinderace\nInteleonMeowscarada\nSkeledirge\nQuaquaval":
                c.execute(f"Select * from 'wild' where name='{nam}'")
                m=c.fetchone()
                if m!=None and len(m)!=0:
                    shinyodd=random.randint(1,512)
                    shiny="No"
                    if shinyodd==7:
                        shiny="Yes"
                    p=Pokemon(name=m[0],primaryType=m[1],secondaryType=m[2],level=m[3],hp=m[4],atk=m[5],defense=m[6],spatk=m[7],spdef=m[8],speed=m[9],moves=m[10], ability=m[11],sprite=m[12],gender=m[15],shiny=shiny)
                    p.moves=f"{p.moves}"
                    p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
                    cx.execute(f"""CREATE TABLE IF NOT EXISTS [{ctx.user.id}] (
                    Name text,
                    Nickname text,
                    Level integer,
                    hpiv integer,
                    atkiv integer,
                    defiv integer,
                    spatkiv integer,
                    spdefiv integer,
                    speediv integer,
                    hpev integer,
                    atkev integer,
                    defev integer,
                    spatkev integer,
                    spdefev integer,
                    speedev integer,
                    ability text,
                    nature text,
                    shiny text,
                    item text,
                    gender text,
                    teratype text,
                    maxiv text,
                    moves text,
                    rarity text,
                    time text,
                    totaliv integer,
                    egg text)""")
                    clk=datetime.datetime.now()
                    catchtime=clk.strftime("%Y-%m-%d %H:%M:%S")
                    cx.execute(f"""INSERT INTO "{ctx.user.id}" VALUES (
                    "{p.name}",
                    "{p.nickname}",
                    "{p.level}",
                    "{p.hpiv}",
                    "{p.atkiv}",
                    "{p.defiv}",
                    "{p.spatkiv}",
                    "{p.spdefiv}",
                    "{p.speediv}",
                    "{p.hpev}",
                    "{p.atkev}",
                    "{p.defev}",
                    "{p.spatkev}",
                    "{p.spdefev}",
                    "{p.speedev}",
                    "{p.ability}",
                    "{p.nature}",
                    "{p.shiny}",
                    "{p.item}",
                    "{p.gender}",
                    "{p.tera}",
                    "Custom",
                    "{p.moves}",
                    "{m[14]}",
                    "{catchtime}",
                    "{p.totaliv}",
                    "{m[18]}")""")
                    dx.commit()
                    db.commit()
                    show=discord.Embed(title=f"Congratulations {ctx.user.display_name}! You chose {p.name} as your starter!")
                    show.set_thumbnail(url=ctx.user.avatar)
                    show.set_image(url=p.sprite)
                    show.set_footer(text="Enter '/pokeinfo' to see more details or '/spawn' to start catching pokémons.")
                    await ctx.channel.send(embed=show)
                    break     
                   
@bot.tree.command(name="marketlist",description="Lists pokémon in market.")
async def marketlist(ctx:discord.Interaction,num:int=1,cost:int=1):
    db=sqlite3.connect("owned.db")
    c=db.cursor()
    dt=sqlite3.connect("pokemondata.db")
    ct=dt.cursor()
    num=await row(ctx,num,c)
    p, allmon, mon, spc=await pokonvert(ctx,ctx.user,num)
    ct.execute(f"select * from 'wild' where name='{p.name}'")
    m=ct.fetchone()
    p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
    p.totalev=(p.hpev+p.atkev+p.defev+p.spatkev+p.spdefev+p.speedev)  
    types=await typeicon(p.primaryType)
    clr=await moncolor(p.tera)
    if p.secondaryType!="???":
        types=f"{await typeicon(p.primaryType)}{await typeicon(p.secondaryType)}"
    infos=discord.Embed(title=f"Do you want to list {p.nickname} on Pokémon Market for {await numberify(cost)} <:pokecoin:1134595078892044369>?", description=f"""**Types:** {types}\n**Tera-Type:** {await teraicon(p.tera)}\n**Ability:** {p.ability}\n**Nature:** {p.nature}\n**Gender:** {await statusicon(p.gender)}\n**Held Item:** {await itemicon(p.item)} {p.item}\n**HP:** {p.maxhp} - IV: {p.hpiv}/31 - EV: {p.hpev}\n**Attack:** {p.maxatk} - IV: {p.atkiv}/31 - EV: {p.atkev}\n**Defense:** {p.maxdef} - IV: {p.defiv}/31 - EV: {p.defev}\n**Sp. Atk:** {p.maxspatk} - IV: {p.spatkiv}/31 - EV: {p.spatkev}\n**Sp. Def:** {p.maxspdef} - IV: {p.spdefiv}/31 - EV: {p.spdefev}\n**Speed:** {p.maxspeed} - IV: {p.speediv}/31 - EV: {p.speedev}\n**Total IV %:** {p.totaliv}%\n**Total EV :** {p.totalev}/508""",color=clr)
    infos.set_image(url=p.sprite)
    await ctx.response.send_message(embed=infos)
    while True:
        response=await bot.wait_for('message', check=lambda message: message.author == ctx.user)
        if response.content.lower() in ["no","n"]:
            await ctx.channel.send("Listing canceled.")
            break
        elif response.content.lower() in ["yes","y"]:
            code="abcdefghijklmnopqrstuvwxyz0123456789"
            gen="".join(random.choices(code,k=5))
            db=sqlite3.connect("market.db")
            dx=sqlite3.connect("owned.db")
            c=db.cursor()
            cx=dx.cursor()
            c.execute(f"""CREATE TABLE IF NOT EXISTS "market" (
                    Name text,
                    Nickname text,
                    Level integer,
                    hpiv integer,
                    atkiv integer,
                    defiv integer,
                    spatkiv integer,
                    spdefiv integer,
                    speediv integer,
                    hpev integer,
                    atkev integer,
                    defev integer,
                    spatkev integer,
                    spdefev integer,
                    speedev integer,
                    ability text,
                    nature text,
                    shiny text,
                    item text,
                    gender text,
                    teratype text,
                    maxiv text,
                    moves text,
                    rarity text,
                    time text,
                    totaliv integer,
                    price integer,
                    sellerid integer,
                    serialno text,
                    egg text)""")
            db.commit()
            c.execute(f"""INSERT INTO "market" VALUES (
                    "{p.name}",
                    "{p.nickname}",
                    "{p.level}",
                    "{p.hpiv}",
                    "{p.atkiv}",
                    "{p.defiv}",
                    "{p.spatkiv}",
                    "{p.spdefiv}",
                    "{p.speediv}",
                    "{p.hpev}",
                    "{p.atkev}",
                    "{p.defev}",
                    "{p.spatkev}",
                    "{p.spdefev}",
                    "{p.speedev}",
                    "{p.ability}",
                    "{p.nature}",
                    "{p.shiny}",
                    "{p.item}",
                    "{p.gender}",
                    "{p.tera}",
                    "Custom",
                    "{p.moves}",
                    "Traded",
                    "{p.catchdate}",
                    "{p.totaliv}",
                    "{cost}",
                    "{ctx.user.id}",
                    "{gen}",
                    "{m[18]}")""")
            db.commit()      
            cx.execute(f"delete from '{ctx.user.id}' where rowid={num}")  
            dx.commit()
            await ctx.channel.send(f"{p.nickname} was listed on the Pokémon Market successfully!")
            break
        else:
            break
        
@bot.tree.command(name="marketinfo",description="Shows infos about particular pokémon in market.")
async def marketinfo(ctx:discord.Interaction,code:str):
    dt = sqlite3.connect("pokemondata.db")
    db = sqlite3.connect("market.db")
    cx = dt.cursor()
    c = db.cursor()
    allmon = []
    c.execute(f"SELECT * FROM 'market' where serialno='{code}'")
    n = c.fetchone()
    cx.execute(f"SELECT * FROM 'wild' WHERE name=?", (n[0],))
    m = cx.fetchall()[0]
    p = Pokemon(
        name=m[0],
        nickname=n[1],
        primaryType=m[1],
        secondaryType=m[2],
        level=m[3],
        hp=m[4],
        atk=m[5],
        defense=m[6],
        spatk=m[7],
        spdef=m[8],
        speed=m[9],
        moves=n[22],
        ability=n[15],
        sprite=m[12],
        gender=n[19],
        tera=n[20],
        maxiv="Custom",
        item=n[18],
        shiny=n[17],
        nature=n[16],
        hpiv=n[3],
        atkiv=n[4],
        defiv=n[5],
        spatkiv=n[6],
        spdefiv=n[7],
        speediv=n[8],
        hpev=n[9],
        atkev=n[10],
        defev=n[11],
        spatkev=n[12],
        spdefev=n[13],
        speedev=n[14],
        catchdate=n[24],
        icon=m[22],
        weight=m[13]
    )
    known=""
    for i in p.moves:
        known+=f"{await movetypeicon(p,i)} {i} {await movect(i)}\n"
    if code!=None:
        types=await typeicon(p.primaryType)
        clr=await moncolor(p.tera)
        if p.secondaryType!="???":
            types=f"{await typeicon(p.primaryType)}{await typeicon(p.secondaryType)}"
        p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
        p.totalev=(p.hpev+p.atkev+p.defev+p.spatkev+p.spdefev+p.speedev)  
        infos=discord.Embed(title=f"#{code} {p.nickname} Lv.{p.level}", description=f"""**Types:** {types}\n**Tera-Type:** {await teraicon(p.tera)}\n**Ability:** {p.ability}\n**Nature:** {p.nature}\n**Gender:** {await statusicon(p.gender)}\n**Held Item:** {await itemicon(p.item)} {p.item}\n**OT:** {(await bot.fetch_user(n[27])).display_name}\n**<:hp:1140877395050647613>HP:** {p.maxhp} - IV: {p.hpiv}/31 - EV: {p.hpev}\n**<:attack:1140877438746890280>ATK:** {p.maxatk} - IV: {p.atkiv}/31 - EV: {p.atkev}\n**<:defense:1140877538072203344>DEF:** {p.maxdef} - IV: {p.defiv}/31 - EV: {p.defev}\n**<:spatk:1140877607185956954>SPA:** {p.maxspatk} - IV: {p.spatkiv}/31 - EV: {p.spatkev}\n**<:spdef:1140877582691209286>SPD:** {p.maxspdef} - IV: {p.spdefiv}/31 - EV: {p.spdefev}\n**<:speed:1140877488055128115>SPE:** {p.maxspeed} - IV: {p.speediv}/31 - EV: {p.speedev}\n**Total IV %:** {p.totaliv}%\n**Total EV :** {p.totalev}/508\n**Price:** {await numberify(n[26])} <:pokecoin:1134595078892044369>""",color=clr)
        infos.set_author(name=(await bot.fetch_user(n[27])).display_name,icon_url=(await bot.fetch_user(n[27])).avatar)
        infos.add_field(name="Moves:",value=known)
        infos.set_image(url=p.sprite)
        await ctx.response.send_message(embed=infos)  


class PokeInfoView(discord.ui.View):
    def __init__(self, ctx: discord.Interaction, current_index: int, total_pokemon: int):
        super().__init__(timeout=180)
        self.ctx = ctx
        self.current_index = current_index
        self.total_pokemon = total_pokemon
        
        # Disable buttons if at the edge
        if self.current_index == 1:
            self.children[0].disabled = True  # Previous button
        if self.current_index == self.total_pokemon:
            self.children[1].disabled = True  # Next button

    # --- Button Callbacks ---

    async def update_message(self, interaction: discord.Interaction):
        # Ensure only the original user can interact
        if interaction.user != self.ctx.user:
            return await interaction.response.send_message("This isn't your information panel!", ephemeral=True)
            
        # 1. Defer the interaction
        await interaction.response.defer()

        # 2. Use aiosqlite for the connection
        async with aiosqlite.connect("owned.db") as db:
            
            # 3. Create a cursor to pass to the asynchronous row function
            async with db.cursor() as c:
                row_id = await row(self.ctx, self.current_index, c) 
            p, allmon, mon, spc = await pokonvert(self.ctx, self.ctx.user, row_id) # row_id is the actual ID needed
        
        await db.close()

        # 3. Rebuild the embed content (identical to the original logic)
        known = ""
        for i in p.moves:
            known += f"{await movetypeicon(p,i)} {i} {await movect(i)}\n"
            
        types = await typeicon(p.primaryType)
        clr = await moncolor(p.tera)
        if p.secondaryType != "???":
            types = f"{await typeicon(p.primaryType)}{await typeicon(p.secondaryType)}"
        
        p.totaliv = round(((p.hpiv + p.atkiv + p.defiv + p.spatkiv + p.spdefiv + p.speediv) / 186) * 100, 2)
        p.totalev = (p.hpev + p.atkev + p.defev + p.spatkev + p.spdefev + p.speedev) 
        
        infos = discord.Embed(
            title=f"#{self.current_index} {p.nickname} Lv.{p.level}", 
            description=f"""**Types:** {types}\n**Tera-Type:** {await teraicon(p.tera)}\n**Nature:** {p.nature}\n**Gender:** {await statusicon(p.gender)}\n**Held Item:** {await itemicon(p.item)} {p.item}\n**<:hp:1140877395050647613>HP:** {p.maxhp} - IV: {p.hpiv}/31 - EV: {p.hpev}\n**<:attack:1140877438746890280>ATK:** {p.maxatk} - IV: {p.atkiv}/31 - EV: {p.atkev}\n**<:defense:1140877538072203344>DEF:** {p.maxdef} - IV: {p.defiv}/31 - EV: {p.defev}\n**<:spatk:1140877607185956954>SPA:** {p.maxspatk} - IV: {p.spatkiv}/31 - EV: {p.spatkev}\n**<:spdef:1140877582691209286>SPD:** {p.maxspdef} - IV: {p.spdefiv}/31 - EV: {p.spdefev}\n**<:speed:1140877488055128115>SPE:** {p.maxspeed} - IV: {p.speediv}/31 - EV: {p.speedev}\n**Total IV %:** {p.totaliv}%\n**Total EV :** {p.totalev}/508\n**Ability:** {p.ability}\n{await abilitydesc(p.ability)}""",
            color=clr
        )
        infos.set_author(name=self.ctx.user.display_name, icon_url=self.ctx.user.avatar)
        infos.add_field(name="Moves:", value=known)
        infos.set_image(url=p.sprite)
        infos.set_footer(text=f"Catching Date: {p.catchdate}\nDisplaying Pokémon: {self.current_index}/{self.total_pokemon}")

        # 6. Create a new view instance to update button state
        new_view = PokeInfoView(self.ctx, self.current_index, self.total_pokemon)

        # 7. Edit the original message
        await interaction.edit_original_response(embed=infos, view=new_view)


    # The 'Previous' button
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.blurple, emoji="⬅️")
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.user:
            return await interaction.response.send_message("This isn't your information panel!", ephemeral=True)
            
        if self.current_index > 1:
            self.current_index -= 1
        
        await self.update_message(interaction)


    # The 'Next' button
    @discord.ui.button(label="Next", style=discord.ButtonStyle.blurple, emoji="➡️")
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.user:
            return await interaction.response.send_message("This isn't your information panel!", ephemeral=True)
            
        if self.current_index < self.total_pokemon:
            self.current_index += 1
            
        await self.update_message(interaction)

    # Handle the view timeout
    async def on_timeout(self):
        # Disable all components when the view times out
        for item in self.children:
            item.disabled = True   
            
@bot.tree.command(name="pokeinfo", description="Shows infos about particular pokémon.")
async def pokeinfo(ctx: discord.Interaction, num: int = None):
    "Shows infos about your captured pokémons."
    await ctx.response.defer()
    # Use aiosqlite to open the connection asynchronously
    async with aiosqlite.connect("owned.db") as db:
        
        # 1. Get all Pokémon to determine the total count
        # pokonvert is called with None to get the full list (p=None, allmon=list)
        # Assuming pokonvert returns a list of allmon even if p is None
        p, allmon, mon, spc = await pokonvert(ctx, ctx.user, None)
        total_pokemon = len(allmon)

        if total_pokemon == 0:
            # Note: Since the command uses aiosqlite, we don't need to manually close db here
            await ctx.response.send_message(
                "Unfortunately you don't have any Pokémon. Please catch some Pokémon using `/spawn` command.", 
                ephemeral=True
            )
            return

        # 2. Determine the Pokémon Index to Display (1-based)
        if num is not None:
            if not (1 <= num <= total_pokemon):
                await ctx.followup.send(
                    f"Invalid Pokémon number. You only have {total_pokemon} Pokémon (1 to {total_pokemon}).", 
                    ephemeral=True
                )
                return
            current_index = num
        else:
            # Default to the latest (highest index) Pokémon.
            current_index = total_pokemon 

        # 3. Fetch Data for the Selected Index
        # We pass the index (current_index) to get the specific Pokémon data
        p, allmon, n, m = await pokonvert(ctx, ctx.user, current_index)
        
        # This check should ideally not fail if total_pokemon > 0, but is a safety
        if p is None:
            await ctx.edit_original_response("Could not retrieve Pokémon data.", ephemeral=True)
            return

        # --- 4. Build the Embed (UNCHANGED LOGIC) ---
        
        known = ""
        # The list 'p.moves' needs to be checked for validity
        if p.moves and isinstance(p.moves, (list, tuple)):
            for i in p.moves:
                known += f"{await movetypeicon(p, i)} {i} {await movect(i)}\n"
        
        types = await typeicon(p.primaryType)
        clr = await moncolor(p.tera)
        if p.secondaryType != "???":
            types = f"{await typeicon(p.primaryType)}{await typeicon(p.secondaryType)}"
            
        p.totaliv = round(((p.hpiv + p.atkiv + p.defiv + p.spatkiv + p.spdefiv + p.speediv) / 186) * 100, 2)
        p.totalev = (p.hpev + p.atkev + p.defev + p.spatkev + p.spdefev + p.speedev) 
        
        infos = discord.Embed(
            title=f"#{current_index} {p.nickname} Lv.{p.level}", 
            description=f"""**Types:** {types}\n**Tera-Type:** {await teraicon(p.tera)}\n**Nature:** {p.nature}\n**Gender:** {await statusicon(p.gender)}\n**Held Item:** {await itemicon(p.item)} {p.item}\n**<:hp:1140877395050647613>HP:** {p.maxhp} - IV: {p.hpiv}/31 - EV: {p.hpev}\n**<:attack:1140877438746890280>ATK:** {p.maxatk} - IV: {p.atkiv}/31 - EV: {p.atkev}\n**<:defense:1140877538072203344>DEF:** {p.maxdef} - IV: {p.defiv}/31 - EV: {p.defev}\n**<:spatk:1140877607185956954>SPA:** {p.maxspatk} - IV: {p.spatkiv}/31 - EV: {p.spatkev}\n**<:spdef:1140877582691209286>SPD:** {p.maxspdef} - IV: {p.spdefiv}/31 - EV: {p.spdefev}\n**<:speed:1140877488055128115>SPE:** {p.maxspeed} - IV: {p.speediv}/31 - EV: {p.speedev}\n**Total IV %:** {p.totaliv}%\n**Total EV :** {p.totalev}/508\n**Ability:** {p.ability}\n{await abilitydesc(p.ability)}""",
            color=clr
        )
        infos.set_author(name=ctx.user.display_name, icon_url=ctx.user.avatar)
        infos.add_field(name="Moves:", value=known if known else "No moves learned.")
        infos.set_image(url=p.sprite)
        infos.set_footer(text=f"Catching Date: {p.catchdate}\nDisplaying Pokémon: {current_index}/{total_pokemon}")

        # 5. Send Message with View
        view = PokeInfoView(ctx, current_index, total_pokemon)
        
        await ctx.edit_original_response(embed=infos, view=view)

@bot.tree.command(name="marketlists",description="Shows pokémons in market.")
async def marketlists(ctx:discord.Interaction,num:int=1):   
    dt=sqlite3.connect("pokemondata.db")
    ct=dt.cursor()
    db=sqlite3.connect("market.db")
    c=db.cursor()         
    c.execute(f"Select * from 'market' where sellerid={ctx.user.id}")
    n=c.fetchall()
    numbers=[]
    if len(n)!=0:
        for i in n:
            numbers.append(i)
        list_of_lists = []
        list_temp = []
        limit = 10
        # iterate through the list
        i = 0
        while i < len(numbers):
            if len(list_temp) < limit:
                list_temp.append(numbers[i])
                i += 1
            else:
                # when the limit is reached, add the sub-list to the list of lists
                list_of_lists.append(list_temp)
                list_temp = []
        # add the remaining items to the list of lists
        list_of_lists.append(list_temp)
        pages=len(list_of_lists)
        if 0<num<=len(list_of_lists):
            x=discord.Embed(title="Your listings in Pokémon Market:", description=f"There's total {len(n)} Pokémons you listed for sale.",color=0x220022)
            for i in list_of_lists[num-1]:
                c.execute(f"select * from 'market'")
                ll=c.fetchall()
                name=i[1]
                ct.execute(f"Select * from 'wild' where name='{i[0]}'")
                mon=ct.fetchone()
                icon=mon[22]
                ivp=round((i[3]+i[4]+i[5]+i[6]+i[7]+i[8])/1.86,2)
                x.add_field(name=f"#{i[28]} {icon} {name} {await teraicon(i[20])}",value=f"**Gender:** {await statusicon(i[19])} | **Ability:** {i[15]} | **IV:** {ivp}% | **Price:** {await numberify(i[26])} <:pokecoin:1134595078892044369>",inline=False)
            x.set_footer(text=f"Showing {num} out of {len(list_of_lists)} pages.")
            await ctx.response.send_message(embed=x)
            
@bot.tree.command(name="market",description="Shows all of market pokemons.")    
async def market(ctx:discord.Interaction,num:int=1,name:str=None):
    dt=sqlite3.connect("pokemondata.db")
    ct=dt.cursor()
    db=sqlite3.connect("market.db")
    c=db.cursor() 
    if name!=None:        
        name=name.split(" ")
    if name==None:
        c.execute(f"Select * from 'market' order by totaliv DESC")
    if name!=None:
        name=name.title()
    if name!=None and name=="Shiny":
        c.execute(f"Select * from 'market' where shiny='Yes' order by totaliv DESC")
    elif name!=None and name!="Shiny":
        c.execute(f"Select * from 'market' where name='{name}' order by totaliv DESC")
    n=c.fetchall()
    numbers=[]
    if len(n)!=0:
        for i in n:
            numbers.append(i)
        list_of_lists = []
        list_temp = []
        limit = 10
        # iterate through the list
        i = 0
        while i < len(numbers):
            if len(list_temp) < limit:
                list_temp.append(numbers[i])
                i += 1
            else:
                # when the limit is reached, add the sub-list to the list of lists
                list_of_lists.append(list_temp)
                list_temp = []
        # add the remaining items to the list of lists
        list_of_lists.append(list_temp)
        pages=len(list_of_lists)
        if 0<num<=len(list_of_lists):
            x=discord.Embed(title="Pokémon Market:", description=f"There's total {len(n)} Pokémons for sale.",color=0x220022)
            for i in list_of_lists[num-1]:
                c.execute(f"select * from 'market'")
                ll=c.fetchall()
                name=i[1]
                ct.execute(f"Select * from 'wild' where name='{i[0]}'")
                mon=ct.fetchone()
                icon=mon[22]
                ivp=round((i[3]+i[4]+i[5]+i[6]+i[7]+i[8])/1.86,2)
                x.add_field(name=f"**ID:** {i[28]} | {icon} {name} {await teraicon(i[20])}",value=f"**Ability:** {i[15]} | **Nature:** {i[16]}\n**IVs:** {i[3]}-{i[4]}-{i[5]}-{i[6]}-{i[7]}-{i[8]} ({ivp}%)\n**Price:** {await numberify(i[26])} <:pokecoin:1134595078892044369>",inline=False)
            x.set_image(url="https://cdn.discordapp.com/attachments/1102579499989745764/1134736129250300045/image_search_1690612550924.jpg")
            x.set_footer(text=f"Showing {num} out of {len(list_of_lists)} pages.")
            await ctx.response.send_message(embed=x)
            
@bot.tree.command(name="wipepc",description="Wipes all of your pokemons.") 
async def wipepc(ctx:discord.Interaction):
    await ctx.response.send_message("Do you really wanna wipe your pc?\n⚠️ You will lose all your pokémons!")
    response = await bot.wait_for('message', check=lambda message: message.author == ctx.user)
    if response.content.lower() in ["yes"]:
        db=sqlite3.connect("owned.db")
        c=db.cursor()
        c.execute(f"DROP table IF EXISTS '{ctx.user.id}'")
        db.commit()
        ctx.channel.send("Account erased successfully!")
    else:
        pass   
      
@bot.tree.command(name="wipeaccount",description="Wipes your account.")     
async def wipeaccount(ctx:discord.Interaction):
    await ctx.response.send_message("Do you really wanna wipe your account?\n⚠️ You will lose all your items and pokécoins!")
    response = await bot.wait_for('message', check=lambda message: message.author == ctx.user)
    if response.content.lower() in ["yes"]:
        db=sqlite3.connect("playerdata.db")
        c=db.cursor()
        c.execute(f"DROP table IF EXISTS '{ctx.user.id}'")
        db.commit()
        ctx.channel.send("Account erased successfully!")
    else:
        pass  
                  
class PokemonView(discord.ui.View):
    def __init__(self, user_id: int, total_pokemon: int, list_of_pages: List[List[Tuple]], total_pages: int):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.total_pokemon = total_pokemon
        self.list_of_pages = list_of_pages # Pre-paginated Pokémon data
        self.total_pages = total_pages
        self.current_page = 1
        
        self.update_buttons()

    def update_buttons(self):
        # Update button states based on the current page
        self.children[0].disabled = (self.current_page == 1)      # Previous button
        self.children[1].disabled = (self.current_page == self.total_pages or self.total_pages == 0) # Next button
        
        # Disable both if only one page exists
        if self.total_pages <= 1:
            self.children[0].disabled = True
            self.children[1].disabled = True

    async def get_page_content(self) -> discord.Embed:
        # Connect to pokemondata.db to retrieve icons and base info
        dt = sqlite3.connect("pokemondata.db")
        ct = dt.cursor()
        
        # Connect to owned.db to get the global index (k)
        db = sqlite3.connect("owned.db")
        c = db.cursor()
        
        # Get the Pokémon data for the current page
        pokemon_list = self.list_of_pages[self.current_page - 1]
        
        x = discord.Embed(
            title="Pokémon PC", 
            description=f"You've caught {self.total_pokemon} total Pokémons.",
            color=0x220022
        )
        # Use the ID of the user who ran the command
        x.set_author(name=f"Your PC [{self.user_id}]") 
        
        for i in pokemon_list:
            # i is a single Pokémon data tuple (row from owned.db)
            
            # --- Replicate original index finding logic ---
            # NOTE: This is INEFFICIENT, but necessary to match your original numbering logic.
            # It refetches ALL rows just to find the index.
            c.execute(f"Select * from '{self.user_id}'") 
            ll = c.fetchall()
            k = (ll.index(i)) + 1 # k is the Pokémon's overall index in the list
            # ---------------------------------------------

            name = i[1] # Nickname
            
            # Fetch base Pokémon data (for icon)
            ct.execute(f"Select * from 'wild' where name='{i[0]}'")
            mon = ct.fetchone()
            icon = mon[22] if mon and len(mon) > 22 else "❓"
            
            # IV calculation (i[3] through i[8] are the IV values)
            iv_sum = i[3] + i[4] + i[5] + i[6] + i[7] + i[8]
            ivp = round(iv_sum / 1.86, 2)
            
            status_icon = await statusicon(i[19]) # i[19] is Gender
            tera_icon = await teraicon(i[20])     # i[20] is Tera Type
            
            x.add_field(
                name=f"#{k} {icon} {name} {status_icon} {tera_icon}",
                value=f"**Ability:** {i[15]} | **Nature:** {i[16]}\n**IVs:** {i[3]}-{i[4]}-{i[5]}-{i[6]}-{i[7]}-{i[8]} ({ivp}%)",
                inline=False
            )
            
        x.set_footer(text=f"Showing page {self.current_page} of {self.total_pages}.")
        
        db.close()
        dt.close()
        return x

    # --- Button Callbacks ---

    @discord.ui.button(label="< Previous", style=discord.ButtonStyle.blurple, disabled=True)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_buttons()
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    @discord.ui.button(label="Next >", style=discord.ButtonStyle.blurple)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_buttons()
            embed = await self.get_page_content()
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.defer()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only the user who ran the command can use the buttons
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This PC viewer is not for you!", ephemeral=True)
            return False
        return True

@bot.tree.command(name="pokemons",description="Shows all the pokémons in your PC.")
@app_commands.describe(name="Filter by 'Shiny', 'IV', Egg Group, or Pokémon name.")
async def pokemons(ctx:discord.Interaction, name:str=None): 
    # NOTE: The 'page' argument is removed as the view handles it internally.
    
    await ctx.response.defer(thinking=True) # Defer the response as DB lookups can be slow

    dt = sqlite3.connect("pokemondata.db")
    ct = dt.cursor()
    db = sqlite3.connect("owned.db")
    c = db.cursor() 
    
    user_id = ctx.user.id
    
    # --- 1. Filter Logic (Original Logic Preserved) ---
    sql_query = f"Select * from '{user_id}'"
    
    if name is None:
        pass # Selects all
    else:
        name = name.title()
        egg_groups = ["Monster","Human-Like","Water 1","Water 2","Water 3","Bug","Mineral","Flying","Amorphous","Field","Fairy","Ditto","Grass","Dragon","Undiscovered"]
        rarities = ["Common","Uncommon","Rare","Very Rare","Common Legendary","Legendary","Mythical","Ultra Beasts","Event"]
        
        if name == "Shiny":
            sql_query = f"Select * from '{user_id}' where shiny='Yes'"
        elif name in egg_groups:
            sql_query = f"Select * from '{user_id}' where egg like '%{name}' or egg like '{name}%' order by totaliv DESC"
        elif name in ["Favourite","Fav"]:
            sql_query = f"Select * from '{user_id}' where nickname like '%<:favorite:1144122202942357534>%' order by totaliv DESC"    
        elif name == "Alpha":
            sql_query = f"Select * from '{user_id}' where nickname like '%<:alpha:1127167307198758923>%' order by totaliv DESC"
        elif name == "Item":
            sql_query = f"Select * from '{user_id}' where item!='None'"
        elif name in ["Speediv","Spdefiv","Spatkiv","Defiv","Hpiv","Atkiv"]:
            sql_query = f"Select * from '{user_id}' order by {name} DESC"
        elif name in ["Iv","IV","iv"]:
            sql_query = f"Select * from '{user_id}' order by totaliv DESC"    
        elif name in rarities:
            sql_query = f"Select * from '{user_id}' where rarity='{name.title()}' order by totaliv DESC"
        else:
            # Wildcard search for Pokemon name
            sql_query = f"Select * from '{user_id}' where name like '%{name}' or name like '{name}%' order by totaliv DESC"
            
    c.execute(sql_query)
    n = c.fetchall()
    
    # --- 2. Handle No Pokémon ---
    if not n:
        await ctx.followup.send("Unfortunately you don't have any Pokémon matching that criteria. Please try a different filter or catch some Pokémon using `/spawn` command.")
        db.close()
        dt.close()
        return

    # --- 3. Pagination (Slicing the list) ---
    total_pokemon = len(n)
    list_of_pages = []
    list_temp = []
    limit = 10
    
    for i in range(len(n)):
        if len(list_temp) < limit:
            list_temp.append(n[i])
        else:
            list_of_pages.append(list_temp)
            list_temp = [n[i]]
            
    if list_temp: # Add remaining items
        list_of_pages.append(list_temp)
        
    pages = len(list_of_pages)
    
    # --- 4. Initialize and Send View ---
    view = PokemonView(user_id, total_pokemon, list_of_pages, pages)
    initial_embed = await view.get_page_content()

    await ctx.followup.send(embed=initial_embed, view=view)

    db.close()
    dt.close()
        
class MovesetView(View):
    def __init__(self, pokemon_num: int):
        # Set a short timeout (e.g., 5 minutes) for the view
        super().__init__(timeout=300) 
        self.pokemon_num = pokemon_num

    @discord.ui.button(label="Show /teach command", style=discord.ButtonStyle.primary)
    async def teach_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Callback to remind the user of the command usage."""
        await interaction.response.send_message(
            f"To teach a new move, use: `/teach {self.pokemon_num} <move name>`",
            ephemeral=True # Only the user who clicked can see this
        )
# --------------------------------

class MovesetView(View):
    def __init__(self, pokemon_num: int):
        super().__init__(timeout=300) 
        self.pokemon_num = pokemon_num
        
    @discord.ui.button(label="Show /teach command", style=discord.ButtonStyle.primary)
    async def teach_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            f"To teach a new move, use: `/teach {self.pokemon_num} <move name>`",
            ephemeral=True
        )
# --------------------------------

@bot.tree.command(name="moveset", description="See all the moves this pokémon can learn.")
async def moveset(ctx: discord.Interaction, num: int = 1):
    "Shows all the available and learned moves of that particular pokémon."
    
    # --- 1. Fetch Pokémon Object (p) and allmon using the ID ---
    # We pass the integer ID 'num'. pokonvert will run the necessary DB queries itself.
    p, allmon, mon, spc = await pokonvert(ctx, ctx.user, num) 
    
    if p is None:
        await ctx.response.send_message(f"❌ Pokémon with ID **{num}** not found.", ephemeral=True)
        return

    # --- 2. Retrieve Raw Data (Mon and SPC) for Moveset and Embed ---
    
    # We need the raw data 'mon' and 'spc' to access the list indices (move[22], spc[10], spc[12]).
    # Since 'pokonvert' already fetched this data internally, 
    # we need to re-fetch the raw rows or modify pokonvert to return them.
    # We will re-fetch 'mon' and 'spc' to avoid changing pokonvert's return type.
    
    mon = None
    spc = None

    async with aiosqlite.connect("owned.db") as owned_db:
        # Fetch the raw Pokémon row from the user's private table
        cursor = await owned_db.execute(f"SELECT * FROM '{ctx.user.id}' WHERE rowid=?", (num,))
        mon = await cursor.fetchone()

    async with aiosqlite.connect("pokemondata.db") as data_db:
        # Get the species data
        cursor_data = await data_db.execute("SELECT * FROM wild WHERE name=?", (p.name,))
        spc = await cursor_data.fetchone()

    if not mon or not spc:
        await ctx.response.send_message("❌ Error retrieving detailed moveset data.", ephemeral=True)
        return

    # Learned moves are retrieved from the fetched owned row (index 22)
    move = eval(mon[22]) 
    
    # --- 3. Moveset Logic ---
    # Combine available moves (spc[10]) and filter out currently learned moves
    available_moves = list(set(eval(spc[10]) + ["Tera Blast"]) - set(move))
    
    known_moves_text = ""
    available_moves_text = ""
    MAX_LINES = 15 
    
    # Known moves
    for i in move:
        known_moves_text += f"{await movetypeicon(p, i)} {i} {await movect(i)}\n"
    
    # Available moves (with limit)
    for i in available_moves[:MAX_LINES]:
        available_moves_text += f"{i}\n"
        
    if len(available_moves) > MAX_LINES:
        available_moves_text += f"...\n({len(available_moves) - MAX_LINES} more moves available)"
        
    # --- 4. Embed and Response ---
    now = discord.Embed(
        title=f"{p.name}'s Moveset:", 
        color=0xff0000
    )
    
    now.add_field(name="Current Moveset:", value=known_moves_text or "None", inline=True)
    now.add_field(name="Available Moves:", value=available_moves_text or "None", inline=True)
    
    now.set_footer(text="/teach 'num' 'move name' to update moveset.")
    now.set_image(url=spc[12])

    view = MovesetView(num)
    
    await ctx.response.send_message(embed=now, view=view)
    
@bot.tree.command(name="nickname",description="Change the pokémons nickname.")
async def nickname(ctx: discord.Interaction, num: int = 1, select: str = "None"):
    # Always defer the interaction since we're doing database lookups
    await ctx.response.defer()

    if select != "None":
        # 1. Use aiosqlite.connect with async context managers
        async with aiosqlite.connect("pokemondata.db") as dt, aiosqlite.connect("owned.db") as db:
            
            # Get asynchronous cursors
            cx = await dt.cursor()
            c = await db.cursor()
            
            # 2. Call the (now fixed) asynchronous 'row' function
            # NOTE: You MUST ensure the 'row' function is also updated to use 'await c.execute'
            num = await row(ctx, num, c)  

            # 3. Use await for all cursor operations
            await c.execute(f"select * from `{ctx.user.id}` where rowid=?", (num,))
            mon = await c.fetchone()
            
            if not mon:
                await ctx.edit_original_response(content="Could not find that Pokémon.", ephemeral=True)
                return

            # Append icons to the new nickname string 'select'
            # Note: mon[1] is the nickname column
            if "<:traded:1127340280966828042>" in mon[1]:
                select = select + " <:traded:1127340280966828042>"
            if "<:shiny:1127157664665837598>" in mon[1]:
                select = select + " <:shiny:1127157664665837598>"
            elif "<:alpha:1127167307198758923>" in mon[1]:
                select = select + " <:alpha:1127167307198758923>"
            elif "<:hatched:1134745434506666085>" in mon[1]:
                select = select + " <:hatched:1134745434506666085>"      
            
            # Update the nickname (using '?' placeholder for security)
            await c.execute(f"""UPDATE `{ctx.user.id}` SET nickname=? WHERE rowid=?""", (select, num))
            
            # Commit the change
            await db.commit()
            
            # 4. Use edit_original_response to send the final message
            await ctx.edit_original_response(content=f"Nickname updated to **{select}**!")
    else:
        # If no nickname is provided
        await ctx.edit_original_response(
            content="Please provide a nickname. Example: `/nickname num:1 select:Pikachu`", 
            ephemeral=True
        )

@bot.tree.command(name="data", description="Shows competitive usage statistics for a Pokémon.")
@app_commands.describe(pokemon_name="The name of the Pokémon to look up (e.g., 'Garchomp').")
async def data_slash(interaction: discord.Interaction, pokemon_name: str):
    # Standardizing the name for database lookup
    name = pokemon_name.title()

    # --- Database Connections ---
    db = sqlite3.connect("record.db")
    c = db.cursor()
    dt = sqlite3.connect("pokemondata.db")
    ct = dt.cursor()

    # Get Pokémon basic info from 'pokemondata.db'
    ct.execute(f"SELECT * FROM 'wild' WHERE name=?", (name,))
    mon = ct.fetchone()

    if mon is None:
        await interaction.response.send_message(f"Pokémon '{name}' not found in the database.", ephemeral=True)
        db.close()
        dt.close()
        return

    # Get competitive data from 'record.db'
    c.execute(f"SELECT * FROM 'pokemons' WHERE name=?", (name,))
    p = c.fetchone()
    
    # Get total matches for userate calculation from 'alltime'
    c.execute(f"SELECT * FROM 'alltime'")
    v = c.fetchone() # Assuming v[0] is the total match count

    # --- Data Processing and Embed Creation ---
    
    # mon[22] is the icon/emoji, mon[12] is the thumbnail URL
    pokemon_icon = mon[22]
    thumbnail_url = mon[12]

    if p is not None and v is not None:
        # p[4] = Matches, p[5] = Wins, p[1]=Natures, p[2]=Items, p[3]=Abilities
        total_matches_played = v[0]
        pokemon_matches = p[4]
        pokemon_wins = p[5]

        # Calculate Rates
        userate = round((pokemon_matches / total_matches_played) * 100, 2) if total_matches_played > 0 else 0.00
        winrate = round((pokemon_wins / pokemon_matches) * 100, 2) if pokemon_matches > 0 else 0.00

        # Create Embed
        data = discord.Embed(title=f"{pokemon_icon} {name}:", color=discord.Color.blue())
        data.add_field(
            name="Statistics:",
            value=f"**Matches:** {pokemon_matches}\n**Wins:** {pokemon_wins}\n**Userate:** {userate}%\n**Winrate:** {winrate}%",
            inline=False
        )
        
        # --- Top Usage Data ---
        
        # p[1]=Natures, p[2]=Items, p[3]=Abilities
        natures = await convert_items_string(p[1])
        items = await convert_items_string(p[2])
        abilities = await convert_items_string(p[3])

        # Get top 3 Natures, top 5 Items, top 3 Abilities
        # Sorting dictionaries by value (count) descending and slicing
        top_natures = dict(sorted(natures.items(), key=lambda item: item[1], reverse=True)[:3])
        top_items = dict(sorted(items.items(), key=lambda item: item[1], reverse=True)[:5])
        top_abilities = dict(sorted(abilities.items(), key=lambda item: item[1], reverse=True)[:3])
        
        # Format Natures
        nt = ""
        for k, vl in top_natures.items():
            percent = round((vl / pokemon_matches) * 100, 2)
            nt += f"**{k}:** {percent}%\n"
        data.add_field(name="Top Natures:", value=nt or "N/A", inline=True)
        
        # Format Abilities
        ab = ""
        for k, vl in top_abilities.items():
            percent = round((vl / pokemon_matches) * 100, 2)
            ab += f"**{k.replace('_', ' ')}:** {percent}%\n"
        data.add_field(name="Top Abilities:", value=ab or "N/A", inline=True)

        # Format Items
        it = ""
        for k, vl in top_items.items():
            percent = round((vl / pokemon_matches) * 100, 2)
            item_display = k.replace('_', ' ')
            icon = await itemicon(item_display)
            it += f"{icon} **{item_display}:** {percent}%\n"
        data.add_field(name="Top Items:", value=it or "N/A", inline=True)

        data.set_thumbnail(url=thumbnail_url)
        
        # Send the successful response
        await interaction.response.send_message(embed=data)

    else:
        # Case where Pokémon exists (mon is not None) but no usage data is recorded (p is None or v is None)
        data = discord.Embed(
            title=f"{pokemon_icon} {name}:",
            description="No competitive usage data available!",
            color=discord.Color.orange()
        )
        data.set_thumbnail(url=thumbnail_url)
        await interaction.response.send_message(embed=data)
    
    # Close database connections
    db.close()
    dt.close()
    
# --- Custom View for Move Replacement ---
class MovesetSelectView(View):
    def __init__(self, ctx: discord.Interaction, pokemon_id: int, new_move: str, current_moves: list):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.pokemon_id = pokemon_id
        self.new_move = new_move
        self.current_moves = current_moves
        self.user_id = ctx.user.id
        
        # Create a button for each current move
        for index, move_name in enumerate(current_moves):
            # Button label includes the number (1-4) and the move name
            button = Button(
                label=f"({index + 1}) Replace {move_name}", 
                style=discord.ButtonStyle.secondary, 
                custom_id=f"replace_{index}"
            )
            button.callback = self.create_callback(index, move_name)
            self.add_item(button)
            
    def create_callback(self, index, old_move_name):
        async def callback(interaction: discord.Interaction):
            # Only the original user can interact
            if interaction.user.id != self.user_id:
                return await interaction.response.send_message("This interaction is not for you!", ephemeral=True)

            self.current_moves[index] = self.new_move
            
            # Convert list back to a clean string format for SQLite
            # Note: Using str() on a list of strings often results in double quotes, 
            # so we explicitly replace them for safety.
            updated_moves_str = str(self.current_moves).replace('"', "'")

            # --- Asynchronous Database Write ---
            try:
                async with aiosqlite.connect("owned.db") as db:
                    await db.execute(
                        f"""UPDATE '{self.user_id}' SET moves=? WHERE rowid=?""", 
                        (updated_moves_str, self.pokemon_id)
                    )
                    await db.commit()
            except Exception as e:
                print(f"DB Update Error: {e}")
                return await interaction.response.edit_message(
                    content=f"❌ Database error: Could not update moveset.", 
                    embed=None, view=None
                )

            # Update the original message and disable buttons
            self.stop()
            await interaction.response.edit_message(
                content=f"✅ Success! **{old_move_name}** was replaced by **{self.new_move}**.",
                embed=None, 
                view=None
            )

        return callback
        
    async def on_timeout(self):
        # Disable buttons on timeout
        for item in self.children:
            item.disabled = True
        try:
            # Check if the message is still there to edit
            await self.ctx.edit_original_response(content="❌ Move teaching timed out.", view=self)
        except Exception:
            pass # Interaction might be gone
# --------------------------------

# --- Teach Command ---

@bot.tree.command(name="teach", description="Teach your pokémon a new move.")
async def teach(ctx: discord.Interaction, mon: int, move: str):
    "Teaches your pokémon a certain move."
    
    select = move.strip()
    # Handle specific case for 'U-Turn' where it might be mis-capitalized
    if select.lower() != "u-turn":
        select = select.title()
    
    # --- Asynchronous Database Connection Setup ---
    # We open the connections here to fetch necessary data
    async with aiosqlite.connect("pokemondata.db") as dt_db, \
               aiosqlite.connect("owned.db") as db_db:
        
        # 1. Fetch raw data using the helper functions (assuming they are fixed)
        # Note: We pass the DB connection objects for the helpers to use aiosqlite.
        # Although your latest 'pokonvert' runs its own connections, 
        # this ensures compatibility if 'row' needs it.
        
        # Assuming row returns the raw rowid or handles errors
        # If your fixed pokonvert takes the ID, we use 'mon' as the ID.
        pokemon_id = mon # Use the mon integer as the rowid
        
        # 2. Get Pokémon data using the fixed helper function
        # This will fetch the p object and the raw row data
        p, allmon, mon_row, spc_row = await pokonvert(ctx, ctx.user, pokemon_id) 

        if p is None:
            await ctx.response.send_message(f"❌ Pokémon #{mon} not found in your collection.", ephemeral=True)
            return

        # 3. Extract necessary data from fetched rows
        current_moves = eval(mon_row[22]) # Learned moves from owned.db row (index 22)
        can_learn = eval(spc_row[10]) + ["Tera Blast"] # Available moves from wild.db row (index 10)
        pokemon_name = mon_row[0]
        
        # 4. Check if the move can be learned
        if select not in can_learn:
            return await ctx.response.send_message(f"❌ **{pokemon_name}** cannot learn **{select}** or you misspelled it.", ephemeral=True)
            
        if select in current_moves:
            return await ctx.response.send_message(f"ℹ️ **{pokemon_name}** already knows **{select}**.", ephemeral=True)

        # 5. Build the confirmation embed
        known_moves_text = ""
        for n, i in enumerate(current_moves):
            # Using the 'p' object to fetch the icon/category
            known_moves_text += f"({n+1}) {await movetypeicon(p, i)} {i} {await movect(i)}\n" 
        
        now = discord.Embed(
            title=f"{pokemon_name}'s Moveset:", 
            description=f"Select a move to replace with **{select}**!", 
            color=0xff0000
        )
        now.add_field(
            name="New Move:",
            value=f"{await movetypeicon(p, select)} {select} {await movect(select)}"
        )
        now.add_field(name="Current Moveset (Pick 1-4):", value=known_moves_text)
        
        # 6. Send the interactive response with buttons
        view = MovesetSelectView(ctx, pokemon_id, select, current_moves)
        await ctx.response.send_message(embed=now, view=view) 
                    
@bot.tree.command(name="evtrain",description="EV train your pokémon.")
async def evtrain(ctx: discord.Interaction, num: int = 1, hpev: int = 0, atkev: int = 0, defev: int = 0, spatkev: int = 0, spdefev: int = 0, speedev: int = 0):
    "EV trains your pokémon for free!"
    
    evlist = [hpev, atkev, defev, spatkev, spdefev, speedev]
    total = hpev + atkev + defev + spatkev + spdefev + speedev
    
    # ⚠️ Security Note: The original query uses f-string for SQL. 
    # The updated code below is safer and uses parameter substitution.

    if max(evlist) <= 252 and len(evlist) == 6 and total <= 508:
        try:
            # ⬅️ Connect using aiosqlite and async with
            async with aiosqlite.connect("owned.db") as db:
                sql_update = f"""
                UPDATE `{ctx.user.id}` SET 
                hpev = ?,
                atkev = ?,
                defev = ?,
                spatkev = ?,
                spdefev = ?,
                speedev = ?
                WHERE rowid = ?
                """
                
                # The values are passed as a tuple.
                values = (hpev, atkev, defev, spatkev, spdefev, speedev, num)
                
                await db.execute(sql_update, values)
                await db.commit() # ⬅️ Commit is also awaited
                
                # --- END: Modified for Safe Parameterized Query ---
                
            await ctx.response.send_message("EV training complete.")
            
        except Exception as e:
            # Handle potential database or connection errors
            print(f"Database error: {e}")
            await ctx.response.send_message("An error occurred during EV training.", ephemeral=True)
            
    else:
        await ctx.response.send_message("Invalid input.")
        
@bot.tree.command(name="iteminfo",description="Shows details about an item.")
async def iteminfo(ctx:discord.Interaction,item:str):
    "Shows you an item."
    item=item.title()
    db=sqlite3.connect("pokemondata.db")    
    c=db.cursor()   
    c.execute(f"select * from 'itemshop' where item='{item}'")
    item=c.fetchone()
    if item!=None:
        show=discord.Embed(title=f"{item[0]}", description=f"**Price:** {await numberify(item[1])} <:pokecoin:1134595078892044369>")
        if item[3]!="None":
            show.add_field(name="Description:",value=item[3])
        show.set_thumbnail(url=item[2])
        show.set_footer(text="Use `!buy 'item name' to buy the item.")
        await ctx.response.send_message(embed=show)
    
class BreedConfirmView(discord.ui.View):
    def __init__(self, user_id: int, mon1: 'Pokemon', mon2: 'Pokemon', child_p: 'Pokemon'):
        # Set a 60-second timeout to prevent the bot from blocking indefinitely
        super().__init__(timeout=60.0)
        self.user_id = user_id
        self.mon1 = mon1
        self.mon2 = mon2
        self.child_p = child_p
        self.confirmed = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only the command user can interact with the buttons
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This action is not for you.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        # Disable buttons and notify on timeout
        for item in self.children:
            item.disabled = True
        try:
            # Edit the original message to show the view is inactive
            # Note: This requires getting the message ID, which is typically done by storing interaction.message
            # or editing the original response from the command function.
            pass
        except:
            pass
        self.stop() 

    @discord.ui.button(label="Yes, Proceed (50,000 PC)", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop() # Stop the view

    @discord.ui.button(label="No, Cancel", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.stop() # Stop the view
        
@bot.tree.command(name="breed", description="Breed two pokemons.")
async def breed(ctx: discord.Interaction, mon1: int = 1, mon2: int = 2):
    """Breed two compatible pokémons. Costs 50,000 <:pokecoin:1134595078892044369>."""
    user_id = ctx.user.id
    BREEDING_COST = 50000
    try:
        async with aiosqlite.connect("playerdata.db") as dn:
            async with dn.cursor() as cn:
                await cn.execute(f"SELECT Balance FROM '{user_id}'")
                money = (await cn.fetchone())[0] # Assumes money is the first column
    except Exception as e:
        await ctx.response.send_message(f"Error accessing player data: {e}", ephemeral=True)
        return

    # Check for sufficient funds
    if money < BREEDING_COST:
        await ctx.response.send_message(f"You need **{BREEDING_COST:,}** <:pokecoin:1134595078892044369> to breed, but you only have **{money:,}**.")
        return

    async with aiosqlite.connect("owned.db") as db:
        # 💥 FIX: Obtain the cursor object 'c' from the connection 'db'
        async with db.cursor() as c: 
            # Now, pass the cursor 'c' to the row function
            num1_data = await row(ctx, mon1, c) 
            num2_data = await row(ctx, mon2, c)

    # Assuming pokonvert fetches the Pokémon object from the row data
    mon1_data = await pokonvert(ctx, ctx.user, num1_data)
    mon2_data = await pokonvert(ctx, ctx.user, num2_data)

    mon1_obj = mon1_data[0]
    mon2_obj = mon2_data[0]
    
    # --- 3. Compatibility Checks ---
    eg1 = await egggroup(mon1_obj.name) 
    eg2 = await egggroup(mon2_obj.name)
    canbreed = common(eg1, eg2)

    is_undiscovered = ("Undiscovered" in eg1) or ("Undiscovered" in eg2)

    # 2. Standard Breeding (Opposite gender AND share a group AND neither is Undiscovered)
    standard_breeding = (
        mon1_obj.gender != mon2_obj.gender and 
        not is_undiscovered and 
        canbreed
    )

    # 3. Ditto Breeding (One is Ditto AND the other is not Undiscovered)
    is_ditto = "Ditto" in (mon2_obj.name, mon1_obj.name)
    ditto_breeding = is_ditto and not is_undiscovered

    # Combine the breeding rules
    is_compatible = standard_breeding or ditto_breeding

    if not is_compatible:
        # This sends the response if any compatibility check fails
        await ctx.response.send_message(f"You can't breed a {mon1_obj.gender} {mon1_obj.name} with a {mon2_obj.gender} {mon2_obj.name} (Incompatible egg groups or gender combination).")
        return

    # --- 4. Child Pokémon Creation (aiosqlite) ---
    async with aiosqlite.connect("pokemondata.db") as dt:
        async with dt.cursor() as ct:
            name = ""
            if mon1_obj.gender == "Female":
                name = mon1_obj.name
            elif mon2_obj.gender == "Female":
                name = mon2_obj.name
            elif mon1_obj.name == "Ditto":
                name = mon2_obj.name
            elif mon2_obj.name == "Ditto":
                name = mon1_obj.name

            await ct.execute(f"SELECT * FROM 'wild' WHERE name='{name}'")
            m = await ct.fetchone() # m is the raw base data
            
    if m is None:
        await ctx.response.send_message(f"Error: Could not find base data for {name}.", ephemeral=True)
        return

    # IV Inheritance: Take the maximum IV from parents for each stat
    hpiv = max([mon1_obj.hpiv, mon2_obj.hpiv])
    atkiv = max([mon1_obj.atkiv, mon2_obj.atkiv])
    defiv = max([mon1_obj.defiv, mon2_obj.defiv])
    ter = random.choice([mon1_obj.tera, mon2_obj.tera])
    spatkiv = max([mon1_obj.spatkiv, mon2_obj.spatkiv])
    spdefiv = max([mon1_obj.spdefiv, mon2_obj.spdefiv])
    speediv = max([mon1_obj.speediv, mon2_obj.speediv])
    
    shiny = "No"
    if random.randint(1, 256) == 7:
        shiny = "Yes"

    # Create new Pokemon object 'p' (assuming Pokemon constructor works)
    p = Pokemon(name=m[0], primaryType=m[1], secondaryType=m[2], level=m[3], hp=m[4], atk=m[5], defense=m[6], spatk=m[7], spdef=m[8], speed=m[9], moves=m[10], ability=m[11], sprite=m[12], gender=m[15], maxiv="Custom", shiny=shiny, hpiv=hpiv, atkiv=atkiv, defiv=defiv, spatkiv=spatkiv, spdefiv=spdefiv, speediv=speediv, tera=ter)
    
    p.totaliv = round(((p.hpiv + p.atkiv + p.defiv + p.spatkiv + p.spdefiv + p.speediv) / 186) * 100, 2)
    # Ensure EV values exist on the object before access
    p.totalev = getattr(p, 'hpev', 0) + getattr(p, 'atkev', 0) + getattr(p, 'defev', 0) + getattr(p, 'spatkev', 0) + getattr(p, 'spdefev', 0) + getattr(p, 'speedev', 0)

    # --- 5. Confirmation Embed & View ---
    bred = discord.Embed(
        title="Proceed breeding?", 
        description=f"Sacrifice **{mon1_obj.name}** and **{mon2_obj.name}** to breed a better pokémon!\nPrice: **{BREEDING_COST:,}** <:pokecoin:1134595078892044369>"
    )
    types = p.primaryType
    if p.secondaryType != "???":
        types = f"{p.primaryType}/{p.secondaryType}"
        
    bred.add_field(name=f"Newborn {p.name}", value=f"""**Types:** {types}\n**Tera-Type:** {p.tera}\n**Ability:** {p.ability}\n**Nature:** {p.nature}\n**Gender:** {await statusicon(p.gender)}\n**Held Item:** {p.item}\n**HP:** {p.maxhp} - IV: {p.hpiv}/31 - EV: {getattr(p, 'hpev', 0)}\n**Attack:** {p.maxatk} - IV: {p.atkiv}/31 - EV: {getattr(p, 'atkev', 0)}\n**Defense:** {p.maxdef} - IV: {p.defiv}/31 - EV: {getattr(p, 'defev', 0)}\n**Sp. Atk:** {p.maxspatk} - IV: {p.spatkiv}/31 - EV: {getattr(p, 'spatkev', 0)}\n**Sp. Def:** {p.maxspdef} - IV: {p.spdefiv}/31 - EV: {getattr(p, 'spdefev', 0)}\n**Speed:** {p.maxspeed} - IV: {p.speediv}/31 - EV: {getattr(p, 'speedev', 0)}\n**Total IV %:** {p.totaliv}%\n**Total EV :** {p.totalev}/508""")
    bred.set_image(url=p.sprite)
    
    confirm_view = BreedConfirmView(user_id, mon1_obj, mon2_obj, p)
    await ctx.response.send_message(embed=bred, view=confirm_view)
    
    # Wait for confirmation (non-blocking)
    await confirm_view.wait()

    # --- 6. Execution Logic (aiosqlite) ---
    if confirm_view.confirmed:
        async with aiosqlite.connect("owned.db") as db:
            async with db.cursor() as c:
                
                # 6.1 Delete Parents (must be done in descending rowid order)
                num = [num1_data, num2_data] # Assuming num1_data and num2_data are the rowids
                num.sort()
                
                await c.execute(f"DELETE FROM '{user_id}' WHERE rowid={num[1]}")
                await db.commit()
                await c.execute(f"DELETE FROM '{user_id}' WHERE rowid={num[0]}")
                await db.commit()

                # 6.2 Insert Child
                clk = datetime.datetime.now()
                catchtime = clk.strftime("%Y-%m-%d %H:%M:%S")
                
                nickname = getattr(p, 'nickname', p.name) # Use safe access for nickname
                if "<:hatched:1134745434506666085>" not in nickname:
                    nickname = nickname + " <:hatched:1134745434506666085>"
                
                # This uses the same INSERT format as your original code
                await c.execute(f"""
                    INSERT INTO "{user_id}" VALUES (
                    "{p.name}", "{nickname}", "{p.level}", "{p.hpiv}", "{p.atkiv}", 
                    "{p.defiv}", "{p.spatkiv}", "{p.spdefiv}", "{p.speediv}", "{getattr(p, 'hpev', 0)}", 
                    "{getattr(p, 'atkev', 0)}", "{getattr(p, 'defev', 0)}", "{getattr(p, 'spatkev', 0)}", "{getattr(p, 'spdefev', 0)}", "{getattr(p, 'speedev', 0)}", 
                    "{p.ability}", "{p.nature}", "{p.shiny}", "{p.item}", "{p.gender}", 
                    "{p.tera}", "Custom", "{p.moves}", "{m[14]}", "{catchtime}", 
                    {p.totaliv}, '{m[18]}')
                """)
                await db.commit()
            
            # 6.3 Deduct Money (Assumed to be an async helper function that handles its own DB connection)
            await addmoney(ctx, ctx.user, -BREEDING_COST) 
            
            await ctx.channel.send("Breeding successful!")
            
    else:
        # Edit the original response to show cancellation status
        await ctx.edit_original_response(content="Breeding cancelled!", embed=bred, view=None)
        return
    
    # Final cleanup (optional, as the button click should have handled it)
    try:
        await ctx.edit_original_response(view=None)
    except:
        pass
               
@bot.tree.command(name="takeitem", description="Take item from a pokémon by its owned ID(s).")
async def takeitem(ctx: discord.Interaction, num: str):
    # 1. IMMEDIATE ACKNOWLEDGEMENT
    # Acknowledge the interaction immediately to prevent the "Interaction has already been acknowledged" error
    # and to ensure the user gets instant feedback. We will use followup messages for the results.
    await ctx.response.send_message("⚙️ Processing item return request...", ephemeral=True)
    
    user_id_str = str(ctx.user.id)
    results = [] # To store messages about the items taken

    # 2. Input Parsing and Validation
    try:
        # Split by space, filter out empty strings, and convert to integer list
        pokemon_ids_to_process = [int(i) for i in num.split() if i.isdigit()]
    except ValueError:
        return await ctx.followup.send(
            "❌ Error: Please enter valid Pokémon IDs (numbers) separated by spaces.",
            ephemeral=True
        )

    # If no valid IDs were found
    if not pokemon_ids_to_process:
        return await ctx.followup.send(
            "❌ Error: No valid Pokémon IDs provided.",
            ephemeral=True
        )

    # 3. Asynchronous Database Access (Use one connection for each database)
    try:
        async with aiosqlite.connect("playerdata.db") as db, \
                   aiosqlite.connect("owned.db") as dt:
            
            # Use active cursors for execution
            async with db.cursor() as c, dt.cursor() as ct:
                
                # Fetch player's item list ONCE outside the loop for efficiency
                await c.execute(f"SELECT * FROM '{user_id_str}'")
                player_data = await c.fetchone()
                
                if player_data is None:
                    return await ctx.followup.send("❌ Error: Player profile not found. Please `/start` your adventure.", ephemeral=True)
                
                # Safely convert item string (index 2) to a list
                items_str = player_data[2]
                items_list = ast.literal_eval(items_str) if items_str else []
                
                # Main Loop to process each Pokémon ID
                for owned_id in set(pokemon_ids_to_process): # Use set to avoid processing the same ID multiple times
                    
                    # NOTE: Your original code uses a function named 'row' which is likely an async function.
                    # This code assumes a direct use of the ID for simplicity, but you might need to adjust 'row'
                    # or ensure 'owned_id' is the correct rowid for the 'owned.db' table.
                    owned_rowid = await row(ctx, owned_id, ct) if 'row' in globals() else owned_id # Adjust based on your 'row' function

                    # Check if the Pokémon exists (owned_rowid is valid)
                    if owned_rowid is None:
                        results.append(f"❓ Pokémon ID **{owned_id}** not found in your collection.")
                        continue
                        
                    # 3.1 Get Held Item
                    await ct.execute(f"SELECT item FROM '{user_id_str}' WHERE rowid=?", (owned_rowid,))
                    item_data = await ct.fetchone()
                    
                    if item_data is None: # Should not happen if owned_rowid is valid, but good to check
                        results.append(f"⚠️ Could not find entry for owned ID **{owned_id}**.")
                        continue

                    held_item = item_data[0]
                    
                    # 3.2 Process Take Item
                    if held_item and held_item.lower() != "none":
                        # Add item to player's bag
                        items_list.append(held_item)
                        
                        # Update the Pokémon's held item to 'None'
                        await ct.execute(f"UPDATE '{user_id_str}' SET item='None' WHERE rowid=?", (owned_rowid,))
                        
                        results.append(f"✅ Item **{held_item.title()}** was removed from Pokémon ID **{owned_id}** and sent to your bag.")
                    else:
                        results.append(f"ℹ️ Pokémon ID **{owned_id}** is not holding any item.")

                # 4. Final Database Commit and Update Player's Bag
                
                # Convert updated items list back to string format for storage
                final_items_str = f"{items_list}"
                await c.execute(f"UPDATE '{user_id_str}' SET Items=? ", (final_items_str,))
                
                await db.commit() # Commit Player Data changes
                await dt.commit() # Commit Owned Pokemon changes
                
    except aiosqlite.Error as e:
        print(f"Database Error in takeitem: {e}")
        return await ctx.followup.send(f"❌ A critical database error occurred. ({e})", ephemeral=True)
    except Exception as e:
        print(f"An unexpected error occurred in takeitem: {e}")
        return await ctx.followup.send(f"❌ An unexpected error occurred. Please try again.", ephemeral=True)


    # 5. Final Response
    final_message = "\n".join(results)
    if not final_message:
        final_message = "No actions were taken."

    # Use followup to send the final result message
    await ctx.followup.send(final_message)
    
class BuyConfirmView(View):
    """
    A persistent view that handles the confirmation and execution of an item purchase
    using aiosqlite for non-blocking database operations.
    """
    def __init__(self, ctx: discord.Interaction, user_id_str: str, item_data: tuple, price: int):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.user_id_str = user_id_str
        self.item_name = item_data[0]
        self.item_price = price
        self.item_data = item_data
        
        # NOTE: Buttons are added via decorators below, so self.add_item() is NOT used here.
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only the user who executed the command can interact
        if interaction.user != self.ctx.user:
            await interaction.response.send_message("This purchase is not for you!", ephemeral=True)
            return False
        return True

    # FIX 1: Explicitly define the label and style in the decorator
    @discord.ui.button(label="Confirm Purchase", style=discord.ButtonStyle.green, custom_id="buy_yes")
    async def confirm_purchase(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop() # Stop listening for further interactions
        
        # --- Database Operations (Atomic Purchase) ---
        try:
            # 1. Check current balance and inventory *again* before committing
            async with aiosqlite.connect("playerdata.db") as dt_db:
                # Fetch the current row (Balance and Items columns)
                cursor = await dt_db.execute(f"SELECT Balance, Items FROM '{self.user_id_str}'")
                b = await cursor.fetchone()
                
                current_balance = b[0]
                items_str = b[1]
                
                # Check for sufficient funds (double-check security)
                if self.item_price > current_balance:
                    return await interaction.response.edit_message(
                        content="❌ Purchase failed: Your balance is now too low!", 
                        embed=None, view=None
                    )
                
                # 2. Update Balance (Assuming addmoney handles the DB write)
                # You must ensure your addmoney function is now asynchronous and uses aiosqlite.
                await addmoney(self.ctx, interaction.user, -self.item_price)
                
                # 3. Update Inventory
                current_items = ast.literal_eval(items_str) if items_str else []
                current_items.append(self.item_name)
                
                # Prepare updated items string for DB
                new_items_str = str(current_items).replace('"', "'")
                
                # Update the Items column
                await dt_db.execute(
                    f"""UPDATE '{self.user_id_str}' SET Items=? WHERE rowid=1""", 
                    (new_items_str,)
                )
                await dt_db.commit()

            # Final success message
            await interaction.response.edit_message(
                content=f"✅ You successfully purchased a **{self.item_name}**!", 
                embed=None, view=None
            )

        except Exception as e:
            print(f"Purchase Error: {e}")
            await interaction.response.edit_message(
                content=f"❌ An error occurred during the purchase. Item not bought.", 
                embed=None, view=None
            )

    # FIX 2: Explicitly define the label and style in the decorator
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red, custom_id="buy_no")
    async def cancel_purchase(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.stop()
        await interaction.response.edit_message(
            content="❌ You canceled the purchase.", 
            embed=None, view=None
        )

    async def on_timeout(self):
        # Disable buttons on timeout
        for item in self.children:
            item.disabled = True
        try:
            # Edit the original interaction response message
            await self.ctx.edit_original_response(content="❌ Purchase window timed out.", view=self)
        except discord.errors.NotFound:
            pass
        
# --- 2. Buyitem Command ---

@bot.tree.command(name="buyitem", description="Buy an item.")
async def buyitem(ctx: discord.Interaction, item: str):
    item_name = item.title()
    user_id_str = str(ctx.user.id)
    
    # --- A. Fetch Item Data (pokemondata.db) ---
    async with aiosqlite.connect("pokemondata.db") as db:
        cursor = await db.execute("SELECT * FROM itemshop WHERE item=?", (item_name,))
        item_data = await cursor.fetchone()
        
    if item_data is None:
        return await ctx.response.send_message(f"❌ Item **{item_name}** not found in the shop.", ephemeral=True)

    item_price = item_data[1]

    # --- B. Fetch Player Data (playerdata.db) ---
    async with aiosqlite.connect("playerdata.db") as dt:
        cursor = await dt.execute(f"SELECT Balance, Items FROM '{user_id_str}'")
        player_row = await cursor.fetchone()

    if player_row is None:
        return await ctx.response.send_message("❌ You do not have a player profile yet!", ephemeral=True)

    balance = player_row[0]

    # --- C. Check Balance and Respond ---
    
    if item_price > balance:
        return await ctx.response.send_message("❌ You don't have enough balance!", ephemeral=True)
    
    # Balance is sufficient, proceed to confirmation
    
    balance_after = balance - item_price
    
    em = discord.Embed(
        title=f"Would you like to buy {item_data[0]}?",
        description=f"**Price:** {await numberify(item_price)} <:pokecoin:1134595078892044369>\n**Balance after purchase:** {await numberify(balance_after)} <:pokecoin:1134595078892044369>"
    )
    em.set_thumbnail(url=item_data[2])
    
    view = BuyConfirmView(ctx, user_id_str, item_data, item_price)
    
    await ctx.response.send_message(embed=em, view=view)
    
class BagPaginator(View):
    def __init__(self, user: discord.User, items: list, newdic: dict, total_pages: int, embed_generator_func):
        super().__init__(timeout=180.0) # Timeout after 3 minutes of inactivity
        self.user = user
        self.items = items
        self.newdic = newdic
        self.total_pages = total_pages
        self.current_page = 1
        self.embed_generator = embed_generator_func
        
        # Initial button state setup
        self.update_buttons()
        
    def update_buttons(self):
        # Find the buttons by their custom_id or index and disable/enable them
        
        # Previous Button
        prev_button = self.children[0]
        prev_button.disabled = self.current_page == 1
        
        # Next Button
        next_button = self.children[1]
        next_button.disabled = self.current_page == self.total_pages

    async def generate_bag_embed(self):
        """Generates the actual discord.Embed for the current page."""
        return await self.embed_generator(
            self.user, 
            self.current_page, 
            self.total_pages, 
            self.items, 
            self.newdic
        )

    # --- Buttons ---

    @discord.ui.button(emoji="◀️", style=ButtonStyle.primary, custom_id="prev_page")
    async def prev_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            
        if self.current_page > 1:
            self.current_page -= 1
            self.update_buttons()
            
            new_embed = await self.generate_bag_embed()
            # Edit the original message with the new embed and the updated view
            await interaction.response.edit_message(embed=new_embed, view=self)
        else:
            await interaction.response.defer() # Acknowledge the click without changing the message

    @discord.ui.button(emoji="▶️", style=ButtonStyle.primary, custom_id="next_page")
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("This menu is not for you!", ephemeral=True)
            
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_buttons()
            
            new_embed = await self.generate_bag_embed()
            # Edit the original message with the new embed and the updated view
            await interaction.response.edit_message(embed=new_embed, view=self)
        else:
            await interaction.response.defer() # Acknowledge the click without changing the message

    async def on_timeout(self):
        # Disable all buttons when the view times out
        for item in self.children:
            item.disabled = True
        # Try to edit the message to remove interactive elements
        try:
            # Need to get the original message from the interaction's channel
            # This is a bit tricky without storing the message, so we rely on the message attribute being set after the send_message call
            if hasattr(self, 'message'):
                 await self.message.edit(view=self)
        except Exception:
            pass
async def create_bag_embed(user: discord.User, page: int, total_pages: int, all_items: list, item_counts: dict) -> discord.Embed:
    """Helper function to create the bag embed for a given page."""
    
    # gensub logic applied here
    sorted_item_names = sorted(item_counts.keys())
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    
    bag_embed = discord.Embed(
        title=f"{user.display_name}'s Backpack:",
        description=f"Total unique items: **{len(item_counts)}** (Total quantity: **{len(all_items)}**)",
        color=discord.Color.blue()
    )
    bag_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1102579499989745764/1134073215803723827/image_search_1690454504333.png")

    txt = ""
    if len(all_items) != 0:
        for item_name in sorted_item_names[start_index:end_index]:
            count = item_counts[item_name]
            # Assumes itemicon is an awaitable function
            txt += f"{await itemicon(item_name)} **{item_name.title()}** ×{count}\n"
        
        bag_embed.add_field(name="Item List:", value=txt, inline=False)
    else:
        bag_embed.add_field(name="Item List:", value="Your backpack is empty! Go explore!", inline=False)
        
    bag_embed.set_footer(text=f"Page {page} of {total_pages}")
    return bag_embed


@bot.tree.command(name="bag", description="Shows all the items in your bag.")
async def bag(ctx: discord.Interaction, page: int = 1):
    user_id_str = str(ctx.user.id)
    
    # 1. Use aiosqlite for asynchronous database access
    async with aiosqlite.connect("playerdata.db") as db:
        # Fetch the entire row for the user's table
        # NOTE: Your original code used SELECT * and then fetched items[2]. 
        # We need to ensure the user's table name is safe and the column is correct.
        # Assuming column 2 (index 2) is the 'items' column:
        try:
            async with db.execute(f"SELECT * FROM '{user_id_str}'") as cursor:
                row = await cursor.fetchone()
                
            if row is None:
                # Handle case where player data doesn't exist
                return await ctx.response.send_message(
                    "You do not have a player profile yet. Please start your adventure!", 
                    ephemeral=True
                )
            
            # The list of item names is stored in the 3rd column (index 2) as a string
            items_str = row[2] 
            
        except aiosqlite.OperationalError:
            # Catch errors like "no such table"
            return await ctx.response.send_message(
                "You do not have a player profile yet. Please start your adventure!", 
                ephemeral=True
            )

    # 2. Safely evaluate the string into a list
    try:
        # Use ast.literal_eval for safety over eval()
        all_items = ast.literal_eval(items_str) if items_str else []
    except (ValueError, SyntaxError):
        # Handle malformed data in the database
        print(f"Error evaluating items string for user {ctx.user.id}: {items_str}")
        all_items = []
    
    # 3. Process item counts and calculate pages
    item_counts = await listtodic(all_items) # Dict of {item_name: count}
    
    total_unique_items = len(item_counts)
    total_pages = math.ceil(total_unique_items / ITEMS_PER_PAGE) if total_unique_items > 0 else 1
    
    # Ensure starting page is valid
    if not (1 <= page <= total_pages):
        page = 1 

    # 4. Create the Paginator View and the initial Embed
    paginator_view = BagPaginator(ctx.user, all_items, item_counts, total_pages, create_bag_embed)
    paginator_view.current_page = page # Set the starting page
    paginator_view.update_buttons() # Update button states
    
    # Generate the initial embed
    initial_embed = await paginator_view.generate_bag_embed()

    # 5. Send the initial message with the view
    if total_pages > 1:
        # Store the message object in the view for on_timeout to work reliably
        message = await ctx.response.send_message(embed=initial_embed, view=paginator_view)
        paginator_view.message = await message.original_response()
    else:
        # If there's only one page, send the embed without buttons
        await ctx.response.send_message(embed=initial_embed)
            
class BottleCapSelect(discord.ui.View):
    def __init__(self, original_interaction: discord.Interaction, db_connection, dt_connection, user_items_list: list, user_owned_data: tuple, owned_rowid: int, bot_instance):
        # We need to pass the connections, item list, and owned data to the view
        super().__init__(timeout=180)
        self.original_interaction = original_interaction
        self.db = db_connection
        self.dt = dt_connection
        self.user_items = user_items_list
        self.user_owned_data = user_owned_data
        self.owned_rowid = owned_rowid
        self.bot = bot_instance
        self.item_name = "Bottle Cap" # Constant item name

        # The options need to be created based on the current IVs
        options = []
        stats = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]
        # IVs are stored from index 3 to 8 (m[3] to m[8] in your original code)
        for i, stat_name in enumerate(stats, start=3):
            iv_value = user_owned_data[i]
            if iv_value < 31:
                options.append(
                    discord.SelectOption(
                        label=f"{stat_name} IV: {iv_value}",
                        value=str(i), # Store the column index as the value
                        description=f"Max out {stat_name} IV to 31."
                    )
                )

        if not options:
            self.add_item(discord.ui.Button(label="All IVs are already maxed!", style=discord.ButtonStyle.secondary, disabled=True))
        else:
            self.add_item(
                discord.ui.Select(
                    placeholder="Choose a stat to max out...",
                    options=options,
                    custom_id="bottle_cap_select"
                )
            )

    @discord.ui.select(custom_id="bottle_cap_select", placeholder="Choose a stat...")
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user != self.original_interaction.user:
            return await interaction.response.send_message("This menu is not for you!", ephemeral=True)

        selected_index = int(select.values[0])
        stat_name = select.options[selected_index - 3].label.split(" IV")[0] # Get the stat name (HP, Attack, etc.)

        # 1. Update IV in owned.db
        stat_col = ["hpiv", "atkiv", "defiv", "spatkiv", "spdefiv", "speediv"][selected_index - 3]
        user_id_str = str(self.original_interaction.user.id)

        # Use the passed-in connection to execute
        await self.dt.execute(f"UPDATE '{user_id_str}' SET {stat_col}=31 WHERE rowid=?", (self.owned_rowid,))

        # 2. Remove item from player bag in playerdata.db
        self.user_items.remove(self.item_name)
        final_items_str = f"{self.user_items}"
        await self.db.execute(f"UPDATE '{user_id_str}' SET Items=? ", (final_items_str,))

        # 3. Commit both
        await self.dt.commit()
        await self.db.commit()

        # 4. Final Response
        self.stop() # Stop the view
        await interaction.response.edit_message(
            content=f"✅ Success! **{self.user_owned_data[0]}'s** **{stat_name}** IV is now maxed out (31) using one **{self.item_name}**!",
            embed=None,
            view=None
        )

    async def on_timeout(self):
        # Disable all components on timeout
        for item in self.children:
            item.disabled = True
        try:
             # Edit the original message to reflect the timeout
            await self.original_interaction.edit_original_response(content="⚠️ Bottle Cap selection timed out. Run the command again to use.", view=self)
        except:
            pass # Ignore if original response is gone

class AbilitySelectView(View):
    """
    A persistent view that allows the user to select a new ability for their Pokémon
    after an Ability Capsule has been consumed.
    """
    def __init__(self, ctx: discord.Interaction, user_id_str: str, pokemon_id: int, options: list):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.user_id_str = user_id_str
        self.pokemon_id = pokemon_id
        
        # Create a Select Menu
        ability_select = Select(
            placeholder="Choose the new ability...",
            options=options,
            custom_id="ability_swap_select"
        )
        ability_select.callback = self.select_callback
        self.add_item(ability_select)

    async def select_callback(self, interaction: discord.Interaction):
        # Ensure only the original user can interact
        if interaction.user.id != self.ctx.user.id:
            # Respond to the unauthorized user ephemerally
            return await interaction.response.send_message("This menu is not for you!", ephemeral=True)

        new_ability = interaction.data['values'][0]
        
        # --- Asynchronous Database Write (Owned Pokémon Update) ---
        try:
            async with aiosqlite.connect("owned.db") as db:
                async with db.cursor() as c:
                    rowid=await row(self.ctx,self.pokemon_id,c)
                    print(rowid)
                    pokemon_update_sql = f'UPDATE "{self.user_id_str}" SET ability=? WHERE ROWID=?'
                    await db.execute(pokemon_update_sql,(new_ability, rowid))
                    await db.commit()
                
            # Disable the menu, stop the view, and send success message
            self.stop()
            await interaction.response.edit_message(
                content=f"💊 Success! Ability changed to **{new_ability}**.",
                embed=None, 
                view=None
            )
        except Exception as e:
            # Log the error for debugging
            print(f"DB Update Error (Ability Capsule): {e}")
            # Edit the message to show an error occurred
            await interaction.response.edit_message(
                content=f"❌ An error occurred during the database update. Please try again.", 
                embed=None, view=None
            )
            
    async def on_timeout(self):
        # Disable all items on timeout
        for item in self.children:
            item.disabled = True
        try:
            # Edit the original interaction response message
            await self.ctx.edit_original_response(content="❌ Ability selection timed out.", view=self)
        except discord.errors.NotFound:
            # Handle case where the message might have been deleted
            pass
                
@bot.tree.command(name="useitem", description="Use item on a pokémon.")
async def useitem(ctx: discord.Interaction, item: str, num: int):
    # 1. Acknowledge immediately as this involves database lookups
    await ctx.response.defer(ephemeral=False)

    input_item_name = item.title()
    user_id_str = str(ctx.user.id)
    
    # Placeholder for database connections and data
    db, dt, user_items_list, owned_rowid, mon_data = None, None, [], None, None
    
    try:
        # Use two connections in the outer try block for BottleCapSelect to access them later
        async with aiosqlite.connect("playerdata.db") as db_conn, \
                   aiosqlite.connect("owned.db") as dt_conn, \
                   aiosqlite.connect("pokemondata.db") as dx_conn:
            
            db, dt, dx = db_conn, dt_conn, dx_conn

            # 2. Universal Data Fetch (Player Items & Pokémon RowID)
            async with dt.cursor() as ct:
                # Get owned Pokémon's rowid
                owned_rowid = await row(ctx, num, ct) 

                if owned_rowid is None:
                    return await ctx.followup.send(f"❌ Error: Could not find Pokémon with ID **{num}** in your collection.", ephemeral=True)
                
                # Get owned Pokémon data (for stats/updates) - Assuming mon[0] is name, mon[1] is nickname, mon[3-8] are IVs
                await ct.execute(f"SELECT * FROM '{user_id_str}' WHERE rowid=?", (owned_rowid,))
                mon_data = await ct.fetchone()

            async with db.cursor() as c:
                # Get player's items
                await c.execute(f"SELECT Items FROM '{user_id_str}'")
                player_data = await c.fetchone()
                
                if player_data is None:
                    return await ctx.followup.send("❌ Error: Player profile not found.", ephemeral=True)
                
                items_str = player_data[0] 
                user_items_list = ast.literal_eval(items_str) if items_str else []

            # 3. Validation: Check if item is in bag
            if input_item_name not in user_items_list:
                 return await ctx.followup.send(f"❌ Error: You do not have the item **{input_item_name}** in your bag.", ephemeral=True)


            # --- Item Logic Starts ---
            
            # --- Helper function to update bag and Pokémon data ---
            async def commit_changes(pokemon_update_sql: str = None, success_message: str = None):
                # Remove item from bag
                user_items_list.remove(input_item_name)
                final_items_str = f"{user_items_list}"
                await db.execute(f"UPDATE '{user_id_str}' SET Items=?", (final_items_str,))
                
                # Update Pokémon data
                if pokemon_update_sql:
                    await dt.execute(pokemon_update_sql, (owned_rowid,))
                
                await db.commit()
                await dt.commit()
                
                if success_message:
                    await ctx.followup.send(f"✅ Success! {mon_data[0]}'s stats may have changed due to the effects of the **{input_item_name}**!")


            # A. Mint Logic (Nature Change)
            if "Mint" in input_item_name:
                new_nature = input_item_name.replace(" Mint", "")
                pokemon_id = mon_data[-1] # Assuming rowid is the last element in mon_data

                # --- 1. CONSUME THE ITEM from playerdata.db (Existing Logic) ---
                try:
                    # ... (Item consumption logic remains the same) ...
                    async with aiosqlite.connect("playerdata.db") as db:
                        # 1a. Fetch the current items list string
                        async with db.execute(f"SELECT items FROM '{user_id_str}'") as cursor:
                            player_row = await cursor.fetchone()
                        
                        if not player_row or player_row[0] is None:
                            return await ctx.followup.send("❌ Player profile not found. Cannot consume item.")

                        items_str = player_row[0]
                        current_items_list = ast.literal_eval(items_str) if items_str else []

                        if input_item_name not in current_items_list:
                            return await ctx.followup.send(f"❌ You no longer possess a **{input_item_name}**.")

                        # 1b. Remove one instance
                        current_items_list.remove(input_item_name)
                        new_items_str = str(current_items_list).replace('"', "'")

                        # 1c. Update the 'items' column
                        await db.execute(
                            f"""UPDATE '{user_id_str}' SET items=? WHERE rowid=1""", 
                            (new_items_str,)
                        )
                        await db.commit()
                        
                except Exception as e:
                    print(f"Mint Item Consumption Error: {e}")
                    return await ctx.followup.send("❌ A database error occurred while consuming the item.")

                # --- 2. UPDATE POKÉMON NATURE in owned.db ---
                try:
                    async with aiosqlite.connect("owned.db") as db:
                        async with db.cursor() as c: 
                            rowid=await row(ctx,num,c)
                            print(rowid)
                            pokemon_update_sql = f'UPDATE "{user_id_str}" SET nature=? WHERE ROWID=?'
                            await db.execute(pokemon_update_sql,(new_nature, rowid))
                            await db.commit()
                except Exception as e:
                    # If the nature update or stat recalculation fails, the item is already consumed! 
                    print(f"Mint Nature/Stat Update Error: {e}")
                    return await ctx.followup.send(
                        "❌ Item consumed, but failed to update Pokémon's nature and/or recalculate stats due to a database error."
                    )

                # --- 3. Confirmation ---
                return await ctx.followup.send(
                    f"✅ Success! **{mon_data[0]}'s** nature is now **{new_nature}** and its stats have been updated."
                )

            # B. Golden Bottle Cap (Max All IVs)
            elif input_item_name == "Golden Bottle Cap":
                pokemon_update_sql = f"UPDATE '{user_id_str}' SET hpiv=31,atkiv=31,defiv=31,spatkiv=31,spdefiv=31,speediv=31 WHERE rowid=?"
                await commit_changes(pokemon_update_sql)
                return await ctx.followup.send(
                    f"👑 Success! **{mon_data[0]}'s** **all IVs** are now maxed out (31)!"
                )

            # C. Bottle Cap (Interactive Max One IV) - Uses View
            elif input_item_name == "Bottle Cap":
                # Check if all IVs are already maxed
                if all(mon_data[i] == 31 for i in range(3, 9)):
                    return await ctx.followup.send(f"ℹ️ **{mon_data[0]}'s** IVs are already maxed out (31) for all stats. Bottle Cap not needed.")

                em = discord.Embed(
                    title=f"🧊 Use Bottle Cap on {mon_data[0]}?",
                    description="Select which IV stat you want to max out to 31. This action is irreversible and will consume one Bottle Cap."
                )
                
                # Pass necessary data to the View for execution
                view = BottleCapSelect(ctx, db, dt, user_items_list, mon_data, owned_rowid, bot)
                # Send the initial embed with the view. The View handles the followup.
                return await ctx.followup.send(embed=em, view=view)

            # D. Tera Shard (Tera Type Change)
            elif "Tera Shard" in input_item_name:
                new_teratype = input_item_name.replace(" Tera Shard", "")
                pokemon_update_sql = f"UPDATE '{user_id_str}' SET teratype='{new_teratype}' WHERE rowid=?"
                await commit_changes(pokemon_update_sql)
                return await ctx.followup.send(
                    f"✨ Success! **{mon_data[0]}'s** Tera Type is now **{new_teratype}**."
                )

            # E. Ability Capsule (Ability Change) - Needs Pokemondata DB
            elif input_item_name == "Ability Capsule":
                pokemon_species_name = mon_data[0]
                current_ability = mon_data[1].strip()
                pokemon_id = mon_data[-1] 

                # --- 1. Fetch Wild Data & Check Swap Possibility ---
                try:
                    async with aiosqlite.connect("pokemondata.db") as wild_db:
                        # CORRECT AIOSQLITE PATTERN
                        cursor = await wild_db.execute("SELECT * FROM wild WHERE name=?", (pokemon_species_name,))
                        wild_data = await cursor.fetchone()
                except Exception as e:
                    print(f"Wild Data Fetch Error: {e}")
                    return await ctx.followup.send("❌ Error fetching species data.")

                if wild_data is None:
                    return await ctx.followup.send(f"❌ Error: Cannot find base data for **{pokemon_species_name}**.")

                all_abilities = [ab.strip() for ab in wild_data[11].split(",")]
                available_abilities = [ab for ab in all_abilities if ab != current_ability]
                if not available_abilities:
                    return await ctx.followup.send(
                        f"ℹ️ **{pokemon_species_name}** only has one switchable base ability (**{current_ability}**). "
                        f"The Ability Capsule cannot be used."
                    )

                # --- 2. CONSUME THE ITEM from playerdata.db ---
                try:
                    async with aiosqlite.connect("playerdata.db") as db: # Use playerdata.db for inventory
                        # 2a. Fetch the current items list string
                        async with db.execute(f"SELECT items FROM '{user_id_str}'") as cursor:
                            player_row = await cursor.fetchone()
                        
                        if not player_row or player_row[0] is None:
                            return await ctx.followup.send("❌ Player profile not found or inventory is empty.")

                        items_str = player_row[0]
                        current_items_list = ast.literal_eval(items_str) if items_str else []

                        if input_item_name not in current_items_list:
                            return await ctx.followup.send(f"❌ You no longer possess an **{input_item_name}**.")

                        # 2b. Remove one instance
                        current_items_list.remove(input_item_name)
                        new_items_str = str(current_items_list).replace('"', "'")

                        # 2c. Update the database (assuming 'items' is the column name for index 2)
                        await db.execute(
                            f"""UPDATE '{user_id_str}' SET items=? WHERE rowid=1""", 
                            (new_items_str,)
                        )
                        await db.commit()
                        
                except aiosqlite.OperationalError as e:
                    print(f"Item Consumption DB Error: {e}")
                    return await ctx.followup.send("❌ A database error occurred while consuming the item.")
                except Exception as e:
                    print(f"Item Consumption Data/Logic Error: {e}")
                    return await ctx.followup.send("❌ Error in item consumption process.")
                
                # --- 3. Prepare View and Send Response ---
                
                # CRITICAL FIX 2: Generate options using the filtered list (available_abilities)
                options = [
                    SelectOption(label=ab, value=ab, description=f"Swap from {current_ability} to {ab}")
                    for ab in available_abilities 
                ]

                ability_view = AbilitySelectView(
                    ctx=ctx,
                    user_id_str=user_id_str,
                    pokemon_id=num,
                    options=options
                )
                
                return await ctx.followup.send(
                    f"Choose the new ability for **{pokemon_species_name}**. The Capsule has been consumed:",
                    view=ability_view,
                    ephemeral=True
                )

            # F. Transformation Items (Gracidea, Prison Bottle, Reveal Glass)
            # This logic is complicated and heavily relies on your specific database schema and helpers. 
            # I will only provide the framework for the Shaymin Gracidea transformation as a complex example.
            
            elif input_item_name == "Gracidea":
                
                current_name = mon_data[0]
                new_name = None
                new_ability = None
                
                if current_name == "Shaymin":
                    new_name = "Sky Shaymin"
                    new_ability = "Serene Grace" # Assuming this is the correct ability for Sky Forme
                elif current_name == "Sky Shaymin":
                    new_name = "Shaymin"
                    new_ability = "Natural Cure" # Assuming this is the correct ability for Land Forme
                
                if new_name:
                    pokemon_update_sql = f"UPDATE '{user_id_str}' SET name='{new_name}', ability='{new_ability}' WHERE rowid=?"
                    await commit_changes(pokemon_update_sql)
                    return await ctx.followup.send(
                        f"🌸 Success! **{current_name}** transformed into **{new_name}**!"
                    )
                else:
                    return await ctx.followup.send(f"ℹ️ **{current_name}** cannot use the **{input_item_name}**.")

            else:
                return await ctx.followup.send(f"ℹ️ The item **{input_item_name}** cannot be used on a Pokémon, or the usage logic is not implemented yet.")
    
    except aiosqlite.Error as e:
        print(f"Database Error in useitem: {e}")
        await ctx.followup.send(f"❌ A critical database error occurred: {e}", ephemeral=True)
    except Exception as e:
        print(f"An unexpected error occurred in useitem: {e}")
        await ctx.followup.send(f"❌ An unexpected error occurred: {e}", ephemeral=True)
                
@bot.tree.command(name="giveitem", description="Give an item to a Pokémon to hold.")
async def giveitem(ctx: discord.Interaction, item: str, num: int):
    # Use lowercase for case-insensitive item checks, then title-case for display/storage
    input_item_name = item.title()
    user_id_str = str(ctx.user.id)
    
    # 1. IMMEDIATE ACKNOWLEDGEMENT
    # Acknowledge the interaction immediately. We'll use followup for the result.
    await ctx.response.defer(ephemeral=False)
    
    try:
        async with aiosqlite.connect("playerdata.db") as db, \
                   aiosqlite.connect("owned.db") as dt:
            
            async with db.cursor() as c, dt.cursor() as ct:
                
                # --- Step 1: Validate Pokémon and get its owned rowid ---
                
                # Assume 'row' is defined and returns the unique rowid (or ID) of the owned Pokémon
                owned_rowid = await row(ctx, num, ct) 

                if owned_rowid is None:
                    return await ctx.followup.send(
                        f"❌ Error: Could not find Pokémon with ID **{num}** in your collection.",
                        ephemeral=True
                    )
                
                # Get the Pokémon's current held item and its name for the final message
                await ct.execute(f"SELECT name, item FROM '{user_id_str}' WHERE rowid=?", (owned_rowid,))
                poke_data = await ct.fetchone()
                
                if poke_data is None:
                    return await ctx.followup.send(
                        f"❌ Error: Could not retrieve data for Pokémon ID **{num}**.",
                        ephemeral=True
                    )
                    
                poke_name, current_held_item = poke_data[0], poke_data[1]
                
                # --- Step 2: Fetch and Update Player's Item Bag ---
                
                await c.execute(f"SELECT Items FROM '{user_id_str}'")
                player_data = await c.fetchone()
                
                if player_data is None:
                    return await ctx.followup.send("❌ Error: Player profile not found. Please start your adventure!", ephemeral=True)
                
                items_str = player_data[0] # Assuming Items is the first (and only) column selected
                items_list = ast.literal_eval(items_str) if items_str else []

                # --- Step 3: Handle Existing Item (If any) ---
                
                return_message = ""
                if current_held_item and current_held_item.lower() != "none":
                    # Put the old item back in the bag
                    items_list.append(current_held_item)
                    return_message = f"**{current_held_item.title()}** was removed and sent to your bag.\n"
                    
                # --- Step 4: Check for New Item in Bag ---
                
                if input_item_name not in items_list:
                    # Commit the return action even if the give fails
                    final_items_str = f"{items_list}"
                    await c.execute(f"UPDATE '{user_id_str}' SET Items=?", (final_items_str,))
                    await db.commit()
                    
                    # Update the Pokémon to hold 'None' if an item was returned
                    if current_held_item and current_held_item.lower() != "none":
                         await ct.execute(f"UPDATE '{user_id_str}' SET item='None' WHERE rowid=?", (owned_rowid,))
                         await dt.commit()
                         
                    return await ctx.followup.send(
                        f"❌ Error: You do not have the item **{input_item_name}** in your bag.", 
                        ephemeral=True
                    )
                
                # --- Step 5: Perform the GIVE Action ---
                
                # 5a. Update Pokémon's held item
                await ct.execute(f"UPDATE '{user_id_str}' SET item=? WHERE rowid=?", (input_item_name, owned_rowid))
                
                # 5b. Remove item from player's bag
                items_list.remove(input_item_name)
                final_items_str = f"{items_list}"
                await c.execute(f"UPDATE '{user_id_str}' SET Items=?", (final_items_str,))
                
                # 5c. Commit all changes
                await dt.commit()
                await db.commit()
                
                # --- Step 6: Final Success Message ---
                
                final_message = f"✅ Success!\n{return_message}**{poke_name}** is now holding a **{input_item_name}**."
                await ctx.followup.send(final_message)


    except aiosqlite.Error as e:
        print(f"Database Error in giveitem: {e}")
        await ctx.followup.send(f"❌ A critical database error occurred. ({e})", ephemeral=True)
    except Exception as e:
        print(f"An unexpected error occurred in giveitem: {e}")
        await ctx.followup.send(f"❌ An unexpected error occurred. Please try again.", ephemeral=True)
            
async def egggroup(name: str) -> list[str]:
    async with aiosqlite.connect("pokemondata.db") as db:
        # Assuming column 18 (index 18) is the egg group string
        async with db.execute("SELECT * FROM wild WHERE name=?", (name.title(),)) as cursor:
            n = await cursor.fetchone()
            
            if n is None:
                # Return an empty list or handle the error appropriately
                return [] 
            
            egggroup_str = n[18]
            
            # Use ast.literal_eval for safe conversion from string to list
            return egggroup_str.split(',')
                        
@bot.tree.command(name="trainerinfo", description="Shows a random team of a certified trainer.")
async def trainerinfo(ctx: discord.Interaction, num: int = 1):
    
    # Use defer as this command performs multiple database lookups
    await ctx.response.defer()
    
    # 1. Fetch the Trainer's Team and Base Data
    try:
        # Assuming gameteam is an async function
        tr1 = await gameteam(ctx, num) 
    except Exception as e:
        print(f"Error fetching game team: {e}")
        return await ctx.followup.send("❌ Error: Could not fetch trainer data. Please check the input number.", ephemeral=True)

    user_id_str = str(ctx.user.id)
    mm = tr1.name.split("> ")[-1]
    trainer_data = None

    # 2. Fetch Detailed Trainer Info from Database
    async with aiosqlite.connect("pokemondata.db") as db:
        # NOTE: Using a parameterized query for safety, though table name is hardcoded
        async with db.execute("SELECT * FROM Trainers WHERE name=?", (mm,)) as cursor:
            trainer_data = await cursor.fetchone()

    # 3. Process Trainer Metadata for Immersion
    
    # Determine the trainer's specialization or rank for a flavor sentence
    if trainer_data and trainer_data[1] and trainer_data[1].lower() != "none":
        badge_name = trainer_data[1]
        badge_icon = trainer_data[2] # Assuming trainer_data[2] holds the icon/emoji
        specialization_text = f"They hold the **{badge_name}** {badge_icon} Badge, indicating mastery in a particular domain."
    else:
        specialization_text = "This trainer appears to be a formidable challenger, but their specialty is unknown."
        badge_name = "Challenger" # Default name for use in the embed

    # Choose an appropriate flavor quote/opening line
    flavor_quotes = [
        f"**{badge_name} {tr1.name}'s** data is being downloaded...",
        f"Intel secured. Get ready to face a tough challenge from **{tr1.name}**!",
        f"Trainer **{tr1.name}** has entered the battle. Analyze their strategy!",
    ]
    
    description_text = (
        f"{random.choice(flavor_quotes)}\n\n"
        f"This is a **sample team**. While you can't rely on it entirely, it provides crucial insight into their potential strategy.\n\n"
        f"**Trainer Focus:** {specialization_text}"
    )

    # 4. Create the Embed
    info = discord.Embed(
        title=f"⚔️ Trainer Battle Intel: {tr1.name}",
        description=description_text,
        color=discord.Color.dark_red()
    )
    info.set_thumbnail(url=tr1.sprite)
    
    # 5. Add Immersive Fields for Each Pokémon
    
    pokemon_fields = []
    
    # Assuming tr1.pokemons is a list of Pokémon objects with attributes like:
    # .name (Pokedex name), .nickname, .level, .ability, .item, .tera, .moves (list of 4)
    
    for n, i in enumerate(tr1.pokemons, 1):
        
        # Determine the Pokémon's type icons (assuming get_pokemon_type_icons is implemented)
        # Using .name is safer if the object doesn't store the types directly
        try:
            type_icons = await get_pokemon_type_icons(i.name)
        except:
            type_icons = ""
            
        # Strategy/Role Text (You might need a separate database for this flavor text)
        role_text = "A versatile threat." # Placeholder - replace with actual strategy notes if available

        # Construct the value field with enhanced detail
        value_field = (
            f"**Level:** Lvl. {i.level}\n"
            f"**Type:** {type_icons}\n"
            f"**Ability:** {i.ability}\n"
            f"**Held Item:** {await itemicon(i.item)} {i.item}\n"
            f"**Role:** *{role_text}*\n"
            f"--- **Moveset** ---\n"
            f"{await movetypeicon(i, i.moves[0])} {i.moves[0].title()} {await movect(i.moves[0])}\n"
            f"{await movetypeicon(i, i.moves[1])} {i.moves[1].title()} {await movect(i.moves[1])}\n"
            f"{await movetypeicon(i, i.moves[2])} {i.moves[2].title()} {await movect(i.moves[2])}\n"
            f"{await movetypeicon(i, i.moves[3])} {i.moves[3].title()} {await movect(i.moves[3])}"
        )
        
        info.add_field(
            name=f"**#{n} {i.icon} {i.nickname}** (Lv.{i.level}) {await teraicon(i.tera)}",
            value=value_field,
            inline=True # Use inline=True to fit 2 Pokémon per row (better visualization)
        )
        
    # Add a blank field to ensure the last row of fields aligns correctly if the total is odd
    if len(tr1.pokemons) % 2 != 0:
         info.add_field(name="\u200b", value="\u200b", inline=True) # Invisible spacer field
         
    info.set_footer(text=f"Total Pokémon: {len(tr1.pokemons)}. Prepare for battle!")

    await ctx.followup.send(embed=info)        

@bot.tree.command(name="claim",description="Claim event pokemons.")           
async def claim(ctx:discord.Interaction,code:str):
    db=sqlite3.connect("event.db")
    c=db.cursor()
    dx=sqlite3.connect("owned.db")
    cx=dx.cursor()
    c.execute(f"""CREATE TABLE IF NOT EXISTS [{ctx.user.id}] (
        claimed text
        )""")
    if code=="GETY0URMEW":
        c.execute(f"select * from [{ctx.user.id}] where claimed='GETY0URMEW'")
        acc=c.fetchone()
        if acc==None:
            type=random.choice(["Rock","Fire","Water","Grass","Electric","Ground","Flying","Fighting","Fairy","Dragon","Steel","Poison","Dark","Ghost","Normal","Bug","Ice","Psychic"])
            p=Pokemon(name="Mew",primaryType="Psychic",secondaryType="???",level=100,hp=100,atk=100,defense=100,spatk=100,spdef=100,speed=100,moves='["Tera Blast","Life Dew","Psychic","Shadow Ball"]', ability="Synchronize",sprite="http://play.pokemonshowdown.com/sprites/ani/mew.gif",gender="Genderless",shiny="No",tera=type)
            p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
            p.moves=f"{p.moves}"
            clk=datetime.datetime.now()
            catchtime=clk.strftime("%Y-%m-%d %H:%M:%S")
            cx.execute(f"""INSERT INTO "{ctx.user.id}" VALUES (
                    "{p.name}",
                    "{p.nickname}",
                    "{p.level}",
                    "{p.hpiv}",
                    "{p.atkiv}",
                    "{p.defiv}",
                    "{p.spatkiv}",
                    "{p.spdefiv}",
                    "{p.speediv}",
                    "{p.hpev}",
                    "{p.atkev}",
                    "{p.defev}",
                    "{p.spatkev}",
                    "{p.spdefev}",
                    "{p.speedev}",
                    "{p.ability}",
                    "{p.nature}",
                    "{p.shiny}",
                    "{p.item}",
                    "{p.gender}",
                    "{p.tera}",
                    "Custom",
                    "{p.moves}",
                    "Event",
                    "{catchtime}",
                    "{p.totaliv}",
                    "Undiscovered")""")
            dx.commit()   
            c.execute(f"""INSERT INTO "{ctx.user.id}" VALUES (
            "GETY0URMEW"
            )""")
            db.commit()      
            em=discord.Embed(title="Congratulations! You claimed 'GETY0URMEW'!",description=f"You claimed a {type}-TeraType Mew from our first ever event!",color=0xffa6cd)   
            em.set_thumbnail(url=p.sprite)
            em.set_image(url="https://www.serebii.net/scarletviolet/mewevent.jpg")  
            await ctx.response.send_message(embed=em)  
        else:
            await ctx.response.send_message("Oops! You already claimed this event.")