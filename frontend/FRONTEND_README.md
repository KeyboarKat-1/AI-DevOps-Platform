# AI-Powered DevOps Dashboard Frontend

A modern, responsive AI DevOps platform built with React, Vite, and Tailwind CSS. Features real-time system monitoring, Docker container management, incident tracking, and AI-powered insights.

## 🚀 Features

- **Real-time Monitoring**: Live CPU, memory, disk, and network metrics with interactive charts
- **Docker Management**: Monitor and control containers with resource tracking
- **Incident Management**: Track, prioritize, and resolve system incidents
- **Deployment Tracking**: Monitor deployment history and status
- **AI Assistant**: Get intelligent insights and recommendations powered by AI
- **Beautiful UI**: Modern glassmorphism design with dark theme
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Real-time Charts**: Using Recharts for beautiful data visualization
- **API Integration**: Ready to integrate with FastAPI backend

## 📋 Tech Stack

- **React 19**: Latest React with hooks
- **Vite**: Lightning-fast development server
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Composable charting library
- **React Router DOM**: Client-side routing
- **Axios**: HTTP client for API requests
- **Lucide React**: Beautiful icon library

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── common.jsx     # Basic components (Button, Input, Card, etc.)
│   │   ├── dashboard.jsx  # Dashboard-specific components
│   │   ├── navigation.jsx # Sidebar and Navbar
│   │   ├── specialized.jsx# AI Assistant and specialized components
│   │   ├── charts.jsx     # Chart components using Recharts
│   │   └── index.js       # Component exports
│   ├── pages/             # Page components
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── DashboardPage.jsx
│   │   ├── DockerPage.jsx
│   │   ├── IncidentsPage.jsx
│   │   ├── DeploymentsPage.jsx
│   │   ├── SettingsPage.jsx
│   │   ├── AIAssistantPage.jsx
│   │   └── index.js       # Page exports
│   ├── services/          # API service layer
│   │   └── api.js        # Axios configuration and API calls
│   ├── hooks/             # Custom React hooks
│   │   └── index.js      # useLocalStorage, useAsync, useFetch, etc.
│   ├── utils/             # Utility functions
│   │   └── helpers.js    # Formatting, status helpers, etc.
│   ├── context/           # React Context providers
│   │   └── AuthContext.jsx# Authentication context
│   ├── layouts/           # Layout components
│   │   └── index.jsx     # MainLayout, AuthLayout
│   ├── App.jsx            # Main App component with routing
│   ├── main.jsx           # React DOM entry point
│   └── index.css          # Global styles with Tailwind
├── .env                   # Environment variables
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
├── vite.config.js         # Vite configuration
└── package.json           # Dependencies

```

## 🛠️ Installation

1. **Clone the repository**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
# Edit .env file
VITE_API_URL=http://127.0.0.1:8000
VITE_APP_NAME=DevOps Dashboard
```

4. **Start development server**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## 📦 Build

```bash
npm run build
```

Build artifacts will be in the `dist/` directory.

## 🧪 Linting

```bash
npm run lint
```

## 📖 Available Pages

### Authentication
- **Login** (`/login`) - User login with email/password
- **Register** (`/register`) - New user registration

### Dashboard
- **Dashboard** (`/dashboard`) - Main monitoring dashboard with metrics and charts
- **Docker** (`/docker`) - Container management and monitoring
- **Incidents** (`/incidents`) - Incident tracking and management
- **Deployments** (`/deployments`) - Deployment history and tracking
- **AI Assistant** (`/ai-assistant`) - AI-powered insights and recommendations
- **Settings** (`/settings`) - User preferences and configuration

## 🎨 UI Components

### Core Components (`components/common.jsx`)
- `Button` - Customizable button with variants and sizes
- `Input` - Text input with label and error states
- `Card` - Glass-morphism card container
- `Badge` - Status badges (success, warning, error, info)
- `LoadingSpinner` - Animated loading indicator
- `Tooltip` - Hover tooltips
- `Modal` - Dialog component
- `Alert` - Alert notifications
- `Pagination` - Pagination controls

### Dashboard Components (`components/dashboard.jsx`)
- `MetricsCard` - Metric display with change indicators
- `ChartCard` - Chart container component
- `ContainerCard` - Docker container display
- `DeploymentCard` - Deployment status card
- `IncidentCard` - Incident display
- `ActivityLog` - Recent activity timeline
- `StatBox` - Statistics display

### Navigation Components (`components/navigation.jsx`)
- `Sidebar` - Collapsible navigation sidebar
- `Navbar` - Top navigation bar with user menu
- `MobileMenu` - Mobile menu overlay

### Chart Components (`components/charts.jsx`)
- `CPUChart` - CPU usage area chart
- `MemoryChart` - Memory usage chart
- `DiskChart` - Disk usage bar chart
- `ContainerStatusChart` - Container status pie chart
- `NetworkChart` - Network I/O line chart
- `DeploymentTimelineChart` - Deployment timeline
- `ComparisonChart` - Multi-series comparison chart

### Specialized Components (`components/specialized.jsx`)
- `AIAssistant` - AI chat widget
- `SuggestionPanel` - AI suggestions display
- `HealthIndicator` - System health status

## 🔌 API Integration

The app is configured to connect to the FastAPI backend at `http://127.0.0.1:8000`.

### Available Services

**Authentication**
```javascript
authService.login(email, password)
authService.register(email, password, full_name)
authService.logout()
authService.getCurrentUser()
```

**Deployments**
```javascript
deploymentService.getDeployments()
deploymentService.getDeploymentById(id)
deploymentService.createDeployment(data)
deploymentService.updateDeployment(id, data)
deploymentService.deleteDeployment(id)
```

**Docker**
```javascript
dockerService.getContainers()
dockerService.getContainerStats(containerId)
dockerService.startContainer(containerId)
dockerService.stopContainer(containerId)
```

**Metrics**
```javascript
metricsService.getMetrics(timeRange)
metricsService.getCPUMetrics(timeRange)
metricsService.getMemoryMetrics(timeRange)
metricsService.getDiskMetrics(timeRange)
```

**Incidents**
```javascript
incidentService.getIncidents()
incidentService.getIncidentById(id)
incidentService.createIncident(data)
incidentService.resolveIncident(id)
```

**Insights**
```javascript
insightsService.getInsights()
insightsService.getAISuggestions(context)
```

## 🎯 Custom Hooks

- `useLocalStorage(key, initialValue)` - Persist state to localStorage
- `useAsync(callback, immediate)` - Async data fetching
- `useFetch(url, options)` - Fetch data from URL
- `useDebounce(value, delay)` - Debounce values
- `useMediaQuery(query)` - Media query matching

## 🛡️ Authentication Flow

1. User logs in at `/login`
2. Server returns `access_token`
3. Token is stored in localStorage
4. Token is added to all API requests via Axios interceptor
5. Protected routes check for valid token
6. Expired tokens trigger redirect to login

## 🎨 Theming

The app uses a dark theme with a premium blue accent color. Tailwind CSS configuration includes:

- Custom dark colors with 950 shades
- Glassmorphism effects
- Smooth animations and transitions
- Responsive breakpoints
- Custom shadows and glows

## 🚀 Performance Optimizations

- Code splitting with React Router
- Lazy loading of components
- Memoized components to prevent re-renders
- Optimized chart re-rendering
- Debounced search and input
- Efficient API polling

## 📱 Responsive Breakpoints

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

## 🔐 Security

- JWT token-based authentication
- Secure token storage
- API request interceptors
- Protected routes
- XSS protection via React
- CSRF protection via Axios

## 📝 Environment Variables

```env
VITE_API_URL=http://127.0.0.1:8000
VITE_APP_NAME=DevOps Dashboard
```

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

MIT License

## 🆘 Troubleshooting

### API Connection Issues
- Ensure backend is running at `http://127.0.0.1:8000`
- Check `.env` file for correct API URL
- Verify CORS settings on backend

### Build Errors
- Clear node_modules: `rm -rf node_modules`
- Reinstall dependencies: `npm install`
- Clear build cache: `rm -rf dist`

### Port Already in Use
- Default port is 5173, change with: `npm run dev -- --port 3000`

## 📞 Support

For issues and questions, please check the backend API documentation and ensure the FastAPI server is running correctly.

---

Built with ❤️ for DevOps teams
