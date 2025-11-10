from importlist import *
#intents=discord.Intents.default()
#intents.members=True
#intents.reactions=True
#intents.message_content=True
prefix="!"
bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

MAX_BADGES_PER_PAGE = 8 # Set how many badges fit on one page.
BADGE_METADATA = {}
async def load_badge_metadata():
    """Fetches all badge names, icons, and assigns an order from the Trainers table."""
    global BADGE_METADATA
    
    # Use aiosqlite to read the static Trainers table
    async with aiosqlite.connect("pokemondata.db") as db:
        # Select symbolname (badge name) and symbolicon (icon/emoji)
        async with db.execute("SELECT symbolname, symbolicon FROM Trainers WHERE symbolname IS NOT NULL AND symbolname != 'None' ORDER BY ROWID ASC") as cursor:
            trainer_data = await cursor.fetchall()
            
    # Populate the BADGE_METADATA dictionary
    for index, (name, icon) in enumerate(trainer_data):
        # We use the ROWID (or index after ORDER BY ROWID) as the sorting order
        BADGE_METADATA[name.strip()] = {
            "icon": icon.strip(),
            "order": index + 1 # 1-based ordering
        }
    print(f"✅ Loaded {len(BADGE_METADATA)} badge metadata entries.")


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd,activity=discord.Game("Pokémon"))
    print(f"We have logged in as {bot.user}")
    try:
        synced=await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)!")
        await load_badge_metadata()
    except:
        print(Exception)
