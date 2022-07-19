from pathlib import Path

import cv2
from matplotlib import pyplot as plt

from script_to_pipeline import pipeline


@pipeline(dependencies=["opencv-python==4.5.5.64", "matplotlib==3.5.1"])
def main():
    """Walk /pfs/images and run edge detection on every image file."""
    image_dir = Path("/pfs/images")
    output_dir = Path("/pfs/out")
    for image_file in filter(Path.is_file, image_dir.glob("**/*")):
        output_file = output_dir.joinpath(
            image_file.relative_to(image_dir)
        ).with_suffix(".png")
        print(f"{image_file} -> {output_file}")

        image = cv2.imread(str(image_file))
        edges = cv2.Canny(image, 100, 200)
        plt.imsave(str(output_file), edges, cmap="gray")
