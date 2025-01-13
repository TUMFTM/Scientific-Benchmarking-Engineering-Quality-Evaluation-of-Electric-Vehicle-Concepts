"""
Description: This function has the task to create a class for the masses of the individual components of the vehicle
------------
Sources: None
------------
Input: None
------------
Output: Class element for the masses with all nested classes
------------

Implementation
[0] Define the class of masses
"""

# region [0] Define the class of masses
class Masses:
    def __init__(self):
        self.optional_extras = self.optional_extras()
        self.chassis = self.chassis()
        self.exterior = self.exterior()
        self.interior = self.interior()
        self.powertrain = self.powertrain()
        self.frame = self.frame()
        self.EE = self.EE()

    class optional_extras:
        def __init__(self):
            pass

    class chassis:
        def __init__(self):
            pass

    class exterior:
        def __init__(self):
            pass

    class interior:
        def __init__(self):
            pass

    class powertrain:
        def __init__(self):
            pass

    class frame:
        def __init__(self):
            pass

    class EE:
        def __init__(self):
            pass
# endregion
