from ultralytics import YOLO
import cv2
import numpy
import base64
import os

def find_flower_yolo(b64img: str) -> dict:
    """
    :param b64img: Base64 encoded image string (image string part only).
    :return: A response JSON with processed image and coordinates.
    """

    # sorting key
    sort_key = "y"
    # note to Rusira: use "x" or "y" to coordinates sort by x-axis or y-axis

    # decode the Base64 image
    image_array = numpy.frombuffer(base64.b64decode(b64img), numpy.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Failed to decode image from Base64 input. Check input, don't send this part 'data:image/png;base64,'.")

    # Rotate the image 90 degrees clockwise
    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    if not os.path.exists("YOLOv8-str-flower-model.pt"):
        raise FileNotFoundError("Model file not found")

    # load the YOLO model
    model = YOLO("YOLOv8-str-flower-model.pt")

    # run inference and find flowers
    results = model(image, conf=0.3)

    # extract bounding boxes and normalize coordinates
    height, width, _ = image.shape
    normalized_coords = []

    for box, conf in zip(results[0].boxes.xyxy.cpu().numpy(), results[0].boxes.conf.cpu().numpy()):
        x_min, y_min, x_max, y_max = map(float, box)
        normalized_coords.append({
            "x": round((x_min + x_max) / 2 / width, 4),
            "y": round((y_min + y_max) / 2 / height, 4),
            "confidence": round(float(conf), 2),
        })

        # draw bounding boxes on the image
        cv2.rectangle(
            image,
            (int(x_min), int(y_min)),
            (int(x_max), int(y_max)),
            (0, 255, 0),
            2
        )

        # add confidence score to image
        text = f"{conf:.2f}"
        cv2.putText(
            image, text,
            (int(x_min), int(y_min) - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
            (0, 255, 0),
            1, cv2.LINE_AA
        )

    # sorting
    normalized_coords.sort(key=lambda coord: coord[sort_key])

    # convert processed image to Base64
    _, buffer = cv2.imencode(".png", image)
    result_base64 = base64.b64encode(buffer).decode("utf-8")

    # return JSON
    return {
        "status": 200,
        "image": f"data:image/png;base64,{result_base64}",
        "imageResult": normalized_coords
    }
