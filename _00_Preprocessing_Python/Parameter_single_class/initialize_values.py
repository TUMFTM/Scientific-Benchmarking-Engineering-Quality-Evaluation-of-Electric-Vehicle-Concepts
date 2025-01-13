"""
Description: This function has the task to set the attributes of the parameters classes
             Therefore the dictionaries are split and every key will serve as new attribute
             with the corresponding value
------------
Sources: None
------------
Input:    self: Class which calls the initialize_elements method
          attr_first_class: Name of the added attribute
          values_element_one: Values of the added attribute (in form of a dictionary)
------------
Output: Class element with all the completed attributes
------------

Implementation
[0] Import all necessary Classes from the subfolder Parameter_single_class
[1] Fill attributes for parameter class
[2] Fill attributes for regression class
"""

# region [0] Import all necessary Classes and functions from the sub folders
# Import class
from .Regression_class import Regression
# endregion


# region [1] Fill attributes for parameter class
# Input:    self: Class which calls the initialize_elements method
#           attr_first_class: Name of the added attribute
#           values_first_class: Value of the added attribute (in the form of a dictionary)
#           insert_mode: Switch between insert modes list or value
def initialize_values(self, attr_first_class, values_first_class, insert_mode):

    # Get all the predefined attributes of the class (ergo the nested classes of the self class)
    get_attributes = getattr(self, attr_first_class)

    # Iterate through the entire input dictionary
    for attr_second_class in values_first_class:

        # Get the value of the desired attribute
        values_second_class = values_first_class[attr_second_class]

        # Check if attr_second_class is predefined as another nested class inside the self class
        if hasattr(get_attributes, attr_second_class):

            # Call the same method of the get_attributes class again
            get_attributes.initialize_elements(attr_second_class, values_second_class, insert_mode)
        else:
            # Data from db are array
            if insert_mode == 'list':
                attr_name = attr_second_class[:-3]
                attr_position = int(attr_second_class[-2])

                # Check, if the list has been created already
                all_attr = vars(get_attributes)
                if all_attr:    # There are lists in object
                    values_there = 0
                    for x, y in all_attr.items():    # go through all items
                        if attr_name == x:           # find the right one
                            values_there = 1
                            if attr_position > len(y):
                                y.append(values_second_class)
                            else:
                                y[attr_position - 1] = values_second_class
                    if values_there == 0:
                        # Create the list attribute
                        ls = [None] * attr_position     # Creates a list with the length of the attribute position
                        ls[attr_position - 1] = values_second_class
                        setattr(get_attributes, attr_name, ls)

                else:   # No attributes in the object
                    # Create the list
                    ls = [None] * attr_position  # Creates a list with the length of the attribute position
                    ls[attr_position - 1] = values_second_class
                    setattr(get_attributes, attr_name, ls)
            else:
                # Attr_second_class is not a predefined attribute. Create this one in the self class
                try:
                    setattr(get_attributes, attr_second_class, values_second_class)
                except AttributeError:
                    print(attr_second_class)
                    print(get_attributes)
# endregion


# region [2] Fill attributes for the regression class
# Input:    self: Class which calls the initialize_elements method
#           attr_first_class: Name of the added attribute
#           values_first_class: Value of the added attribute (in the form of a dictionary)
def initialize_values_regr(self, attr_first_class, values_first_class):

    # Get all the predefined attributes of the class (ergo the nested classes of the self class)
    get_attributes = getattr(self, attr_first_class)

    # Iterate through the entire input dictionary
    for attr_second_class in values_first_class:

        # Check if this regression is divided into different specifications
        # (for example mass regressions are sometimes divided into alu and steel regressions)
        if hasattr(get_attributes, attr_second_class):
            # Get the values of the subdivided regression
            values_second_class = values_first_class[attr_second_class]
            # Execute the same function again and assign the regression parameters
            get_attributes.initialize_elements(attr_second_class, values_second_class)
        else:
            # Insert the regression object in the attr_second_class
            # Initialize an empty regression class
            regression = Regression()

            # Get the values of the desired attribute
            # Ergo all nine regression parameters as 'coefficients', 'limits', etc..
            values_second_class = values_first_class[attr_second_class]

            # Iterate through all the regression parameters
            for attr_third_class in values_second_class:

                # Get the value of the desired regression parameter
                value_third_class = values_second_class[attr_third_class]

                # Add this parameter to the regression class
                setattr(regression, attr_third_class, value_third_class)

                try:
                    # Check if there are attributes already
                    lower_class = getattr(get_attributes, attr_second_class)

                    if type(lower_class) != type(Regression()):
                        # Add the entire Regression class to the get attributes class
                        setattr(get_attributes, attr_second_class, regression)
                    else:  # There already is one Regression object
                        # Store dict as second attribute of the Regression object
                        setattr(lower_class, attr_third_class, value_third_class)

                except AttributeError:
                    # No attributes in object -> set first one
                    setattr(get_attributes, attr_second_class, regression)

# endregion
