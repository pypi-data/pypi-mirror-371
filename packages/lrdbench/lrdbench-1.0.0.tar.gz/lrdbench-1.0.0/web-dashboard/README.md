# 🔬 Benchmarking Dashboard

A comprehensive web-based dashboard for the DataExploratoryProject benchmarking framework, providing an intuitive interface for running, monitoring, and analyzing long-range dependence estimators across various stochastic data models.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Your DataExploratoryProject with auto-discovery system

### Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd web-dashboard/backend
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Unix/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the backend server:**
   ```bash
   python main.py
   ```

The server will start on `http://localhost:8000`

### Frontend Setup

1. **Open the frontend:**
   - Navigate to `web-dashboard/frontend/`
   - Open `index.html` in your web browser
   - Or serve it with a simple HTTP server:
     ```bash
     cd frontend
     python -m http.server 3000
     ```

2. **Test the dashboard:**
   - Open `http://localhost:3000` in your browser
   - Click "Check API Health" to verify backend connection
   - Explore the different sections

## 🏗️ Architecture

### Backend (FastAPI)

- **Framework**: FastAPI with async support
- **Database**: SQLite (development) / PostgreSQL (production)
- **Auto-Discovery**: Integrated with your existing auto-discovery system
- **API Documentation**: Available at `http://localhost:8000/docs`

### Frontend (HTML/JavaScript)

- **Simple HTML interface** for testing and development
- **Responsive design** with CSS Grid
- **Real-time API testing** capabilities
- **Ready for React/Vue upgrade**

## 📊 Features

### ✅ Implemented

- **Health Check**: API status monitoring
- **Component Discovery**: Browse estimators and data generators
- **Benchmark Management**: Create and list benchmarks
- **Auto-Discovery Integration**: Connects to your existing system
- **Database Integration**: SQLite with SQLAlchemy ORM
- **API Documentation**: Interactive Swagger UI

### 🔄 In Progress

- **Real-time Progress Tracking**: WebSocket integration
- **Benchmark Execution**: Celery job queue
- **Results Visualization**: Interactive charts
- **User Authentication**: JWT-based auth

### 📋 Planned

- **Advanced UI**: React/Vue frontend
- **File Upload**: Custom data support
- **Export Features**: CSV, JSON, PDF reports
- **Performance Analytics**: Trend analysis

## 🔧 API Endpoints

### Health & Status
- `GET /health` - API health check
- `GET /` - API information

### Components
- `GET /api/components/` - List all components
- `GET /api/components/estimators` - List estimators
- `GET /api/components/data-generators` - List data generators
- `GET /api/components/{component_name}` - Get component details
- `POST /api/components/refresh` - Refresh component discovery

### Benchmarks
- `GET /api/benchmarks/` - List benchmarks
- `POST /api/benchmarks/` - Create benchmark
- `GET /api/benchmarks/{id}` - Get benchmark details
- `GET /api/benchmarks/{id}/results` - Get benchmark results
- `POST /api/benchmarks/{id}/start` - Start benchmark execution
- `DELETE /api/benchmarks/{id}` - Delete benchmark

## 🎯 Use Cases

### Academic Research
- **Researchers** can quickly compare multiple estimators
- **Students** can learn about different methods through interactive examples
- **Collaborators** can share benchmark results and configurations

### Industry Applications
- **Data Scientists** can evaluate estimator performance on real data
- **Engineers** can select optimal methods for specific applications
- **Consultants** can generate professional reports for clients

### Development & Testing
- **Developers** can test new estimators against established benchmarks
- **Contributors** can validate their implementations
- **Maintainers** can monitor system performance and component health

## 🔍 Testing the Dashboard

1. **Start the backend server** (see Backend Setup above)

2. **Open the frontend** in your browser

3. **Test the API endpoints:**
   - Click "Check API Health" to verify the server is running
   - Click "Get All Components" to see discovered estimators and data generators
   - Click "Create Benchmark" to test benchmark creation
   - Click "List Benchmarks" to see created benchmarks

4. **Explore the API documentation:**
   - Visit `http://localhost:8000/docs` for interactive API documentation
   - Visit `http://localhost:8000/redoc` for alternative documentation

## 🛠️ Development

### Project Structure
```
web-dashboard/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── models/        # Database models
│   │   ├── services/      # Business logic
│   │   └── utils/         # Utilities
│   ├── main.py           # FastAPI application
│   ├── requirements.txt  # Python dependencies
│   └── venv/             # Virtual environment
├── frontend/
│   └── index.html        # Simple HTML interface
└── README.md
```

### Adding New Features

1. **Backend API Routes**: Add new endpoints in `app/api/`
2. **Database Models**: Define new models in `app/models/database.py`
3. **Services**: Implement business logic in `app/services/`
4. **Frontend**: Update `frontend/index.html` or create React components

## 🔗 Integration with DataExploratoryProject

The dashboard integrates seamlessly with your existing DataExploratoryProject:

- **Auto-Discovery System**: Automatically discovers new estimators and data generators
- **Component Registry**: Uses your existing component registry
- **Benchmarking Framework**: Leverages your comprehensive benchmarking scripts
- **Documentation**: Integrates with your API documentation

## 🚀 Next Steps

1. **Install Node.js** for React frontend development
2. **Set up PostgreSQL** for production database
3. **Configure Redis** for Celery job queue
4. **Add authentication** and user management
5. **Implement real-time features** with WebSockets
6. **Add visualization** with Plotly.js or D3.js

## 📞 Support

For questions or issues:
1. Check the API documentation at `http://localhost:8000/docs`
2. Review the auto-discovery system integration
3. Test individual endpoints using the frontend interface

---

**Status**: ✅ Backend API Complete | 🔄 Frontend Basic | 📋 Advanced Features Planned
