import cv2
import numpy as np
import torch
import urllib.request
import matplotlib.pyplot as plt
from scipy.interpolate import RectBivariateSpline
from ultralytics import YOLO 

model  = YOLO("yolo11n.pt")

focal_length = 10400
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model_type = "DPT_Large"
midas = torch.hub.load("intel-isl/MiDaS", model_type)
midas.to(device)
midas.eval()
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
transform = midas_transforms.dpt_transform

def depth_to_distance(depth_value, depth_scale):
    return 1.0/(depth_value*depth_scale)



alpha = 0.2
previous_depth = 0.0
def apply_ema_filter(current_depth):
    global previous_depth
    filtered_depth = alpha * current_depth + (1 - alpha) * previous_depth
    previous_depth = filtered_depth  # Update the previous depth value
    return filtered_depth


if __name__=="__main__":
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret,frame = cap.read()

        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_batch= transform(img).to(device)
        with torch.no_grad():
            prediction = midas(input_batch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size=img.shape[:2],
                mode = "bicubic",
                align_corners=False
            ).squeeze()
        depth_map = prediction.cpu().numpy()

        # Interpolation for depth
        output_norm = cv2.normalize(depth_map, None, 0,1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        h, w= output_norm.shape
        x = np.arange(w)  # x-coordinates (width)
        y = np.arange(h)  # y-coordinates (height)
        depth_interpolator = RectBivariateSpline(y, x, output_norm)
        results = model(frame, device = device)

        for result in results:
            
            for det in result.boxes:
                class_id = int(det.cls)
                class_name = result.names[class_id]
                confid = det.conf.item()
                if class_name == "tv" and confid >= 0.30:
                    x_min, y_min, x_max, y_max = det.xyxy[0].tolist()

                    x_center = (x_min+x_max)/2
                    y_center=  (y_min+y_max)/2

                    depth_mid_filt = depth_interpolator(y_center, x_center)
                    depth_value =depth_interpolator(y_center, x_center)[0][0]

                    scale_factor = 1/depth_value
                    depth_midas = depth_to_distance(depth_mid_filt, 0.35)
                    depth_mid_filt = (apply_ema_filter(depth_midas)/10)[0][0]
                    # Draw bounding box
                    cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (0, 255, 0), 2)

                    # Add text with distance information
                    label = f"{class_name}: {depth_mid_filt:.2f} m"
                    cv2.putText(frame, label, (int(x_min), int(y_min) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)

        cv2.imshow("Depth map", frame)

        if cv2.waitKey(1) &0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

