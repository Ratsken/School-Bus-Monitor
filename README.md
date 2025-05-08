# School Bus Monitor

---

## **Overview**

The **School Bus Monitor** is a comprehensive Django-based web application designed to provide real-time tracking, monitoring, and management of school buses. This system ensures safety, efficiency, and transparency in bus operations by offering features such as live location tracking, route management, student tracking, driver notifications, and concern reporting.

This README provides detailed instructions on setting up, configuring, and using the project.

---

## **Features**

### **Core Features**
1. **Real-Time Bus Tracking**:
   - Track the current location of active buses on a map.
   - View historical location data for the last 24 hours.

2. **Route Management**:
   - Create and manage bus routes.
   - Assign buses and drivers to specific routes.

3. **Student Monitoring**:
   - Monitor students assigned to each bus.
   - Notify parents about bus delays or maintenance updates.

4. **Driver Dashboard**:
   - Allow drivers to update their current location via GPS.
   - Provide alerts for route deviations or maintenance issues.

5. **Concern Reporting**:
   - Allow users (parents, teachers, etc.) to raise concerns about buses or routes.
   - Track the status of concerns (e.g., open, in progress, resolved).

6. **Notifications**:
   - Send email/SMS notifications to parents and administrators about delays, route changes, or maintenance.

7. **Admin Dashboard**:
   - A centralized dashboard for administrators to view system-wide statistics, including:
     - Total buses
     - Active routes
     - Online drivers
     - Recent concerns

8. **REST API**:
   - Expose APIs for fetching current bus locations and historical data.

---

## **Technology Stack**

- **Backend**: Django, Django REST Framework (DRF)
- **Frontend**: HTML5, CSS3, Bootstrap 4, JavaScript (with Leaflet.js/Mapbox for maps)
- **Database**: PostgreSQL (default), Redis (for caching real-time location data)
- **Geolocation**: GeoDjango, Geopy
- **API Documentation**: Swagger/OpenAPI (via `drf-yasg`)
- **Styling**: Jazzmin (customizable admin theme)
- **Other Tools**: Celery (for background tasks), Redis (for task queue and caching)

---

## **Project Structure**

```
school_bus_monitor/
├── bus_management/               # Main Django project directory
│   ├── core/                     # Core app for bus monitoring logic
│   │   ├── admin.py              # Admin configurations
│   │   ├── models.py             # Database models (Bus, Route, Student, etc.)
│   │   ├── views.py              # Views for handling requests
│   │   ├── urls.py               # URL routing
│   │   ├── utils.py              # Utility functions (Redis, geolocation, etc.)
│   │   └── management/commands/  # Custom management commands
│   ├── accounts/                 # User authentication and roles
│   ├── static/                   # Static files (CSS, JS, images)
│   ├── templates/                # HTML templates
│   └── settings.py               # Project settings
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (API keys, secrets, etc.)
└── README.md                     # This file
```

---

## **Installation and Setup**

### **Prerequisites**
1. Python 3.10 or higher
2. PostgreSQL (or another supported database)
3. Redis (for real-time location tracking and caching)
4. Node.js (optional, for frontend asset management)

### **Steps to Set Up**

#### **1. Clone the Repository**
```bash
git clone https://github.com/your-repo/school-bus-monitor.git
cd school-bus-monitor
```

#### **2. Set Up a Virtual Environment**
```bash
python -m venv .env
source .env/bin/activate  # On Windows: .env\Scripts\activate
```

#### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

#### **4. Configure Environment Variables**
Create a `.env` file in the root directory with the following content:

```dotenv
SECRET_KEY=your_django_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://username:password@localhost:5432/school_bus_monitor
REDIS_URL=redis://localhost:6379/0
MAPBOX_ACCESS_TOKEN=your_mapbox_api_token_here
SMS_GATEWAY_API_KEY=your_sms_gateway_api_key_here
SMS_GATEWAY_API_SECRET=your_sms_gateway_api_secret_here
SMS_FROM_NUMBER=your_sms_from_number_here
GEOPY_USER_AGENT=school_bus_monitor
```

#### **5. Apply Migrations**
```bash
python manage.py migrate
```

#### **6. Load Initial Data**
```bash
python manage.py load_initial_data
```

#### **7. Run the Development Server**
```bash
python manage.py runserver
```

Access the application at `http://127.0.0.1:8000`.

#### **8. Start Redis**
Ensure Redis is running on your system:
```bash
redis-server
```

---

## **Usage**

### **Admin Dashboard**
- Access the admin dashboard at `/admin`.
- Default admin credentials:
  - Username: `admin`
  - Password: `admin123`

### **Driver Dashboard**
- Drivers can log in and update their current location.
- The system uses GPS coordinates stored in Redis for real-time tracking.

### **Parent Portal**
- Parents can view the location of their child's bus and receive notifications about delays or route changes.

### **API Endpoints**
- **Current Bus Locations**: `GET /api/locations/current/`
- **Bus Location History**: `GET /api/locations/history/<bus_id>/`

---

## **API Documentation**

API documentation is available via Swagger/OpenAPI:
- Access it at `http://127.0.0.1:8000/swagger/` or `http://127.0.0.1:8000/redoc/`.

---

## **Customization**

### **Jazzmin Theme**
The admin interface uses the **Jazzmin** theme for customization. Update the `JAZZMIN_SETTINGS` dictionary in `settings.py` to modify the appearance.

### **Map Integration**
The system uses **Mapbox** for mapping. Replace the `MAPBOX_ACCESS_TOKEN` in `.env` with your own token.

### **Notifications**
Configure SMS/email notifications by updating the `SMS_GATEWAY_API_KEY`, `SMS_GATEWAY_API_SECRET`, and `SMS_FROM_NUMBER` in `.env`.

---

## **Deployment**

### **Using Docker**
A `Dockerfile` and `docker-compose.yml` are included for containerized deployment:
```bash
docker-compose up --build
```

### **Production Settings**
- Use a production-ready database like PostgreSQL.
- Set `DEBUG=False` in `.env`.
- Configure a web server (e.g., Nginx) and WSGI server (e.g., Gunicorn).

---

## **Contributing**

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add feature"`) and push (`git push origin feature/your-feature`).
4. Open a pull request.

---

## **License**

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

## **Contact**

For questions or feedback, contact the maintainers:
- Email: [contact@schoolbusmonitoring.com](mailto:contact@schoolbusmonitoring.com)
- GitHub: [https://github.com/your-repo/school-bus-monitor](https://github.com/your-repo/school-bus-monitor)

---

Thank you for using **School Bus Monitor**! 🚍