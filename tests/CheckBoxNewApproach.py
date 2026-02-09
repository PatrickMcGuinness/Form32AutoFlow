import logging

import cv2
import numpy as np
from pdf2image import convert_from_path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def interactive_roi_locator(pdf_path: str, page_index: int = 8, init_x: int = 87, init_y: int = 200, init_w: int = 30, init_h: int = 30) -> tuple[int, int, int, int]:
    """
    Converts a PDF page to an image and opens interactive windows to adjust the ROI.
    You can adjust X, Y, Width, and Height using trackbars. A red rectangle is drawn on the image
    indicating the ROI, and the ROI is shown in a separate window.

    Press 'q' to quit and print the chosen ROI parameters.

    Returns:
        A tuple (x, y, w, h) representing the ROI parameters.
    """
    # Convert PDF page to image using pdf2image.
    images = convert_from_path(pdf_path, poppler_path=r"C:\Program Files\poppler-24.08.0\Library\bin")
    form_page = images[page_index]  # page_index is 0-based (e.g., 8 means page 9)
    img = cv2.cvtColor(np.array(form_page), cv2.COLOR_RGB2BGR)

    # Create windows for the full image and the ROI.
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.namedWindow("ROI", cv2.WINDOW_NORMAL)
    cv2.waitKey(1)  # Allow windows to initialize

    # Create trackbars for X, Y, Width, and Height in the "Image" window.
    cv2.createTrackbar("X", "Image", init_x, img.shape[1] - 1, lambda _: None)
    cv2.createTrackbar("Y", "Image", init_y, img.shape[0] - 1, lambda _: None)
    cv2.createTrackbar("Width", "Image", init_w, img.shape[1] - init_x, lambda _: None)
    cv2.createTrackbar("Height", "Image", init_h, img.shape[0] - init_y, lambda _: None)

    print("Adjust the 'X', 'Y', 'Width', and 'Height' sliders in the 'Image' window to locate the checkbox ROI.")
    print("Press 'q' to quit and see the chosen ROI parameters.")

    while True:
        # Read current trackbar positions.
        x = cv2.getTrackbarPos("X", "Image")
        y = cv2.getTrackbarPos("Y", "Image")
        w = cv2.getTrackbarPos("Width", "Image")
        h = cv2.getTrackbarPos("Height", "Image")

        # Draw a red rectangle on a copy of the image showing the ROI.
        display_img = img.copy()
        cv2.rectangle(display_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.imshow("Image", display_img)

        # Extract and show the ROI.
        roi = img[y:y + h, x:x + w]
        cv2.imshow("ROI", roi)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            print("Chosen ROI parameters:")
            print(f"X: {x}, Y: {y}, Width: {w}, Height: {h}")
            break

    cv2.destroyAllWindows()
    return x, y, w, h


def main() -> None:
    pdf_path = r"C:\Users\billy_knott\Form32pdf\LEROY.pdf"
    x, y, w, h = interactive_roi_locator(pdf_path, page_index=7, init_x=87, init_y=200, init_w=30, init_h=30)
    print(f"Final chosen ROI: X = {x}, Y = {y}, Width = {w}, Height = {h}")


if __name__ == "__main__":
    main()
