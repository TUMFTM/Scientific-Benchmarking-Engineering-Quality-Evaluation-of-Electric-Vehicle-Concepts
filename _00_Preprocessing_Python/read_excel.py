"""
Description: This function is used to read the Excel file. The variables name from the first column of the sheet are
             combined with the values in the corresponding column of the analyzed vehicle
------------
Sources:  None
------------
Input: data_excel: Dataframe where the variable names are stored in the first column.
                   The corresponding values are stored in the second column
       main_class: Corresponding class element (necessary as first class element
       basisname_struct: Name of the main_class as string
------------
Output: Filled class object with all the variables from the Excel sheet
------------
Implementation
region [0] Import modules, classes and functions
region [1] Find the equivalent nested class inside the main_class:
region [2]: Get the desired value of the variable
region [3] Check if the variable is part of an array or dictionary
region [4]: Generate the dictionary
region [5]: Generate the array
region [6] Set the attribute
"""


# region [0] Import modules, classes and functions
# import modules
import numpy as np
# endregion
def read_excel(data_excel, main_class, basisname_struct):

    # Get the size of all the rows in the Excel sheet.
    size_excel = data_excel.shape[0]
    # Iterate through every row of the Excel sheet to get all the necessary variables.
    for i in range(0, size_excel):
        # Determine the entry of the cells in the first column of the Excel Sheet
        variable_path = data_excel.iloc[i, 0]
        # Check if this cell is filled with a valid entry (nan (float variable) means the cell is empty)
        if isinstance(variable_path, str):
            # Split up the directory of the variable after each dot (Creates a new list entry after each dot)
            variable_path_split = variable_path.split('.')
            # The actual name of the variable is stored in the last entry of the list
            variable_name = variable_path_split[-1]

            # Check if the first entry of the list is equal to the basisname_struct-string
            # --> To differentiate between vehicle and parameters class
            if variable_path_split[0] == basisname_struct:
                # region [1] Find the equivalent nested class inside the main_class:
                # Define the main_class as reference to check for its attributes
                get_attr = main_class
                counting_variable = 1
                # Check if the main_class has an attribute equal to the second entry of the variables list
                check_attr = hasattr(main_class, variable_path_split[counting_variable])

                # Iterate through the variables list and find the corresponding class directory
                # until no attribute with the same name is found
                while check_attr:
                    # Extract the next deeper attribute of the class based on the next element of the variables list
                    get_attr = getattr(get_attr, variable_path_split[counting_variable])
                    # if not isinstance(get_attr_new, dict):
                    # get_attr = get_attr_new
                    counting_variable += 1

                    # Check if this deeper attribute exists inside the class
                    if len(variable_path_split)-1 > counting_variable:
                        check_attr = hasattr(get_attr, variable_path_split[counting_variable])
                    else:
                        check_attr = False
                # endregion

                # region [2]: Get the desired value of the variable
                # Value of the variable is stored in the second column of the extract_vehicle-variable
                value = data_excel.iloc[i, 1]
                # If in Excel is an '-' inside the cell the desired value should be nan for the setattr function
                if value == '-':
                    value = np.nan
                # endregion

                # region [3] Check if the variable is part of an array or dictionary
                in_val = ['[', ']']
                modus = 'none'
                extract_info = 0

                # Check if inside the variable name is an open bracket
                if all(x in variable_name for x in in_val):
                    # Find the index of the opening and closing brackets
                    start = variable_name.index('[')
                    end = variable_name.index(']')

                    # Get the information inside the squared brackets.
                    # Necessary for the determination whether the variable shall be an array or a dictionary
                    extract_info = variable_name[start + 1:end]

                    # Remove the square brackets from the variable name
                    variable_name = variable_name[0:start]
                    variable_path_split[-1] = variable_name

                    # If the extracted string can be converted into an integer the variable shall be an array.
                    # If there occurs an error (ergo no conversion into an integer is possible) it`s a dictionary
                    try:
                        extract_info = int(extract_info)
                        modus = 'array'
                    except ValueError:
                        modus = 'dictionary'
                # endregion

                # region [4]: Generate the dictionary
                if modus == 'dictionary':
                    # The key is the information written in the squared brackets
                    key = extract_info

                    has_attr_dict = hasattr(get_attr, variable_name)
                    # Check if this dictionary already exists
                    if has_attr_dict:   # Dictionary is already stored in the main class
                        # Get the already stored dictionary
                        get_dict = getattr(get_attr, variable_path_split[counting_variable])
                        # Add new entry with new key
                        get_dict[key] = value
                        value = get_dict
                    else:   # Dictionary is not created yet
                        value = {key: value}
                # endregion

                # region [5]: Generate the array
                elif modus == 'array':
                    # check if the array has already been created
                    has_attr_array = hasattr(get_attr, variable_name)

                    if has_attr_array:  # Array is already stored inside the main class

                        # Get the already stored array
                        get_array = getattr(get_attr, variable_path_split[counting_variable])

                        if len(get_array) >= extract_info:  # Position inside the array is already reserved
                            get_array[extract_info-1] = value
                            value = get_array

                        elif len(get_array) == extract_info - 1:    # Position is not defined yet
                            value = np.append(get_array, value)
                        else:   # There is no ascending order of the indexing
                            raise ValueError('This is not possible. Please ensure, that the elements of an array \
                                              are defined in ascending order') from None
                    else:   # Array is not created yet
                        if extract_info == 1:
                            # Create the array with the value inside
                            value = np.array([value], dtype=float)
                        else:   # There is no ascending order of the indexing
                            raise ValueError('This is not possible. Please ensure, that the elements of an array \
                                              are defined in ascending order') from None
                # endregion

                # region [6] Set the attribute
                setattr(get_attr, variable_path_split[counting_variable], value)
                # endregion
    return main_class