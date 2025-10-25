class Trainer:
	def __init__(self,name="Billy",pokemons=[],region="Kanto",hazard=None,ai=False,lightscreen=False,reflect=False,auroraveil=False,faintedmon=[],tailwind=False,wishhp=False,vcdmg=False,vcturn=False,vcendturn=False,canmega=True,canmax=True,canz=True,cantera=True,mon="None",future=0,ftmul=0,sub="None",winner=False,doom=0,item=[],sprite="Trainers/unknown.png",id=0,member="None"):
		self.name=name
		self.ai=ai
		self.winner=winner
		self.pokemons=pokemons
		self.fullteam=pokemons.copy()
		self.cantera=cantera
		self.canmax=canmax
		self.member=member
		self.party=["<:ball:1127196564948009052>","<:ball:1127196564948009052>","<:ball:1127196564948009052>","<:ball:1127196564948009052>","<:ball:1127196564948009052>","<:ball:1127196564948009052>"]
		self.sparty=["<:healthy:1140746496657080420>","<:healthy:1140746496657080420>","<:healthy:1140746496657080420>","<:healthy:1140746496657080420>","<:healthy:1140746496657080420>","<:healthy:1140746496657080420>"]
		self.id=id
		self.future=future
		self.doom=doom
		self.sprite=sprite
		self.ftmul=ftmul
		self.sub=sub
		self.faintedmon=faintedmon
		self.lightscreen=lightscreen
		self.reflect=reflect		
		self.mon=mon
		self.canmega=canmega
		self.canz=canz
		self.tailwind=tailwind
		self.auroraveil=auroraveil
		self.region=region
		self.reflecturn=0
		self.wishhp=wishhp
		self.tailturn=0
		self.auroraturn=0
		self.lsturn=0
		self.vcdmg=vcdmg
		self.vcturn=vcturn
		self.vcendturn=vcendturn
		self.screenend=self.lsturn+6
		self.twendturn=self.tailturn+4
		self.rfendturn=self.reflecturn+6
		self.avendturn=self.auroraturn+6
		self.sunturn=0
		self.sunend=0
		self.rainturn=0
		self.rainend=0
		self.sandturn=0
		self.sandend=0
		self.hailturn=0
		self.hailend=0
		self.item=item
		if self.item == []:
			self.item = ["Full Restore", "Full Restore", "Full Restore"]
		if hazard is None:
			self.hazard = []
		else:
			self.hazard = hazard

	# Assuming these are methods of the same class (e.g., Field or Battle):

	def lightscreenend(self, mon, mon2):
		# FIX: Correct the screen duration logic using an item check.
		# The duration is normally 5 turns (self.lsturn + 5).
		# If Light Clay is found on either active mon, it's 8 turns.
		if "Light Clay" in (mon.item, mon2.item):
			self.screenend = self.lsturn + 8
		else:
			self.screenend = self.lsturn + 5
		return self.screenend
		
	def reflectend(self, mon, mon2):
		# FIX: Correct the screen duration logic using an item check.
		if "Light Clay" in (mon.item, mon2.item):
			self.rfendturn = self.reflecturn + 8
		else:
			self.rfendturn = self.reflecturn + 5
		return self.rfendturn
		
	def auroraend(self, mon, mon2):
		# Fix 1: Simplify logic, check abilities/items first.
		# Fix 2: Ensure the Aurora Veil check is accurate.
		
		# Check for custom "North Wind" ability/move interaction
		if mon.ability == "North Wind" and mon.use not in ("Aurora Veil", "G-Max Resonance"):
			self.avendturn = self.auroraturn + 3
		
		# Check for Light Clay extension (standard rule is 8 turns)
		elif "Light Clay" in (mon.item, mon2.item):
			self.avendturn = self.auroraturn + 8
			
		# Default duration
		else:
			self.avendturn = self.auroraturn + 5
			
		return self.avendturn
		
	def twend(self, mon, mon2):
		# Standard Tailwind duration is 4 turns from the turn it was used (self.tailturn + 4).
		self.twendturn = self.tailturn + 4
		return self.twendturn       
