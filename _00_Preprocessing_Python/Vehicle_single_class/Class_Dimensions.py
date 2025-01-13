"""
Description: This function has the task to create an object for the vehicle dimensions
------------
Sources: None
------------
Input: All necessary elements to describe the dimensions of a vehicle
------------
Output: Class element for the dimensions
------------

Implementation
[0] Define the class of dimensions
"""

# region [0] Define the class of dimensions
class Dimensions:
    def __init__(self):
        self.CX = self.CX()  # Definition of the length of components in X-direction
        self.CY = self.CY()  # Definition of the width of components in Y-direction
        self.CZ = self.CZ()  # Definition of the length of components in Z-direction
        self.EX = self.EX()  # Definition of the relative position in X-direction based on point of origin
        self.EY = self.EY()  # Definition of the relative position in Y-direction based on point of origin
        self.EZ = self.EZ()  # Definition of the relative position in Z-direction based on point of origin
        self.GX = self.GX()  # Definition of generell dimensions in X-direction
        self.GY = self.GY()  # Definition of generell dimensions in Y-direction
        self.GZ = self.GZ()  # Definition of generell dimensions in Z-direction

    class CX:
        def __init__(self):
            pass

    class CY:
        def __init__(self):
            pass

    class CZ:
        def __init__(self):
            pass

    class EX:
        def __init__(self):
            pass

    class EY:
        def __init__(self):
            pass

    class EZ:
        def __init__(self):
            pass

    class GX:
        def __init__(self):
            pass

    class GY:
        def __init__(self):
            pass

    class GZ:
        def __init__(self):
            pass
