YOLO Intrusion Detection — explanation file
1. The project goal
To create a video surveillance system, which determines the intrusion of a human into a restricted area with the help of the YOLOv8 and OpenCV.
2. Architectural decisions
The project is built in a modular way:
core/— the object detection module (YOLO);
io_utils/— zones loading and saving;
utils/— geometric functions;
main.py— the main control module.
The separation is done for understanding and easy expansion:
the detector, interface or zones geometry can be changed separately no touching the rest of the code.
3. Libraries used
Library Purpose Reason for choosing
ultralytics (YOLOv8) Detecting people in video Modern and accurate model, easy integration
opencv-python Processing video and graphics Convenient visualization, fast API
numpy Handling arrays and coordinates Efficient point operations for zones
json Zones storage in a file Simplicity and readability of data structure
4. Technical aspects
The intersection is determined by the contact point of the human's legs (lower part of the box), not by the center, for more accuracy.
The areas are defined as polygons (point_in_polygon).
Once the human is detected in the area, the text "ALARM!" and a red marker at the intersection point will appear.
The architecture makes it possible easily to add new zones or signals (for example, a sound one).

5. Conclusion
The project showcases the application of computer vision for automatic monitoring of restricted areas.
The main decisions are directed towards simplicity, flexibility, and stability of the system.