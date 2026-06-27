# 🩺 Health Prediction Application

A Machine Learning-powered Health Prediction Application that collects patient health information, predicts possible health risks using a Random Forest model, and generates professional medical remarks using the Groq AI API.

---

## 📌 Project Overview

This application allows users to:

- Add patient details
- Predict health risk using Machine Learning
- Generate AI-based medical remarks
- Store patient records
- Perform CRUD (Create, Read, Update, Delete) operations

The application combines Machine Learning with an external AI service to provide easy-to-understand health remarks.

---

## 🚀 Features

- Patient Registration
- Health Risk Prediction
- AI-generated Medical Remarks
- Create, Read, Update, Delete (CRUD)
- SQLite Database
- Input Validation
- User-friendly Streamlit Interface

---

## 🛠️ Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend Development |
| Streamlit | User Interface |
| SQLite | Database |
| Scikit-learn | Machine Learning |
| Random Forest | Prediction Model |
| Groq API | AI-generated Medical Remarks |
| Pandas | Data Processing |
| Joblib | Model Loading |
| Requests | API Integration |

---

## 📂 Project Structure

```
HealthPredictionApp/
│
├── app.py
├── predictor.py
├── database.py
├── validators.py
├── train_model.py
├── model.pkl
├── health_app.db
├── requirements.txt
├── README.md
├── .env
└── .gitignore
```

---

## ⚙️ Installation

### Clone the Repository

```bash
git clone https://github.com/yourusername/HealthPredictionApp.git
cd HealthPredictionApp
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create a `.env` file

```env
GROQ_API_KEY=your_groq_api_key
```

### Run the Application

```bash
streamlit run app.py
```

---

## 🧠 Machine Learning Workflow

1. Patient enters health parameters.
2. Random Forest model predicts health risk.
3. Prediction and health values are sent to the Groq API.
4. Groq generates a professional medical remark.
5. Results are stored in the SQLite database.

---

## 📊 Input Parameters

- Full Name
- Date of Birth
- Email Address
- Glucose Level
- Haemoglobin Level
- Cholesterol Level

---

## 🤖 AI Integration

This project integrates the **Groq API** as an external AI service.

The application:

- Predicts health risk using a locally trained Random Forest model.
- Sends the prediction and patient values to the Groq API.
- Receives a professional medical remark.
- Displays and stores the generated remark.

---

## 🗄️ Database

SQLite is used for storing:

- Patient Information
- Blood Test Values
- AI-generated Remarks
- Timestamp

---

## 📸 Application Features

- Add Patient
- View Patient Records
- Edit Patient Details
- Delete Patient Record
- AI-generated Medical Remarks

---

## 🔮 Future Enhancements

- Real-world medical datasets
- Multiple disease prediction
- User Authentication
- PDF Report Generation
- Doctor Dashboard
- Cloud Deployment
- Email Notifications

---

## ⚠️ Disclaimer

This project is developed for educational and demonstration purposes only.

The predictions and AI-generated remarks should not be considered medical advice or used for clinical decision-making.

---

## 👨‍💻 Author

**Rik**

Built as a Machine Learning and AI integration project using Python, Streamlit, SQLite, Random Forest, and the Groq API.
