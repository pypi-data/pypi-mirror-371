#!/usr/bin/env python
"""Camera stream viewer with Click CLI."""

import time
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
@click.option(
    "--detect/--no-detect",
    default=False,
    help="Enable object detection with YOLO",
)
@click.option(
    "--model",
    "-m",
    default="yolo11n.pt",
    type=str,
    help="YOLO model to use (default: yolo11n.pt)",
)
@click.option(
    "--confidence",
    "-c",
    default=0.25,
    type=float,
    help="Confidence threshold for detections (default: 0.25)",
)
@click.option(
    "--skip-frames",
    "-s",
    default=1,
    type=int,
    help="Process every Nth frame for detection (default: 1, no skipping)",
)
def main(device, width, height, fps, detect, model, confidence, skip_frames):
    """Open and display a camera stream using OpenCV."""
    # Lazy load YOLO if detection is enabled
    yolo_model = None
    detection_enabled = detect
    
    if detection_enabled:
        click.echo(f"Loading YOLO model: {model}")
        try:
            from ultralytics import YOLO
            yolo_model = YOLO(model)
            yolo_model.conf = confidence
            click.echo(f"Model loaded successfully with confidence threshold: {confidence}")
        except Exception as e:
            click.echo(f"Error loading YOLO model: {e}", err=True)
            click.echo("Continuing without object detection", err=True)
            detection_enabled = False
            yolo_model = None
    
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
    click.echo("Controls:")
    click.echo("  'q' or ESC: Quit")
    if yolo_model is not None:
        click.echo("  'd': Toggle detection on/off")
        click.echo(f"  Detection: {'ON' if detection_enabled else 'OFF'}")
        if skip_frames > 1:
            click.echo(f"  Processing every {skip_frames} frame(s)")
    
    window_name = f"Camera {device}"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    # Variables for FPS calculation
    frame_count = 0
    fps_start_time = time.time()
    display_fps = 0.0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                click.echo("Error: Failed to capture frame", err=True)
                break
            
            # Process frame with YOLO if enabled
            display_frame = frame.copy()
            if yolo_model is not None and detection_enabled:
                # Only process every Nth frame for detection
                if frame_count % skip_frames == 0:
                    results = yolo_model(frame, verbose=False)
                    display_frame = results[0].plot()
                    
                    # Count detections
                    num_detections = len(results[0].boxes) if results[0].boxes is not None else 0
                    if num_detections > 0:
                        click.echo(f"\rDetections: {num_detections} objects", nl=False)
            
            # Calculate and display FPS
            frame_count += 1
            if frame_count % 30 == 0:  # Update FPS every 30 frames
                elapsed = time.time() - fps_start_time
                display_fps = frame_count / elapsed
                frame_count = 0
                fps_start_time = time.time()
            
            # Add FPS overlay
            if display_fps > 0:
                fps_text = f"FPS: {display_fps:.1f}"
                cv2.putText(display_frame, fps_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Add detection status overlay
            if yolo_model is not None:
                status_text = f"Detection: {'ON' if detection_enabled else 'OFF'}"
                color = (0, 255, 0) if detection_enabled else (0, 0, 255)
                cv2.putText(display_frame, status_text, (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            cv2.imshow(window_name, display_frame)
            
            # Check for keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:  # 'q' or ESC
                break
            elif key == ord('d') and yolo_model is not None:  # Toggle detection
                detection_enabled = not detection_enabled
                click.echo(f"\nDetection {'enabled' if detection_enabled else 'disabled'}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        click.echo("Camera stream closed")


if __name__ == "__main__":
    main()