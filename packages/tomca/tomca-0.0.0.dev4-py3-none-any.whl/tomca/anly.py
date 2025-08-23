"""
functions which \b analyze simulation data  
"""

import os
import pandas as pd
import json
from json import dumps, loads
from tabulate import tabulate
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from typing import Any, Optional

def flatten_dict(nestedDict: dict, parentKey="", sepChar="_"):
    """
    Recursively flattens a nested dictionary with possible lists into a single-layer dictionary.

    Args:
    - nestedDict (dict): A nested dictionary or list object to flatten.
    - parentKey (str, optional): Name(s) of key(s) above current key level. Defaults to "".
    - sepChar (str, optional): Separation character to put between levels. Defaults to "_".

    Returns:
    - dict: A flattened dictionary with all keys of original dictionary/lists.
    """
    
    flattened_dict = {}
    for key, value in nestedDict.items():
        new_key = f"{parentKey}{sepChar}{key}" if parentKey else key
        if isinstance(value, dict):
            flattened_dict.update(flatten_dict(value, new_key, sepChar=sepChar))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                list_key = f"{new_key}{sepChar}{i}"
                if isinstance(item, dict) or isinstance(item, list):
                    flattened_dict.update(
                        flatten_dict({str(i): item}, list_key, sepChar=sepChar)
                    )
                else:
                    flattened_dict[list_key] = item
        else:
            flattened_dict[new_key] = value
    return flattened_dict

def create_expt_df(experimentDirectory: str):
    """
    Converts JSON files in the specified directory to a pandas DataFrame with flattened dict keys as columns and simulation states as rows.

    Parameters:
    experimentDirectory (str): The path to the directory containing the JSON files.

    Returns:
    pd.DataFrame: A pandas DataFrame containing the flattened JSON data.
    """
    # Initialize an empty list to store the dictionaries
    data = []

    # Iterate over all the files in the experiment directory
    for folder in os.listdir(experimentDirectory):
        folder_path = os.path.join(experimentDirectory, folder)
        if os.path.isdir(folder_path):
            # Iterate over all the JSON files in the folder
            for file in os.listdir(folder_path):
                if file.endswith("_jcfg.json"):
                    file_path = os.path.join(folder_path, file)
                    # Open the JSON file and load the data
                    with open(file_path, "r") as f:
                        json_data = json.load(f)

                        json_data = flatten_dict(json_data)

                    # Append the dictionary to the list
                    data.append(json_data)

    # Convert the list of dictionaries to a pandas DataFrame
    df = pd.json_normalize(data)

    # Identify columns that contain lists of dictionaries
    listDictColumns = df.applymap(
        lambda x: isinstance(x, list) and all(isinstance(i, dict) for i in x)
    ).any()

    # For each column that contains a list of dictionaries, create a new DataFrame and concatenate it with the original DataFrame
    for column in listDictColumns.index[listDictColumns]:
        # Create a new DataFrame from the list of dictionaries
        temp_df = pd.concat(
            [
                pd.json_normalize(df[column].apply(lambda x: x[i]))
                for i in range(len(df[column][0]))
            ],
            axis=1,
        )
        # Concatenate the new DataFrame with the original DataFrame
        df = pd.concat([df.drop(column, axis=1), temp_df], axis=1)

    return df

def print_ignored_keys_table(ignoredKeys, numColumns=3):
    """
    Prints a table of ignored variable properties to the terminal

    Parameters:
    - ignoredKeys (list): A list of ignored variable properties.
    - numColumns (int, optional): The number of columns to display in the table. Defaults to 3.

    Returns:
    - None: This function does not return anything.
    """
    print('Ignored variable Properties:')
    num_keys = len(ignoredKeys)
    keys_per_column = (num_keys + numColumns - 1) // numColumns  # Ceiling division

    # Create a list of columns, each containing a subset of ignored keys
    columns = [ignoredKeys[i:i + keys_per_column] for i in range(0, num_keys, keys_per_column)]

    # Transpose the list of columns to print keys in a row-wise manner
    transposed_columns = list(map(list, zip(*columns)))

    # Create a table from the transposed columns
    table = [keys for keys in transposed_columns]
    print(tabulate(table, headers=[f"Column {i + 1}" for i in range(numColumns)], tablefmt="grid"))

def find_changing_keys(df, keysToKeep=None, printTable=True):
    """
    Identify columns in a DataFrame with more than one unique value and optionally keep specific keys. 

    Args:
        df (pandas.DataFrame): The DataFrame to analyze.z
        keysToKeep (list, optional): List of keys to keep in the output. If None, all keys are kept. Defaults to None.
        printTable (bool, optional): If True, print a table summarizing the unique values. Defaults to True.

    Returns:
        list: A list containing a dictionary of unique values for the filtered columns and a list of ignored keys.
    """
    
    if keysToKeep is None:
        keysToKeep = df.columns.tolist()

    # Use the nunique() function to count the number of unique values in each column
    uniqueCounts = df.nunique()

    # Select only the columns that have more than one unique value and are in the keysToKeep list
    filteredColumns = [
        col
        for col in df.columns
        if uniqueCounts[col] > 1 and (not keysToKeep or col in keysToKeep)
    ]

    # Create a new DataFrame with only the selected columns
    filtered_df = df[filteredColumns]

    # Initialize a dictionary to store column names and their unique values
    unique_values_dict = {}

    # Populate the dictionary with column names and unique values
    for col in filteredColumns:
        unique_values_dict[col] = filtered_df[col].unique().tolist()

    # Print the table with column names and unique values
    if printTable:
        print('Compared Variable Properties')
        table_rows = [(i + 1, col, unique_values_dict[col]) for i, col in enumerate(filteredColumns)]
        print(
            tabulate(
                table_rows, headers=["#", "Column Name", "Unique Values"], tablefmt="grid"
            )
        )

    # Identify ignored keys in columns with more than one unique value
    ignoredKeys = [
        col
        for col in df.columns
        if col not in filteredColumns and uniqueCounts[col] > 1
    ]
    if printTable:
        print_ignored_keys_table(ignoredKeys)
    
    return unique_values_dict, ignoredKeys

def filter_by_value(filtered_df: pd.DataFrame, column_name: str, value: Any) -> Optional[pd.DataFrame]:
    """
    Filters a pandas DataFrame by a specified column name and value.

    Parameters:
    - filtered_df (pd.DataFrame): The DataFrame to filter.
    - column_name (str): The name of the column to filter by.
    - value (Any): The value to filter by.

    Returns:
    - Optional[pd.DataFrame]: A new DataFrame containing only the rows that match the specified value in the specified column.
    If the specified column name is not found in the input DataFrame, returns None.
    """
    if column_name in filtered_df.columns:
        matching_rows = filtered_df[filtered_df[column_name] == value].copy()
        return matching_rows
    else:
        print(f"Column '{column_name}' not found in the DataFrame.")
        return None
    
def build_pkl_path(jcfg_state: dict) -> str:
    """
    Builds a path to a simulated jcfg file based on the specified state.

    Parameters:
    - jcfg_state (dict): The flattened jcfg dict of the state containing the experiment path, time, and state name.

    Returns:
    - str: A string representing the path to the simulated jcfg file.
    """
    pklPath = (jcfg_state.Expt_pathState+ "\\"+ jcfg_state.Expt_time+ jcfg_state.Expt_stateName+ "_simulated_jcfg.pkl")
    return pklPath

def gaussian(x: np.ndarray, A: float, mu: float, sigma: float, offset: float) -> np.ndarray:
    """
    Returns the value of a Gaussian function at the specified x values.

    Parameters:
    - x (np.ndarray): An array of x values.
    - A (float): The amplitude of the Gaussian function.
    - mu (float): The mean of the Gaussian function.
    - sigma (float): The standard deviation of the Gaussian function.
    - offset (float): The offset of the Gaussian function.

    Returns:
    - np.ndarray: An array of y values representing the Gaussian function evaluated at the specified x values.
    """
    return A * np.exp(-(x - mu)**2 / (2 * sigma**2)) + offset

def fit_gaussian_dip(xSection: np.ndarray) -> list[np.ndarray, np.ndarray, float, float, float, float]:
    """
    Fits a Gaussian function to a xSection and returns the fitted parameters of a gaussian on a background.

    Parameters:
    - xSection (np.ndarray): An array of xSection values.

    Returns:
    - list[np.ndarray, np.ndarray, float, float, float, float]: A tuple containing the x values, fitted curve, amplitude,
    mean, standard deviation, and offset of the Gaussian function.
    """
    x = np.arange(len(xSection))

    # Initial guess for parameters
    A_guess = -np.max(xSection) + np.min(xSection)
    mu_guess = len(xSection)/2
    sigma_guess = len(xSection) / 10
    offset_guess = np.min(xSection)

    initial_guess = [A_guess, mu_guess, sigma_guess, offset_guess]

    # Fit the Gaussian function to the xSection
    params, covariance = curve_fit(gaussian, x, xSection, p0=initial_guess)

    # Extract fitted parameters
    A_fit, mu_fit, sigma_fit, offset_fit = params

    # Generate the fitted curve
    fitted_curve = gaussian(x, A_fit, mu_fit, sigma_fit, offset_fit)

    return x, fitted_curve, A_fit, mu_fit, sigma_fit, offset_fit


def image_detectors(jcfg, coordinates, radius, function='mean'):
    """
    Analyzes an image to calculate average pixel values within specified regions, 
    using either circular or square filters based on the detector shape defined in the configuration.

    Parameters:
    - jcfg (dict): A configuration dictionary containing:
        - 'res' key with a subkey 'IM' for the image to be analyzed.
        - 'Optode' key with a subkey 'imgDetectors' that may contain a 'Shape' key indicating the shape of the detector ('square' for square, any other value defaults to circular).
        - 'Expt' key with a subkey 'verb' indicating the verbosity level (>=2 enables plotting).
    - coordinates (list of tuples): A list of (x, y) tuples indicating the center points of regions to analyze.
    - radius (int): The radius of the regions to analyze. For square detectors, this defines half the side length of the square.

    Returns:
    - jcfg (dict): The input configuration dictionary updated with a new key under 'res' -> 'imgDetectors' -> 'Avg', containing a list of average pixel values for each region.

    This function first checks the shape of the detectors specified in the configuration. 
    If 'square', it uses convolution to calculate averages within square regions around each coordinate.
    Otherwise, it calculates averages within circular regions.
    The function optionally plots the image, the regions of interest, and their centers if the verbosity level is set accordingly.
    Finally, it updates the input configuration dictionary with the calculated averages and returns it.
    """
    import numpy as np
    import scipy.ndimage as ndimage
    import matplotlib.pyplot as plt
    from src import tomca
    from enum import Enum
    
    # Create an empty array to store the average values
    averages = []
    image = jcfg['res']['IM']

    # Possible shapes that a detector can be
    class DetectorShapes(Enum):
        CIRCLE = 0
        SQUARE = 1

    detector_shape = DetectorShapes.CIRCLE.value
    
    if 'Shape' in jcfg['Optode']['imgDetectors']:
        detector_shape = int(jcfg['Optode']['imgDetectors']['Shape'] == 'square')
    if 'math_function' in jcfg['Optode']['imgDetectors']:
        function = jcfg['Optode']['imgDetectors']['math_function']

    # Create a circular filter with the given radius
    def circular_filter_average(image_data, radius, center_x, center_y, function = 'mean'):
        y_coords, x_coords = np.ogrid[:image.shape[0], :image.shape[1]]
        mask = (x_coords - center_x) ** 2 + (y_coords - center_y) ** 2 <= radius ** 2

        # Calculate the average pixel value within the circular region
        if function == 'mean':
            average_value = np.mean(image_data[mask])
        if function == 'sum':
            average_value = np.sum(image_data[mask])

        return average_value

    # Create a square filter with the given radius using convolution
    def square_filter_average(image_data, radius):
        # Calculate the size of the square kernel
        size = 2 * radius + 1

        # Define the square kernel
        kernel = np.ones((size, size)) / (size ** 2)

        # Convolve the image with the square kernel
        convolved_image = ndimage.convolve(image_data, kernel, mode='constant', cval=0.0)

        # # Get the average value at the specified coordinate
        # average_value = convolved_image[center_y, center_x]

        return convolved_image

    if jcfg['Expt']['verb'] >= 2:

        fig_imgDetectors = plt.figure()
        # plt.imshow(image)

    if detector_shape == DetectorShapes.SQUARE.value:
        convolvedImage = square_filter_average(image, int(radius))
        if jcfg['Expt']['verb'] >= 2:
            plt.imshow(convolvedImage)
        for coord in coordinates:
            x, y = map(int, coord)
            if jcfg['Expt']['verb'] >= 2:
                plt.scatter(x, y, s=radius, color='k', alpha=0.5, edgecolors='k')
            # Append the average value to the averages array
            averages.append(convolvedImage[y, x])

    elif detector_shape == DetectorShapes.CIRCLE.value:
        if jcfg['Expt']['verb'] >= 2:
            
            from matplotlib.patches import Circle
            fig, ax = plt.subplots()  # Create a figure and an axes
            # plt.imshow(image)
            
        # Iterate over the coordinates
        for coord in coordinates:
            # Get the x and y coordinates
            x = coord[0]
            y = coord[1] 

            # Check if the coordinates are within the image boundaries
            if 0 <= x < image.shape[1] and 0 <= y < image.shape[0]:
                # Get the average value at the coordinate math_function
                average = circular_filter_average(image, radius, x, y, function=function)
                if jcfg['Expt']['verb'] >= 2:
                    circle = Circle((x, y), radius, color='k', alpha=0.5, edgecolor='k')  # Create a circle
                    ax.set_aspect('equal', 'box')  # Set aspect ratio to equal
                    ax.add_patch(circle)  # Add the circle to the axes
                # Append the average value to the averages array
                averages.append(average)

    if jcfg['Expt']['verb'] >= 2:
        fig_imgDetectors.suptitle('Virtual detector locations')
        plt.xlabel('X-axis voxel')
        plt.ylabel('Y-axis voxel')
        tomca.writ.fig(jcfg, fig_imgDetectors, 'CCD_imgDetectors')

    if "imgDetectors" not in jcfg['res']:
        jcfg['res']['imgDetectors'] = {}
    jcfg['res']['imgDetectors']['Avg'] = averages
    # Return the averages array
    return jcfg

def img_detectors_donut(jcfg):
    """
    Calculates the average intensity of an image within a donut-shaped region for every possible inner radius value.
    
    Parameters:
    - image_data: A grayscale image (numpy array)
    - source_x: The x-coordinate of the center of the donut
    - source_y: The y-coordinate of the center of the donut
    - donut_width: The width of the donut in mm
    
    Returns:
    - A list of average intensities for each inner radius
    """
    
    image_data=jcfg['res']['IM']
    source_x=jcfg["Optode"]["Source"]["Pos"][0]
    source_y=jcfg["Optode"]["Source"]["Pos"][1]
    donut_widths=[]
    for width in jcfg["Optode"]["imgDetectors"]["donut_widths"]:
        donut_widths.append(width/jcfg["Domain"]["LengthUnit"])  # Converting donut width into vx
    
    # Calculate the maximum radius from the source point to the edge of the image
    max_radius = max(source_x, source_y, image_data.shape[0] - source_x, image_data.shape[1] - source_y)
    
    average_intensities = []
    inner_rads=[]
    for donut_width in donut_widths:
        # Initialize a list to store the average intensities for each inner radius
        intensities_i=[]
        inner_rads_i=[]
        list_inner_rads = []
        if "pitches" in jcfg["Optode"]["imgDetectors"]:
            list_inner_rads = jcfg["Optode"]["imgDetectors"]["pitches"]
        else:
            list_inner_rads = range(0, int(max_radius - donut_width)) 
        # Iterate over each possible inner radius
        for inner_radius in list_inner_rads:
            outer_radius = inner_radius + donut_width
            y_coords, x_coords = np.ogrid[:image_data.shape[0], :image_data.shape[1]]
            mask = (x_coords - source_x)**2 + (y_coords - source_y)**2 >= inner_radius**2
            mask &= (x_coords - source_x)**2 + (y_coords - source_y)**2 <= outer_radius**2
            
            # Calculate the average pixel value within the donut region
            average_value = np.mean(image_data[mask])
            
            # Append the average value to the list
            intensities_i.append(average_value)
            inner_rads_i.append(inner_radius)
        average_intensities.append(intensities_i)
        inner_rads.append(inner_rads_i)

    
    jcfg['res']['imgDetectors']={}
    jcfg["res"]["imgDetectors"]["Avg"]=average_intensities
    inner_rads_mm=[]
    for inner_radvoxes in inner_rads[0]:
        inner_rads_mm.append(inner_radvoxes*jcfg["Domain"]["LengthUnit"])
    jcfg["res"]["imgDetectors"]["innerRads"]=inner_rads_mm
    
    if jcfg['Expt']['verb']>2:
        plt.figure()
        for ii, avg in enumerate(jcfg['res']['imgDetectors']['Avg']): 
            plt.plot(np.arange(0,len(avg)*jcfg["Domain"]["LengthUnit"],jcfg["Domain"]["LengthUnit"]),np.log(avg), label=str(donut_widths[ii]*jcfg["Domain"]["LengthUnit"]))
        plt.xlabel('Inner Radius (mm)')
        plt.ylabel('Average Detected Intensity')
        plt.title('Average Detected Photon Intensity vs. Inner Radius for Donut-Shaped Regions')
        plt.legend(title='Donut width, mm')
        plt.show()
    return jcfg
