import os
import sys

def main():
    model_path = os.path.join(os.path.dirname(__file__), "models", "best.pt")
    if not os.path.exists(model_path):
        print(f"Error: Model file '{model_path}' does not exist.")
        print("Please place your trained best.pt file inside the 'models/' folder before running export.")
        sys.exit(1)
        
    try:
        from ultralytics import YOLO
        print("Loading fine-tuned YOLOv8 model for ONNX export...")
        model = YOLO(model_path)
        
        output_onnx = model.export(format="onnx")
        print(f"Successfully exported model to ONNX: {output_onnx}")
        
        # TensorRT Export Option (Uncomment if running on target Jetson hardware with TensorRT installed):
        # print("Exporting to TensorRT engine...")
        # model.export(format="engine", device=0)
        
    except Exception as e:
        print(f"Failed to export model: {e}")

if __name__ == "__main__":
    main()
