# 🌾 Fasaldhan Backend

<div align="center">

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/DRF-ff1709?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)

**A Modern Contract Farming Platform Connecting Farmers with Buyers**

*Empowering agricultural communities through technology and fair trade practices*

</div>

---

## 🚀 About Fasaldhan

Fasaldhan is a comprehensive contract farming platform that bridges the gap between farmers and buyers through technology. Our platform enables direct connections, fair pricing, and transparent transactions in the agricultural sector.

### ✨ Key Features

- 🔐 **Secure Authentication** - JWT-based user authentication and authorization
- 👨‍🌾 **Farmer Profiles** - Comprehensive farmer management with farm details
- 🏢 **Buyer Profiles** - Business profile management for agricultural buyers
- 📋 **Crop Listings** - Easy listing and browsing of available crops
- 📄 **Smart Contracts** - Digital contract management with terms and conditions
- ⭐ **Review System** - Rating and feedback system for quality assurance
- 📊 **Analytics Dashboard** - Data-driven insights and market trends
- 🤖 **ML Integration** - AI-powered price prediction and quality assessment

---

## 🏗️ Architecture

```
fasaldhan-backend/
├── 📁 user/              # User management & authentication
├── 📁 contract/          # Contract farming system
├── 📁 fasaldhan/         # Django project settings
├── 📁 myenv/             # Virtual environment
└── 📄 manage.py          # Django management script
```

### 🛠️ Built With

| Technology | Purpose | Version |
|------------|---------|---------|
| **Django** | Web Framework | 5.x |
| **Django REST Framework** | API Development | Latest |
| **JWT** | Authentication | Latest |
| **SQLite** | Database | Built-in |
| **TensorFlow** | ML Models | 2.x |
| **CORS Headers** | Cross-Origin Requests | Latest |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ 🐍
- pip package manager 📦
- Virtual environment (recommended) 🛡️

### Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd fasaldhan-backend
   ```

2. **Activate Virtual Environment**
   ```bash
   myenv\Scripts\activate  # Windows
   # or
   source myenv/bin/activate  # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run Development Server**
   ```bash
   python manage.py runserver
   ```

🎉 **Server runs at:** `http://localhost:8000`

---

## 🌟 User Types

<table>
<tr>
<td align="center" width="50%">

### 👨‍🌾 Farmers
- Create detailed farm profiles
- List crops for sale
- Manage farming contracts
- Track earnings and analytics
- Get ML-powered insights

</td>
<td align="center" width="50%">

### 🏢 Buyers
- Browse available crops
- Create purchase contracts
- Manage business profiles
- Access market trends
- Rate and review farmers

</td>
</tr>
</table>

---

## 📊 Platform Highlights

<div align="center">

| Feature | Farmers | Buyers | Admins |
|---------|---------|--------|--------|
| Profile Management | ✅ | ✅ | ✅ |
| Crop Listings | ✅ | 👀 | ✅ |
| Contract Creation | 👀 | ✅ | ✅ |
| Reviews & Ratings | ✅ | ✅ | 👀 |
| Analytics Dashboard | ✅ | ✅ | ✅ |
| ML Predictions | ✅ | ✅ | ✅ |

</div>

---

## 🛡️ Security Features

- 🔒 **JWT Authentication** - Secure token-based authentication
- 🛡️ **Permission System** - Role-based access control
- 🔐 **Data Validation** - Comprehensive input validation
- 📱 **Phone Verification** - Mobile number verification system
- ✉️ **Email Verification** - Email address confirmation

---

## 📁 Project Structure

```
📦 Fasaldhan Backend
├── 🔐 Authentication System
├── 👤 User Management
│   ├── Farmer Profiles
│   └── Buyer Profiles
├── 🌾 Contract System
│   ├── Crop Categories
│   ├── Crop Listings
│   ├── Contract Management
│   └── Review System
├── 🤖 ML Services
│   ├── Price Prediction
│   ├── Quality Assessment
│   └── Yield Forecasting
└── 📊 Analytics & Dashboard
```

---

## 🔧 Development

### Available Commands

```bash
# Database operations
python manage.py makemigrations
python manage.py migrate

# Development server
python manage.py runserver

# Create admin user
python manage.py createsuperuser

# Run tests
python manage.py test

# Collect static files
python manage.py collectstatic
```

### 🌐 Important URLs

- **Admin Panel:** `/admin/`
- **API Root:** `/api/`
- **Documentation:** `API_Documentation.md`
- **DRF Interface:** `/api/` (browsable API)

---

## 📡 API Integration

For complete API documentation, testing, and integration:

📖 **[View API Documentation](API_Documentation.md)**

🔧 **[Import Postman Collection](Fasaldhan_API_Collection.postman_collection.json)**

⚙️ **[Use Postman Environment](Fasaldhan_Development_Environment.postman_environment.json)**

---

## 🤝 Contributing

We welcome contributions to Fasaldhan! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch
3. 💻 Make your changes
4. ✅ Run tests
5. 📤 Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Django & DRF community for excellent frameworks
- Agricultural experts for domain knowledge
- Open source contributors for various packages
- Farmers and buyers for valuable feedback

---

<div align="center">

**Made with ❤️ for the Agricultural Community**

*Connecting Farmers • Empowering Trade • Building Sustainability*

---

**[🌐 Live Demo](#) | [📧 Contact](#) | [📱 Mobile App](#)**

</div>
