"""
Description: This function has the task to create an object for the gearbox
             (actual state is that one object is sufficient for lay-shaft and planetary)
------------
Sources: None
------------
Input: All necessary elements to describe the electrical machine
------------
Output: Object element for a machine
------------

Implementation
[0] Define the class of gearboxes
"""

# region [0] Define the class of gearboxes
class Gearbox:
    def __init__(self):
        self.Input = self.Input()
        self.differential = self.differential()
        self.dimension_house = self.dimension_house()
        self.results = self.results()
        self.position = self.position()
        self.gears_12 = self.gears_12()
        self.gears_34 = self.gears_34()
        self.bearings_1 = self.bearings_1()
        self.bearings_2 = self.bearings_2()
        self.bearings_3 = self.bearings_3()
        self.forces = self.forces()
        self.factors = self.factors()
        self.shafts = self.shafts()
        self.error = self.error()
        self.driveshaft = self.driveshaft()
        self.masses = self.masses()
        # self.Parameters = Gearbox_Parameters
# endregion

    class Input:
        def __init__(self):
            pass

    class differential:
        def __init__(self):
            pass

    class dimension_house:
        def __init__(self):
            pass

    class results:
        def __init__(self):
            pass

    class position:
        def __init__(self):
            pass

    class gears_12:
        def __init__(self):
            pass

    class gears_34:
        def __init__(self):
            pass

    class bearings_1:
        def __init__(self):
            pass

    class bearings_2:
        def __init__(self):
            pass

    class bearings_3:
        def __init__(self):
            pass

    class forces:
        def __init__(self):
            pass

    class factors:
        def __init__(self):
            pass

    class shafts:
        def __init__(self):
            pass

    class error:
        def __init__(self):
            pass

    class driveshaft:
        def __init__(self):
            pass

    class masses:
        def __init__(self):
            pass
