from misc import *

@bot.tree.command(name="levelup",description="Levels up a pokemon.")
async def levelup(ctx:discord.Interaction,num:int=1,level:int=1): 
    db=sqlite3.connect("owned.db")
    c=db.cursor()
    if num is not None:
        num=await row(ctx,num,c)
    c.execute(f"SELECT * FROM '{ctx.user.id}'")
    allmon=c.fetchall()
    if num==None:
        num=len(allmon)
        num=await row(ctx,num,c)
    c.execute(f"SELECT * FROM '{ctx.user.id}' where rowid={num}")
    n = c.fetchone() 
    
@bot.tree.command(name="evolve",description="Evolves a pokemon.")
async def evolve(ctx:discord.Interaction,num:int=1): 
    ev="" 
    dt=sqlite3.connect("pokemondata.db")
    ct=dt.cursor()
    db=sqlite3.connect("owned.db")
    c=db.cursor()
    if num is not None:
        num=await row(ctx,num,c)
    c.execute(f"SELECT * FROM '{ctx.user.id}'")
    allmon=c.fetchall()
    if num==None:
        num=len(allmon)
        num=await row(ctx,num,c)
    c.execute(f"SELECT * FROM '{ctx.user.id}' where rowid={num}")
    n = c.fetchone()
    ct.execute(f"SELECT * FROM 'wild' WHERE name=?", (n[0],))
    m = ct.fetchone()
    level=0
    if m[20] not in [None,"None"] and "-" in m[20]:
       level=int(m[20].split('-')[1])-1 
       if n[2]>level and m[20] not in [None,"None"]:
            c.execute(f"""Update `{ctx.user.id}` set name="{m[20].split('-')[0]}" where rowid={num}""") 
            if n[0]==n[1]:
             c.execute(f"""Update `{ctx.user.id}` set nickname="{m[20].split('-')[0]}" where rowid={num}""") 
            db.commit()
            ev=discord.Embed(title="Evolution:",description=f"Congratulations, Your {await pokeicon(n[0])} {n[0]} evolved into {await pokeicon(m[20].split('-')[0])} {m[20].split('-')[0]}!")
    else:
        ev=discord.Embed(title="Evolution:",description=f"Unfortunately, Your {await pokeicon(n[0])} {n[0]} cannot evolve!")
    await ctx.response.send_message(embed=ev)
@bot.tree.command(name="ranking",description="Shows ranking of the pokémons.")
async def ranking(ctx:discord.Interaction,page:int=1):    
    dt=sqlite3.connect("pokemondata.db")
    ct=dt.cursor()
    db=sqlite3.connect("record.db")
    c=db.cursor()  
    c.execute(f"Select * from 'pokemons' order by wins DESC")
    n=c.fetchall()
    numbers=[]
    if len(n)!=0:
        for i in n:
            numbers.append(i)
        list_of_lists = []
        list_temp = []
        limit = 10
        i = 0
        while i < len(numbers):
            if len(list_temp) < limit:
                list_temp.append(numbers[i])
                i += 1
            else:
                list_of_lists.append(list_temp)
                list_temp = []
        list_of_lists.append(list_temp)
        pages=len(list_of_lists)
        if 0<page<=len(list_of_lists):
            x=discord.Embed(title="Pokémon Ranking", description=f"Total {len(n)} ranked pokémons.",color=0x220022)
            x.set_author(name=ctx.user.display_name)
            k=0
            if page>1:
                k=(page-1)*10
            for i in list_of_lists[page-1]:
                c.execute(f"select * from 'pokemons'")
                ll=c.fetchall()
                k+=1
                name=i[0]
                ct.execute(f"Select * from 'wild' where name='{i[0]}'")
                mon=ct.fetchone()
                icon=mon[22]
                x.add_field(name=f"#{k} {icon} {name}",value=f"Total Matches: {i[4]} ; Wins: {i[5]} ; Winrate: {round(((i[5]/i[4])*100),2)}%")
            x.set_footer(text=f"Showing {page} out of {len(list_of_lists)} pages.")
            await ctx.response.send_message(embed=x)
    else:
        await ctx.response.send_message("Unfortunately not many pokémons are ranked. ")        
            
class TradeOffer:
    def __init__(self):
        self.offer1: Optional[str] = None # 'Pokemon', 'Money', 'Free', or 'Cancel'
        self.offer2: Optional[str] = None
        self.lock = asyncio.Lock()
        
    def is_complete(self):
        return self.offer1 is not None and self.offer2 is not None

# --- TradeSelectView (Initial Choice) ---
class TradeSelectView(discord.ui.View):
    def __init__(self, user1: discord.User, user2: discord.User, offer: TradeOffer):
        super().__init__(timeout=300)
        self.user1 = user1
        self.user2 = user2
        self.offer = offer

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id in (self.user1.id, self.user2.id)

    async def select_offer(self, interaction: discord.Interaction, offer_type: str):
        user_num = 1 if interaction.user.id == self.user1.id else 2

        async with self.offer.lock:
            if user_num == 1 and self.offer.offer1 is None:
                self.offer.offer1 = offer_type
            elif user_num == 2 and self.offer.offer2 is None:
                self.offer.offer2 = offer_type
            else:
                await interaction.response.send_message("You already made your selection or are not part of the trade.", ephemeral=True)
                return

        await interaction.response.send_message(f"You selected **{offer_type}**.", ephemeral=True)

        if self.offer.is_complete():
            self.stop() 

    @discord.ui.button(label="Pokémon", style=discord.ButtonStyle.secondary, emoji="🟢")
    async def pokemon_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select_offer(interaction, "Pokemon")

    @discord.ui.button(label="Money", style=discord.ButtonStyle.secondary, emoji="💰")
    async def money_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select_offer(interaction, "Money")

    @discord.ui.button(label="Free/Gift", style=discord.ButtonStyle.secondary, emoji="🎁")
    async def free_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.select_offer(interaction, "Free")
        
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_num = 1 if interaction.user.id == self.user1.id else 2
        
        async with self.offer.lock:
            if user_num == 1: self.offer.offer1 = "Cancel"
            if user_num == 2: self.offer.offer2 = "Cancel"
        
        await interaction.response.send_message(f"Trade cancelled by {interaction.user.mention}.", ephemeral=False)
        self.stop()

class MoneyInputModal(discord.ui.Modal, title='Enter Trade Amount'):
    def __init__(self, user: discord.User, current_money: int):
        super().__init__(timeout=300)
        self.user = user
        self.amount = 0
        self.current_money = current_money
        
    money_to_give = discord.ui.TextInput(
        label='Amount to Trade',
        placeholder='Enter a whole number...',
        required=True,
        style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = int(self.money_to_give.value)
            if amount <= 0:
                await interaction.response.send_message("The amount must be a positive number.", ephemeral=True)
                return
            if amount > self.current_money:
                await interaction.response.send_message(f"You only have {self.current_money} Pokécoins.", ephemeral=True)
                return
            
            self.amount = amount
            await interaction.response.defer() 
            self.stop() 
            
        except ValueError:
            await interaction.response.send_message("Invalid input. Please enter a whole number.", ephemeral=True)
            self.stop()
            
class PokemonSelect(discord.ui.Select):
    def __init__(self, user: discord.User, monlist):
        self.user = user
        self.selected_mon_index = None # Stores the original index (1-based)
        
        # Create select options (using list index + 1 for user-facing slot number)
        options = [
            discord.SelectOption(label=f"#{i+1} - {mon[1]} ({mon[0]})", value=str(i + 1))
            for i, mon in enumerate(monlist)
        ]
        
        # Truncate to Discord's limit of 25 options
        super().__init__(placeholder="Choose a Pokémon to trade...", 
                         min_values=1, max_values=1, options=options[:25])

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("This menu is not for you.", ephemeral=True)
            return

        self.selected_mon_index = int(self.values[0])
        
        # Acknowledge and stop the view
        await interaction.response.edit_message(content=f"Selected Pokémon #{self.selected_mon_index} to trade.", view=None)
        self.view.stop()


class PokemonSelectView(discord.ui.View):
    def __init__(self, user: discord.User, monlist):
        super().__init__(timeout=300)
        self.user = user
        self.select_menu = PokemonSelect(user, monlist)
        self.add_item(self.select_menu)
        self.selected_index = None 

    async def on_timeout(self):
        # We don't want to edit the message here, as it might interfere with interaction responses.
        pass

    async def wait(self) -> Optional[int]:
        await super().wait()
        return self.select_menu.selected_mon_index               
        
@bot.tree.command(name="trade", description="Initiate a trade with another user.")
@app_commands.describe(member="The user you want to trade with.")
async def trade_slash(interaction: discord.Interaction, member: discord.Member):
    user1 = interaction.user
    user2 = member

    if user1.id == user2.id:
        await interaction.response.send_message("You can't trade with yourself!", ephemeral=True)
        return

    # Defer the initial response
    await interaction.response.defer(thinking=True, ephemeral=False)
    
    # 1. Initial Trade Type Selection (Handles tr1 and tr2)
    offer_data = TradeOffer()
    initial_msg_content = f"**{user1.mention}** and **{user2.mention}**, please select what you are offering by pressing the buttons below."
    
    select_view = TradeSelectView(user1, user2, offer_data)
    
    msg = await interaction.followup.send(initial_msg_content, view=select_view)
    await select_view.wait() 
    
    # Clean up and retrieve results
    try:
        await msg.edit(view=None)
    except Exception:
        pass # Ignore if message was deleted/error
        
    tr1 = offer_data.offer1
    tr2 = offer_data.offer2
    
    # 🛑 REVISED: Only cancel if explicitly requested by a user
    if "Cancel" in (tr1, tr2):
        # If cancelled, the view already sent a message, so we just return.
        return

    # --- Database Connection (Using the common connection for efficiency) ---
    try:
        db = sqlite3.connect("playerdata.db")
        owned_db = sqlite3.connect("owned.db")
        
        # --- Trade Logic Implementation ---

        # Case 1: Money <-> Free (tr1="Money", tr2="Free" or vice versa)
        if (tr1 == "Money" and tr2 == "Free") or (tr2 == "Money" and tr1 == "Free"):
            money_giver = user1 if tr1 == "Money" else user2
            free_receiver = user2 if tr1 == "Money" else user1
            
            c = db.cursor()
            c.execute(f"SELECT money FROM '{money_giver.id}'")
            money_data = c.fetchone()
            current_money = money_data[0] if money_data else 0

            # Present Money Input Modal
            money_modal = MoneyInputModal(money_giver, current_money)
            
            # Send an invisible message and wait for the modal result
            prompt_msg = await interaction.followup.send(f"{money_giver.mention}, a **modal** has popped up for you to enter the money amount.", ephemeral=True)
            await money_giver.send(f"Please enter the amount of money you want to trade to {free_receiver.mention}.", view=money_modal)
            
            await money_modal.wait()
            
            new_amount = money_modal.amount
            
            if new_amount > 0:
                await addmoney(None, free_receiver, new_amount) # Use interaction context if addmoney requires it, otherwise None
                await addmoney(None, money_giver, -new_amount)
                
                await interaction.followup.send(f"✅ **Money Trade Complete!** {money_giver.mention} sent **{new_amount}** Pokécoins to {free_receiver.mention}.")
            else:
                await interaction.followup.send("Trade cancelled due to invalid money input.")

        elif tr1 == "Money" and tr2 == "Money":
            c = db.cursor()
            
            # Sub-step 1: Get money amount for User 1
            c.execute(f"SELECT money FROM '{user1.id}'")
            money_data1 = c.fetchone()
            current_money1 = money_data1[0] if money_data1 else 0

            money_modal1 = MoneyInputModal(user1, current_money1)
            await interaction.followup.send(f"{user1.mention}, enter the amount you want to send to {user2.mention}.", ephemeral=True)
            await user1.send(f"Please enter the amount of money you want to trade to {user2.mention}.", view=money_modal1)
            await money_modal1.wait()
            amount1 = money_modal1.amount
            
            if amount1 <= 0:
                await interaction.followup.send(f"Trade cancelled by {user1.mention} due to invalid amount.")
                return

            # Sub-step 2: Get money amount for User 2
            c.execute(f"SELECT money FROM '{user2.id}'")
            money_data2 = c.fetchone()
            current_money2 = money_data2[0] if money_data2 else 0

            money_modal2 = MoneyInputModal(user2, current_money2)
            await interaction.followup.send(f"{user2.mention}, enter the amount you want to send to {user1.mention}.", ephemeral=True)
            await user2.send(f"Please enter the amount of money you want to trade to {user1.mention}.", view=money_modal2)
            await money_modal2.wait()
            amount2 = money_modal2.amount

            if amount2 <= 0:
                await interaction.followup.send(f"Trade cancelled by {user2.mention} due to invalid amount.")
                return
            
            # Sub-step 3: Finalize transfer
            await addmoney(None, user2, amount1)
            await addmoney(None, user1, -amount1)
            
            await addmoney(None, user1, amount2)
            await addmoney(None, user2, -amount2)
            
            await interaction.followup.send(
                f"✅ **Money Transfer Complete!** "
                f"{user1.mention} sent **{amount1}** Pokécoins to {user2.mention}. "
                f"{user2.mention} sent **{amount2}** Pokécoins to {user1.mention}."
            )

        # Case 3: Pokemon <-> Pokemon (Swap)
        elif tr1 == "Pokemon" and tr2 == "Pokemon":
            
            c_owned = owned_db.cursor()
            
            # --- 1. User 1 Selects Pokémon ---
            
            c_owned.execute(f"SELECT name, nickname FROM '{user1.id}'")
            monlist1 = c_owned.fetchall()

            if not monlist1:
                await interaction.followup.send(f"{user1.mention} has no Pokémon to trade. Trade cancelled.")
                return

            # Prompt User 1 for their Pokémon
            pokemon_view_1 = PokemonSelectView(user1, monlist1) 
        
        # 2. Send the message using the view
        await interaction.followup.send(
            f"**{user1.mention}**, select the Pokémon you wish to trade.", 
            view=pokemon_view_1, ephemeral=True
        )
        
        # 3. Call .wait() on the VIEW OBJECT
        poke_index_1 = await pokemon_view_1.wait() 
        
        if not poke_index_1:
            await interaction.followup.send("Pokémon selection timed out or was cancelled. Trade cancelled.")
            return
            
            # Retrieve User 1's Pokémon details (p1) and row ID (nm1)
            nm1 = await row(None, poke_index_1, c_owned)
            p1, _ = await pokonvert(None, user1, poke_index_1) 
            
            # --- 2. User 2 Selects Pokémon ---
            
            c_owned.execute(f"SELECT name, nickname FROM '{user2.id}'")
            monlist2 = c_owned.fetchall()

            if not monlist2:
                await interaction.followup.send(f"{user2.mention} has no Pokémon to trade. Trade cancelled.")
                return

            # Prompt User 2 for their Pokémon
            pokemon_view_2 = PokemonSelectView(user2, monlist2)
            
            # 2. Send the message using the view
            await interaction.followup.send(
                f"**{user2.mention}**, select the Pokémon you wish to trade.", 
                view=pokemon_view_2, ephemeral=True
            )
            
            # 3. Call .wait() on the VIEW OBJECT
            poke_index_2 = await pokemon_view_2.wait() 
            
            if not poke_index_2:
                await interaction.followup.send("Pokémon selection timed out or was cancelled. Trade cancelled.")
                return
            
            # Retrieve User 2's Pokémon details (p2) and row ID (nm2)
            nm2 = await row(None, poke_index_2, c_owned)
            p2, _ = await pokonvert(None, user2, poke_index_2)


            # --- 3. Final Confirmation ---

            # Build the confirmation embed
            
            # Assuming typeicon/teraicon return string icons and p.icon is available
            desc = (
                f"**{user1.mention}** trades: {p1.icon} **{p1.nickname}** Lv.{p1.level} (IV: {round(((p1.hpiv+p1.atkiv+p1.defiv+p1.spatkiv+p1.spdefiv+p1.speediv)/186)*100,2)}%)\n"
                f"**{user2.mention}** trades: {p2.icon} **{p2.nickname}** Lv.{p2.level} (IV: {round(((p2.hpiv+p2.atkiv+p2.defiv+p2.spatkiv+p2.spdefiv+p2.speediv)/186)*100,2)}%)"
            )

            confirm_embed = discord.Embed(
                title=f"Confirm Pokémon Swap",
                description=desc,
                color=discord.Color.gold()
            )
            
            # For simplicity, we just use the first Pokémon's sprite, or you could combine them
            if p1.sprite: confirm_embed.set_thumbnail(url=p1.sprite)
            
            # Use a simple button view for mutual confirmation
            confirm_view = discord.ui.View(timeout=120)
            confirm_view.users_confirmed = set()

            @discord.ui.button(label="Confirm Swap", style=discord.ButtonStyle.secondary, emoji="🤝")
            async def mutual_confirm_button(interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id not in (user1.id, user2.id):
                    await interaction.response.send_message("You are not part of this trade.", ephemeral=True)
                    return
                
                confirm_view.users_confirmed.add(interaction.user.id)
                
                if len(confirm_view.users_confirmed) == 2:
                    await interaction.response.edit_message(content="Both parties have confirmed the trade.", view=None)
                    confirm_view.stop()
                else:
                    await interaction.response.edit_message(content=f"Waiting for **{user2.mention if interaction.user.id == user1.id else user1.mention}** to confirm...", view=confirm_view)

            @discord.ui.button(label="Cancel Swap", style=discord.ButtonStyle.secondary, emoji="❌")
            async def cancel_swap_button(interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id in (user1.id, user2.id):
                    confirm_view.users_confirmed.clear()
                    await interaction.response.edit_message(content=f"Trade cancelled by {interaction.user.mention}.", view=None)
                    confirm_view.stop()
                else:
                    await interaction.response.send_message("You are not part of this trade.", ephemeral=True)

            await interaction.followup.send(f"{user1.mention} and {user2.mention}, please confirm the Pokémon Swap:", embed=confirm_embed, view=confirm_view)
            await confirm_view.wait()

            # --- 4. Database Execution (Swapping) ---
            if len(confirm_view.users_confirmed) == 2:
                clk = datetime.datetime.now()
                catchtime = clk.strftime("%Y-%m-%d %H:%M:%S")

                # Mark both Pokémon as traded
                if "<:traded:1127340280966828042>" not in p1.nickname:
                    p1.nickname = p1.nickname + " <:traded:1127340280966828042>"
                if "<:traded:1127340280966828042>" not in p2.nickname:
                    p2.nickname = p2.nickname + " <:traded:1127340280966828042>"

                # ⚠️ WARNING: SWAPPING ROWS IN SQLITE IS TRICKY AND PRONE TO ERROR.
                # The safest way is to DELETE and INSERT, ensuring the original rowid (nm1/nm2) is not reused
                # unless you specifically manage it. We use the safe DELETE/INSERT here.

                # Insert p1 (from user1) into user2's table
                c_owned.execute(f"""INSERT INTO "{user2.id}" VALUES (
                "{p1.name}", "{p1.nickname}", "{p1.level}", "{p1.hpiv}", "{p1.atkiv}", 
                "{p1.defiv}", "{p1.spatkiv}", "{p1.spdefiv}", "{p1.speediv}", "{p1.hpev}", 
                "{p1.atkev}", "{p1.defev}", "{p1.spatkev}", "{p1.spdefev}", "{p1.speedev}", 
                "{p1.ability}", "{p1.nature}", "{p1.shiny}", "{p1.item}", "{p1.gender}", 
                "{p1.tera}", "Custom", "{p1.moves}", "Traded", "{catchtime}")""")

                # Insert p2 (from user2) into user1's table
                c_owned.execute(f"""INSERT INTO "{user1.id}" VALUES (
                "{p2.name}", "{p2.nickname}", "{p2.level}", "{p2.hpiv}", "{p2.atkiv}", 
                "{p2.defiv}", "{p2.spatkiv}", "{p2.spdefiv}", "{p2.speediv}", "{p2.hpev}", 
                "{p2.atkev}", "{p2.defev}", "{p2.spatkev}", "{p2.spdefev}", "{p2.speedev}", 
                "{p2.ability}", "{p2.nature}", "{p2.shiny}", "{p2.item}", "{p2.gender}", 
                "{p2.tera}", "Custom", "{p2.moves}", "Traded", "{catchtime}")""")

                # Delete the original Pokémon from both users' tables
                c_owned.execute(f"DELETE FROM '{user1.id}' WHERE rowid={nm1}")
                c_owned.execute(f"DELETE FROM '{user2.id}' WHERE rowid={nm2}")
                
                owned_db.commit()

                await interaction.followup.send(f"🎉 **Pokémon Swap Successful!** {p1.nickname} was swapped for {p2.nickname}!")
            else:
                await interaction.followup.send("Pokémon swap cancelled.")
        # Case 2 & 3: Pokémon <-> Free OR Pokémon <-> Money
        elif (tr1 == "Pokemon" and tr2 == "Free") or \
             (tr2 == "Pokemon" and tr1 == "Free") or \
             (tr1 == "Pokemon" and tr2 == "Money") or \
             (tr2 == "Pokemon" and tr1 == "Money"):
            
            # Determine roles
            pokemon_giver = user1 if tr1 == "Pokemon" or (tr1 == "Pokemon" and tr2 == "Money") else user2
            other_trader = user2 if pokemon_giver.id == user1.id else user1
            
            # Sub-step 1: Get money amount if applicable (Money <-> Pokemon trade)
            money_amount = 0
            if "Money" in (tr1, tr2):
                money_giver = other_trader # The other trader is the money giver
                c = db.cursor()
                c.execute(f"SELECT money FROM '{money_giver.id}'")
                money_data = c.fetchone()
                current_money = money_data[0] if money_data else 0

                money_modal = MoneyInputModal(money_giver, current_money)
                
                # Send a prompt to the money giver
                await interaction.followup.send(f"{money_giver.mention}, a **modal** has popped up for you to enter the money amount.", ephemeral=True)
                await money_giver.send(f"Please enter the amount of money you are giving for the Pokémon.", view=money_modal)
                
                await money_modal.wait()
                money_amount = money_modal.amount
                
                if money_amount <= 0:
                    await interaction.followup.send("Trade cancelled. Invalid money amount provided.")
                    return

            # Sub-step 2: Pokémon Selection
            c_owned = owned_db.cursor()
            c_owned.execute(f"SELECT name, nickname FROM '{pokemon_giver.id}'")
            monlist = c_owned.fetchall()

            if not monlist:
                await interaction.followup.send(f"{pokemon_giver.mention} has no Pokémon to trade. Trade cancelled.")
                return

            pokemon_view = PokemonSelectView(pokemon_giver, monlist)
            
            prompt_msg = await interaction.followup.send(f"{pokemon_giver.mention}, please select the Pokémon you wish to trade via the dropdown menu.", view=pokemon_view)
            pokemon_index_to_trade = await pokemon_view.wait() 
            
            if not pokemon_index_to_trade:
                await interaction.followup.send("Pokémon selection timed out or was cancelled. Trade cancelled.")
                return

            # Sub-step 3: Confirmation (Only needed for money trade or complex trades)
            # Fetch Pokémon details for the embed
            nm = await row(None, pokemon_index_to_trade, c_owned) # Get rowid
            p, allmon = await pokonvert(None, pokemon_giver, pokemon_index_to_trade) 
            
            # Build the confirmation embed
            # (Note: Using placeholders for missing functions like typeicon/teraicon/moncolor)
            types = p.primaryType
            if p.secondaryType != "???":
                # Assuming typeicon/teraicon return string icons
                types = f"({p.primaryType}/{p.secondaryType})" 

            trade_details = f"{p.icon} {p.nickname} Lv.{p.level}"
            if "Money" in (tr1, tr2):
                trade_details += f" for {money_amount}<:pokecoin:1134595078892044369>"

            confirm_embed = discord.Embed(
                title=f"Confirm Trade: {trade_details}",
                description=f"**Pokémon Giver:** {pokemon_giver.mention}\n**Receiver:** {other_trader.mention}\n\n**Total IV %:** {round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)}%",
                color=discord.Color.orange()
            )
            confirm_embed.set_image(url=p.sprite)

            await interaction.followup.send(f"{other_trader.mention}, do you confirm this trade?", embed=confirm_embed)
            
            # Final confirmation logic (using simple buttons)
            confirm_view = discord.ui.View(timeout=120)
            confirm_view.value = None

            @discord.ui.button(label="Confirm", style=discord.ButtonStyle.secondary)
            async def confirm_button(interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != other_trader.id:
                    await interaction.response.send_message("Only the receiving trader can confirm.", ephemeral=True)
                    return
                confirm_view.value = True
                await interaction.response.edit_message(content="Trade confirmed by receiver.", view=None)
                confirm_view.stop()

            @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
            async def cancel_button(interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id == pokemon_giver.id or interaction.user.id == other_trader.id:
                    confirm_view.value = False
                    await interaction.response.edit_message(content="Trade cancelled.", view=None)
                    confirm_view.stop()
                else:
                    await interaction.response.send_message("You are not part of this trade.", ephemeral=True)

            confirm_msg = await interaction.followup.send(f"Awaiting confirmation from {other_trader.mention}.", view=confirm_view)
            await confirm_view.wait()
            
            if confirm_view.value is True:
                # Sub-step 4: EXECUTE TRADE
                clk = datetime.datetime.now()
                catchtime = clk.strftime("%Y-%m-%d %H:%M:%S")

                if "<:traded:1127340280966828042>" not in p.nickname:
                    p.nickname = p.nickname + " <:traded:1127340280966828042>"

                # 1. Insert into receiver's owned DB
                c_owned.execute(f"""INSERT INTO "{other_trader.id}" VALUES (
                "{p.name}", "{p.nickname}", "{p.level}", "{p.hpiv}", "{p.atkiv}", 
                "{p.defiv}", "{p.spatkiv}", "{p.spdefiv}", "{p.speediv}", "{p.hpev}", 
                "{p.atkev}", "{p.defev}", "{p.spatkev}", "{p.spdefev}", "{p.speedev}", 
                "{p.ability}", "{p.nature}", "{p.shiny}", "{p.item}", "{p.gender}", 
                "{p.tera}", "Custom", "{p.moves}", "Traded", "{catchtime}")""")
                
                # 2. Delete from giver's owned DB
                c_owned.execute(f"DELETE FROM '{pokemon_giver.id}' WHERE rowid={nm}")
                
                # 3. Handle Money Transfer (if applicable)
                if money_amount > 0:
                    await addmoney(None, pokemon_giver, money_amount)
                    await addmoney(None, money_giver, -money_amount) 

                owned_db.commit()

                await interaction.followup.send(f"🎉 **Trade Successful!** {p.nickname} has been traded from {pokemon_giver.mention} to {other_trader.mention} (for {money_amount} Pokécoins if applicable).")
            else:
                await interaction.followup.send("Trade cancelled by one of the participants.")
        
    finally:
        # ALWAYS close the database connections
        if 'db' in locals():
            db.close()
        if 'owned_db' in locals():
            owned_db.close()
            
# @bot.command(aliases=["td"])
# async def trade(ctx,member:discord.Member):
#   tr1="None"
#   tr2="None"
#   while (tr1=="None" and tr2=="None"):
#     await ctx.send(f"{ctx.author.mention} what you wanna trade? (pokemon/money/free)")
#     response=await bot.wait_for('message',check=lambda message:message.author==ctx.author)
#     if response.content.lower() in ["p","poke","pokemon","pk"]:
#       tr1="Pokemon"
#     elif response.content.lower() in ["c","cash","money","dollar","mn"]:
#       tr1="Money" 
#     elif response.content.lower() in ["fr","free","gift"]:
#       tr1="Free"            
#     elif response.content.lower() in ["cn","cancel","end","en"]:
#       tr1="Cancel"      
#     await ctx.send(f"{member.mention} what you wanna trade? (pokemon/money/free)")   
#     res1=await bot.wait_for('message',check=lambda message:message.author==member)
#     if res1.content.lower() in ["p","poke","pokemon","pk"]:
#       tr2="Pokemon"
#     elif res1.content.lower() in ["c","cash","money","dollar","mn"]:
#       tr2="Money" 
#     elif res1.content.lower() in ["fr","free","gift"]:
#       tr2="Free"            
#     elif res1.content.lower() in ["cn","cancel","end","en"]:
#       tr2="Cancel"    
#   if "Cancel" in (tr1,tr2):
#     await ctx.send("Trade cancelled.")
#   elif tr1=="Money" and tr2=="Free":
#     db=sqlite3.connect("playerdata.db")
#     c=db.cursor()
#     c.execute(f"select * from '{ctx.author.id}'")
#     m=c.fetchone()
#     money=m[0]
#     while True:
#       await ctx.send(f"{ctx.author.mention} how much money you wanna give?")
#       response=await bot.wait_for('message',check=lambda message:message.author==ctx.author)
#       try:
#         if int(response.content)<=money:
#           new=int(response.content)
#           await addmoney(ctx,member,new)
#           await addmoney(ctx,ctx.author,-new)
#           break
#       except:
#         await ctx.send(f"{ctx.author.mention},you don't have enough money!")
#         break
#   elif tr2=="Money" and tr1=="Free":
#     db=sqlite3.connect("playerdata.db")
#     c=db.cursor()
#     c.execute(f"select * from '{member.id}'")
#     m=c.fetchone()
#     money=m[0]
#     while True:
#       await ctx.send(f"{member.mention} how much money you wanna give?")
#       response=await bot.wait_for('message',check=lambda message:message.author==member)
#       try:
#         if int(response.content)<=money:
#           new=int(response.content)
#           await addmoney(ctx,ctx.author,new)
#           await addmoney(ctx,member,-new)
#           break
#       except:
#         await ctx.send(f"{member.mention},you don't have enough money!")
#         break          
#   elif tr1=="Pokemon" and tr2=="Free":
#     await ctx.send(f"{ctx.author.mention} which pokemon you wanna trade for free?")
#     while True:
#       response=await bot.wait_for('message',check=lambda message:message.author==ctx.author)
#       db=sqlite3.connect("owned.db")
#       c=db.cursor()
#       c.execute(f"select * from '{ctx.author.id}'")
#       monlist=c.fetchall()
#       if int(response.content)<=len(monlist):
#         num=int(response.content)
#         nm=await row(ctx,num,c)
#         p,allmon=await pokonvert(ctx,ctx.author,num)
#         types=await typeicon(p.primaryType)
#         clr=await moncolor(p.tera)
#         p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
#         if p.secondaryType!="???":
#           types=f"{await typeicon(p.primaryType)}{await typeicon(p.secondaryType)}"
#         infos=discord.Embed(title=f"{p.icon} {p.nickname} Lv.{p.level} will be traded to {member.mention}!",description=f"""**Types:** {types}{await teraicon(p.tera)}\n**Ability:** {p.ability}\n**Nature:** {p.nature}\n**Gender:** {p.gender}\n**Held Item:** {p.item}\n**Total IV %:** {p.totaliv}%""",color=clr)
#         infos.set_image(url=p.sprite)
#         await ctx.send(embed=infos)
#         while True:
#           response=await bot.wait_for('message',check=lambda message:message.author==ctx.author)
#           if (response.content).lower() in ["yes","y","confirm","cm"]:
#             clk=datetime.datetime.now()
#             catchtime=clk.strftime("%Y-%m-%d %H:%M:%S")
#             if "<:traded:1127340280966828042>" not in p.nickname:
#               p.nickname=p.nickname+" <:traded:1127340280966828042>"
#             c.execute(f"""INSERT INTO "{member.id}" VALUES (
#           "{p.name}",
#           "{p.nickname}",
#           "{p.level}",
#           "{p.hpiv}",
#           "{p.atkiv}",
#           "{p.defiv}",
#           "{p.spatkiv}",
#           "{p.spdefiv}",
#           "{p.speediv}",
#           "{p.hpev}",
#           "{p.atkev}",
#           "{p.defev}",
#           "{p.spatkev}",
#           "{p.spdefev}",
#           "{p.speedev}",
#           "{p.ability}",
#           "{p.nature}",
#           "{p.shiny}",
#           "{p.item}",
#           "{p.gender}",
#           "{p.tera}",
#           "Custom",
#           "{p.moves}",
#           "Traded",
#           "{catchtime}")""")
#             db.commit()
#             c.execute(f"delete from '{ctx.author.id}' where rowid={nm}")
#             db.commit()
#             await ctx.send("Traded successfully.")  
#           else:
#             break
#       else:       
#         break     
#   elif tr2=="Pokemon" and tr1=="Free":
#     await ctx.send(f"{member.mention} which pokemon you wanna trade for free?")
#     while True:
#       response=await bot.wait_for('message',check=lambda message:message.author==member)
#       db=sqlite3.connect("owned.db")
#       c=db.cursor()
#       c.execute(f"select * from '{member.id}'")
#       monlist=c.fetchall()
#       if int(response.content)<=len(monlist):
#         num=int(response.content)
#         nm=await row(ctx,num,c)
#         p,allmon=await pokonvert(ctx,ctx.author,num)
#         types=await typeicon(p.primaryType)
#         clr=await moncolor(p.tera)
#         p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
#         if p.secondaryType!="???":
#           types=f"{await typeicon(p.primaryType)}{await typeicon(p.secondaryType)}"
#         infos=discord.Embed(title=f"{p.icon} {p.nickname} Lv.{p.level} will be traded to {member.mention}!",description=f"""**Types:** {types}{await teraicon(p.tera)}\n**Ability:** {p.ability}\n**Nature:** {p.nature}\n**Gender:** {p.gender}\n**Held Item:** {p.item}\n**Total IV %:** {p.totaliv}%""",color=clr)
#         infos.set_image(url=p.sprite)
#         await ctx.send(embed=infos)
#         while True:
#           response=await bot.wait_for('message',check=lambda message:message.author==member)
#           if (response.content).lower() in ["yes","y","confirm","cm"]:
#             clk=datetime.datetime.now()
#             catchtime=clk.strftime("%Y-%m-%d %H:%M:%S")
#             if "<:traded:1127340280966828042>" not in p.nickname:
#               p.nickname=p.nickname+" <:traded:1127340280966828042>"
#             c.execute(f"""INSERT INTO "{ctx.author.id}" VALUES (
#           "{p.name}",
#           "{p.nickname}",
#           "{p.level}",
#           "{p.hpiv}",
#           "{p.atkiv}",
#           "{p.defiv}",
#           "{p.spatkiv}",
#           "{p.spdefiv}",
#           "{p.speediv}",
#           "{p.hpev}",
#           "{p.atkev}",
#           "{p.defev}",
#           "{p.spatkev}",
#           "{p.spdefev}",
#           "{p.speedev}",
#           "{p.ability}",
#           "{p.nature}",
#           "{p.shiny}",
#           "{p.item}",
#           "{p.gender}",
#           "{p.tera}",
#           "Custom",
#           "{p.moves}",
#           "Traded",
#           "{catchtime}")""")
#             db.commit()
#             c.execute(f"delete from '{member.id}' where rowid={nm}")
#             db.commit()
#             await ctx.send("Traded successfully.")  
#           else:
#             break        
#       else:       
#         break             
#   elif tr2=="Money" and tr1=="Pokemon":
#     db=sqlite3.connect("playerdata.db")
#     c=db.cursor()
#     c.execute(f"select * from '{member.id}'")
#     m=c.fetchone()
#     money=m[0]
#     while True:
#       await ctx.send(f"{member.mention} how much money you wanna give?")
#       response=await bot.wait_for('message',check=lambda message:message.author==member)
#       if int(response.content)<=money:
#         new=int(response.content)
#         break
#       else:
#         break
#     await ctx.send(f"{ctx.author.mention} which pokemon you wanna trade for {new}<:pokecoin:1134595078892044369>?")
#     while True:
#       response=await bot.wait_for('message',check=lambda message:message.author==ctx.author)
#       db=sqlite3.connect("owned.db")
#       c=db.cursor()
#       c.execute(f"select * from '{ctx.author.id}'")
#       monlist=c.fetchall()
#       if int(response.content)<=len(monlist):
#         num=int(response.content)
#         nm=await row(ctx,num,c)
#         p,allmon=await pokonvert(ctx,ctx.author,num)
#         types=await typeicon(p.primaryType)
#         clr=await moncolor(p.tera)
#         p.totaliv=round(((p.hpiv+p.atkiv+p.defiv+p.spatkiv+p.spdefiv+p.speediv)/186)*100,2)
#         if p.secondaryType!="???":
#           types=f"{await typeicon(p.primaryType)}{await typeicon(p.secondaryType)}"
#         infos=discord.Embed(title=f"{p.icon} {p.nickname} Lv.{p.level} will be traded to {member.mention} for {new}<:pokecoin:1134595078892044369>. {ctx.author.mention},Do you confirm?",description=f"""**Types:** {types}{await teraicon(p.tera)}\n**Ability:** {p.ability}\n**Nature:** {p.nature}\n**Gender:** {p.gender}\n**Held Item:** {p.item}\n**Total IV %:** {p.totaliv}%""",color=clr)
#         infos.set_image(url=p.sprite)
#         await ctx.send(embed=infos)  
#         p1=""  
#         p2=""
#         while True:
#           response=await bot.wait_for('message',check=lambda message:message.author==ctx.author)
#           if (response.content).lower() in ["yes","y","confirm","cm"]:
#             p1="Confirmed"
#             break
#           else:
#             break
#         if p1=="Confirmed":
#           while True:
#             await ctx.send(f"{member.mention} do you want to confirm the trade?")
#             response=await bot.wait_for('message',check=lambda message:message.author==member)
#             if (response.content).lower() in ["yes","y","confirm","cm"]:
#               p2="Confirmed"
#               clk=datetime.datetime.now()
#               catchtime=clk.strftime("%Y-%m-%d %H:%M:%S")
#               if "<:traded:1127340280966828042>" not in p.nickname:
#                 p.nickname=p.nickname+" <:traded:1127340280966828042>"
#               c.execute(f"""INSERT INTO "{member.id}" VALUES (
#           "{p.name}",
#           "{p.nickname}",
#           "{p.level}",
#           "{p.hpiv}",
#           "{p.atkiv}",
#           "{p.defiv}",
#           "{p.spatkiv}",
#           "{p.spdefiv}",
#           "{p.speediv}",
#           "{p.hpev}",
#           "{p.atkev}",
#           "{p.defev}",
#           "{p.spatkev}",
#           "{p.spdefev}",
#           "{p.speedev}",
#           "{p.ability}",
#           "{p.nature}",
#           "{p.shiny}",
#           "{p.item}",
#           "{p.gender}",
#           "{p.tera}",
#           "Custom",
#           "{p.moves}",
#           "Traded",
#           "{catchtime}")""")
#               db.commit()
#               c.execute(f"delete from '{ctx.author.id}' where rowid={nm}")
#               db.commit()
#               await addmoney(ctx,ctx.author,new)
#               await addmoney(ctx,member,-new)
#               await ctx.send("Traded successfully.")
#               break
#             else:
#               break
#   else:
#     await ctx.send("Trade cancelled.")  
          
@bot.command(aliases=["bt"])
async def battle(ctx,member:discord.Member):
    await ctx.send(f"{member.mention} do you want to battle?")
    while True:
        response=await bot.wait_for('message',check=lambda message:message.author==member)
        if response.content.lower() in ["y","yes"]:
            await ctx.send(f"Battle starting between {ctx.author.display_name} and {member.display_name}!")
            await multiplayer(ctx,ctx.author,member)
            break
        else:
            break
@bot.command(aliases=["rnk"])
async def ranked(ctx):
    await multiplayer(ctx,ctx.author,"ranked")            
@bot.command(aliases=["gm"])
async def game(ctx,num=0):
    await multiplayer(ctx,ctx.author,num)
    
@bot.tree.command(name="view", description="View a Pokémon's stats from your team.")
@app_commands.describe(num="The slot number of the Pokémon you want to view (1-6).")
async def view(interaction: discord.Interaction, num: app_commands.Range[int, 1, 6] = 1):
    # Use interaction.user instead of ctx.author
    user = interaction.user
    
    # NOTE: teamconvert must be updated to accept the user object or ID instead of ctx.author/ctx.author.id
    # We pass the user object here, assuming teamconvert is designed to handle it.
    team = await teamconvert(interaction, user, user.id) 
    
    if not team:
        # Send an immediate, visible error response if the team can't be loaded or is empty
        await interaction.response.send_message("❌ Could not load your team.", ephemeral=True)
        return
        
    if not (1 <= num <= len(team)):
        await interaction.response.send_message(f"❌ Please select a Pokémon number between 1 and {len(team)}.", ephemeral=True)
        return

    p = team[num - 1]
    
    # --- Pokémon Info Logic (Remains mostly the same) ---
    types = p.primaryType
    if p.secondaryType != "???":
        types = f"{p.primaryType}/{p.secondaryType}"
        
    # Calculate Total IV/EV (Assuming p is a mutable object or is re-assigned attributes)
    p.totaliv = round(((p.hpiv + p.atkiv + p.defiv + p.spatkiv + p.spdefiv + p.speediv) / 186) * 100, 2)
    p.totalev = (p.hpev + p.atkev + p.defev + p.spatkev + p.spdefev + p.speedev) 
    
    description = f"""
**Types:** {types}
**Tera-Type:** {p.tera}
**Ability:** {p.ability}
**Nature:** {p.nature}
**Gender:** {p.gender}
**Held Item:** {p.item}
**HP:** {p.hp} - IV: {p.hpiv}/31 - EV: {p.hpev}
**ATK:** {p.maxatk} - IV: {p.atkiv}/31 - EV: {p.atkev}
**DEF:** {p.maxdef} - IV: {p.defiv}/31 - EV: {p.defev}
**SPA:** {p.maxspatk} - IV: {p.spatkiv}/31 - EV: {p.spatkev}
**SPD:** {p.maxspdef} - IV: {p.spdefiv}/31 - EV: {p.spdefev}
**SPE:** {p.maxspeed} - IV: {p.speediv}/31 - EV: {p.speedev}
**Total IV %:** {p.totaliv}%
**Total EV :** {p.totalev}/508
"""

    infos = discord.Embed(
        title=f"#{num} {p.nickname} Lv.{p.level}",
        description=description,
        color=discord.Color.blue() # Added a color for aesthetics
    )
    
    # Use interaction.user.avatar
    infos.set_thumbnail(url=user.avatar.url if user.avatar else None)
    infos.set_image(url=p.sprite)
    
    # --- Response Handling ---
    
    # 1. Acknowledge the slash command immediately (required)
    await interaction.response.defer(ephemeral=True) 

    # 2. Send the embed privately to the user in DMs (as per your original code)
    try:
        await user.send(embed=infos)
        # Follow up in the channel to confirm the DM was sent
        await interaction.followup.send(f"✅ Sent the details for **{p.nickname}** to your DMs.", ephemeral=True)
    except discord.Forbidden:
        # If DMs are disabled, send the info privately in the channel instead
        await interaction.followup.send(f"⚠️ Could not send to DMs. Displaying the details for **{p.nickname}** privately here instead.", embed=infos, ephemeral=True)
    
@bot.tree.command(name="addfavorite",description="Add pokémon to you favorite list.")
async def addfavorite(ctx:discord.Interaction,num:int):
    new=int(num)
    dt=sqlite3.connect("owned.db")
    ct=dt.cursor()
    num=await row(ctx,new,ct)
    ct.execute(f"select * from '{ctx.user.id}' where rowid={num}")
    v=ct.fetchone()
    if "<:favorite:1144122202942357534>" not in v[1]:
        ct.execute(f"""update '{ctx.user.id}' set nickname="{v[1]+' <:favorite:1144122202942357534>'}" where rowid={num}""")
        dt.commit()
        await ctx.response.send_message("Favorite added.")
        
@bot.tree.command(name="teambuild",description="Build a team for battling.")
async def teambuild(ctx: discord.Interaction, mon1: int = 1, mon2: int = 2, mon3: int = 3, mon4: int = 4, mon5: int = 5, mon6: int = 6):
    
    # 1. Use aiosqlite for both database connections
    async with aiosqlite.connect("playerdata.db") as db, \
               aiosqlite.connect("owned.db") as dt:
        
        # We don't need to manually create cursors (cx, ct) here, 
        # but we need one for the 'row' function call.
        
        tm = [mon1, mon2, mon3, mon4, mon5, mon6] 
        new_rowids = []
        
        # Use an active aiosqlite cursor to call the asynchronous 'row' function
        async with dt.cursor() as ct:
            for i in tm:
                # 2. Await the 'row' function call
                n = await row(ctx, i, ct)
                
                # Check if the row_id was successfully retrieved
                if n is None:
                    # If any Pokémon index is invalid, stop and notify the user
                    return await ctx.response.send_message(
                        f"Error: Could not find Pokémon at position #{i}. Please ensure all numbers are valid.",
                        ephemeral=True
                    )
                new_rowids.append(n)
        
        # Note: mx = max(new) is unused for the team update, so we can ignore it.
        
        team_squad_string = f"{new_rowids}" # Storing the list of rowids as a string
        
        # 3. Use the asynchronous execute method on the 'db' connection
        if len(new_rowids) == 6:
            user_id_str = str(ctx.user.id)
            
            # Use parameterized query for safety, even for table/column names if possible,
            # but table name f-string is necessary for your current structure.
            await db.execute(f"""UPDATE '{user_id_str}' SET squad = ?""", (team_squad_string,))
            
            # 4. Use the asynchronous commit method
            await db.commit()
            
            await ctx.response.send_message("Team updated successful! The team is now: " + ", ".join(map(str, new_rowids)))
        else:
            await ctx.response.send_message("Team build failed. Please provide exactly 6 valid Pokémon numbers.")
        
@bot.tree.command(name="profile",description="Shows profile.")     
async def profile(ctx:discord.Interaction):
    db=sqlite3.connect("playerdata.db")
    dt=sqlite3.connect("owned.db")
    c=db.cursor()
    ct=dt.cursor()
    c.execute(f"select * from '{ctx.user.id}'")
    ct.execute(f"select * from '{ctx.user.id}'")
    det=c.fetchone()
    allmon=ct.fetchall()
    ct.execute(f"select * from '{ctx.user.id}' where shiny='Yes'")
    shinies=ct.fetchall()
    dy=(datetime.datetime.today()-datetime.datetime.strptime(det[3],"%Y-%m-%d %H:%M:%S")).days
    ttl=""
    if ctx.user.id==1084473178400755772:
        ttl="<:owner:1133682173413699714>"
    data=discord.Embed(title=f"{ctx.user.display_name}{ttl}'s Profile:",description=f"**<:pokecoin:1134595078892044369> Balance:** {await numberify(det[0])}\n**<:ball:1127196564948009052> Pokémons Caught:** {len(allmon)}\n**<:shiny:1127157664665837598> Shinies Caught:** {len(shinies)}\n**<:currentwin:1140763688668766249> Winstreak:** {det[4]}\n**<:winstreak:1140763720683880478> Highest Winstreak:** {det[5]}")
    data.set_footer(text=f"Creation Date: {det[3]} ({dy} days ago)")
    sq=eval(det[1])
    if True:
        team=await teamconvert(ctx,ctx.user,ctx.user.id)
        ll=0
        for i in team:
            ll+=1
            data.add_field(name=f"#{await findnum(ctx,sq[ll-1])} {i.icon} {i.nickname} {await teraicon(i.tera)}",value=f"**Ability:** {i.ability}\n**Item:** {await itemicon(i.item)} {i.item}",inline=False)
    else:
        data.add_field(name="Current Team:",value="Not available")
    data.set_thumbnail(url=ctx.user.avatar)
    await ctx.response.send_message(embed=data)
             
     
async def teamconvert(ctx,p,id):
    db=sqlite3.connect("playerdata.db")
    c=db.cursor()
    c.execute(f"select squad from '{id}'")
    lt=c.fetchone()
    lt=eval(lt[0])
    team=[]
    for i in lt:
        m=await pokonvert(ctx,p,i)
        mi=m[0]
        team.append(mi)
    return team
class LeadSelectionView(discord.ui.View):
    def __init__(self, trainer: 'Trainer', timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.trainer = trainer
        self.chosen_pokemon: Optional['Pokemon'] = None
        
        # Create a button for each Pokémon in the team
        for i, mon in enumerate(trainer.pokemons):
            # Ensure we don't exceed the 25 component limit (max 5 rows of 5)
            if i >= 6: 
                break 
                
            button = discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label=f"{mon.name}",
                emoji=getattr(mon, 'icon', None), # Use mon.icon if available
                custom_id=str(i) # Store the index as the custom_id
            )
            button.callback = self.create_callback(mon)
            self.add_item(button)

    def create_callback(self, pokemon: 'Pokemon'):
        # Creates a unique async function for each button
        async def callback(interaction: discord.Interaction):
            # 1. Validation: Only the intended player can choose
            if interaction.user != self.trainer.member:
                return await interaction.response.send_message("This selection isn't for you!", ephemeral=True)
                
            # 2. Store selection and confirm
            self.chosen_pokemon = pokemon
            await interaction.response.send_message(f"You chose **{pokemon.name}** as your lead Pokémon. Getting ready for battle!", ephemeral=True)
            
            # 3. Stop the view
            self.stop()
            
        return callback

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Prevent interaction if the user is not the trainer
        return interaction.user == self.trainer.member

    async def on_timeout(self):
        # Disable all buttons on timeout
        for item in self.children:
            item.disabled = True    
async def multiplayer(ctx, p1, p2):
    field = Field()
    
    # --- 1. Team Setup ---
    p1team = await teamconvert(ctx, p1, p1.id)
    if p2 == "ranked":
        tr2 = await rankedteam(ctx)
    elif isinstance(p2, int):
        tr2 = await gameteam(ctx, p2, p1team)
    else:
        p2team = await teamconvert(ctx, p2, p2.id)
        tr2 = Trainer(p2.display_name, p2team, "Earth", sprite=p2.avatar, member=p2) 
        
    tr1 = Trainer(p1.display_name, p1team, "Earth", sprite=p1.avatar, member=p1) 
    
    # --- 2. Intro Embed ---
    intro = discord.Embed(title=f"{tr1.name} vs {tr2.name}")
    intro.set_thumbnail(url="https://cdn.discordapp.com/attachments/1102579499989745764/1103853991760248924/VS.png")
    
    # Determine the intro message based on opponent type
    if tr2.ai == False:
        intro.add_field(name="Task:", value="Choose your lead pokémon! Check your DM!")
    else:
        intro.add_field(name="Task:", value="Choose your lead pokémon using the buttons below!")

    intro.set_image(url=tr2.sprite)
    intro.set_footer(text=f"Location: {field.location} | Weather: {field.weather} | Terrain: {field.terrain}")
    
    # --- 3. Lead Selection Setup ---
    x, y = None, None # x = P1 lead, y = P2 lead
    
    # Helper to send the menu to the correct location
    async def get_lead(trainer: Trainer, target_channel: discord.abc.Messageable):
        lead_view = LeadSelectionView(trainer)
        
        # Build the simple embed for the view
        pklist = ""
        for i, p in enumerate(trainer.pokemons):
            pklist += f" {getattr(p, 'icon', '')} {p.name}\n"
            
        em = discord.Embed(title="Choose your lead pokémon!", description=pklist)
        em.set_footer(text="Select the button corresponding to your desired Pokémon.")
        
        # Send the message and wait for selection
        msg = await target_channel.send(embed=em, view=lead_view)
        await lead_view.wait() 
        
        # Clean up the message after selection or timeout
        try:
            await msg.edit(view=None)
        except:
            pass
            
        return lead_view.chosen_pokemon

    # --- 4. Human vs. AI (P1 chooses in channel, P2 is random) ---
    if tr2.ai:
        # Send the main intro message
        await ctx.send(embed=intro)
        
        # P1 chooses in the main channel
        x = await get_lead(tr1, ctx.channel)
        
        # AI chooses randomly
        y = random.choice(tr2.pokemons)
        
    # --- 5. Human vs. Human (Both choose in DM simultaneously) ---
    else:
        # Send the main intro message
        await ctx.send(embed=intro)

        # Simultaneously get leads from both players in DM
        p1_task = get_lead(tr1, p1)
        p2_task = get_lead(tr2, p2)
        
        # Use asyncio.gather to wait for both players
        x, y = await asyncio.gather(p1_task, p2_task)
        
        # Send confirmation to the main channel
        if x and y:
            await ctx.send(f"Both leads chosen! **{tr1.name}** chose **{x.name}** and **{tr2.name}** chose **{y.name}**!")
        else:
            await ctx.send("Lead selection failed due to timeout or cancellation. Ending match.")
            return # Exit the game     
    turn=0        
    if x.speed>=y.speed:
        await entryeff(ctx,x,y,tr1,tr2,field,turn)
        await entryeff(ctx,y,x,tr2,tr1,field,turn)        
    if y.speed>x.speed:
        await entryeff(ctx,y,x,tr2,tr1,field,turn)      
        await entryeff(ctx,x,y,tr1,tr2,field,turn) 
    lead1=discord.Embed(title=f"{tr1.name}: Go,{x.nickname}!",description=f"{tr1.name} sents out **{x.name}**!")
    lead1.set_image(url=x.sprite)   
    lead1.set_thumbnail(url=tr1.sprite)
    lead2=discord.Embed(title=f"{tr2.name}: Go,{y.nickname}!",description=f"{tr2.name} sents out **{y.name}**!")
    lead2.set_image(url=y.sprite)
    lead2.set_thumbnail(url=tr2.sprite)     
    if x.speed>=y.speed:
        await ctx.send(embed=lead1)
        await ctx.send(embed=lead2)
    if y.speed>x.speed:
        await ctx.send(embed=lead2)
        await ctx.send(embed=lead1)    
    while True:
        if None not in (x,y):
            tr1.party=await partyup(tr1,x)
            tr2.party=await partyup(tr2,y) 
        turn+=1
        bg = int("FFFFFF",16)
        color_map = {
    "Normal": "E5E7E2",
    "Clear": "E5E7E2",
    "None": "E5E7E2",
    "Cloudy": "E5E7E2",
    "Misty": "FEB8B7",
    "Psychic": "BD61E6",
    "Electric": "D5CD73",
    "Grassy": "9CF7BD",
    "Strong Winds": "90FFF0",
    "Extreme Sunlight": "FF5E20",
    "Heavy Rain": "0790FF",
    "Hail": "7EC8FF",
    "Snowstorm": "CCECFF",
    "Rainy": "32C7FF",
    "Sunny": "FAFF6C",
    "Sandstorm": "CCAF5E"
}
        if field.weather in color_map:
            bg = int(color_map[field.weather],16)
        if field.terrain in color_map and field.terrain!="Normal":
            bg = int(color_map[field.terrain],16)
        wt="Clear"
        ts="Normal"
        trm=""
        if field.weather=="Sunny":
            wt=f"<:sunny:1141089317150793798> Sunny ({field.sunendturn-turn+1} turns left)"
        elif field.weather=="Rainy":
            wt=f"<:rainy:1141087852436922378> Rainy ({field.rainendturn-turn+1} turns left)"
        elif field.weather=="Sandstorm":
            wt=f"<:sandstorm:1141088700047048744> Sandstorm ({field.sandendturn-turn+1} turns left)"
        elif field.weather=="Snowstorm":
            wt=f"<:snowstorm:1141089242731266180> Snowstorm ({field.snowendturn-turn+1} turns left)"
        elif field.weather=="Hail":
            wt=f"<:hail:1141090300501176511> Hail ({field.hailendturn-turn+1} turns left)"   
        elif field.weather=="Heavy Rain":
            wt=f"<:heavyrain:1141093451765665823> Heavy Rain"               
        elif field.weather=="Extreme Sunlight":
            wt=f"<:extremesunlight:1141093481276776490> Extreme Sunlight"            
        elif field.weather=="Strong Winds":
            wt=f"<:strongwind:1141093937273114704> Strong Winds"
        elif field.weather in ["Clear","Cloudy","Normal"]:
            wt=f"<:clear:1141211018974994462> Clear"      
        if field.terrain=="Grassy":
            ts=f"<:grassy:1141090982788603985> Grassy ({field.grassendturn-turn+1} turns left)"
        elif field.terrain=="Electric":
            ts=f"<:electric:1141092625038970922> Electric ({field.eleendturn-turn+1} turns left)"
        elif field.terrain=="Psychic":
            ts=f"<:psychic:1141091324376911923> Psychic ({field.psyendturn-turn+1} turns left)"
        elif field.terrain=="Misty":
            ts=f"<:misty:1141091967162384404> Misty ({field.misendturn-turn+1} turns left)"
        elif field.terrain in ["Clear","Cloudy","Normal"]:
            ts=f"<:clear:1141211018974994462> Normal"   
        if field.trickroom==True:
            trm=f"**Dimension:** <:trickroom:1142045158200840313> Trick Room ({field.troomendturn-turn+1} turns left)"
        turnem=discord.Embed(title=f"Turn: {turn}",description=f"**Location:** {field.location}\n**Weather:** {wt}\n**Terrain:** {ts}\n{trm}",color=bg)
        await ctx.send(embed=turnem)
        if x.protect==True and x.use in ["Protect","Spiky Shield","King's Shield","Baneful Bunker","Obstruct","Silk Trap"]:
            x.protect = "Pending"
        elif x.protect==True and x.use=="Max Guard":
            x.protect=False
        if y.protect==True and y.use in ["Protect","Spiky Shield","King's Shield","Baneful Bunker","Obstruct","Silk Trap"]:
            y.protect = "Pending"
        elif y.protect==True and y.use=="Max Guard":
            y.protect=False
        action1 = None
        action2 = None
        await prebuff(ctx,x,y,tr1,tr2,turn,field)
        await prebuff(ctx,y,x,tr2,tr1,turn,field)
        if tr2.ai:
            await score(ctx,y,x,tr2,tr1,turn,bg)
            await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
        elif tr2.ai is False:
            await score(ctx,x,y,tr1,tr2,turn,bg)
            await score(ctx,y,x,tr2,tr1,turn,bg)
            await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
            await advscore(ctx,y,x,tr2,tr1,turn,field,bg)
        while action1 is None or action2 is None:
            if action1 not in [1,2]:
                action1 = await action(bot,ctx,tr1,tr2,x,y)
            if action2 not in [1,2]:
                action2 = await action(bot,ctx,tr2,tr1,y,x)
        if action1 == 3 and action2 != 3:
            await winner(ctx,tr2,tr1)
            break
        if action2 == 3 and action1 != 3:
            await winner(ctx,tr1,tr2)
            break
        em1 = ""
        em2 = ""
        if tr2.ai == False:
            await tr1.member.send("Please wait...")
            await tr2.member.send("Please wait...")
        if action1 in [7,8]:
            if action1 == 7:
                x,em1 = await ulttrans(ctx,x,y,tr1,tr2,field,turn)
            elif action1 == 8:
                x,em1 = await maxtrans(ctx,x,tr1,turn)
            action1 = 1

        elif action1 == 6:
            x,em1 = await megatrans(ctx,x,y,tr1,tr2,field,turn)
            action1 = 1
        elif action1==5:
            x.zuse=True
            action1=1
        elif action1 == 9:
            x,em1 = await teratrans(ctx,x,tr1,field)
            action1 = 1

        if action2 in [7,8]:
            if action2 == 7:
                y,em2 = await ulttrans(ctx,y,x,tr2,tr2,field,turn)
            elif action2 == 8:
                y,em2 = await maxtrans(ctx,y,tr2,turn)
            action2 = 1

        elif action2 == 6:
            y,em2 = await megatrans(ctx,y,x,tr2,tr1,field,turn)
            action2 = 1
        elif action2==5:
            y.zuse=True
            action2=1
        elif action2 == 9:
            y,em2 = await teratrans(ctx,y,tr2,field)
            action2 = 1

        if action1 == 2 and len(tr1.pokemons) == 1:
            action1 = 1

        if action2 == 2 and len(tr2.pokemons) == 1:
            action2 = 1

        if em1:
            await ctx.send(embed=em1)
        if em2:
            await ctx.send(embed=em2)

        if action1==1 and action2==1:
            if tr2.ai==True:
                await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
                await score(ctx,y,x,tr2,tr1,turn,bg)
            if tr2.ai==False:
                await score(ctx,x,y,tr1,tr2,turn,bg)
                await score(ctx,y,x,tr2,tr1,turn,bg)
                await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
                await advscore(ctx,y,x,tr2,tr1,turn,field,bg)
            choice1="None"
            choice2="None"
            choice1=await fchoice(ctx,bot,x,y,tr1,tr2,field)
            if choice1!="None" and tr2.ai==False:
                await tr1.member.send(f"{x.nickname} will use {choice1}!")
            choice2=await fchoice(ctx,bot,y,x,tr2,tr1,field)
            if choice2!="None" and tr2.ai==False:
                await tr2.member.send(f"{y.nickname} will use {choice2}!")
            xPriority=0
            yPriority=0
            if y.ability=="Quick Draw":
                yPriority=random.randint(1,100)
                if yPriority<20:
                    y.priority=True
            if x.ability=="Quick Draw":
                xPriority=random.randint(1,100)
                if xPriority<20:
                    x.priority=True
            if x.item=="Quick Claw":
                xPriority=random.randint(1,100)
                if xPriority<18:
                    x.priority=True
            if y.item=="Quick Claw":
                yPriority=random.randint(1,100)
                if yPriority<18:
                    y.priority=True
            if y.item=="Quick Claw" and y.ability=="Quick Draw":
                yPriority=random.randint(1,100)
                if yPriority<36:
                    y.priority=True
            if x.item=="Quick Claw" and x.ability=="Quick Draw":
                xPriority=random.randint(1,100)
                if xPriority<36:
                    x.priority=True
            if (
    choice1 in typemoves.prioritymove
    or x.priority==True
    or (x.ability == "Prankster" and choice1 in typemoves.statusmove and "Dark" not in (y.primaryType,y.secondaryType))
    or (choice1 in typemoves.firemoves and x.ability == "Blazing Soul")
    or (choice1 in typemoves.flyingmoves and x.ability == "Gale Wings")
    or (field.terrain == "Grassy" and choice1 == "Grassy Glide")
    or (x.ability == "Triage" and choice1 in typemoves.healingmoves)
    or choice2 in typemoves.negprioritymove
    or (choice2 in typemoves.statusmove and y.ability == "Mycelium Might")
    or y.item == "Lagging Tail"
):
                if x.priority==True and x.item=="Quick Claw":
                    qc=discord.Embed(title=f"{x.nickname}'s Quick Claw!",description=f"{x.nickname} can act faster than normal,thanks to its Quick Claw")
                    await ctx.send(embed=qc)
                await weather(ctx,field,bg)   
                x,y=await attack(ctx,bot,x,y,tr1,tr2,choice1,choice2,field,turn)
                await prebuff(ctx,x,y,tr1,tr2,turn,field)
                await prebuff(ctx,y,x,tr2,tr1,turn,field)
                if x.hp<=0:
                    x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                    if len(tr1.pokemons)==0:
                        await winner(ctx,tr2,tr1)
                        break
                if y.hp<=0:
                    y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                    if len(tr2.pokemons)==0:
                        await winner(ctx,tr1,tr2)
                        break 
                elif y.hp>0:                     
                    y,x=await attack(ctx,bot,y,x,tr2,tr1,choice2,choice1,field,turn)
                    await effects (ctx,x,y,tr1,field,turn)
                    await effects(ctx,y,x,tr2,field,turn)
                    await prebuff(ctx,x,y,tr1,tr2,turn,field)
                    await prebuff(ctx,y,x,tr2,tr1,turn,field)   
                    if x.hp<=0:
                        x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                        if len(tr1.pokemons)==0:
                            await winner(ctx,tr2,tr1)
                            break
                    if y.hp<=0:
                        y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break 
                if y.hp<=0:
                    y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                    await effects(ctx,x,y,tr1,turn)
                    if x.hp<=0:
                        x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                        if len(tr1.pokemons)==0:
                            await winner(ctx,tr2,tr1)
                            break
                    if len(tr2.pokemons)==0:
                        await winner(ctx,tr1,tr2)
                        break
                x.priority=False       
            elif (
    choice2 in typemoves.prioritymove
    or y.priority==True
    or (y.ability == "Prankster" and choice2 in typemoves.statusmove and "Dark" not in (x.primaryType,x.secondaryType))
    or (choice2 in typemoves.firemoves and y.ability == "Blazing Soul")
    or (choice2 in typemoves.flyingmoves and y.ability == "Gale Wings")
    or (field.terrain == "Grassy" and choice2 == "Grassy Glide")
    or (y.ability == "Triage" and choice2 in typemoves.healingmoves)
    or choice1 in typemoves.negprioritymove
    or (choice1 in typemoves.statusmove and x.ability == "Mycelium Might")
    or x.item == "Lagging Tail"
):
                if y.priority==True and y.item=="Quick Claw":
                    qc=discord.Embed(title=f"{y.nickname}'s Quick Claw!",description=f"{y.nickname} can act faster than normal,thanks to its Quick Claw")
                    await ctx.send(embed=qc)
                await weather(ctx,field,bg)   
                y,x=await attack(ctx,bot,y,x,tr2,tr1,choice2,choice1,field,turn)
                await prebuff(ctx,y,x,tr2,tr1,turn,field)
                await prebuff(ctx,x,y,tr1,tr2,turn,field)
                if y.hp<=0:
                    y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                    if len(tr2.pokemons)==0:
                        await winner(ctx,tr1,tr2)
                        break 
                if x.hp<=0:
                    x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                    if len(tr1.pokemons)==0:
                        await winner(ctx,tr2,tr1)
                        break      
                elif x.hp>0:                     
                    x,y=await attack(ctx,bot,x,y,tr1,tr2,choice1,choice2,field,turn)
                    await effects(ctx,y,x,tr2,field,turn)
                    await effects (ctx,x,y,tr1,field,turn)
                    await prebuff(ctx,y,x,tr2,tr1,turn,field)  
                    await prebuff(ctx,x,y,tr1,tr2,turn,field)
                    if y.hp<=0:
                        y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break 
                    if x.hp<=0:
                        x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                        if len(tr1.pokemons)==0:
                            await winner(ctx,tr2,tr1)
                            break 
                if y.hp<=0:
                    y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                    if y!=None:
                        await effects(ctx,y,x,tr2,field,turn)
                    if y==None:
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break
                    while y.hp<=0 and y!=None:
                        y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break
                    if len(tr1.pokemons)==0:
                        await winner(ctx,tr2,tr1)
                        break
                y.priority=False        
                
            elif x.speed>=y.speed and field.trickroom==False:
                await weather(ctx,field,bg)        
                x,y=await attack(ctx,bot,x,y,tr1,tr2,choice1,choice2,field,turn)                         
                await prebuff(ctx,x,y,tr1,tr2,turn,field)
                await prebuff(ctx,y,x,tr2,tr1,turn,field)
                if x.hp<=0:
                    x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                    if len(tr1.pokemons)==0:
                        await winner(ctx,tr2,tr1)
                        break       
                elif y.hp>0:                    
                    y,x=await attack(ctx,bot,y,x,tr2,tr1,choice2,choice1,field,turn)
                    await effects (ctx,x,y,tr1,field,turn)
                    await effects(ctx,y,x,tr2,field,turn)
                    await prebuff(ctx,x,y,tr1,tr2,turn,field)
                    await prebuff(ctx,y,x,tr2,tr1,turn,field)
                    if x.hp<=0:
                        x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                        if len(tr1.pokemons)==0:
                            await winner(ctx,tr2,tr1)
                            break       
                    if y.hp<=0:
                        y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break
                if y.hp<=0:
                    y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                    if x.hp<=0:
                        x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                        if len(tr1.pokemons)==0:
                            await winner(ctx,tr2,tr1)
                            break      
                    if len(tr2.pokemons)==0:
                        await winner(ctx,tr1,tr2)
                        break   
            elif x.speed<y.speed and field.trickroom==True:
                await weather(ctx,field,bg)
                x,y=await attack(ctx,bot,x,y,tr1,tr2,choice1,choice2,field,turn)
                await prebuff(ctx,x,y,tr1,tr2,turn,field)
                await prebuff(ctx,y,x,tr2,tr1,turn,field)
                if x.hp<=0:
                    x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                    if len(tr1.pokemons)==0:
                        await winner(ctx,tr2,tr1)
                        break   
                elif y.hp>0:                     
                    y,x=await attack(ctx,bot,y,x,tr2,tr1,choice2,choice1,field,turn)
                    await effects (ctx,x,y,tr1,field,turn)
                    await effects(ctx,y,x,tr2,field,turn)
                    await prebuff(ctx,x,y,tr1,tr2,turn,field)
                    await prebuff(ctx,y,x,tr2,tr1,turn,field)
                    if x.hp<=0:
                        x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                        if len(tr1.pokemons)==0:
                            await winner(ctx,tr2,tr1)
                            break   
                    if y.hp<=0:
                        y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break
                if y.hp<=0:
                    y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                    await effects (ctx,x,y,tr1,field,turn)
                    if x.hp<=0:
                        x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                        if len(tr1.pokemons)==0:
                            await winner(ctx,tr2,tr1)
                            break   
                    if len(tr2.pokemons)==0:
                        await winner(ctx,tr1,tr2)
                        break
                        
            elif y.speed>x.speed and field.trickroom==False:
                await weather(ctx,field,bg)
                y,x=await attack(ctx,bot,y,x,tr2,tr1,choice2,choice1,field,turn)
                await prebuff(ctx,x,y,tr1,tr2,turn,field)
                await prebuff(ctx,y,x,tr2,tr1,turn,field)
                if y.hp<=0:
                    y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                    if len(tr2.pokemons)==0:
                        await winner(ctx,tr1,tr2)
                        break
                elif x.hp>0:                    
                    x,y=await attack(ctx,bot,x,y,tr1,tr2,choice1,choice2,field,turn)
                    await effects(ctx,y,x,tr2,field,turn)
                    await effects (ctx,x,y,tr1,field,turn)
                    await prebuff(ctx,x,y,tr1,tr2,turn,field)
                    await prebuff(ctx,y,x,tr2,tr1,turn,field)
                    if y.hp<=0:
                        y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break
                    if x.hp<=0:
                        x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                        if len(tr1.pokemons)==0:
                            await winner(ctx,tr2,tr1)
                            break   
                if x.hp<=0:
                    x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                    await effects(ctx,y,x,tr2,field,turn)
                    if y.hp<=0:
                        y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break
                    if len(tr1.pokemons)==0:
                        await winner(ctx,tr2,tr1)
                        break   

            elif y.speed<=x.speed and field.trickroom==True:
                await weather(ctx,field,bg)
                y,x=await attack(ctx,bot,y,x,tr2,tr1,choice2,choice1,field,turn)
                await prebuff(ctx,x,y,tr1,tr2,turn,field)
                await prebuff(ctx,y,x,tr2,tr1,turn,field)
                if y.hp<=0:
                    y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                    if len(tr2.pokemons)==0:
                        await winner(ctx,tr1,tr2)
                        break
                elif x.hp>0:                    
                    x,y=await attack(ctx,bot,x,y,tr1,tr2,choice1,choice2,field,turn)
                    await effects(ctx,y,x,tr2,field,turn)
                    await effects (ctx,x,y,tr1,field,turn)
                    await prebuff(ctx,x,y,tr1,tr2,turn,field)
                    await prebuff(ctx,y,x,tr2,tr1,turn,field)
                    if y.hp<=0:
                        y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break
                    if x.hp<=0:
                        x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                        if len(tr1.pokemons)==0:
                            await winner(ctx,tr2,tr1)
                            break
                if x.hp<=0:
                    x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                    await effects(ctx,y,x,tr2,field,turn)
                    if y.hp<=0:
                        y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                        if len(tr2.pokemons)==0:
                            await winner(ctx,tr1,tr2)
                            break
                    if len(tr1.pokemons)==0:
                        await winner(ctx,tr2,tr1)
                        break
        elif action1==2 and action2==1:
            choice1="None"
            if tr2.ai==True:
                await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
                await score(ctx,y,x,tr2,tr1,turn,bg)
            if tr2.ai==False:
                await score(ctx,x,y,tr1,tr2,turn,bg)
                await score(ctx,y,x,tr2,tr1,turn,bg)
                await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
                await advscore(ctx,y,x,tr2,tr1,turn,field,bg)
            choice2=await fchoice(ctx,bot,y,x,tr2,tr1,field)
            await weather(ctx,field,bg)
            x=await switch(ctx,bot,x,y,tr1,tr2,field,turn)
            y,x=await attack(ctx,bot,y,x,tr2,tr1,choice2,choice1,field,turn)
            await effects (ctx,x,y,tr1,field,turn)
            await effects(ctx,y,x,tr2,field,turn)
            if y.hp<=0:
                y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                if len(tr2.pokemons)==0:
                    await winner(ctx,tr1,tr2)
                    break
            if x.hp<=0:
                x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                if len(tr1.pokemons)==0:
                   await winner(ctx,tr2,tr1)
                   break
            
#tr1 ATTACKS AND tr2 SWITCHES                
        elif action1==1 and action2==2:
            choice2="None"
            if tr2.ai==True:
                await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
                await score(ctx,y,x,tr2,tr1,turn,bg)
            if tr2.ai==False:
                await score(ctx,x,y,tr1,tr2,turn,bg)
                await score(ctx,y,x,tr2,tr1,turn,bg)
                await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
                await advscore(ctx,y,x,tr2,tr1,turn,field,bg)
            choice1=await fchoice(ctx,bot,x,y,tr1,tr2,field)
            await weather(ctx,field,bg)
            y=await switch(ctx,bot,y,x,tr2,tr1,field,turn)
            x,y=await attack(ctx,bot,x,y,tr1,tr2,choice1,choice2,field,turn)
            if x.hp<=0:
                x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                if len(tr1.pokemons)==0:
                   await winner(ctx,tr2,tr1)
                   break
            await effects (ctx,x,y,tr1,field,turn)
            await effects(ctx,y,x,tr2,field,turn)
            await prebuff(ctx,x,y,tr1,tr2,turn,field)
            await prebuff(ctx,y,x,tr2,tr1,turn,field)
            if x.hp<=0:
                x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                if len(tr1.pokemons)==0:
                   await winner(ctx,tr2,tr1)
                   break
            if y.hp<=0:
                y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                if len(tr2.pokemons)==0:
                    await winner(ctx,tr1,tr2)
                    break
            
#IF BOTH SWITCHES                
        elif action1==2 and action2==2:
            if tr2.ai==True:
                await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
                await score(ctx,y,x,tr2,tr1,turn,bg)
            if tr2.ai==False:
                await score(ctx,x,y,tr1,tr2,turn,bg)
                await score(ctx,y,x,tr2,tr1,turn,bg)
                await advscore(ctx,x,y,tr1,tr2,turn,field,bg)
                await advscore(ctx,y,x,tr2,tr1,turn,field,bg)
            await weather(ctx,field,bg)
            if x.speed>=y.speed:
                x=await switch(ctx,bot,x,y,tr1,tr2,field,turn)  
                y=await switch(ctx,bot,y,x,tr2,tr1,field,turn)
            elif y.speed>x.speed:
                y=await switch(ctx,bot,y,x,tr2,tr1,field,turn)
                x=await switch(ctx,bot,x,y,tr1,tr2,field,turn)  
            await effects(ctx,y,x,tr2,field,turn)
            await effects (ctx,x,y,tr1,field,turn)   
            if y.hp<=0:
                y=await faint(ctx,bot,y,x,tr2,tr1,field,turn)
                if len(tr2.pokemons)==0:
                    await winner(ctx,tr1,tr2)
                    break
            await effects (ctx,x,y,tr1,field,turn)          
            if x.hp<=0:
                x=await faint(ctx,bot,x,y,tr1,tr2,field,turn)
                if len(tr1.pokemons)==0:
                   await winner(ctx,tr2,tr1)
                   break            
keep_alive()
bot.run(token)    