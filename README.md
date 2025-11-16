# Taskify

Taskify is a comprehensive Trello-inspired project, task management web application built with a Django REST Framework backend and a Vue 3 frontend. It offers robust features for managing projects, tasks, teams, and user authentication, providing an intuitive and efficient user experience.

## Features
- **Core Functionality:**
    - Project management: create project, assign leader, description, status.
	- Kanban board: drag-and-drop tasks between columns to manage workflow.
	- Task management: create tasks, assign assignee, set deadlines, checklists, comments.
	- Team & Membership: create teams, add/remove members, assign roles.
- **Technical Features:**
	- REST API backend with Django REST Framework.
    - Token-based authentication using JWT and robust authorization.
	- Frontend SPA using Vue 3 + Pinia + Vue Router, user-friendly and intuitive UI with Tailwind CSS.
    - Email Service: SMTP configuration supporting 2FA via App Passwords for robust security.
    - Modular and maintainable code structure for both frontend and backend.

## Architecture

- **Project structure:**
```
├── 📁 backend
│   ├── 📁 taskify_backend
│   │   ├── 📁 taskify_auth             # handle user model (CustomUser), authentication, user-related endpoints
│   │   ├── 📁 taskify_backend
│   │   ├── 📁 taskify_core             # handle main domain — projects, teams, tasks, services, serializers, and API views
│   │   │   ├── 📁 serializers          # serializers for data transformation
│   │   │   ├── 📁 services             # business logic and service layer
│   │   │   ├── 📁 views                # API views
│   │   │   ├── 🐍 models.py            # database models
│   │   │   ├── 🐍 permissions.py       # custom permissions
│   │   │   └── 🐍 urls.py              # URL routing
│   │   └── 🐍 manage.py                # Django management script
│   ├── ⚙️ .gitignore
│   └── 📄 requirements2.txt
├── 📁 frontend
│   ├── 📁 src
│   │   ├── 📁 api                      # axios wrappers for backend API endpoints
│   │   ├── 📁 assets                   # static assets (images, styles, etc.)
│   │   ├── 📁 components               # main domain-related components + UI components
│   │   │   ├── 📁 Projects         
│   │   │   ├── 📁 Tasks            
│   │   │   ├── 📁 Teams            
│   │   │   ├── 📁 Users            
│   │   │   ├── 📄 Header.vue       
│   │   │   ├── 📄 KanbanBoard.vue
│   │   │   ├── 📄 LoginForm.vue
│   │   │   ├── 📄 RegisterForm.vue
│   │   │   └── 📄 Sidebar.vue
│   │   ├── 📁 composables              # reusable composition API functions
│   │   ├── 📁 layouts                  # contains shared UI and layout components
│   │   │   ├── 📄 AuthLayout.vue
│   │   │   └── 📄 DashboardLayout.vue
│   │   ├── 📁 pages                    # route pages
│   │   │   ├── 📁 Auth
│   │   │   ├── 📁 Dashboard
│   │   │   ├── 📄 ProjectListPage.vue
│   │   │   ├── 📄 TaskDetailPage.vue
│   │   │   ├── 📄 TaskPage.vue
│   │   │   ├── 📄 TeamListPage.vue
│   │   │   ├── 📄 Unauthorized.vue
│   │   │   └── 📄 UserListPage.vue
│   │   ├── 📁 router                   # Vue Router setup
│   │   ├── 📁 store                    # Pinia stores
│   │   ├── 📁 utils                    # utility functions
│   │   ├── 📄 App.vue
│   │   └── 📄 main.js
│   ├── ⚙️ .gitignore
└── 📝 README.md
```

## Technology Stack

- **Backend:**
    - Language: Python
    - Framework: Django, Django REST Framework
    - Authentication: SimpleJWT + Djoser
    - Database: MySQL
    - ORM: Django ORM
    - API Documentation: Swagger
- **Frontend:**
    - Framework: Vue 3
    - State Management: Pinia
    - Routing: Vue Router
    - CORS Handling: vue-cors
    - HTTP Client: Axios
    - Styling: Tailwind CSS
    - ESLint & Prettier for code quality
- **Dev / Tooling:**
    - Node.js, npm
    - Python virtualenv
    - Git for version control
    - Editor: VS Code
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
pip install -r requirements2.txt
```
- Environment Configuration
    -  Create a `.env` file in the `backend/taskify_backend/` directory with the following variables:
    ```
    DEBUG=True_or_False
    SECRET_KEY=your_django_secret_key

    DB_NAME=your_database_name
    DB_USER=your_database_user
    DB_PASSWORD=your_database_password
    DB_HOST=your_database_host
    DB_PORT=your_database_port
    
    EMAIL_HOST_USER=your_email_host
    EMAIL_HOST_PASSWORD=your_email_password
    EMAIL_HOST=your_email_host_address
    EMAIL_PORT=your_email_port
    EMAIL_USE_TLS=True_or_False
    ```
    See this [guide](https://www.geeksforgeeks.org/python/setup-sending-email-in-django-project/) for configuring your email sending service.
- Database Setup and Migrations
    1. Ensure MySQL is installed and running on your machine and run this command to create database:
    ```
    CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    ```
    2. Run Migrations
    ```
    cd backend/taskify_backend
    python manage.py makemigrations
    python manage.py migrate
    ```
- How to run
```
python manage.py runserver
```

### Frontend
- Prerequisites
    - Ensure Node.js and npm are installed on your machine by opening your terminal and running:
    ```
    node -v
    npm -v
    ```

- Install
```
npm install -g @vue/cli
cd frontend
npm install
```
- Run development server
```
npm run serve
```

