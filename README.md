🏆 Sports Celebrity Face Recognition with Generative AI

A full end-to-end AI pipeline that identifies sports celebrities from an input image and generates a detailed career summary using Google Gemini.
The project covers the entire data science workflow — preprocessing, feature engineering, classical machine learning, model selection, deployment, and a fully interactive web UI.

📌 System Architecture

<img width="1137" height="485" alt="Screenshot 2025-12-11 193309" src="https://github.com/user-attachments/assets/5e0bf196-fe76-4b5d-a9fb-308a2474b3f2" />

This system consists of:

Frontend (HTML/JS/Dropzone/Webcam)
Flask Backend
OpenCV Preprocessing
Hybrid Feature Extraction (Raw Pixels + DWT)
SVM Classifier
Google Gemini Generation Engine


🚀 Features
🔍 Face Recognition
Haar Cascade face detection
Two-eye validation for clean and consistent samples

🧠 Hybrid Feature Engineering
Raw grayscale pixels
Wavelet coefficients (DWT)
Concatenated into a single discriminative feature vector

🤖 Classical ML Models
SVM (Best Model)
Random Forest
Logistic Regression
Hyperparameters tuned with GridSearchCV

🌐 Backend + Frontend
Flask REST API
Web UI for uploads
Webcam Look-Alike Mode
Probability table + highlighted result
Auto-generated Gemini descriptions

📊 Model Performance

GridSearchCV Results
<img width="862" height="272" alt="Screenshot 2025-12-11 193431" src="https://github.com/user-attachments/assets/e5a60ce8-1eb3-4de4-b35f-d205f9ebdf0f" />

SVM achieved the highest score (≈ 84.12%)
Logistic Regression also performed well
Random Forest was less consistent due to small dataset size

Confusion Matrix
<img width="941" height="501" alt="Screenshot 2025-12-11 193457" src="https://github.com/user-attachments/assets/60ba8a23-b664-4287-8dca-021382edbf74" />


The model performs strongly overall, with some misclassifications between visually similar faces.

Classification Report
<img width="898" height="534" alt="Screenshot 2025-12-11 193513" src="https://github.com/user-attachments/assets/33b79797-f1e1-46cb-96d9-c1e5c5a74d43" />


Key insights:
Strong recall for most classes
Weighted F1 score ≈ 0.75
Performance limited mainly by dataset size


🎥 Web Application UI
Webcam Look-Alike Mode
<img width="973" height="452" alt="Screenshot 2025-12-11 193533" src="https://github.com/user-attachments/assets/18e4ec57-f0bf-497a-bfca-e8524f42ad82" />


The system detects your face live and predicts the most similar sports celebrity.

Image Upload Mode

<img width="327" height="303" alt="Screenshot 2025-12-11 193554" src="https://github.com/user-attachments/assets/a1c82c10-8df1-4326-ad2e-e85bdc26e031" />



The UI displays:
<img width="936" height="580" alt="Screenshot 2025-12-11 193554" src="https://github.com/user-attachments/assets/c32b236d-dd80-43c8-bd4b-88e7c7c9c212" />

The predicted celebrity
A detailed probability table
Gemini-generated career summary



🔬 How It Works (Summary)
1️⃣ Preprocessing

Convert to grayscale
Detect face
Validate eyes
Crop & resize

2️⃣ Hybrid Feature Extraction

Flatten raw pixels
Apply DWT → flatten coefficients
Concatenate

3️⃣ Model Training

Split into train/test
Tune hyperparameters
Evaluate & save model

4️⃣ Prediction + Gemini Integration

Detect face

Extract features
Predict class
Generate a complete career summary


