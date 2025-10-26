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
          
@bot.tree.command(name="compare",description="Compare two pokémons.")
async def compare(ctx:discord.Interaction,num1:int,num2:int):        
    db = sqlite3.connect("owned.db")
    c = db.cursor()
    nm1=await row(ctx,num1,c)
    nm2=await row(ctx,num2,c)
    p,allmon=await pokonvert(ctx,ctx.user,nm1)
    q,allmon=await pokonvert(ctx,ctx.user,nm2)
    com=discord.Embed(title=f"#{num1} {p.name} {p.icon} vs {q.icon} {q.name} #{num2}",description="Sample comparison between these two pokemons are shown below!")
    com.add_field(name="Attributes:",value=f"**HP:** {await bufficon(p.hp,q.hp)}{p.hp} - {q.hp}{await bufficon(q.hp,p.hp)}\n**ATK:** {await bufficon(p.atk,q.atk)}{p.atk} - {q.atk}{await bufficon(q.atk,p.atk)}\n**DEF:** {await bufficon(p.defense,q.defense)}{p.defense} - {q.defense}{await bufficon(q.defense,p.defense)}\n**SPA:** {await bufficon(p.spatk,q.spatk)}{p.spatk} - {q.spatk}{await bufficon(q.spatk,p.spatk)}\n**SPD:** {await bufficon(p.spdef,q.spdef)}{p.spdef} - {q.spdef}{await bufficon(q.spdef,p.spdef)}\n**SPE:** {await bufficon(p.speed,q.speed)}{p.speed} - {q.speed}{await bufficon(q.speed,p.speed)}")
    com.add_field(name="IVs:",value=f"**HP IV:** {await bufficon(p.hpiv,q.hpiv)}{p.hpiv} - {q.hpiv}{await bufficon(q.hpiv,p.hpiv)}\n**ATK IV:** {await bufficon(p.atkiv,q.atkiv)}{p.atkiv} - {q.atkiv}{await bufficon(q.atkiv,p.atkiv)}\n**DEF IV:** {await bufficon(p.defiv,q.defiv)}{p.defiv} - {q.defiv}{await bufficon(q.defiv,p.defiv)}\n**SPA IV:** {await bufficon(p.spatkiv,q.spatkiv)}{p.spatkiv} - {q.spatkiv}{await bufficon(q.spatkiv,p.spatkiv)}\n**SPD IV:** {await bufficon(p.spdefiv,q.spdefiv)}{p.spdefiv} - {q.spdefiv}{await bufficon(q.spdefiv,p.spdefiv)}\n**SPE IV:** {await bufficon(p.speediv,q.speediv)}{p.speediv} - {q.speediv}{await bufficon(q.speediv,p.speediv)}")
    com.add_field(name="EVs:",value=f"**HP EV:** {await bufficon(p.hpev,q.hpev)}{p.hpev} - {q.hpev}{await bufficon(q.hpev,p.hpev)}\n**ATK EV:** {await bufficon(p.atkev,q.atkev)}{p.atkev} - {q.atkev}{await bufficon(q.atkev,p.atkev)}\n**DEF EV:** {await bufficon(p.defev,q.defev)}{p.defev} - {q.defev}{await bufficon(q.defev,p.defev)}\n**SPA EV:** {await bufficon(p.spatkev,q.spatkev)}{p.spatkev} - {q.spatkev}{await bufficon(q.spatkev,p.spatkev)}\n**SPD EV:** {await bufficon(p.spdefev,q.spdefev)}{p.spdefev} - {q.spdefev}{await bufficon(q.spdefev,p.spdefev)}\n**SPE EV:** {await bufficon(p.speedev,q.speedev)}{p.speedev} - {q.speedev}{await bufficon(q.speedev,p.speedev)}")
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
        await ctx.response.send_message(embed=data)
        
@bot.tree.command(name="movedex",description="Shows move infos.")
async def movedex(ctx:discord.Interaction,name:str):
    name=name.title()
    db=sqlite3.connect("pokemondata.db")
    c=db.cursor()   
    c.execute(f"select * from 'moves' where Name='{name}'")
    p=c.fetchone() 
    if p: 
        clr=await movecolor(p[0])
        data=discord.Embed(title=p[0],description=p[1],color=clr)
        data.add_field(name='Power:',value=p[2],inline=False)
        data.add_field(name='PP:',value=p[3],inline=False) 
        data.add_field(name='Accuracy:',value=p[4],inline=False)
        data.add_field(name='Type:',value=f'{await movetypeicon(None,p[0])}',inline=False)
        data.add_field(name='Catagory:',value=f'{await movect(p[0])}',inline=False)   
        await ctx.response.send_message(embed=data)  
              
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
            print(p.name)
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
    p,allmon=await pokonvert(ctx,ctx.user,num)
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
            p, allmon = await pokonvert(self.ctx, self.ctx.user, row_id) # row_id is the actual ID needed
        
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
        _, allmon = await pokonvert(ctx, ctx.user, None)
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
        p, _ = await pokonvert(ctx, ctx.user, current_index)
        
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
        x.set_author(name=f"{self.user_id}'s PC") 
        
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
        
@bot.tree.command(name="moveset",description="See all the moves this pokémon can learn.")
async def moveset(ctx:discord.Interaction,num:int=1):
    "Shows all the available and learned moves of that particular pokémon."
    dt=sqlite3.connect("pokemondata.db")
    db=sqlite3.connect("owned.db")
    cx=dt.cursor()
    c=db.cursor()       
    num=await row(ctx,num,c)
    p,allmon=await pokonvert(ctx,ctx.user,num)
    c.execute(f"Select * from '{ctx.user.id}' where rowid={num}")
    mon=c.fetchone()
    move=eval(mon[22])
    cx.execute(f"Select * from 'wild' where name='{mon[0]}'")
    spc=cx.fetchone()
    canlearn=list(set(eval(spc[10])+["Tera Blast"])-set(move))
    known=""
    can=""
    n=0
    for i in move:
        n+=1
        known+=f"{await movetypeicon(p,i)} {i} {await movect(i)}\n"
    for i in canlearn:
        can+=f"{i}\n"
    now=discord.Embed(title=f"{mon[0]}'s Moveset:",color=0xff0000)
    now.add_field(name="Current Moveset:",value=known)
    now.add_field(name="Available Moves:",value=can)
    now.set_footer(text="/teach 'num' 'move name' to update moveset.")
    now.set_image(url=spc[12])
    await ctx.response.send_message(embed=now)
    
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
@bot.tree.command(name="teach",description="Teach your pokémon a new move.")
async def teach(ctx:discord.Interaction,mon:int,move:str):
    "Teaches your pokémon a certain move."
    if move!=None:
        select=move.strip()
        if select.lower not in ["u-turn"]:
            select=select.title()
        dt=sqlite3.connect("pokemondata.db")
        db=sqlite3.connect("owned.db")
        cx=dt.cursor()
        c=db.cursor()
        num=await row(ctx,mon,c)        
        p,allmon=await pokonvert(ctx,ctx.user,num) 
        c.execute(f"Select * from '{ctx.user.id}' where rowid={num} ")
        mon=c.fetchone()
        move=eval(mon[22])
        cx.execute(f"Select * from 'wild' where name='{mon[0]}'")
        spc=cx.fetchone()
        canlearn=eval(spc[10])+["Tera Blast"]
        known=""
        n=0
        for i in move:
            n+=1
            known+=f"{await movetypeicon(p,i)} {i} ({n}) {await movect(i)}\n"    
        now=discord.Embed(title=f"{mon[0]}'s Moveset:", description=f"Select a move to replace with {select}!",color=0xff0000)
        now.add_field(name="New Move:",value=f"{await movetypeicon(p,select)} {select} {await movect(select)}")
        now.add_field(name="Current Moveset:",value=known)
        now.set_footer(text="Enter the 'number' of the move you want to replace!")
        if select in canlearn and select not in move:
            await ctx.response.send_message(embed=now)
            while True:
                response = await bot.wait_for('message', check=lambda message: message.author == ctx.user)
                if response.author==ctx.user and "!" in response.content:
                    break
                if response.author==ctx.user and 0<int(response.content)<=4:
                    rep=move[int(response.content)-1]
                    move[int(response.content)-1]=select
                    move=f"{move}".replace('"',"'")
                    c.execute(f"""Update `{ctx.user.id}` set moves="{move}" where rowid={num}""")
                    db.commit()
                    db.close()
                    await ctx.channel.send(f"{rep} was replaced by {select}!")
                    break
        else:
            await ctx.channel.send(f"{mon[0]} cannot learn {select} or you misspelled it.")          
@bot.tree.command(name="evtrain",description="EV train your pokémon.")
async def evtrain(ctx:discord.Interaction,num:int=1,hpev:int=0,atkev:int=0,defev:int=0,spatkev:int=0,spdefev:int=0,speedev:int=0):
    "EV trains your pokémon for free!"
    evlist=[hpev,atkev,defev,spatkev,spdefev,speedev]
    total=hpev+atkev+defev+spatkev+spdefev+speedev
    if max(evlist)<=252 and len(evlist)==6 and total<=508:
        db=sqlite3.connect("owned.db")
        c=db.cursor()
        num=await row(ctx,num,c)
        c.execute(f"""Update `{ctx.user.id}` set 
        hpev="{hpev}",
        atkev="{atkev}",
        defev="{defev}",
        spatkev="{spatkev}",
        spdefev="{spdefev}",
        speedev="{speedev}"
        where rowid={num}""")
        db.commit()
        await ctx.response.send_message("EV training complete.")
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
    
@bot.tree.command(name="breed",description="Breed two pokemons.")
async def breed(ctx:discord.Interaction,mon1:int=1,mon2:int=2):
    "Breed two compatible pokémons. Costs 5,000 <:pokecoin:1134595078892044369>."
    db=sqlite3.connect("owned.db")
    c=db.cursor()
    num1=await row(ctx,mon1,c)
    num2=await row(ctx,mon2,c)
    mon1=await pokonvert(ctx,ctx.user,num1)
    mon2=await pokonvert(ctx,ctx.user,num2)
    mon1=mon1[0]
    mon2=mon2[0]
    eg1=await egggroup(ctx,mon1.name)
    eg2=await egggroup(ctx,mon2.name)
    canbreed=await common(eg1.split(","),eg2.split(","))
    dn=sqlite3.connect("playerdata.db")
    cn=dn.cursor()
    cn.execute(f"select * from '{ctx.user.id}'")
    mmm=cn.fetchone()
    money=mmm[0]
    if (mon1.gender!=mon2.gender and "Undiscovered" not in (eg1,eg2) and canbreed==True) or ("Ditto" in (mon2.name,mon1.name) and "Undiscovered" not in (eg1,eg2)) and money>=50000:
        dt=sqlite3.connect("pokemondata.db")
        ct=dt.cursor()
        name=""
        if mon1.gender=="Female":
            name=mon1.name
        elif mon2.gender=="Female":
            name=mon2.name
        elif mon1.name=="Ditto":
            name=mon2.name
        elif mon2.name=="Ditto":
            name=mon1.name
        ct.execute(f"Select * from 'wild' where name='{name}' ")
        m=ct.fetchone()
        hpiv=max([mon1.hpiv,mon2.hpiv])
        atkiv=max([mon1.atkiv,mon2.atkiv])
        defiv=max([mon1.defiv,mon2.defiv])
        ter=random.choice([mon1.tera,mon2.tera])
        spatkiv=max([mon1.spatkiv,mon2.spatkiv])
        spdefiv=max([mon1.spdefiv,mon2.spdefiv])
        speediv=max([mon1.speediv,mon2.speediv])
        shinyodd=random.randint(1,256)
        shiny="No"
        if shinyodd==7:
            shiny="Yes"
        p=Pokemon(name=m[0],primaryType=m[1],secondaryType=m[2],level=m[3],hp=m[4],atk=m[5],defense=m[6],spatk=m[7],spdef=m[8],speed=m[9],moves=m[10], ability=m[11],sprite=m[12],gender=m[15],maxiv="Custom",shiny=shiny,hpiv=hpiv,atkiv=atkiv,defiv=defiv,spatkiv=spatkiv,spdefiv=spdefiv,speediv=speediv,tera=ter)
        p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
        p.totalev=(p.hpev+p.atkev+p.defev+p.spatkev+p.spdefev+p.speedev)  
        bred=discord.Embed(title="Proceed breeding?", description=f"Sacrifice {mon1.name} and {mon2.name} to breed a better pokémon!\nPrice: 50,000 <:pokecoin:1134595078892044369>")
        types=p.primaryType
        if p.secondaryType!="???":
            types=f"{p.primaryType}/{p.secondaryType}"
        bred.add_field(name=f"Newborn {p.name}", value=f"""**Types:** {types}\n**Tera-Type:** {p.tera}\n**Ability:** {p.ability}\n**Nature:** {p.nature}\n**Gender:** {await statusicon(p.gender)}\n**Held Item:** {p.item}\n**HP:** {p.maxhp} - IV: {p.hpiv}/31 - EV: {p.hpev}\n**Attack:** {p.maxatk} - IV: {p.atkiv}/31 - EV: {p.atkev}\n**Defense:** {p.maxdef} - IV: {p.defiv}/31 - EV: {p.defev}\n**Sp. Atk:** {p.maxspatk} - IV: {p.spatkiv}/31 - EV: {p.spatkev}\n**Sp. Def:** {p.maxspdef} - IV: {p.spdefiv}/31 - EV: {p.spdefev}\n**Speed:** {p.maxspeed} - IV: {p.speediv}/31 - EV: {p.speedev}\n**Total IV %:** {p.totaliv}%\n**Total EV :** {p.totalev}/508""")
        bred.set_image(url=p.sprite)
        await ctx.response.send_message(embed=bred)
        while True:
            ans=await bot.wait_for('message',check=lambda message: message.author==ctx.user)
            if "!" in ans.content or ans.content.lower() in ["n","no"]:
                await ctx.channel.send("Breeding cancelled!")
                break
            if ans.content.lower() in ["y","yes"]:
                c.execute(f"Select *,rowid from '{ctx.user.id}'")
                r=c.fetchall()
                num=[num1,num2]
                num.sort()
                c.execute(f"delete from '{ctx.user.id}' where rowid={num[1]}")
                db.commit()
                c.execute(f"delete from '{ctx.user.id}' where rowid={num[0]}")
                db.commit()
                clk=datetime.datetime.now()
                catchtime=clk.strftime("%Y-%m-%d %H:%M:%S")
                if "<:hatched:1134745434506666085>" not in p.nickname:
                    p.nickname=p.nickname+" <:hatched:1134745434506666085>"
                c.execute(f"""INSERT INTO "{ctx.user.id}" VALUES (
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
                {p.totaliv},
                '{m[18]}')""")
                db.commit()
                await addmoney(ctx,ctx.user,-50000)
                await ctx.channel.send("Breeding successful!")
                break
    else:
        await ctx.channel.send(f" You can't breed a {mon1.gender} {mon1.name} with a {mon2.gender} {mon2.name} or You don't have sufficient balance!")
        
@bot.tree.command(name="takeitem",description="Take item from a pokémon.")
async def takeitem(ctx:discord.Interaction,num:str):
    num=num.split(" ")
    num=list(num)
    new=[]
    for i in num:
        new.append(int(i))
    db=sqlite3.connect("playerdata.db")
    c=db.cursor()
    dt=sqlite3.connect("owned.db")
    ct=dt.cursor()
    for i in new:
        c.execute(f"Select * from '{ctx.user.id}'")
        items=c.fetchone()
        items=eval(items[2])
        num=await row(ctx,i,ct)
        ct.execute(f"select item from '{ctx.user.id}' where rowid={num}")
        item=ct.fetchone()
        item=item[0]
        if item!="None":
            items.append(item)
            items=f"{items}"
            c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
            db.commit()
            ct.execute(f"update '{ctx.user.id}' set item='None' where rowid={num}")
            dt.commit()
            await ctx.response.send_message(f"{item} was sent to your inventory!")
        elif item=="None":
            await ctx.response.send_message(f"It's not holding any item!")
@bot.tree.command(name="buyitem",description="Buy an item.")
async def pokemons(ctx:discord.Interaction,item:str):
    item=item.title()
    db=sqlite3.connect("pokemondata.db")
    c=db.cursor()
    c.execute(f"select * from 'itemshop' where item='{item}'")
    item=c.fetchone()
    dt=sqlite3.connect("playerdata.db")
    ct=dt.cursor()
    ct.execute(f"select * from '{ctx.user.id}'")
    b=ct.fetchone()
    balance=b[0]
    if item[1]>balance:
        await ctx.response.send_message("You don't have enough balance!")
    if item[1]<balance:
        em=discord.Embed(title=f"Would you like to buy {item[0]}?",description=f"**Price:** {await numberify(item[1])} <:pokecoin:1134595078892044369>\n**Balance after purchase:** {await numberify(balance-item[1])} <:pokecoin:1134595078892044369>")
        em.set_thumbnail(url=item[2])
        await ctx.response.send_message(embed=em)
        while True:
            response=await bot.wait_for('message')
            ct.execute(f"select * from '{ctx.user.id}'")
            b=ct.fetchone()
            balance=b[0]
            if response.content.lower() in ["n","no","!"] and response.author==ctx.user and item[1]>balance:
                await ctx.channel.send("You canceled the purchase!")
                break
            if response.content.lower() in ["y","yes"] and response.author==ctx.user and item[1]<balance:
                await addmoney(ctx,ctx.user,-item[1])
                items=eval(b[2])
                items.append(item[0])
                ct.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
                dt.commit()
                await ctx.channel.send(f"You purchased a {item[0]}!")
                break
@bot.tree.command(name="bag",description="Shows all the items in your bag.")
async def bag(ctx:discord.Interaction,page:int=1):  
    db=sqlite3.connect("playerdata.db")
    c=db.cursor()
    c.execute(f"Select * from '{ctx.user.id}'")
    items=c.fetchone()
    items=eval(items[2])
    items.sort()
    newdic=await listtodic(items)
    sub=await gensub(page,newdic)
    tot=round(len(newdic)//15)+1
    bag=discord.Embed(title=f"{ctx.user.display_name}'s Backpack:",description=f"Total item: {len(items)}")
    txt=""
    if len(items)!=0:
        for k,v in sub.items():
            txt+=f"{await itemicon(k)} {k} ×{v}\n"
        bag.add_field(name="Item List:",value=txt)
    else:
        bag.add_field(name="Item List:",value="Your backpack is empty!")     
    bag.set_footer(text=f"Showing {page} out of {tot} pages")
    bag.set_thumbnail(url="https://cdn.discordapp.com/attachments/1102579499989745764/1134073215803723827/image_search_1690454504333.png")       
    await ctx.response.send_message(embed=bag)
    
@bot.tree.command(name="useitem",description="Use item on a pokémon.")
async def useitem(ctx:discord.Interaction,item:str,num:int=1):      
    it=item.title()
    db=sqlite3.connect("playerdata.db")
    c=db.cursor()
    c.execute(f"Select * from '{ctx.user.id}'")
    items=c.fetchone()
    items=eval(items[2])
    dt=sqlite3.connect("owned.db")
    ct=dt.cursor()
    num=await row(ctx,num,ct)
    if "Mint" in it and it in items:
        itm=it.replace(" Mint","")
        ct.execute(f"update '{ctx.user.id}' set nature='{itm}' where rowid={num}")
        dt.commit()
        items.remove(it)
        items=f"{items}"
        c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
        db.commit()
        ct.execute(f"select * from '{ctx.user.id}' where rowid={num}")
        mon=ct.fetchone()
        await ctx.response.send_message(f"{mon[0]}'s stats may have changed due to the effects of the {it}!")
    elif it=="Golden Bottle Cap" and it in items:
        ct.execute(f"update '{ctx.user.id}' set hpiv=31,atkiv=31,defiv=31,spatkiv=31,spdefiv=31,speediv=31 where rowid={num}")
        dt.commit()
        items.remove(it)
        items=f"{items}"
        c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
        db.commit()
        ct.execute(f"select * from '{ctx.user.id}' where rowid={num}")
        mon=ct.fetchone()
        await ctx.response.send_message(f"{mon[0]}'s stats may have changed due to the effects of the {it}!")   
    elif it=="Bottle Cap" and it in items:
        ct.execute(f"select * from `{ctx.user.id}` where rowid={num}")
        m=ct.fetchone()
        em=discord.Embed(title="Which IV stat you wanna max out?",description=f"#1 HP IV : {m[3]}\n#2 Attack IV : {m[4]}\n#3 Defense IV : {m[5]}\n#4 Special Attack IV : {m[6]}\n#5 Special Defense IV : {m[7]}\n#6 Speed IV : {m[8]}\n")
        await ctx.response.send_message(embed=em)
        response = await bot.wait_for('message', check=lambda message: message.author == ctx.user)
        n=int(response.content)
        if n==1 and m[3]!=31:
            ct.execute(f"update '{ctx.user.id}' set hpiv=31 where rowid={num}")
            dt.commit()
            items.remove(it)
            items=f"{items}"
            c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
            db.commit()
        elif n==2 and m[4]!=31:
            ct.execute(f"update '{ctx.user.id}' set atkiv=31 where rowid={num}")
            dt.commit()
            items.remove(it)
            items=f"{items}"
            c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
            db.commit()          
        elif n==3 and m[5]!=31:
            ct.execute(f"update '{ctx.user.id}' set defiv=31 where rowid={num}")
            dt.commit()
            items.remove(it)
            items=f"{items}"
            c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
            db.commit()  
        elif n==4 and m[6]!=31:
            ct.execute(f"update '{ctx.userid}' set spatkiv=31 where rowid={num}")
            dt.commit()
            items.remove(it)
            items=f"{items}"
            c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
            db.commit()
        elif n==5 and m[7]!=31:
            ct.execute(f"update '{ctx.user.id}' set spdefiv=31 where rowid={num}")
            dt.commit()
            items.remove(it)
            items=f"{items}"
            c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
            db.commit()
        elif n==6 and m[8]!=31:
            ct.execute(f"update '{ctx.user.id}' set speediv=31 where rowid={num}")
            dt.commit()
            items.remove(it)
            items=f"{items}"
            c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
            db.commit()
        else:
            await ctx.channel.send("IV is already maxed for this stat.")
        if n in [1,2,3,4,5,6]:
            await ctx.channel.send(f"{m[0]}'s stats may have changed due to the effects of the {it}!")             
    elif it=="Ability Capsule" and it in items:
        dx=sqlite3.connect("pokemondata.db")
        cx=dx.cursor()
        ct.execute(f"select * from '{ctx.user.id}' where rowid={num}")
        mon=ct.fetchone()
        cx.execute(f"select * from 'wild' where name='{mon[0]}'")
        m=cx.fetchone()
        abilities=m[11].split(",")
        ablist=""
        n=0
        for i in abilities:
            n+=1
            ablist+=f"**#{n} {i}**\n{await abilitydesc(i)}\n"
        em=discord.Embed(title=f"Select the desired ability for {mon[1]}!",description=ablist,color=0x00ff00)
        await ctx.response.send_message(embed=em)
        response = await bot.wait_for('message', check=lambda message: message.author == ctx.user)
        try:
            nm=int(response.content)
            if nm<=len(abilities):
                nm-=1
                ab=abilities[nm]
                ct.execute(f"""Update `{ctx.user.id}` set ability="{ab}" where rowid={num}""")
                dt.commit()
                items.remove(it)
                items=f"{items}"
                c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
                db.commit()
                await ctx.channel.send(f"{mon[0]}'s ability may have changed due to the effects of the {it}!")
        except:
            await ctx.channel.send("Process failed!")
    elif "Tera Shard" in it and it in items:
        itm=it.replace(" Tera Shard","")
        ct.execute(f"update '{ctx.user.id}' set teratype='{itm}' where rowid={num}")
        dt.commit()
        items.remove(it)
        items=f"{items}"
        c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
        db.commit()
        ct.execute(f"select * from '{ctx.user.id}' where rowid={num}")
        mon=ct.fetchone()
        await ctx.response.send_message(f"{mon[0]}'s tera-Type may have changed due to the effects of the {it}!")        
    elif it=="Gracidea" and it in items:
        ct.execute(f"select * from '{ctx.user.id}' where rowid={num}")
        mons=c.fetchone()
        mon=mons[0]
    if "Sky" in mon:
        mon=mon.replace("Sky ","")
        ct.execute(f"""Update `{ctx.user.id}` set name="{mon}",ability="Natural Cure" where rowid={num}""")        
        dt.commit()
        await ctx.response.send_message(f"{mon} transformed!")
    elif mon=="Shaymin":
        mon="Sky "+mon
        ct.execute(f"""Update `{ctx.user.id}` set name="{mon}",ability="Serene Grace" where rowid={num}""")        
        dt.commit()        
        await ctx.response.send_message(f"{mon.replace('Sky ','')} tranformed!")
    elif it=="Prison Bottle" and it in items:
        ct.execute(f"select * from '{ctx.user.id}' where rowid={num}")
        mons=c.fetchone()
        mon=mons[0]
    if "Unbound" in mon:
        mon=mon.replace(" Unbound","")
        ct.execute(f"""Update `{ctx.user.id}` set name="{mon}" where rowid={num}""")        
        dt.commit()
        await ctx.send(f"{mon} transformed!")
    elif mon=="Hoopa":
        mon=mon+" Unbound"
        ct.execute(f"""Update `{ctx.user.id}` set name="{mon}" where rowid={num}""")        
        dt.commit()        
        await ctx.response.send_message(f"{mon.replace(' Unbound','')} transformed!")           
    elif it=="Reveal Glass" and it in items:
        ct.execute(f"select * from '{ctx.user.id}' where rowid={num}")
        mons=c.fetchone()
        mon=mons[0]
    if "Therian" in mon:
        mon=mon.replace("Therian ","")
        ab=""
        if mon=="Landorus":
            ab="Intimidate"
        elif mon=="Tornadus":
            ab="Regenerator"
        elif mon=="Thundurus":
            ab="Volt Absorb"
        elif mon=="Enamorus":
            ab="Overcoat"
        ct.execute(f"""Update `{ctx.user.id}` set name="{mon}",ability="{ab}" where rowid={num}""")        
        dt.commit()
        await ctx.response.send_message(f"{mon} transformed!")
    elif mon in ["Thundurus","Landorus","Tornadus","Enamorus"]:
        mon="Therian "+mon
        ab=""
        if mon=="Therian Landorus":
            ab=random.choice(["Sand Force","Sheer Force"])
        elif mon=="Therian Tornadus":
            ab=random.choice(["Defiant","Prankster"])
        elif mon=="Therian Thundurus":
            ab=random.choice(["Defiant","Prankster"])
        elif mon=="Therian Enamorus":
            ab=random.choice(["Contrary","Fairy Aura"])
        ct.execute(f"""Update `{ctx.user.id}` set name="{mon}" where rowid={num}""")        
        dt.commit()        
        await ctx.response.send_message(f"{mon.replace('Therian ','')} transformed!")
        
@bot.tree.command(name="giveitem",description="Give item to a pokémon to hold it..")
async def giveitem(ctx:discord.Interaction,item:str,num:int=1):
    it=item.title()
    db=sqlite3.connect("playerdata.db")
    c=db.cursor()
    c.execute(f"Select * from '{ctx.user.id}'")
    items=c.fetchone()
    items=eval(items[2])
    dt=sqlite3.connect("owned.db")
    ct=dt.cursor()
    num=await row(ctx,num,ct)
    ct.execute(f"select item from '{ctx.user.id}' where rowid={num}")
    item=ct.fetchone()
    item=item[0]
    if item!="None":
        items.append(item)
        items=f"{items}"
        c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
        db.commit()
        ct.execute(f"update '{ctx.user.id}' set item='None' where rowid={num}")
        dt.commit()
        items=eval(items)
        await ctx.response.send_message(f"{item} was sent to your inventory!")
    if it in items:
        ct.execute(f"update '{ctx.user.id}' set item='{it}' where rowid={num}")
        dt.commit()
        items.remove(it)
        items=f"{items}"
        c.execute(f"""update '{ctx.user.id}' set Items="{items}" """)
        db.commit()
        ct.execute(f"select * from '{ctx.user.id}' where rowid={num}")
        x=ct.fetchone()
        try:
            await ctx.response.send_message(f"{x[0]} is now holding a {it}!")
        except:
            await ctx.response.send_message(f"{x[0]} is now holding a {it}!")
async def egggroup(ctx,name):
    db=sqlite3.connect("pokemondata.db")          
    c=db.cursor() 
    c.execute(f"Select * from 'wild' where name='{name}'")
    n=c.fetchone()
    return n[18]
async def common(l1,l2):
    for i in l1:
        if i in l2:
            return True
    return False            
@bot.tree.command(name="trainerinfo",description="Shows a random team of a certified trainer.")
async def trainerinfo(ctx:discord.Interaction,num:int=1):
    tr1=await gameteam(ctx,num)
    db=sqlite3.connect("pokemondata.db")
    c=db.cursor()
    mm=tr1.name.split("> ")[-1]
    c.execute(f"select * from 'Trainers' where name='{mm}'")
    dat=c.fetchone()
    n=0
    txt=""
    if dat!=None:
        if dat[1]!="None":
            txt=f"\n**Badge:**\n{dat[2]} {dat[1]}"
    info=discord.Embed(title=f"{tr1.name}'s Team:",description=f"This is a team sample. You can't rely on it entirely. But you can get an idea about who you are dealing with.{txt}")
    info.set_thumbnail(url=tr1.sprite)
    for i in tr1.pokemons:
        n+=1
        info.add_field(name=f"#{n} {i.icon} {i.nickname} {await teraicon(i.tera)}",value=f"**Ability:** {i.ability}\n**Item:** {await itemicon(i.item)} {i.item}\n{await movetypeicon(i,i.moves[0])} {i.moves[0]} {await movect(i.moves[0])}\n{await movetypeicon(i,i.moves[1])} {i.moves[1]} {await movect(i.moves[1])}\n{await movetypeicon(i,i.moves[2])} {i.moves[2]} {await movect(i.moves[2])}\n{await movetypeicon(i,i.moves[3])} {i.moves[3]} {await movect(i.moves[3])}",inline=False)
    await ctx.response.send_message(embed=info)        

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