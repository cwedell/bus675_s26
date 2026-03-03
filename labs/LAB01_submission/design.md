# Game Design Document

## Theme / Setting
Light sci-fi/eldritch horror

## Player's Goal
Get back to your real life before it's too late.

## Locations (4-6)
- The endless overpass. Very hard to find the offramp.
- The radio tower. Are these broadcasts... from me?
- The subdivision. I wouldn't move in if I were you.
- The gas station. You need fuel in your car, I'm sure of it.
- The sinkhole. Nice views from the bridge.
- The police blockade. Did they get there soon enough?

```
You start the game driving north, along the western highway. You find the police blockade first.


------------------------ Subdivision ------------------------------ Radio tower
|                             |                                          |
|                             |                                          |
|                             |                                          |
Police roadblock -------- Sinkhole ------------------------------------- |
|                                                                        |
|                                                                        |
|                                                                        |
Gas station -------------------- Endless overpass ------------------------
                                     (loops)

To exit, go to the endless overpass once the mystery is solved.

```

## Enemies (2-4 types)
- The passenger. Only talks when you can't hear him.
- The children. They just want to find a new friend.
- The police officer. To protect and serve.
- The being. Better not to think about it.

## Win Condition
Solve the mystery, then enter the overpass.

## Lose Condition
Run out of gas and be trapped forever.
Run out of mental stability and succumb to the being.

## Class Hierarchy
[Sketch your class design]

Character
- name/identity
- description/intro text

Player (inherits Character)
- mental stability
- collected clues

Entity (inherits Character)
- encounter options
- special phrases
- clue interactions
- consequences for player

Location
- connection to roads
- holds clues
- houses entities
- environment description

Clue
- player message
- alter entity encounters

Road
- connects locations
- environmental description
- random events
- spends fuel

Game
- tracks fuel
- tracks clue collections
- tracks entity encounters
- controls entity movement
- handles win/loss conditions

======

As I developed the game, the class structure changed significantly as needed to fit the game's architecture. Here is a class structure which reflects the actual game.

Player
- name, fuel, mental stability, clues, current location
- methods to add clues, change fuel, change stability
- methods to print current fuel and stability
- method to handle entity encounters
- method to distort the player's text as their mental stability decreases

Entity
- name, introductory (descriptive) text, options for encounter, clue required for special option

Passenger, Children, Police Officer, Being (all inherit from Entity)
- text for encounter options and specific clue required
- method to enact consequences to the player after handling the encounter (including 1 option for each entity that is a 50/50 outcome)

Area
- name, description, item found there, bool visited by player

Location
- name, description, clue found there, entity found there, 3 areas, list of road exits, bool clue found by player, bool entity encountered by player, bool location locked
- method to introduce the location
- method to allow player to choose which area to explore
- method to handle player discovering a clue (triggering a subsequent entity encounter)
- method to handle player encountering an entity (triggering a subsequent clue discovery)
- method to shuffle areas so the player cannot guess what will be found in each area

Clue
- name, description
- method to reveal its contents to the player after being found

Road
- name, description, fuel cost, locations connected
- method to introduce the road

Game
- player object, clue, entity, road, and location objects, and tracker for roads traveled
- method to begin the game (calling the world builder function), collect all game objects, and print introductory text and instructions to the player
- methods to change player fuel and stability - tracking their game-ending status
- method to generate an encounter with the Passenger entity (only found while traveling)
- methods to check if the game should end due to zero fuel or stability
- methods to end the game should either of those things occur
- method to check if the game should end due to the player winning
- method to end the game should that occur
- method to display the next locations to travel to (more accurately, which direction to drive on what road)
- method to take the player's input, travel them down that road (and handle whatever might occur during the trip), then change their location
- method to unlock the boss location
- method to trigger random road events

Outside of these classes, the following functions exist:

- slow_print(): to print descriptive text in a rolling fashion, encouraging the player to take in the environment and pay attention to the details
- is_key_pressed() and get_key(): to allow the player to skip the slow_print()
- build_world(): to create each game object with all of its details - this function hosts all of the names and descriptive text to avoid clogging each class definition

## Additional Notes
[Any other design decisions, ideas, or plans]
