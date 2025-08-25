#!/usr/bin/env python
"""Camera stream viewer with Click CLI."""

import click
import cv2


@click.command()
@click.option(
    "--device",
    "-d",
    default=0,
    type=int,
    help="Camera device index (default: 0)",
)
@click.option(
    "--width",
    "-w",
    default=None,
    type=int,
    help="Set capture width in pixels",
)
@click.option(
    "--height",
    "-h",
    default=None,
    type=int,
    help="Set capture height in pixels",
)
@click.option(
    "--fps",
    "-f",
    default=None,
    type=float,
    help="Set capture frame rate",
)
def main(device, width, height, fps):
    """Open and display a camera stream using OpenCV."""
    # Open camera
    cap = cv2.VideoCapture(device)
    
    if not cap.isOpened():
        click.echo(f"Error: Could not open camera device {device}", err=True)
        return 1
    
    # Set camera properties if specified
    if width is not None:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    if height is not None:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if fps is not None:
        cap.set(cv2.CAP_PROP_FPS, fps)
    
    # Display actual camera settings
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    click.echo(f"Camera opened: {actual_width}x{actual_height} @ {actual_fps:.1f} fps")
    click.echo("Press 'q' or ESC to quit")
    
    window_name = f"Camera {device}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                click.echo("Error: Failed to capture frame", err=True)
                break
            
            cv2.imshow(window_name, frame)
            
            # Check for quit keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        click.echo("Camera stream closed")


if __name__ == "__main__":
    main()