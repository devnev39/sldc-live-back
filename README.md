# SLDC Live Backend

This backend service for SLDC Live extracts valuable data from images. It runs on Google Cloud Run and leverages EasyOCR for object detection. The service utilizes a schema file (schema.json) containing labelled rectangles to guide the model in its detection tasks.

## Architecture
The image processing and data extraction service runs on Google Cloud Run. Eventarc triggers the FastAPI service every hour to process the SLDC Kalwa image and extract generation data for Maharashtra. The extracted data is then stored in Firestore with timestamps for easy retrieval.

[![My Skills](https://skillicons.dev/icons?i=gcp,react,redux,vite,firebase,)](https://skillicons.dev)


