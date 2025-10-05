# Taskify


## Installation & Setup
- Clone the Repository
```
git clone https://github.com/hahuy1708/Taskify.git
cd Taskify
```
### Backend
- Create and Activate virtualenv
```
cd backend
python -m venv venv
venv\Scripts\activate
```
- Install Dependencies
```
pip install Django djangorestframework djoser djangorestframework-simplejwt django-cors-headers django-environ
# API Documentation
pip install drf-spectacular
# MySQL connector 
pip install PyMySQL
```
### Frontend
- Install
```
npm install -g @vue/cli
cd frontend
npm install axios vue-router@4 pinia jwt-decode
```
