"""
Binarizer component
"""

from typing import Literal, get_args

import cv2
import numpy as np
from numpy.typing import NDArray

from otary.image.base import BaseImage

from otary.image.components.transformer.components.binarizer.utils.thresholding import (
    threshold_niblack_like,
)

BinarizationMethods = Literal[
    "sauvola", "niblack", "nick", "wolf", "adaptative", "otsu"
]


class BinarizerImage:
    """BinarizerImage class"""

    def __init__(self, base: BaseImage) -> None:
        self.base = base

    def threshold_simple(self, thresh: int) -> None:
        """Compute the image thesholded by a single value T.
        All pixels with value v <= T are turned black and those with value v > T are
        turned white.

        Args:
            thresh (int): value to separate the black from the white pixels.
        """
        self.base.as_grayscale()
        self.base.asarray = np.array((self.base.asarray > thresh) * 255, dtype=np.uint8)

    def threshold_adaptative(self) -> None:
        """Apply adaptive thresholding.
        This is a local thresholding method that computes the threshold for a pixel
        based on a small region around it.

        A gaussian blur is applied before for better thresholding results.
        See why in https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html.

        As the input image must be a grayscale before applying any thresholding
        methods we convert the image to grayscale.
        """
        self.base.as_grayscale()
        binary = cv2.adaptiveThreshold(
            self.base.asarray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2,
        )
        self.base.asarray = binary

    def threshold_otsu(self) -> None:
        """Apply Ostu thresholding.
        This is a global thresholding method that automatically determines
        an optimal threshold value from the image histogram.

        Comes from the article "A Threshold Selection Method from Gray-Level
        Histograms" by Nobuyuki Otsu, 31 January 1979. Link to article:
        https://ieeexplore.ieee.org/document/4310076

        Consider applying a gaussian blur before for better thresholding results.
        See why in https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html.

        As the input image must be a grayscale before applying any thresholding
        methods we convert the image to grayscale.
        """
        self.base.as_grayscale()
        _, img_thresholded = cv2.threshold(
            self.base.asarray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        self.base.asarray = img_thresholded

    def threshold_sauvola(
        self, window_size: int = 15, k: float = 0.2, r: float = 128.0
    ) -> None:
        """Apply Sauvola thresholding.
        This is a local thresholding method that computes the threshold for a pixel
        based on a small region around it.

        Comes from the article "Adaptive Document Image Binarization" by
        J. Sauvola and M. Pietikainen. Link to article:
        https://www.researchgate.net/publication/3710586_Adaptive_Document_Binarization

        See https://scikit-image.org/docs/stable/auto_examples/segmentation/\
                plot_niblack_sauvola.html.

        As the input image must be a grayscale before applying any thresholding
        methods we convert the image to grayscale.

        Args:
            window_size (int, optional): sauvola window size to apply on the
                image. Defaults to 15.
            k (float, optional): sauvola k factor to apply to regulate the impact
                of the std. Defaults to 0.2.
            r (float, optional): sauvola r value. Defaults to 128.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_niblack_like(
            img=self.base.asarray, method="sauvola", window_size=window_size, k=k, r=r
        )[1]

    def threshold_niblack(self, window_size: int = 15, k: float = 0.2) -> None:
        """Apply Niblack thresholding.
        This is a local thresholding method that computes the threshold for a pixel
        based on a small region around it.

        See https://scikit-image.org/docs/stable/auto_examples/segmentation/\
                plot_niblack_sauvola.html

        As the input image must be a grayscale before applying any thresholding
        methods we convert the image to grayscale.

        Args:
            window_size (int, optional): apply on the
                image. Defaults to 15.
            k (float, optional): factor to apply to regulate the impact
                of the std. Defaults to 0.2.
        """
        self.base.as_grayscale()
        self.base.asarray = threshold_niblack_like(
            img=self.base.asarray, method="niblack", window_size=window_size, k=k
        )[1]

    def binary(self, method: BinarizationMethods = "sauvola") -> NDArray:
        """Binary representation of the image with values that can be only 0 or 1.
        The value 0 is now 0 and value of 255 are now 1. Black is 0 and white is 1.
        We can also talk about the mask of the image to refer to the binary
        representation of it.

        The sauvola is generally the best binarization method however it is
        way slower than the others methods. The adaptative or otsu method are the best
        method in terms of speed and quality.

        Args:
            method (str, optional): the binarization method to apply.
                Must be in ["adaptative", "otsu", "sauvola", "niblack", "nick", "wolf"].
                Defaults to "sauvola".

        Returns:
            NDArray: array where its inner values are 0 or 1
        """
        if method not in list(get_args(BinarizationMethods)):
            raise ValueError(
                f"Invalid binarization method {method}. "
                f"Must be in {BinarizationMethods}"
            )
        getattr(self, f"threshold_{method}")()
        return self.base.asarray_binary

    def binaryrev(self, method: BinarizationMethods = "sauvola") -> NDArray:
        """Reversed binary representation of the image.
        The value 0 is now 1 and value of 255 are now 0. Black is 1 and white is 0.
        This is why it is called the "binary rev" or "binary reversed".

        Args:
            method (str, optional): the binarization method to apply.
                Defaults to "adaptative".

        Returns:
            NDArray: array where its inner values are 0 or 1
        """
        return 1 - self.binary(method=method)
