import random
import sys
import time
import os
import textwrap
import shutil

# For Windows
try:
    import msvcrt
    def is_key_pressed():
        return msvcrt.kbhit()
    def get_key():
        return msvcrt.getch()
# For Mac/Linux
except ImportError:
    import select
    def is_key_pressed():
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
    def get_key():
        return sys.stdin.read(1)

def slow_print(text, player=None, delay=0.02):
    # Detect terminal width for dynamic text wrapping
    columns, _ = shutil.get_terminal_size(fallback=(80, 24))
    width = columns - 2

    processed_text = player.distort_text(text) if player else text

    # Add line breaks to create text wrapping
    lines = processed_text.splitlines()
    wrapped_lines = [textwrap.fill(line, width=width) for line in lines]
    final_text = "\n".join(wrapped_lines)

    skipped = False
    print() # New line at the beginning
    for char in final_text:
        sys.stdout.write(char)
        sys.stdout.flush()
        # Check if the player tapped a key to skip
        if not skipped and is_key_pressed():
            get_key() # Clear the key from the buffer
            skipped = True
        if not skipped:
            time.sleep(delay)
    print() # New line at the end
    if not skipped:
        time.sleep(2)
    else:
        time.sleep(0.5)

class Player():
    def __init__(self, name):
        self.name = name
        self.stability = 10
        self.fuel = 120
        self.clues = []
        self.location = None
    
    def add_clue(self, clue):
        if clue in self.clues:
            return
        self.clues.append(clue)
        print(f"You obtain a clue: {clue.name}")
        time.sleep(1)
        clue.reveal()
        if len(self.clues) == 5:
            slow_print("A distant rumble echoes across the liminal space...")
            slow_print("A new path has opened somewhere far away.")
        if len(self.clues) == 6:
            slow_print("You have found all the clues. But, your struggle has not ended.")
            slow_print("Find the path back to your real life.")

    def change_fuel(self, amount):
        self.fuel = self.fuel + amount if self.fuel + amount <= 120 else 120
        print(f"You have {self.fuel}/120 fuel remaining.")
        if self.fuel <= 0:
            slow_print("The engine gives one final, pathetic cough before the cabin falls into a silence so heavy it feels physical. You coast for a few feet, the tires crunching to a halt on the gravel shoulder.")
            time.sleep(1)
            slow_print("You turn the key, but there is no spark - only the rhythmic click-click-click of a heart that has stopped beating. Outside, the fog begins to press against the glass, thick and hungry. You realize now that the fuel wasn't just gasoline; it was your will to move forward.")
            time.sleep(1)
            slow_print("As the cabin light flickers and dies, you look into the rearview mirror. Your reflection is already starting to blur, becoming rain-slicked and featureless. You open the door and step out onto the shoulder to wait.")
            time.sleep(1)
            slow_print("You are the new Passenger. Someone will be along shortly. They won't stop for you, either.")
            time.sleep(3)
            sys.exit()

    def reduce_stability(self, amount):
        self.stability = self.stability - amount if self.stability - amount <= 10 else 10
        print(f"You have {self.stability}/10 stability remaining.")
        if self.stability <= 0:
            slow_print("The world finally stops pretending to be a road. The concrete beneath your tires turns into a slurry of grey static, and the dashboard icons begin to weep black oil.")
            time.sleep(1)
            slow_print("You try to remember your name, but all you can hear is the screaming of a thousand neglected Saturdays and the hollow salute of a reflected officer. The 'rules' of the world have dissolved, leaving only the raw, jagged edges of your own regrets.")
            time.sleep(1)
            slow_print("You don't scream when the car door vanishes. You don't struggle when the sky becomes a ceiling of fluorescent office lights. You simply lean back and let the obsidian static fill your lungs. The highway didn't go anywhere because there was nowhere left for you to go.")
            time.sleep(1)
            slow_print("You have become a part of the architecture. The Sinkhole has found its center.")
            time.sleep(3)
            sys.exit()

    def display_stats(self):
        fuel_bar = "█" * (self.fuel // 10) + "░" * ((120 - self.fuel) // 10)
        stab_bar = "●" * self.stability + "◊" * (10 - self.stability)
        
        print(f"\n[ FUEL: {fuel_bar} {self.fuel}/120 ]")
        print(f"[ MIND: {stab_bar} {self.stability}/10 ]")
        print("=" * 30)
    
    def encounter(self, entity):
        print(f"You have encountered {entity.name}.")
        entity.intro(self)
        print("You must choose an option.")
        options = entity.options.copy()

        for clue in self.clues:
            if entity.required_clue and entity.required_clue == clue.name:
                options["5"] = entity.special_option_text
                break
        
        print("Your options:")
        for key, text in options.items():
            print(f"{key}: {text}")
        
        choice = None
        while choice not in options:
            choice = input("Enter your choice: ").strip()
            if choice not in options:
                print("Invalid choice. Please try again.")
        
        entity.resolve(choice, self)

    def distort_text(self, text):
        if self.stability > 3:
            return text

        if self.stability <= 3:
            chars = list(text)
            for i in range(len(chars)):
                if random.random() < 0.05: # 5% chance per character to glitch
                    chars[i] = random.choice(['...', '?', '!', '█', '§', '¶'])
            distorted = "".join(chars)
            return distorted

class Entity():
    def __init__(self, name, intro_text, options = None, required_clue = None, special_option_text = None):
        self.name = name        
        self.intro_text = intro_text
        self.options = options
        self.required_clue = required_clue
        self.special_option_text = special_option_text
    
    def intro(self, player):
        slow_print(self.intro_text, player)

class Passenger(Entity):
    def __init__(self, name, intro_text):
        super().__init__(name, intro_text)
        self.options = {"1": "Offer a Ride: Take him where he needs to go.",
                        "2": "Speed Past: Ignore him.",
                        "3": "Brandish a Tool: Intimidation might force him back - or not.",
                        "4": "Leave an Offering: Perhaps a gift will satisfy him."}
        self.required_clue = "Rearview Mirror"
        self.special_option_text = "Acknowledge Him: Use your memory of that rainy Tuesday to settle a debt."
    
    def resolve(self, choice, player):
        match choice:
            case "1":
                slow_print("He is impossibly heavy, and the detour takes hours. Still, the silence feels lighter.")
                player.change_fuel(-20)
                player.reduce_stability(-1) # gain
            case "2":
                slow_print("You leave him in the dust. His cries echo through the car speakers.")
                player.change_fuel(-2)
                player.reduce_stability(2)
            case "3":
                if random.random() > 0.5:
                    slow_print("He recoils into the fog, dropping a small canister of fuel in his haste.")
                    player.change_fuel(5)
                else:
                    slow_print("He lunges at the window. The look in his eyes haunts you.")
                    player.reduce_stability(3)
            case "4":
                slow_print("You leave a jug on the asphalt. He watches you go, satisfied for now.")
                player.change_fuel(-10)
            case "5":
                slow_print("You speak the words you should have said years ago. He tips his hat and vanishes into the rain.")
                player.change_fuel(-2)
            case _:
                print("This option is not implemented yet.")
        time.sleep(2)

class Children(Entity):
    def __init__(self, name, intro_text):
        super().__init__(name, intro_text)
        self.options = {"1": "Join the Game: Stay and play with them.",
                        "2": "Drive Through: Force your way past.",
                        "3": "Toss a Distraction: Throw them some supplies.",
                        "4": "Scold Them: Assert your authority."}
        self.required_clue = "Forgotten Recital"
        self.special_option_text = "Fulfill the Promise: Hand over the gift you promised to give them at that recital."
    
    def resolve(self, choice, player):
        match choice:
            case "1":
                slow_print("You lose track of time playing their strange, looping games. Your fuel is lower, but your heart is lighter.")
                player.change_fuel(-18)
                player.reduce_stability(-2) # gain
            case "2":
                slow_print("The masks don't move as you strike them. There is no thud. Only the sound of shattering glass echoing in your skull for miles.")
                player.change_fuel(-2)
                player.reduce_stability(4)
            case "3":
                slow_print("You toss a flare and some rations. They swarm the items like locusts, leaving the road clear.")
                player.change_fuel(-10)
                player.reduce_stability(1)
            case "4":
                if random.random() > 0.5:
                    slow_print("They scatter into the weeds, frightened by your anger. The path is clear.")
                else:
                    slow_print("They cling to the bumper, their small hands leaving dents in the metal as they weep. You drag them for a mile before they let go.")
                    player.change_fuel(-5)
                    player.reduce_stability(2)
            case "5":
                slow_print("You hand them the dusty wrapped box. The animal masks tilt in unison, and they dissolve into white flower petals that catch in the wind.")
                player.change_fuel(-2)
                player.reduce_stability(-3) # gain
            case _:
                print("This option is not implemented yet.")

class PoliceOfficer(Entity):
    def __init__(self, name, intro_text):
        super().__init__(name, intro_text)
        self.options = {"1": "Submit to Search: Let him inspect the car.",
                        "2": "Pay the Fine: Offer him a bribe.",
                        "3": "Argue Rights: Assert your logic.",
                        "4": "Ram the Blockade: Break through."}
        self.required_clue = "Shield of Policy"
        self.special_option_text = "Surrender the Armor: Admit that 'policy' was just a mask for your own cowardice."
    
    def resolve(self, choice, player):
        match choice:
            case "1":
                slow_print("He moves through your car with cold, mechanical efficiency, touching things that should be private. You feel violated and small by the time he waves you through.")
                player.change_fuel(-5)
                player.reduce_stability(2)
            case "2":
                slow_print("You pump your precious fuel into his idling car. He offers a sharp, hollow salute as he pulls the cruiser aside to let you pass.")
                player.change_fuel(-25)
            case "3":
                if random.random() > 0.5:
                    slow_print("The officer seems confused by your defiance, as if he forgot the laws he's enforcing. He slowly reverses into the fog.")
                else:
                    slow_print("He doesn't speak. He simply smashes your window and drags the clock forward, imprisoning your fragile mind.")
                    player.change_fuel(-10)
                    player.reduce_stability(3)
            case "4":
                slow_print("Metal screams against metal. You jolt past the blockade, leaving a trail of sparks and precious fuel leaking from a stressed line.")
                player.change_fuel(-15)
                player.reduce_stability(1)
            case "5":
                slow_print("You speak the truth: you weren't following orders; you were being cruel. The officer's uniform collapses into a pile of dry autumn leaves.")
                player.change_fuel(-5)
                player.reduce_stability(-2) # gain
            case _:
                print("This option is not implemented yet.")

class Being(Entity):
    def __init__(self, name, intro_text):
        super().__init__(name, intro_text)
        self.options = {"1": "Hold the Gaze: Absorb the truth of your existence.",
                        "2": "Run the Length: Sprint across the bridge.",
                        "3": "Recite Regrets: Admit your faults.",
                        "4": "Blind Defiance: Refuse to acknowledge its power."}
        self.required_clue = "The Final Audit"
        self.special_option_text = "x"
    
    def resolve(self, choice, player):
        match choice:
            case "1":
                slow_print("You see your entire life - not as you remember it, but as it actually was. The weight of your own coldness shatters something deep inside you.")
                player.reduce_stability(4)
            case "2":
                slow_print("You run until your lungs burn like acid and the car's engine screams in sympathy. You reach the other side, but you are physically and mechanically spent.")
                player.change_fuel(-45)
            case "3":
                slow_print("You speak until your throat is raw. The Being stills, absorbing your words like a sponge. You are allowed to pass, but a piece of your soul stays behind.")
                player.change_fuel(-20)
                player.reduce_stability(3)
            case "4":
                if random.random() > 0.5:
                    slow_print("Your defiance creates a momentary ripple in the static. You stumble past as the Being recoils in confusion.")
                    player.reduce_stability(1)
                else:
                    slow_print("The Being lashes out, dragging you into a nightmare of your own failures. You barely crawl back to the path.")
                    player.reduce_stability(6)
            case "5":
                pass
                # not reachable
            case _:
                print("This option is not implemented yet.")

class Area():
    def __init__(self, name, description, contains = None):
        self.name = name
        self.description = description
        self.contains = contains
        self.visited = False

class Location():
    def __init__(self, name, intro_text, clue, entity, area1, desc1, contains1, area2, desc2, contains2, area3, desc3, contains3):
        self.name = name
        self.intro_text = intro_text
        self.clue = clue
        self.entity = entity
        self.areas = {
            "1": Area(area1, desc1, contains = contains1),
            "2": Area(area2, desc2, contains = contains2),
            "3": Area(area3, desc3, contains = contains3)
        }
        self.exits = {}
        self.clue_found = False
        self.entity_encountered = False
        self.locked = False
        self.shuffle_areas()
    
    def intro(self, player):
        print(f"You arrive at the {self.name}.")
        slow_print(self.intro_text, player)

    def choose_area(self, player):
        if self.name == "Sinkhole":
            # Only one area, always encounter the Being
            area = self.areas["1"]
            print(f"\nYou approach {area.name}.")
            slow_print(area.description, player)
            self.handle_entity_area(player)
            return

        while True:
            player.display_stats()
            print(f"\n--- {self.name.upper()} ---")
            print("Areas to explore:")
            for key, area in self.areas.items():
                status = "[visited]" if area.visited else "[ ]"
                print(f"{key}. {area.name} {status}")

            print("L. Return to the car (Leave Location)")
            time.sleep(1)

            choice = input("\nWhat will you do? ").strip().upper()

            if choice == "L":
                print(f"You return to your car, leaving the {self.name} behind.")
                return

            if choice not in self.areas:
                print("That is not a path you can take. Please choose again.")
                continue

            area = self.areas[choice]
            area.visited = True
            print(f"\nExploring: {area.name}")
            slow_print(area.description, player)

            # Handle what the area contains
            if area.contains == self.clue:
                self.handle_clue_area(player)
            
            elif area.contains == self.entity and self.entity is not None:
                self.handle_entity_area(player)
            
            elif area.contains == "fuel_gain":
                print("\nYou use the canisters to refuel your tank...")
                player.change_fuel(min(40, 120 - player.fuel)) # 40 fuel or full tank
                time.sleep(1)
                area.contains = None # no fuel farming
            
            elif area.contains == "fuel_loss":
                print("\nThe fuel pump coughs a thick, oily shadow into your tank...")
                player.change_fuel(-15)
                time.sleep(1)

            else:
                flavor_text = [
                    "\nThe wind whistles through the rusted metal.",
                    "\nYou feel like someone is watching you from the treeline.",
                    "\nA discarded newspaper dances across the asphalt."
                ]
                print(random.choice(flavor_text))

    def handle_clue_area(self, player):
        if not self.clue_found:
            print("\nYou discover a clue!")
            player.add_clue(self.clue)
            self.clue_found = True

            # If entity not yet encountered, trigger it immediately
            if not self.entity_encountered and self.entity is not None:
                print("\nSomething stirs nearby...")
                time.sleep(1)
                self.handle_entity_area(player)

        else:
            print("\nYou've already found the clue here.")

    def handle_entity_area(self, player):
        if not self.entity_encountered:
            print("\nA presence emerges...")
            time.sleep(1)
            # If clue was found first, player gets special option
            self.entity_encountered = True
            player.encounter(self.entity)

            # give final clue after defeating the Being
            if self.name == "Sinkhole":
                print("\nAs the Being dissolves into the void, something remains behind...")
                time.sleep(1)
                self.handle_clue_area(player)
                return

            # If entity was found first, give clue afterward
            if not self.clue_found:
                print("\nAfter the encounter, you notice something on the ground...")
                time.sleep(1)
                self.handle_clue_area(player)

        else:
            print("\nThe presence has faded from this area.")

    def shuffle_areas(self):
        # Convert dictionary values to a list and shuffle them
        area_list = list(self.areas.values())
        random.shuffle(area_list)
        
        # Re-assign the shuffled areas to the string keys
        self.areas = {str(i+1): area for i, area in enumerate(area_list)}

class Clue():
    def __init__(self, name, description):
        self.name = name
        self.description = description
    
    def reveal(self):
        print("\n" + "/" * 20 + " " * 10 + "\\" * 20)
        slow_print(self.description)
        print("\n" + "\\" * 20 + " " * 10 + "/" * 20)

class Road():
    def __init__(self, name, description, fuel_cost):
        self.name = name
        self.description = description
        self.fuel_cost = fuel_cost
        self.locations = []
    
    def intro(self, player):
        print(f"You are on the {self.name}.")
        slow_print(self.description, player)

class Game():
    def __init__(self):
        self.player = Player("The Driver")
        self.clues = {}
        self.entities = {}
        self.roads = {}
        self.locations = {}
        self.roads_traveled = 0
    
    def start(self):
        if 'TERM_PROGRAM' in os.environ.keys() and os.environ['TERM_PROGRAM'] == 'vscode':
            print("Please run this in a native terminal, fullscreen! It will look much better!")
            input("Ctrl+C, or press Enter and ruin my nice ASCII art :(")

        # build the world and insert game objects
        world = build_world()
        self.clues = world["clues"]
        self.entities = world["entities"]
        self.roads = world["roads"]
        self.locations = world["locations"]

        self.player.location = world["starting_location"]

        os.system('cls' if os.name == 'nt' else 'clear')
        slow_print("The last thing you remember wasn't a crash. It was a feeling.")
        time.sleep(1)
        slow_print("The hum of a fluorescent office light. The taste of lukewarm coffee. The sight of your own hands typing a report for a man whose face you can no longer recall. You were 'making good time.' You were 'getting ahead.' Then, the fluorescent hum deepened into a low, rhythmic thrum - the sound of tires on old asphalt.")
        time.sleep(1)
        slow_print("You blink, and the office is gone. You are behind the wheel of a car that feels like a second skin, driving through a world that is nothing but a grey, infinite ribbon of highway.")
        time.sleep(3)
        os.system('cls' if os.name == 'nt' else 'clear')
        time.sleep(1)
        
        title = r"""
██╗███╗   ██╗████████╗███████╗██████╗ ███████╗████████╗ █████╗ ████████╗███████╗    ███████╗███████╗██████╗  ██████╗ 
██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗╚══██╔══╝██╔════╝    ╚══███╔╝██╔════╝██╔══██╗██╔══██╗ 
██║██╔██╗ ██║   ██║   █████╗  ██████╔╝███████╗   ██║   ███████║   ██║   █████╗        ███╔╝ █████╗  ██████╔╝██║  ██║ 
██║██║╚██╗██║   ██║   ██╔════╝██╔══██╗╚════██║   ██║   ██╔══██║   ██║   ██╔════╝     ███╔╝  ██╔════╝██╔══██╗██║  ██║ 
██║██║ ╚████║   ██║   ███████╗██║  ██║███████║   ██║   ██║  ██║   ██║   ███████╗    ███████╗███████╗██║  ██║╚██████╔╝
╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝   ╚══════╝    ╚══════╝╚══════╝╚═╝  ╚═╝ ╚═════╝ 
        """
        columns, _ = shutil.get_terminal_size(fallback=(80, 24))
        for line in title.splitlines():
            print(line.center(columns))
            time.sleep(0.25)
        print("\n" * 3)
        print("[ Press Enter to start. ]".center(columns))
        input()
        os.system('cls' if os.name == 'nt' else 'clear')

        print("\nThe Rules of the Road")
        slow_print("To survive this place, you must manage two dwindling flickers of light:")
        time.sleep(1)
        slow_print("FUEL: Your physical momentum. Every stretch of road consumes it. If the needle hits empty, the car stops. In this world, to stop is to be forgotten.")
        time.sleep(1)
        slow_print("STABILITY: Your grip on reality. The horrors of the highway will pull at your mind. As your stability fades, the world will begin to distort - words will shift, and the descriptions of your surroundings will grow increasingly nightmarish.")
        time.sleep(1)

        print("\nThe Objective")
        slow_print("You aren't sure where you're going, but your hands remember the turn. Somewhere ahead, the road is supposed to lift. You have a fading memory of a high, concrete horizon - a place where the shadows of the pillars stop and the light finally breaks through. But the fog is thick, and the way is shuttered. To find the ascent, you must scavenge for Clues: fragments of the life you left behind. Only by facing the truth of why you are here can you hope to leave.")

        slow_print("You've been driving for what feels like hours, the radio spitting out nothing but white noise and the occasional, distorted sob. The fog ahead thickens, turning a bruised purple, until your headlights catch the glint of orange plastic and jagged metal.")
        time.sleep(1)
        slow_print("The road doesn't just stop; it is denied.")
        time.sleep(1)
        slow_print("You pull the car to a halt, the engine idling with a wet, heavy rattle. The silence that follows is louder than the drive ever was. You have reached your first obstacle.")
        time.sleep(1)
        slow_print("You are at: THE ROADBLOCK")
        time.sleep(3)

        self.player.location.intro(self.player)
        self.player.location.choose_area(self.player)

    def change_fuel(self, amount):
        self.player.fuel = min(120, self.player.fuel + amount)
        print(f"You have {self.player.fuel} fuel remaining.")
        if self.player.fuel <= 0:
            print("You have run out of fuel.")
            self.game_over_fuel()
    
    def reduce_stability(self, amount):
        self.player.stability = min(10, self.player.stability - amount)
        if self.player.stability <= 0:
            print("Your mind has shattered.")
            self.game_over_stability()
        else:
            print(f"You have {self.player.stability} stability remaining.")
         
    def passenger_encounter(self):
        if random.randint(1, 8) <= self.roads_traveled: # experiment with chance of encounter
            for entity in self.entities.values():
                if "Passenger" in entity.name:
                    self.player.encounter(entity)
                    self.entities.pop(entity.name) # only encounter once
                    break

    def check_game_over(self):
        if self.player.fuel <= 0:
            slow_print("You have run out of fuel.")
            self.game_over_fuel()
        if self.player.stability <= 0:
            slow_print("Your mind has shattered.")
            self.game_over_stability()

    def game_over_fuel(self):
        slow_print("The engine gives one final, pathetic cough before the cabin falls into a silence so heavy it feels physical. You coast for a few feet, the tires crunching to a halt on the gravel shoulder.")
        time.sleep(1)
        slow_print("You turn the key, but there is no spark - only the rhythmic click-click-click of a heart that has stopped beating. Outside, the fog begins to press against the glass, thick and hungry. You realize now that the fuel wasn't just gasoline; it was your will to move forward.")
        time.sleep(1)
        slow_print("As the cabin light flickers and dies, you look into the rearview mirror. Your reflection is already starting to blur, becoming rain-slicked and featureless. You open the door and step out onto the shoulder to wait.")
        time.sleep(1)
        slow_print("You are the new Passenger. Someone will be along shortly. They won't stop for you, either.")
        time.sleep(3)
        sys.exit()
    
    def game_over_stability(self):
        slow_print("The world finally stops pretending to be a road. The concrete beneath your tires turns into a slurry of grey static, and the dashboard icons begin to weep black oil.")
        time.sleep(1)
        slow_print("You try to remember your name, but all you can hear is the screaming of a thousand neglected Saturdays and the hollow salute of a reflected officer. The 'rules' of the world have dissolved, leaving only the raw, jagged edges of your own regrets.")
        time.sleep(1)
        slow_print("You don't scream when the car door vanishes. You don't struggle when the sky becomes a ceiling of fluorescent office lights. You simply lean back and let the obsidian static fill your lungs. The highway didn't go anywhere because there was nowhere left for you to go.")
        time.sleep(1)
        slow_print("You have become a part of the architecture. The Sinkhole has found its center.")
        time.sleep(3)
        sys.exit()
    
    def check_game_win(self):
        if len(self.player.clues) >= 6 and self.player.location.name == "Overpass":
            slow_print("\n" + "="*40)
            slow_print("THE WAY OUT", delay=0.1)
            slow_print("="*40)
            time.sleep(1)
            self.game_win()

    def game_win(self):
        slow_print("The steering wheel feels lighter in your grip. As you clear the final barricade, the road begins to tilt upward. The heavy, stagnant air of the lowlands thins, replaced by a wind that smells of ozone and - impossibly - freshly cut grass.")
        slow_print("You reach the crest of the Overpass. For the first time, the rhythmic thump-thump of the tires matches the beating of your own heart. Below you, the labyrinth of grey concrete and shifting static begins to dissolve into a sea of morning mist.")
        slow_print("Ahead, the flickering neon of the liminal world is replaced by a single, steady glow: the sun rising over the suburbs of your youth. You see the exit ramp - the one you took a thousand times without thinking. You take it now with both hands on the wheel.")
        slow_print("The car glides into the driveway. The engine, finally silent, gives one last warm click as it cools. You step out, the gravel crunching under your shoes. You are no longer 'making time.' You are simply home.")
        time.sleep(3)
        slow_print("Thank you for playing.")
        time.sleep(1)
        sys.exit()

    def show_location_menu(self):
        time.sleep(2)
        os.system('cls' if os.name == 'nt' else 'clear')
        self.player.display_stats()
        location = self.player.location

        self.try_unlock_sinkhole()
        
        print(f"\nYou are at: {location.name}")
        print("Where would you like to go?")

        # Filter exits based on whether the destination is locked
        visible_exits = {}
        for direction, road in location.exits.items():
            locA, locB = road.locations
            destination = locB if location == locA else locA

            if hasattr(destination, "locked") and destination.locked:
                continue  # hide locked locations

            visible_exits[direction] = road

        for direction, road in visible_exits.items():
            print(f"{direction}: {road.name}")

        choice = None
        while choice not in visible_exits:
            choice = input("Choose a direction: ").strip().lower()
            if choice not in visible_exits:
                print("Invalid choice. Try again.")

        return visible_exits[choice]

    def handle_player_choice(self, road):
        self.change_fuel(-road.fuel_cost)
        self.roads_traveled += 1
        road.intro(self.player)
        time.sleep(1)
        if self.roads_traveled >= 2:
            self.passenger_encounter()
        self.trigger_road_event()
        # change player.location to the location in road.locations that is not the current location
        locA, locB = road.locations
        destination = locB if self.player.location == locA else locA

        self.player.location = destination
        self.check_game_win()
        os.system('cls' if os.name == 'nt' else 'clear')
        self.player.display_stats()
        destination.intro(self.player)
        destination.choose_area(self.player)

    def try_unlock_sinkhole(self):
        sinkhole = self.locations["Sinkhole"]
        if len(self.player.clues) >= 5 and sinkhole.locked:
            sinkhole.locked = False
    
    def trigger_road_event(self):
        # 15% chance of a random event occurring
        if random.random() < 0.15:
            events = [
                {
                    "text": "The radio suddenly screams with the sound of a thousand birds. You fumble to turn it off, but the dial is burning hot.",
                    "effect": "stability",
                    "amount": -1
                },
                {
                    "text": "A thick, oily sludge coats the road. The tires spin fruitlessly, burning through your reserves just to keep moving.",
                    "effect": "fuel",
                    "amount": -15
                },
                {
                    "text": "For a split second, the rearview mirror shows your own face, but your eyes are sewn shut with silver thread.",
                    "effect": "stability",
                    "amount": -1
                }
            ]
            
            event = random.choice(events)
            print("\n== UNSETTLING EVENT ==")
            slow_print(event["text"], self.player)
            
            if event["effect"] == "stability":
                self.reduce_stability(abs(event["amount"]))
                time.sleep(2)
            else:
                self.change_fuel(event["amount"])
                time.sleep(2)

def build_world():
    # details of the world here
    clue_1 = Clue("Rearview Mirror", "A memory of a rainy Tuesday. You saw a figure on the shoulder of the highway, shivering. You checked the clock, thought of your dinner plans, and pressed the accelerator.") # passenger / radio tower
    clue_2 = Clue("Forgotten Recital", "It was a Saturday, and you promised you'd be in the front row. Instead, you spent the evening under fluorescent office lights, chasing a promotion that eventually forgot your name.") # children / subdivision
    clue_3 = Clue("Shield of Policy", "You remember the day you let him go, citing 'standard procedure' to avoid looking him in the eye while his world collapsed. You wore your professional decorum like a suit of armor.") # police officer / overpass
    clue_4 = Clue("The Final Audit", "The highway was never a path to somewhere else; it was the life you chose to live while waiting for your 'real' life to begin. From the rainy Tuesday on the road to the empty seat at the recital, every mile was a brick in this prison of your own design. You are not lost in the liminal space - you are finally, for the first time, exactly where your choices were leading.") # being / sinkhole - only after
    clue_5 = Clue("Idle Engine", "You spent your life treating every destination as a chore and every stop as a delay. You were so focused on having 'enough' to get to the next mile that you never realized you were burning the only years you actually had.") # gas station
    clue_6 = Clue("Path of Least Resistance", "Whenever the road grew dark or the signs became confusing, you chose to turn back rather than face the truth. You mistook comfort for safety, unaware that a path without friction is just a slow way to disappear.") # roadblock

    entity_passenger = Passenger("Passenger", "A figure in a rain-slicked trench coat stands by the roadside. His face is a blur of motion, like a long-exposure photograph. He doesn't wave, but the car slows down of its own accord as you approach.")
    entity_children = Children("Children", "A cluster of small figures stands in the center of the road, their faces obscured by paper animal masks that appear to be melting. They stand in a perfect, silent circle, clutching frayed ribbons that lead into the tall, dead grass.")
    entity_police_officer = PoliceOfficer("Police Officer", "A cruiser sits perpendicular to the road, its light bar pulsing in a rhythm that mimics a dying heartbeat. An officer stands by the driver's side, his hand resting on a holster made of leather and shadow, his face a perfect, empty mirror.")
    entity_being = Being("Being", "The rope bridge sways over an abyss that isn't empty, but filled with a humming, obsidian static that tastes like copper and old photographs. The Being is a shifting architecture of glass teeth and weeping oil, vibrating with the overlapped voices of everyone you ever ignored. It is the destination you were always driving toward: the silent auditor of a life spent in transit.")

    # location coding:
    # 1 = overpass
    # 2 = radio tower
    # 3 = subdivision
    # 4 = gas station
    # 5 = roadblock
    # 6 = sinkhole

    road_1_2 = Road("The Grid-Iron Viaduct", "You drive along a narrow ribbon of concrete suspended miles above a sea of static-filled fog. To your left, power lines stretch like spiderwebs toward the horizon, humming with a frequency that makes your teeth ache.", 8)
    road_1_4 = Road("The Petroleum Slope", "The road descends into a valley of rusted refineries and silent smoke-stacks. The air grows thick and oily, and the sky turns the color of a fresh bruise as you pass fields of discarded oil drums that rattle in your wake.", 8)
    road_1_6 = Road("The Fractal Interchange", "The lanes begin to split and merge in impossible geometries. You see yourself driving on a parallel ramp three levels up, but they have no head; the concrete starts to spiral inward toward the center of the world.", 8)
    road_2_3 = Road("Frequency Boulevard", "Every house you pass in the distance has a television antenna pointed directly at the tower behind you. The shadows of the trees look like jagged audio waveforms, flickering in sync with the white noise on your car radio.", 8)
    road_2_6 = Road("The Static Corridor", "The asphalt beneath your tires begins to break into grey pixels. The horizon isn't a line anymore, but a jagged tear in the sky where the broadcast ends and the silence of the abyss begins.", 8)
    road_3_5 = Road("The Picket Perimeter", "White picket fences line the road for miles, but there are no houses behind them—only an infinite, flat expanse of dead grass. Every few miles, a child's bicycle lies abandoned in the middle of the lane, perfectly upright.", 8)
    road_3_6 = Road("The Domestic Spillway", "Household furniture begins to litter the shoulder—armchairs, lamps, and dining tables half-submerged in the asphalt as if the road is swallowing a home. The air smells of stagnant laundry water and dust.", 8)
    road_4_5 = Road("The Low-Octane Bypass", "You traverse a salt-flat desert where the only landmarks are piles of discarded hubcaps. The sun is a pale, heatless disc, and the road is so straight it feels like a line drawn by a shaking hand.", 8)
    road_5_6 = Road("The Impact Zone", "The road surface turns into a smooth, black glass that reflects a sky you don’t recognize. Warning signs fly past, but they are all blank, their yellow paint peeling off like dead skin as you approach the gravity of the pit.", 8)

    overpass = Location("Overpass",
                            "A monolithic knot of grey concrete rises from the mist, spanning layers of highway that seem to weave into themselves like a Gordian knot. The air here is heavy with the smell of old exhaust and cold rain, and the only sound is the rhythmic, ghostly thump-thump of tires passing on a road you cannot see. It is a place of transition that has forgotten its destination - a border crossing where the only thing being checked is the weight of your own conscience.",
                            clue_3,
                            entity_police_officer,
                            "Abandoned Toll Booth",
                            "A cramped, glass-walled box sits in the center of the lane, its interior lit by a flickering, sickly yellow fluorescent bulb. Stacks of yellowing citations and logbooks are piled to the ceiling, their ink bleeding into the damp paper like old bruises. It is a place built for gatekeeping, where every movement required a signature that no longer matters.",
                            clue_3,
                            "Median Emergency Turnaround",
                            "A break in the high concrete barrier reveals a gravel-strewn patch designed for official vehicles to change direction. The air here is unnervingly still, smelling of burnt rubber and ozone, and the shadows under the bridge seem to pulse with a rhythmic, blue-and-red tint that has no visible source.",
                            entity_police_officer,
                            "Concrete Support Forest",
                            "Massive, brutalist pillars rise from the dirt like the trunks of grey, bloodless trees, supporting the layers of highway above. The only sound is the rhythmic thump-thump of invisible cars passing overhead, a heartbeat of a world you can no longer see. There is nothing here but the cold weight of the structure and the dust of a thousand journeys.",
                            None)
    overpass.exits["northeast"] = road_1_2
    overpass.exits["west"] = road_1_4
    overpass.exits["northwest"] = road_1_6
    
    radio_tower = Location("Radio Tower",
                            "A skeletal spire of rusted iron stabs upward into the low, bruised clouds, humming with a frequency that vibrates in your very teeth. Guy-wires thick as human torsos vanish into the fog, moaning like cello strings as the wind whips through the lattice. This is the source of the static that has been bleeding through your car speakers - a lonely lighthouse for signals that were sent long ago and never received.",
                            clue_1,
                            None, # no entity
                            "Signal Monitoring Room",
                            "A wall of flickering CRT monitors displays grainy, looping footage of a rain-slicked highway from a perspective that seems to follow your car. Dozens of reel-to-reel tapes spin in a discordant symphony of static and half-remembered whispers. It is a room designed for the obsessive act of watching what has already passed you by.",
                            clue_1,
                            "Lattice Catwalk",
                            "A rusted iron walkway suspended hundreds of feet above the fog-choked forest floor, where the wind screams through the metal girders like a wounded animal. The height is dizzying, but the view offers no horizon—only an infinite, grey void stretching in every direction. There is nothing here but the cold, thin air and the terrifying realization of how small you've become.",
                            None,
                            "Backup Generator Vault",
                            "A heavy steel door leads into a concrete bunker that vibrates with the low, rhythmic thrum of a massive, ancient diesel engine. The air is thick with the sweet, choking scent of unrefined gasoline and old machine grease, making your eyes sting. In the corner, several red metal canisters sit undisturbed, their weight promising a few more miles of borrowed time.",
                            "fuel_gain")
    radio_tower.exits["west"] = road_2_3
    radio_tower.exits["southwest"] = road_2_6
    radio_tower.exits["south"] = road_1_2
    
    subdivision = Location("Subdivision",
                            "Rows of identical, pastel-colored houses stretch into the twilight, their windows staring back at you like sightless, milky eyes. The lawns are perfectly manicured but the grass is a dry, pale yellow that crunches like bone underfoot. There is no sound of barking dogs or playing children - only the low, rhythmic hum of air conditioners cooling empty rooms in a neighborhood that has no end.",
                            clue_2,
                            entity_children,
                            "Parlor of Echoes",
                            "Inside this house, the furniture is draped in heavy white sheets that have gathered a thick layer of grey dust. An upright piano sits in the corner, its keys permanently depressed as if held down by invisible fingers, while a single, wilted corsage rests on the bench. It is a room preserved in the exact moment of a disappointment that occurred years ago and hasn't stopped happening since.",
                            clue_2,
                            "Cul-de-Sac of Ribbons",
                            "The street ends in a perfect circle where the asphalt is spider-webbed with deep cracks. Frayed silk ribbons in faded primary colors are tied to every mailbox and porch railing, all of them trailing along the ground toward a single point in the center of the road. The air here is unnervingly cold, carrying the faint, metallic scent of a playground after a heavy rain.",
                            entity_children,
                            "Model Home",
                            "The front door stands slightly ajar, inviting you into an interior that is perfectly staged but entirely hollow. There are no family photos on the mantle and no food in the pantry - only the sterile, suffocating smell of new carpet and stagnant air. It is a shell of a life designed for a brochure, offering plenty of space but no reason to stay.",
                            None)
    subdivision.exits["southwest"] = road_3_5
    subdivision.exits["south"] = road_3_6
    subdivision.exits["east"] = road_2_3
    
    gas_station = Location("Gas Station",
                            "A lone island of flickering neon stands in a sea of cracked asphalt, its overhead canopy sagging like a heavy, tired eyelid. The air is thick with the sweet, sickening scent of old petroleum and ozone, a smell that promises progress but offers only a pause. Here, the hum of the fluorescent lights is the only voice left, singing a buzzing dirge for every driver who was too afraid to run on empty.",
                            clue_5,
                            None, # no entity
                            "Office of Stagnant Records",
                            "Behind a counter of cracked laminate and sun-bleached snacks, a mountain of handwritten logs and crinkled receipts spills onto the floor. Every entry is a frantic ledger of a life lived in increments of 'almost there,' recording gallons and miles that never added up to a destination. It is a room where the clocks have all stopped at different hours, reflecting the fractured time of a man who was always in a hurry to be nowhere.",
                            clue_5,
                            "Sun-Bleached Aisles",
                            "Row after row of metal shelves hold identical, label-less cans and dusty bags of air that rattle in the draft. The cooling fans in the back moan with mechanical exhaustion, rattling the glass doors of refrigerators filled with nothing but condensed, grey fog. There is no nourishment here—only the quiet, crushing realization that you are standing in a store designed to satisfy a hunger that no longer exists.",
                            None,
                            "Pump Number Nine",
                            "A rusted, antique pump stands apart from the others, its digital display spinning wildly with numbers that have no meaning. When you lift the nozzle, a freezing, oily black mist bleeds from the hose, coiling around your wrists like a cold parasite. Instead of filling your tank, the pump seems to inhale, siphoning the very lifeblood of your car back into the dark, thirsty earth.",
                            "fuel_loss")
    gas_station.exits["north"] = road_4_5
    gas_station.exits["east"] = road_1_4
    
    roadblock = Location("Roadblock",
                            "The pavement simply ends, replaced by a wall of jagged orange barricades and tangled rolls of rusted concertina wire that seem to have grown out of the asphalt. A yellow sign, bleached white by a sun that never sets, hangs crookedly from a sawhorse, its black lettering worn down to a faint, mocking smudge. This is where your momentum died - a silent, immovable 'No' at the end of a road that was supposed to go on forever.",
                            clue_6,
                            None, # no entity
                            "Culvert of Discarded Maps",
                            "Below the lip of the road, a concrete drainage pipe is choked with thousands of sodden, pulpy roadmaps that have bled their ink into the mud. You can see the traces of red lines where a traveler once traced a route, only to stop and turn back at the first sign of shadow. It is a graveyard of intentions, a place where every detour was a surrender and every U-turn was a choice to stay lost.",
                            clue_6,
                            "Watchman's Lean-To",
                            "A small shelter made of plywood and blue tarps sits huddled against the barricade, its interior smelling of damp cardboard and cold ash. A half-eaten meal sits on a crate, frozen in time, and a battery-powered lantern flickers with a dying, orange light that reveals nothing but dust. Whoever was supposed to be guarding this dead end has long since vanished, leaving only the crushing weight of their boredom behind.",
                            None,
                            "Perimeter Fence",
                            "Chain-link fencing stretches into the grey woods on either side of the road, its metal diamonds clogged with dead leaves and scraps of plastic that rattle in the wind. There are no holes and no gates; the fence is a continuous, unbroken line of exclusion that marks the boundary of your world. Standing here, you realize the roadblock isn't just stopping your car - it's defining the edges of your cage.",
                            None)
    roadblock.exits["east"] = road_5_6
    roadblock.exits["northeast"] = road_3_5
    roadblock.exits["south"] = road_4_5
    
    sinkhole = Location("Sinkhole",
                        "The asphalt doesn't just end here; it shatters, falling away into a perfectly circular void that seems to swallow the very light from the sky. The edges of the pit are jagged and raw, revealing layers of earth that bleed a thick, black ichor into the depths below. There is no wind here, only a rhythmic, low-frequency thrum that vibrates in your marrow - the sound of a world finally exhaling its last breath.",
                        clue_4,
                        entity_being,
                        "",
                        "",
                        None,
                        "",
                        "",
                        None,
                        "",
                        "",
                        None)
    # override the sinkhole areas for the boss encounter
    sinkhole.areas = {"1": Area("Weaver's Crossing", "A single, fraying rope bridge spans the impossible width of the chasm, its wooden slats groaning as they swing over an abyss of shifting obsidian static. Below you, the 'fog' is actually a roiling sea of lost memories and discarded faces, all reaching upward with silent, desperate intent. As you reach the midpoint, the bridge seems to lengthen, trapping you in the center of a nightmare where the only way out is to face the entity that has been driving beside you the entire time.",
                                contains = sinkhole.entity)}
    sinkhole.exits["southeast"] = road_1_6
    sinkhole.exits["northeast"] = road_2_6
    sinkhole.exits["north"] = road_3_6
    sinkhole.exits["west"] = road_5_6

    road_1_2.locations = [overpass, radio_tower]
    road_1_4.locations = [overpass, gas_station]
    road_1_6.locations = [overpass, sinkhole]
    road_2_3.locations = [radio_tower, subdivision]
    road_2_6.locations = [radio_tower, sinkhole]
    road_3_5.locations = [subdivision, roadblock]
    road_3_6.locations = [subdivision, sinkhole]
    road_4_5.locations = [gas_station, roadblock]
    road_5_6.locations = [roadblock, sinkhole]

    sinkhole.locked = True

    return {
        "clues": {
            clue_1.name: clue_1,
            clue_2.name: clue_2,
            clue_3.name: clue_3,
            clue_4.name: clue_4,
            clue_5.name: clue_5,
            clue_6.name: clue_6
        },
        "entities": {
            entity_passenger.name: entity_passenger,
            entity_children.name: entity_children,
            entity_police_officer.name: entity_police_officer,
            entity_being.name: entity_being
        },
        "roads": {
            road_1_2.name: road_1_2,
            road_1_4.name: road_1_4,
            road_1_6.name: road_1_6,
            road_2_3.name: road_2_3,
            road_2_6.name: road_2_6,
            road_3_5.name: road_3_5,
            road_3_6.name: road_3_6,
            road_4_5.name: road_4_5,
            road_5_6.name: road_5_6
        },
        "locations": {
            overpass.name: overpass,
            radio_tower.name: radio_tower,
            subdivision.name: subdivision,
            gas_station.name: gas_station,
            roadblock.name: roadblock,
            sinkhole.name: sinkhole
        },
        "starting_location": roadblock
    }

if __name__ == "__main__":
    game = Game()
    game.start()

    # main game loop
    while True:
        game.check_game_over()
        game.check_game_win()
        road = game.show_location_menu()
        game.handle_player_choice(road)
