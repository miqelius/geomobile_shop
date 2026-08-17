# 📱 GeoMobile Shop

A modern, responsive e-commerce web application and backend designed for a mobile phones and accessories store. Built with clean architecture, containerized services, and secure administrative controls.

---

## 🚀 Features

* **Responsive Modern UI:** Built with Tailwind CSS for seamless mobile and desktop experiences.
* **Secure Backend API:** Powered by FastAPI with HTTP Basic Authentication protected by environment variables (`.env`).
* **Product Catalog & Cart:** Dynamic product display with category filtering and interactive elements.
* **Git Hygiene & Security:** Strict separation of secrets and dependencies using `.gitignore`.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, Tailwind CSS, JavaScript
* **Backend:** Python, FastAPI, Uvicorn
* **Security & Config:** Python-Dotenv, HTTP Basic Auth
* **Version Control:** Git & GitHub

---

## ⚙️ Installation & Setup

1. **Clone the repository:**
   `git clone https://github.com/miqelius/geomobile_shop.git`

2. **Create and activate a virtual environment:**
   `python3 -m venv venv` && `source venv/bin/activate`

3. **Install dependencies:**
   `pip install fastapi uvicorn python-dotenv`

4. **Configure environment variables (.env):**
    створення `.env` ფაილის:
   `ADMIN_USER=admin`
   `ADMIN_PASSWORD=your_secure_password`

5. **Run the application:**
   `uvicorn main:app --reload`

---

## 📄 License

This project is open-source and available under the MIT License.
