# Prospect to Lead Workflow - Web Dashboard

A beautiful, real-time web dashboard for monitoring and controlling your B2B prospecting workflow.

## 🚀 Features

### Real-Time Monitoring
- **Live Progress Tracking**: See workflow progress in real-time with animated progress bars
- **Step-by-Step Visualization**: Visual workflow steps with status indicators
- **Live Logs**: View agent logs as they execute
- **Interactive Charts**: Campaign metrics with Chart.js visualizations

### Workflow Control
- **Start/Stop Controls**: Launch and stop workflows directly from the web interface
- **Environment Status**: Check API key configuration at a glance
- **Error Handling**: Clear error messages and troubleshooting

### Results Analysis
- **Leads Overview**: Table view of all discovered prospects
- **Generated Messages**: Preview of AI-generated outreach content
- **AI Recommendations**: Performance analysis and optimization suggestions
- **Campaign Metrics**: Open rates, click rates, and engagement analytics

## 🎨 Interface Overview

### Main Dashboard Components

1. **Navigation Bar**
   - Start/Stop workflow buttons
   - Real-time status indicator

2. **Status Panel**
   - Animated progress bar
   - Current step indicator
   - Execution timing information

3. **Three-Column Layout**
   - **Left**: Workflow steps with status indicators
   - **Center**: API status and live logs viewer
   - **Right**: Campaign metrics and results summary

4. **Results Tabs**
   - **Leads Found**: Discovered prospects table
   - **Generated Messages**: AI-created outreach content
   - **AI Recommendations**: Optimization suggestions
   - **Errors**: Error tracking and troubleshooting

## 🔧 Technical Details

### Frontend Stack
- **HTML5** with semantic structure
- **Bootstrap 5** for responsive design
- **Chart.js** for data visualization
- **FontAwesome** for icons
- **Custom CSS** with animations and transitions

### Backend API Endpoints
- `GET /` - Main dashboard page
- `GET /api/status` - Workflow execution status
- `POST /api/start` - Start workflow execution
- `POST /api/stop` - Stop workflow execution
- `GET /api/config` - Workflow configuration
- `GET /api/environment` - API keys status
- `GET /api/logs/<agent>` - Agent-specific logs
- `GET /api/results` - Execution results
- `GET /api/campaign-feedback` - AI recommendations

### Real-Time Updates
- Status refreshes every 2 seconds
- Automatic progress tracking
- Live log streaming
- Dynamic chart updates

## 🎯 Usage

### Starting the Dashboard
```bash
# Method 1: Use the startup script
python start_dashboard.py

# Method 2: Direct Flask app
cd frontend
python app.py
```

### Accessing the Dashboard
- Open your browser to `http://localhost:5000`
- The dashboard will automatically open when using `start_dashboard.py`

### Workflow Operation
1. **Check Environment**: Verify API keys are configured (green checkmarks)
2. **Start Workflow**: Click the green "Start Workflow" button
3. **Monitor Progress**: Watch the progress bar and step indicators
4. **View Logs**: Select agents from the dropdown to see live logs
5. **Analyze Results**: Review leads, messages, and AI recommendations when complete

## 🎨 Visual Features

### Animations & Interactions
- **Pulsing indicators** for active steps
- **Smooth progress transitions** with gradient colors
- **Hover effects** on cards and buttons
- **Responsive design** for all screen sizes
- **Dark terminal-style logs** for better readability

### Status Indicators
- 🔵 **Blue**: Currently running
- 🟢 **Green**: Completed successfully  
- 🔴 **Red**: Failed/Error
- 🟡 **Yellow**: Stopped/Warning
- ⚪ **Gray**: Pending/Idle

### Responsive Design
- **Desktop**: Full three-column layout
- **Tablet**: Stacked layout with maintained functionality
- **Mobile**: Optimized single-column design

## 🔍 Monitoring Features

### Live Workflow Tracking
- Real-time step progression
- Individual agent status
- Execution timing
- Error detection and reporting

### Performance Analytics
- **Campaign Metrics**: Open/click/reply rates
- **Lead Quality**: Scoring and prioritization
- **AI Insights**: Performance analysis
- **Recommendations**: Optimization suggestions

### Log Analysis
- **Agent-specific logs**: View logs for each workflow step
- **Search and filter**: Find specific log entries
- **Export capability**: Save logs for analysis
- **Color-coded entries**: Different log levels

## 🚀 Advanced Features

### Auto-Refresh
- Status updates every 2 seconds
- Progress tracking without page reload
- Live log streaming
- Dynamic content updates

### Error Handling
- Clear error messages
- Modal dialogs for issues
- Troubleshooting suggestions
- Graceful fallback handling

### Data Visualization
- **Doughnut charts** for campaign metrics
- **Progress bars** with animations
- **Status badges** with color coding
- **Interactive tables** for results

## 🛠️ Customization

The dashboard is built with modularity in mind:

- **CSS**: Modify `static/style.css` for visual changes
- **Templates**: Edit `templates/dashboard.html` for layout changes
- **API**: Extend `app.py` for new endpoints
- **Components**: Add new dashboard sections easily

## 📱 Browser Support

Optimized for modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🔧 Development

### File Structure
```
frontend/
├── app.py              # Flask web server
├── templates/
│   └── dashboard.html  # Main dashboard template
├── static/
│   └── style.css       # Custom CSS styles
└── README.md          # This file
```

### Adding New Features
1. **New API Endpoint**: Add routes in `app.py`
2. **Frontend Updates**: Modify `dashboard.html`
3. **Styling**: Update `style.css`
4. **JavaScript**: Add functionality to dashboard template

The dashboard provides a complete, professional interface for monitoring your AI-powered B2B prospecting workflow! 🎉