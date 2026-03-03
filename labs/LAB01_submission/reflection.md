# Reflection: OOP Design Decisions

Write 2-3 paragraphs reflecting on your object-oriented design. Some questions to consider:

- Why did you structure your classes the way you did?
- What inheritance relationships did you use and why?
- What was challenging about managing multiple interacting objects?
- If you had more time, what would you refactor or add?
- How does this experience connect to working with OOP in analytics/ML codebases?

---

My classes were originally structured with a bit more inheritance - I had a Character class that defined both Player and Entity. However, as development went on, the Player and Entity became so distinct that eventually the Character class became totally unnecessary since there was nothing it could share. I ended up leveraging inheritance from the Entity to its four types, although I definitely could have implemented it better - making the options list some kind of dictionary so that each entity's encounter didn't need to be hardcoded within its own class.

Oftentimes I found myself struggling with the scope of particular objects, especially if there were methods that I needed to call within those objects that referenced something outside. For example, the text distortion method lives in the Player class, since it needs to know the Player's stability to work. Yet, it is called by the slow_print function, which lives outside of everything, since it's used all over the place. So, if I needed the text to be distorted, I had to pass the Player object to the slow_print function. A little janky, but at least it's somewhat straightforward to my eyes. Having the Game object possess all the instances of every other object in the game helped with that as well, since I could do anything with the player by simply calling self.player.thing().

With more time, I would probably restructure the Entity mechanics and interactions, and find some more things that could be shared within the base class. The way it's written currently, the four Entity types could practically be their own independent classes, which kind of defeats the purpose. Making them more similar to the Location class, where there was a base setup and anything different is simply overridden when instantiated, is probably a better solution.
