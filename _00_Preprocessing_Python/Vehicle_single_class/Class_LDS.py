"""
Description: This function has the task to create an class for the LDS (longitudinal dynamics simulation)
------------
Sources: None
------------
Input: All necessary elements to describe the vehicle longitudinal dynamics characteristics
------------
Output: Class element for the LDS
------------

Implementation
[0] Define the class of LDS
"""


# region [0] Define the class of LDS
class LDS:
    def __init__(self):
        self.sim_cons = self.sim_cons()
        self.parameters = self.parameters()
        self.settings = self.settings()
        self.sim_acc = self.sim_acc()
        self.sim_speed = self.sim_speed()
        self.sim_range = self.sim_range()
    class sim_cons:
        def __init__(self):
            self.resistance = self.resistance()

        class resistance:
            def __init__(self):
                pass

    class parameters:
        def __init__(self):
            pass
    class settings:
        def __init__(self):
            pass
    class sim_acc:
        def __init__(self):
            self.resistance = self.resistance()
        class resistance:
            def __init__(self):
                pass
    class sim_speed:
        def __init__(self):
            pass

    class sim_range:
        def __init__(self):
            self.resistance = self.resistance()

        class resistance:
            def __init__(self):
                pass
# endregion
