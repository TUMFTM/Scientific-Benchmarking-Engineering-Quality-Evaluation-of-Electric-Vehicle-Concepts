"""
Description: This function has the task to create an object for the performance values of the vehicle
------------
Sources: None
------------
Input: All performance values from the real vehicles (given by the Excel Sheet)
------------
Output: Class element for the performance values
------------

Implementation
[0] Define the class of the performance
"""

# region [0] Define the class of the performance

class Performance:
    def __init__(self):
        self.charging_time = self.charging_time()

    class charging_time:
        def __init__(self):
            pass
