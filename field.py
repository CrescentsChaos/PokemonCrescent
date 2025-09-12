import random

# Pokemon regions and locations
REGIONS = {
    "Kanto": ["Pallet Town", "Viridian City", "Viridian Forest", "Pewter City", "Mt. Moon", 
              "Cerulean Cave", "Cerulean City", "Rock Tunnel", "Lavender Town", "Saffron City", 
              "Celadon City", "Cycling Road", "Fuchsia City", "Seafoam Islands", "Cinnabar Island", 
              "Indigo Plateau", "Vermilion City", "Mount Silver", "Victory Road", "Diglett's Cave", 
              "Pokémon Mansion", "Pokémon Tower", "Power Plant", "Silph Co."],
    
    "Johto": ["New Bark Town", "Goldenrod City", "Violet City", "Olivine City", "Azalea City", 
              "Ecruteak City", "Cianwood City", "Mahogany Town", "Blackthorn City", "Whirl Islands", 
              "Navel Rock", "Bell Tower"],
    
    "Hoenn": ["Littleroot Town", "Petalburg City", "Rustboro City", "Dewford Town", "Mauville City", 
              "Lavaridge Town", "Fortree City", "Mosdeep City", "Sootopolis City", "Evergrande City", 
              "Aqua Hideout", "Magma Hideout", "Terra Cave", "Marine Cave", "Mt. Pyre", "Mt. Chimney", 
              "Faraway Island", "Birth Island", "Mirage Island", "Southern Island", "Crescent Isle", 
              "Cave of Origin", "Fabled Cave", "Gnarled Den", "Granite Cave", "Jagged Pass", 
              "Lilycove City", "Meteor Falls", "Nameless Cavern", "New Mauvile", "Pacifidlog Town", 
              "Pathless Plain", "Scorched Slab", "Sea Mauvile", "Seafloor Cavern", "Shoal Cave", 
              "Sky Pillar", "Slateport City", "Soaring in the Sky", "Trackless Forest", 
              "Rock Peak Ruins", "Iceberg Ruins", "Iron Ruins", f"Route {random.randint(101,134)}"],
    
    "Sinnoh": ["Twinleaf Town", "Oreburgh City", "Eterna City", "Hearthome City", "Veilstone City", 
               "Pastoria City", "Canalave City", "Iron Island", "Snowpoint City", "Sunnyshore City", 
               "Mountain Stark", "Spear Pillar", "Mount Coronet", "Aquity Lakefront", "Celestic Town", 
               "Eterna Forest", "Floaroma Town", "Flower Paradise", "Fuego Ironworks", "Grand Underground", 
               "Great Marsh", "Lake Acuity", "Lake Valor", "Lake Verity", "Lost Tower", "Maniac Tunnel", 
               "Newmoon Island", "Old Chateau", "Oreburgh Mine", "Ramanas Park", "Ravaged Path", 
               "Resort Area", "Ruin Maniac Cave", "Sendoff Spring", "Snowpoint Temple", "Solaceon Ruins", 
               "Stark Mountain", "Trophy Garden", "Turnback Cave", "Valley Windworks", "Valor Lakefront", 
               "Wayward Cave", f"Route {random.randint(201,230)}"],
    
    "Unova": ["Abundant Shrine", "Castelia City", "Celestial Tower", "Challenger's Cave", 
              "Chargestone Cave", "Cold Storage", "Desert Resort", "Dragonspiral Tower", "Dreamyard", 
              "Driftveil City", "Driftveil Drawbridge", "Giant Chasm", "Icirrus City", "Lostlorn Forest", 
              "Marvelous Forest", "Mistralon Cave", "Moon of Icirrus", "N's Castle", "Nacrene City", 
              "P2 Laboratory", "Pinwheel Forest", "Relic Castle", "Striaton City", "Twist Mountain", 
              "Undella Bay", "Undella Town", "Village Bridge", "Wellspring Cave", "Black City", 
              "White Forest", "Accumula Town", "Aspertia City", "Castelia Sewers", "Clay Tunnel", 
              "Floccesy Ranch", "Floccesy Town", "Humilau City", "Nature Santuary", "Nimbasa City", 
              "Relic Passage", "Reversal Mountain", "Seaside Cave", "Strange House", "Underground Ruins", 
              "Virbank City", "Virbank Complex", "Trial Chamber", "Marvelous Bridge"],
    
    "Kalos": ["Ambrette Town", "Aquacorde Town", "Azure Bay", "Connecting Cave", "Couriway Town", 
              "Cyllage City", "Frost Cavern", "Glittering Cave", "Laverre City", "Lost Hotel", 
              "Lumiose City", "Parfum Palace", "Pokémon Village", "Reflection Cave", "Santalune Forest", 
              "Sea Spirit's Den", "Shalour City", "Team Flare Secret HQ", "Terminus Cave", 
              "Tower of Mastery", "Coumarine City", "Anistar City", "Snowbelle City", "Crown Tundra", 
              "Isle of Armor"],
    
    "Alola": ["Aether Paradise", "Akala Outskirts", "Altar of the Moone", "Altar of the Sunne", 
              "Ancient Poni Path", "Berry Fields", "Blush Mountain", "Brooklet Hill", "Diglett's Tunnel", 
              "Exeggutor Island", "Haina Desert", "Hano Beach", "Ha'oli Cemetery", "Hau'oli City", 
              "Iki Town", "Kala'e Bay", "Konikoni City", "Lake of the Moone", "Lake of the Sunne", 
              "Lush Jungle", "Malie City", "Malie Garden", "Melemele Meadow", "Melemele Sea", 
              "Memorial Hill", "Mount Hokulani", "Paniola Ranch", "Paniola Town", "Poke' Pelago", 
              "Poni Breaker Coast", "Poni Coast", "Poni Gauntlet", "Poni Grove", "Poni Meadow", 
              "Poni Plains", "Poni Wilds", "Resolution Cave", "Ruins of Abundance", "Ruins of Conflict", 
              "Ruins of Hope", "Ruins of Life", "Seafolk Village", "Seaward Cave", "Secluded Shore", 
              "Tapu Village", "Ten Carat Hill", "Thrifty Megamart", "Ula'ula Meadow", "Vast Poni Canyon", 
              "Verdant Cavern", "Wela Volcano Park", "Ultra Space Cave", "Ultra Space Cliff", 
              "Ultra Space Crag", "Ultra Space Waterfall", 
              f"Ultra {random.choice(['Crater', 'Deep Sea', 'Desert', 'Forest', 'Jungle', 'Megalopolis', 'Plant', 'Ruin'])}"],
    
    "Galar": ["Axew's Eye", "Ballimere Lake", "Ballonlea", "Brawler's Cave", "Bridge Field", 
              "Challenge Beach", "Challenge Road", "Circhester", "City of Motostoke", "Courageous Cavern", 
              "Crown Shrine", "Dappled Grove", "Dusty Bowl", "East Lake Axewell", "Energy Plant", 
              "Fields of Honor", "Fields of Focus", "Freezington", "Frigid Sea", "Frostpoint Field", 
              "Galar Mine", "Giant's Bed", "Giant's Cap", "Giant's Foot", "Giant's Mirror", "Giant's Seat", 
              "Glimwood Tangle", "Hammerlocke", "Hammerlocke Hills", "Honeycalm Sea", "Hulbury", 
              "Iceberg Ruins", "Insular Sea", "Iron Ruins", "Lake of Outrage", "Lakeside Cave", 
              "Loop Lagoon", "Master Dojo", "Max Lair", "Meetup Spot", "Motostoke", "Motostoke Outskirts", 
              "Motostoke Riverbank", "North Lake Miloch", "Old Cemetery", "Path of the Peak", "Postwick", 
              "Potbottom Desert", "Rock Peak Ruins", "Rolling Fields", "Slippery Slope", "Slumbering Weald", 
              "Snowslide Slope", "Soothing Wetlands", "South Lake Miloch", "Spikemuth", "Split-Decision Ruins", 
              "Stepping-Stone Sea", "Stony Wilderness", "Stow-on-Side", "Three-Point-Pass", "Training Lowlands", 
              "Tunnel to the top", "Turffield", "Warm-Up Tunnel", "Watchtower Ruins", "West Lake Axewell", 
              "Workout Sea", "Wyndon", "Shamouti Island"],
    
    "Paldea": ["Caseeroya Lake", "Area Zero", "Cabo Poco", "Los Platos", "Mesagoza", "Cortondo", 
               "Artazon", "Levincia", "Alfornada", "Cascarrafa", "Porto Marinada", "Medali", 
               "Montenevera", "Poco Path", "Inlet Grotto", "South Paldean Sea", "East Paldean Sea", 
               "West Paldean Sea", "North Paldean Sea", "Alfornada Cavern", "Asado Desert", 
               "Dalizapa Passage", "Glaseado Mountain", "Socarrat Trail", "Tagtree Thicket", 
               "Casseroya Falls", "Colonnade Hollow", "Fury Falls", "Glaseado's Grasp", "Gracia Stones", 
               "Grand Olive Orchard", "Leaking Tower", "Million Volt Skyline", "Secluded Beach", 
               "The Great Crater", "West Province", "North Province"]
}

SPECIAL_LOCATIONS = [
    "Pokémon World Tournament, Unova",
    "Battle Frontier, Hoenn", 
    "Battle Frontier, Sinnoh"
]

# Flatten all locations for easy access
ALL_LOCATIONS = [loc for locations in REGIONS.values() for loc in locations]


class Field:
    """Represents a Pokemon battle field with various environmental conditions."""
    
    def __init__(self, name="Stadium", weather="Clear", trickroom=False, terrain="Normal", 
                 gravity=False, magicroom=False, mudsport=False, watersport=False, 
                 wonderroom=False, location=None):
        # Basic field properties
        self.name = name
        self.weather = weather
        self.trickroom = trickroom
        self.terrain = terrain
        self.gravity = gravity
        self.magicroom = magicroom
        self.mudsport = mudsport
        self.watersport = watersport
        self.wonderroom = wonderroom
        
        # Turn counters - using dictionary for cleaner organization
        self.turn_counters = {
            'rain': {'start': 0, 'end': 200},
            'sun': {'start': 0, 'end': 200},
            'sand': {'start': 0, 'end': 200},
            'hail': {'start': 0, 'end': 200},
            'snow': {'start': 0, 'end': 200},
            'grass': {'start': 0, 'end': 200},
            'electric': {'start': 0, 'end': 200},
            'psychic': {'start': 0, 'end': 200},
            'trickroom': {'start': 0, 'end': 200},
            'misty': {'start': 0, 'end': 200}
        }
        
        # Set location
        self.location = self._generate_location() if location is None else location
    
    def _generate_location(self):
        """Generate a random location with proper region attribution."""
        # Choose between regular locations (90%) and special locations (10%)
        location = random.choices([random.choice(ALL_LOCATIONS), random.choice(SPECIAL_LOCATIONS)], 
                                weights=[10, 1], k=1)[0]
        
        # Add region if it's a regular location
        if location in ALL_LOCATIONS:
            for region, locations in REGIONS.items():
                if location in locations:
                    return f"{location}, {region}"
        
        return location
    
    def _calculate_duration(self, mon, base_duration=5, extender_duration=8, extender_item="Terrain Extender"):
        """Calculate effect duration based on Pokemon's item."""
        return extender_duration if mon.item == extender_item else base_duration
    
    def set_trickroom_duration(self, mon):
        """Set Trick Room duration based on Pokemon's item."""
        duration = self._calculate_duration(mon, extender_item="Room Service")
        self.turn_counters['trickroom']['end'] = self.turn_counters['trickroom']['start'] + duration
        return self.turn_counters['trickroom']['end']
    
    def set_terrain_duration(self, mon, terrain_type):
        """Set terrain duration based on Pokemon's item."""
        if terrain_type in ['psychic', 'electric', 'grass', 'misty']:
            duration = self._calculate_duration(mon)
            self.turn_counters[terrain_type]['end'] = self.turn_counters[terrain_type]['start'] + duration
            return self.turn_counters[terrain_type]['end']
        return None
    
    # Legacy method compatibility
    def troomend(self, mon, mon2=None):
        """Legacy method for Trick Room duration."""
        return self.set_trickroom_duration(mon)
    
    def psyend(self, mon, mon2=None):
        """Legacy method for Psychic Terrain duration."""
        return self.set_terrain_duration(mon, 'psychic')
    
    def eleend(self, mon, mon2=None):
        """Legacy method for Electric Terrain duration."""
        return self.set_terrain_duration(mon, 'electric')
    
    def grassend(self, mon, mon2=None):
        """Legacy method for Grassy Terrain duration."""
        return self.set_terrain_duration(mon, 'grass')
    
    def misend(self, mon, mon2=None):
        """Legacy method for Misty Terrain duration."""
        return self.set_terrain_duration(mon, 'misty')