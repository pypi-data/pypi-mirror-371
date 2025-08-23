# DICTIONARIES
GROCERY = {
    'bread': 10,
    'cheese': 15,
    'wine': 50
}

BOTANICAL_NURSERY = {
    'rose': 5,
    'herbs': 8,
    'magic beans': 100
}

FARMERS_MARKET = {
    'apple': 2,
    'carrot': 1,
    'potato': 3
}

FREELANCERS = {
    'brian': 700,
    'black knight': 200,
    'biccus diccus': 1000,
    'grim reaper': 5000,
    'minstrel': 0,
    'god': 'dedication and hope',
    'nordic': 2000,
    'mage': 5000,
    'ze germane': 1000,
    'raddragonore': 1000
}

ANTIQUES = {
    'french castle': 400,
    'wooden grail': 3,
    'scythe': 1500,
    'catapult': 75,
    'german joke': 5,
    'spear': 100,
    'axe': 200,
    'peace': -2000,
    'rock': 10000,
    'healing potion': 200,
    'body armor': 2000,
}

PET_SHOP = {
    'blue parrot': 100,
    'white rabbit': 50,
    'newt': 20,
    'wolf': 250,
    'dragon': 1000,
    'serpent': 500
}

VILLAGE_QUESTS = {
    'hunt wild boar': 
    {'reward': 150, 
    'description': 'A wild boar terrorizes the fields!'},
    'deliver message to next village': 
    {'reward': 80, 'description': 'Urgent message needs delivery!'},
    'find lost sheep': 
    {'reward': 60, 'description': 'Farmer Johann lost his prize sheep!'},
    'escort merchant caravan': 
    {'reward': 200, 
    'description': 'Dangerous roads need protection!'},
    'gather rare herbs': 
    {'reward': 120, 
    'description': 'Village healer needs mystical herbs!'},
    'repair village well': 
    {'reward': 100, 
    'description': 'Well broken, villagers thirsty!'},
    'catch pickpocket': 
    {'reward': 180, 
    'description': 'Thief stealing from market stalls!'},
    'explore haunted ruins': 
    {'reward': 300, 
    'description': 'Ancient ruins hold treasure... and danger!'},
    'tame wild horse': 
    {'reward': 250, 
    'description': 'Magnificent stallion roams the plains!'},
    'brew healing elixir': 
    {'reward': 140, 
    'description': 'Village plagued by mysterious illness!'}
}

BLACKSMITH_JOBS = {
    'sharpen village weapons': {'reward': 90, 'description': 'Village guard needs weapon maintenance!'},
    'forge horseshoes': {'reward': 50, 'description': 'Stable master needs quality horseshoes!'},
    'repair armor': {'reward': 70, 'description': 'Damaged armor from last skirmish!'},
    'craft ceremonial sword': {'reward': 200, 'description': 'Noble wedding needs special blade!'}
}

TAVERN_ACTIVITIES = {
    'arm wrestling contest': 
    {'reward': 75,
    'description': 'Test your strength against locals!'
    },
    'storytelling night': 
    {'reward': 50,
    'description': 'Entertain patrons with epic tales!'},
    'drinking contest': 
    {'reward': 40, 
    'description': 'Last one standing wins the pot!'},
    'solve riddle challenge':
    {'reward': 85,
    'description': 'Old sage poses mysterious riddles!'},
    'bard performance': 
    {'reward': 65, 
    'description': 'Play music for coin and glory!'}
}

RANDOM_EVENTS = [
    {'event': 'You find a purse dropped by a merchant!', 'gold': 45},
    {'event': 'A grateful villager tips you for your heroic reputation!', 'gold': 30},
    {'event': 'You discover ancient coins while walking!', 'gold': 80},
    {'event': 'A mysterious stranger pays you for information!', 'gold': 60},
    {'event': 'You help catch a runaway pig and get rewarded!', 'gold': 25},
    {'event': 'You find treasure in an old barrel!', 'gold': 95},
    {'event': 'A noble appreciates your service to the village!', 'gold': 120},
    {'event': 'You win a bet on a racing rooster!', 'gold': 35},
    {'event': 'A witch pays you for rare mushrooms you found!', 'gold': 70},
    {'event': 'You return a lost ring and get rewarded!', 'gold': 55},
    {'event': 'Village children pool their coins to thank their hero!', 'gold': 15},
    {'event': 'A traveling bard pays for your heroic story!', 'gold': 40}
]

ITEM_DESCRIPTIONS = {
    # Freelancers
    'brian': 'A simple peasant, surprisingly brave in battle',
    'black knight': 'An invincible warrior who never yields',
    'biccus diccus': 'A Roman centurion with a ridiculous name but serious skills',
    'grim reaper': 'Death incarnate - your most powerful ally',
    'minstrel': 'A seemingly harmless musician... or is he?',
    'god': 'The Almighty himself - requires dedication and hope rather than gold',
    'nordic': 'A fierce Viking warrior from the frozen north',
    'mage': 'A powerful wizard with devastating spells',
    'ze germane': 'A German mercenary of questionable loyalty...',
    'raddragonore': 'A legendary dragonlord with mythical creatures',
    
    # Antiques
    'french castle': 'A portable fortress for strategic defense',
    'wooden grail': 'A humble cup with mysterious powers',
    'scythe': 'Death\'s own weapon, wickedly sharp',
    'catapult': 'A siege weapon for breaking enemy formations',
    'german joke': 'So bad it might actually kill Germans with cringe',
    'spear': 'A reliable thrusting weapon',
    'axe': 'A heavy chopping weapon',
    'peace': 'Pacifism incarnate - might actually pay YOU to take it',
    'rock': 'An extremely expensive rock. Must be special somehow.',
    'healing potion': 'Restores health and can cheat death',
    'body armor': 'Heavy protection for battle',
    
    # Pets
    'blue parrot': 'A colorful bird that might scout for you',
    'white rabbit': 'Quick and lucky, good for escaping danger',
    'newt': 'A small creature with hidden magical properties',
    'wolf': 'A fierce companion for battle',
    'dragon': 'A cool pet ',
}

# Tiffany's Dialogue Lines
TIFFANY_DIALOGUE = {
    'opening': """She doesn't cheer for you. She doesn't swoon. She just gives you a look that clearly says:
    - Don't get yourself killed, idiot -""",
    
    'day_1': "Try not to mess this up. The village has enough problems without you adding to them.",
    'day_2': "Don't do anything stupid. More than usual, I mean.",
    'day_3': "Well, now we know it's not just drama. Try not to make it worse.",
    'day_4': "Idiots with swords. That's what this village is full of.",
    'day_5': "Choices, choices... try not to die. I'm running out of bandages.",
    'day_6': "Well, today's the day. Try not to get killed. Or do. I need the practice.",
    
    'raid_before': "Try not to get killed. I'm running out of bandages.",
    'raid_success': "Well, you're not dead. That's something, I suppose.",
    'raid_failure': "Someone help him! And try not to make it worse!",
    
    'death_alternative_potion': "I can't believe I wasted a good potion on you. Try not to do it again.",
    'death_alternative_mage': "Impressive. Don't make me do this again. My nerves can't take it.",
    'death_alternative_reaper': "What dark bargains have you made? Just... stay away from me with that thing.",
    'death_final': "You idiot. You absolute idiot. Why did you have to be so heroic?",
    
    'freelancer_battle': "Well done. I might actually have to admit you're competent. Don't let it go to your head.",
    
    'ending_legendary': "Well, I suppose you're not completely useless after all. Don't let it go to your head.",
    'ending_martyr': "You idiot! Why did you have to be so heroic?",
    'ending_emperor': "Tyrant. But at least you're consistent. I'll patch up your paper cuts.",
    'ending_champion': "Even you can't mess this up... right? Famous last words.",
    'ending_warlord': "Well, nobody can say you're not efficient. I'll patch up your... victims.",
    'ending_survivor': "You're alive. That's... something, I suppose. Try not to bleed on my floor.",
    'ending_defeat': "I told you this was a bad idea. But does anyone listen to me? No."
}