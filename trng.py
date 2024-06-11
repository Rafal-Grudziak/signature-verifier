import os
import time

import cv2
import numpy as np
from matplotlib import pyplot as plt


def generate_random_bits_from_images(image_folder, num_needed):
    # List all image files in the folder that are of specific formats
    image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if
                   f.endswith(('png', 'jpg', 'jpeg'))]
    final_list = []  # List to hold all generated bits
    num_so_far = 0  # Counter to track the number of bits generated so far

    # Record the start time to calculate the total execution time later
    start_time = time.time()

    # Loop over each image file
    for i, image_file in enumerate(image_files):
        # Stop if the required number of bits have been collected
        if num_so_far >= num_needed:
            break

        # Read the image in grayscale
        image = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
        # If the image couldn't be read, skip it
        if image is None:
            continue

        # Convert the image from a matrix to a one-dimensional array
        image = image.flatten()

        # Filter out pixel values within the specified new brightness range [3, 252]
        valid_pixels = image[(image >= 3) & (image <= 252)]

        # Extract the least significant bit of each valid pixel value
        sublist = np.bitwise_and(valid_pixels, 1)

        # If the index of the image is even, flip the bits to add more randomness
        if i % 2 == 0:
            sublist = np.bitwise_xor(sublist, 1)

        # Extend the final list with the new bits
        final_list.extend(sublist.tolist())
        # Update the total count of bits collected
        num_so_far += len(sublist)

    # Trim the list to the exact number of needed bits
    final_list = final_list[:num_needed]

    # Calculate the total time taken to generate the bits
    end_time = time.time()
    print(f"Total Time: {end_time - start_time} seconds")

    # Return the final list of bits
    return final_list


def convert_bits_to_decimal(bits, chunk_size=8):
    # Convert the list of bits into a list of decimal numbers
    decimals = []
    # Process each chunk of 8 bits
    for i in range(0, len(bits), chunk_size):
        # Get a slice of the list that represents one byte (8 bits)
        chunk = bits[i:i + chunk_size]
        # Break the loop if the last chunk is not a full byte
        if len(chunk) < chunk_size:
            break
        # Convert the binary number in chunk to a decimal number
        decimal = int(''.join(map(str, chunk)), 2)
        # Append the decimal number to the list
        decimals.append(decimal)
    return decimals


def calculate_entropy(values):
    # Calculate the Shannon entropy of a list of values
    # Find unique values and their frequencies
    value, counts = np.unique(values, return_counts=True)
    # Calculate the probabilities of each unique value
    probabilities = counts / counts.sum()
    # Calculate the entropy using Shannon's formula
    entropy = -np.sum(probabilities * np.log2(probabilities))
    return entropy


def plot_histogram(values):
    # Plot a histogram of values
    plt.figure()
    # Plot histogram with bins for each integer from 0 to 255 and normalize it to show probabilities
    plt.hist(values, bins=range(256), edgecolor='k', alpha=0.7, density=True)
    plt.title('Histogram of Decimal Values Derived from Image Bits')
    plt.xlabel('Decimal Value')
    plt.ylabel('Probability')
    plt.grid(True)
    plt.show()


def main():
    # Define the folder containing images
    image_folder = 'photo_dump'
    # Specify the number of random bits needed
    num_needed = 100000
    #Generate random bits from images
    final_bits = generate_random_bits_from_images(image_folder, num_needed)
    print(final_bits)
    # Convert bits to decimal values
    decimal_values = convert_bits_to_decimal(final_bits)
    # Calculate the entropy of the decimal values
    entropy = calculate_entropy(decimal_values)
    print(f"Entropy of the generated values: {entropy}")
    # Plot a histogram of the decimal values
    plot_histogram(decimal_values)


# main()
