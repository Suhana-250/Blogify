# Cosmos' Blog

Welcome to **Cosmos' Blog**, a personal blogging platform built with **Flask**, **PostgreSQL**, **Flask-Login**, and **Bootstrap**! This project offers a clean and responsive design, allowing users to explore and read blog posts effortlessly. It also features user authentication, contact form email notifications, and database integration for storing posts and user data.

---

## 🌟 Features
- **User Authentication**: Secure login and registration with password hashing and Flask-Login.
- **Dynamic Blog Posts**: Blog content is stored in a PostgreSQL database and dynamically loaded.
- **Responsive Design**: Built with Bootstrap for a seamless experience across all devices.
- **Contact Form**: Users can reach out through the contact form, which sends email notifications using Flask-Mail.
- **Protected Routes**: User access is managed with decorators, ensuring only authenticated users can access certain pages.

---

## 🌐 Live Demo  
Check out the live version of the site: [Cosmos' Blog](https://cosmos-flask-blog-2.onrender.com/)

---

## 🚀 Installation

### 📋 Prerequisites
- Python 3.x
- pip (Python package manager)
- PostgreSQL (for database)

---

### 🛠️ Steps to Set Up Locally

#### 1️⃣ Clone the Repository
```
git clone https://github.com/yourusername/cosmos-blog.git
cd cosmos-blog
```
### 2️⃣ Install Dependencies
```
pip install -r requirements.txt
```
### 3️⃣ Set Up Database
Install PostgreSQL and set up a new database.
Create a .env file in the root directory and add the following environment variables:
```
FLASK_APP=main.py
FLASK_ENV=development
DATABASE_URL=postgresql://yourusername:yourpassword@localhost/yourdbname
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
```
### 4️⃣ Run the Application
Start the Flask development server:

```
python main.py
```
### 5️⃣ Open in Browser
Visit the application at:

```
http://127.0.0.1:5000
```
## 📦 Deployment (Optional - Render)
This project is optionally deployed on Render. If you'd like to deploy it, follow the steps below:

### Deployment Steps:
Connect the repository to Render.
Set the Build Command:
```
pip install -r requirements.txt
```
Set the Start Command:
```
gunicorn main:app
```

## 🛠️ Technology Stack
Backend: Flask
Frontend: Bootstrap 5
Database: PostgreSQL (hosted on Render)
Authentication: Flask-Login, Werkzeug for password hashing
Email (Contact Form): Flask-Mail
Deployment: Render (optional)
Web Server: Gunicorn

## 📜 License
This project is open-source and available under the MIT License.

## 👤 Author
Created and maintained by Cosmos Junior.
Feel free to reach out for any inquiries or suggestions at rumeighoraye@gmail.com
