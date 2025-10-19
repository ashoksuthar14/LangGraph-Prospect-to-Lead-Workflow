# 🚀 Prospect to Lead Workflow - AI-Powered B2B Lead Generation System

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

An **autonomous multi-agent B2B prospecting and outreach system** built with LangGraph that automates the entire lead generation process from prospect discovery to response tracking and optimization. This system combines the power of multiple AI agents to deliver a complete, hands-off B2B outreach pipeline.

## 📹 Demo Video

🎥 **[Watch the Complete System Demo](https://www.youtube.com/watch?v=ytsB0F4D18w)**

See the entire workflow in action - from lead discovery to email sending and analytics dashboard!

<img src="dashboard instruction.png" alt="AskMe Pro Chat Interface" />  

## ✨ Key Features

- 🤖 **7 Specialized AI Agents** working in perfect harmony
- 📊 **Real-time Web Dashboard** with live workflow monitoring
- 🎯 **Intelligent Lead Scoring** using ICP criteria and buying signals
- ✉️ **AI-Generated Personalized Emails** powered by Google Gemini
- 📈 **Live Analytics & Metrics** with campaign performance tracking
- 🔄 **Automatic Feedback Loop** with optimization recommendations
- 🌐 **Comprehensive API Integration** (Clay, Apollo, Explorium, SendGrid, etc.)
- 💡 **ReAct-Style Reasoning** for transparent decision-making
- 🖥️ **Two Execution Modes**: Dashboard UI or Direct Pipeline

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow Engine                    │
├─────────────────────────────────────────────────────────────────┤
│  ProspectSearch → Enrichment → Scoring → Content → Execute     │
│       ↓              ↓          ↓         ↓        ↓           │
│  ResponseTracking ← FeedbackTrainer ←────────────────────────   │
└─────────────────────────────────────────────────────────────────┘
```

## 🤖 AI Agents Deep Dive

The system employs 7 specialized AI agents that work together in a coordinated workflow:

### 1. 🔍 **ProspectSearchAgent**
**Role**: Lead Discovery & Initial Qualification
- **APIs Used**: Clay API, Apollo API
- **Key Functions**:
  - Searches for companies matching your ICP (Ideal Customer Profile)
  - Identifies decision-makers and key contacts
  - Detects buying signals (funding, hiring, leadership changes)
  - Validates contact information quality
- **Output**: List of qualified prospects with basic company and contact data

### 2. 📈 **DataEnrichmentAgent** 
**Role**: Data Enhancement & Intelligence Gathering
- **APIs Used**: Explorium API (formerly Clearbit)
- **Key Functions**:
  - Enriches basic prospect data with comprehensive company information
  - Gathers technology stack information
  - Collects funding history and financial data
  - Validates and standardizes contact information
- **Output**: Fully enriched lead profiles with detailed company intelligence

### 3. 🎯 **ScoringAgent**
**Role**: Lead Prioritization & Qualification
- **APIs Used**: Internal scoring algorithms
- **Key Functions**:
  - Scores leads based on ICP fit (company size, industry, revenue)
  - Evaluates buying signals strength
  - Analyzes technology stack compatibility
  - Provides detailed scoring reasoning
- **Output**: Ranked leads with priority scores (1-10) and qualification reasoning

### 4. ✍️ **OutreachContentAgent**
**Role**: Personalized Message Generation
- **APIs Used**: Google Gemini AI
- **Key Functions**:
  - Generates highly personalized email subject lines
  - Creates contextual email body content
  - Incorporates company-specific pain points
  - Adapts tone and messaging to buyer persona
- **Output**: Personalized email messages with subject lines and tracking data

### 5. 📧 **OutreachExecutorAgent**
**Role**: Email Delivery & Campaign Execution
- **APIs Used**: SendGrid API
- **Key Functions**:
  - Validates email addresses before sending
  - Sends personalized emails via SendGrid
  - Implements rate limiting and delivery optimization
  - Generates unique tracking IDs for each email
- **Output**: Delivery status reports and campaign tracking data

### 6. 📊 **ResponseTrackerAgent**
**Role**: Engagement Monitoring & Analytics
- **APIs Used**: SendGrid Events API
- **Key Functions**:
  - Tracks email opens, clicks, and responses
  - Monitors meeting bookings and conversions
  - Calculates engagement metrics (open rates, click rates)
  - Identifies high-engagement prospects
- **Output**: Real-time engagement metrics and response analytics

### 7. 🧠 **FeedbackTrainerAgent**
**Role**: Performance Analysis & Optimization
- **APIs Used**: Google Sheets API (optional)
- **Key Functions**:
  - Analyzes campaign performance data
  - Identifies optimization opportunities
  - Generates actionable recommendations
  - Logs insights for future campaign improvements
- **Output**: Performance reports and optimization recommendations

## 📋 Prerequisites

- Python 3.9+
- API keys for external services (see Setup section)
- Virtual environment (recommended)

## 🔧 Installation

### 1. Clone and Setup Environment

```bash
# Clone the repository
cd prospect_to_lead_workflow

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
```

Required API keys:
- **Clay API**: Sign up at [clay.com](https://www.clay.com/)
- **Apollo API**: Sign up at [apollo.io](https://www.apollo.io/)
- **Clearbit API**: Sign up at [clearbit.com](https://clearbit.com/)
- **Gemini API**: Get key at [Google AI Studio](https://makersuite.google.com/app/apikey)
- **SendGrid API**: Sign up at [sendgrid.com](https://sendgrid.com/)
- **Google Sheets**: Follow [gspread setup guide](https://docs.gspread.org/en/latest/oauth2.html)

### 3. Verify Installation

```bash
# Test the workflow with mock data
python langgraph_builder.py --config workflow.json --verbose
```

## 🚀 How to Run the Project

The system offers **two execution modes** to fit different use cases:

### 🌐 Option 1: Web Dashboard (Recommended)

The **interactive web dashboard** provides real-time monitoring, live metrics, and workflow control.

#### Quick Start with Dashboard:
```bash
# Start the dashboard server
python start_dashboard.py
```

Then open your browser to: **http://127.0.0.1:5000**

#### Dashboard Features:
- 📏 **Live Workflow Monitoring**: See each agent's progress in real-time
- 📊 **Real-time Metrics**: Live campaign performance dashboard
- 📋 **Agent Logs**: View detailed logs from each AI agent
- 🎨 **Visual Workflow**: Interactive workflow step visualization
- ▶️ **Start/Stop Controls**: Control workflow execution with buttons
- 📈 **Results Tables**: Browse found leads, generated messages, and recommendations
- 🔍 **Environment Status**: Check API key configuration

#### Dashboard Screenshots:
```
┌────────────────────────────────────────────────────────────┐
│                    Results Summary                      │
├────────────────────────────────────────────────────────────┤
│     4        4         4        9.8/10      │
│ Leads Found | Messages | Emails Sent | AI Score    │
└────────────────────────────────────────────────────────────┘
```

### ⚙️ Option 2: Direct Pipeline Execution

For **headless execution**, automation, or integration into other systems.

#### Basic Pipeline Commands:
```bash
# Run the complete workflow (headless)
python langgraph_builder.py

# Run with custom configuration
python langgraph_builder.py --config my_workflow.json

# Enable verbose logging
python langgraph_builder.py --verbose

# Run in test mode (no actual emails sent)
ENABLE_EMAIL_SENDING=false python langgraph_builder.py
```

#### Pipeline Features:
- 📄 **Command Line Output**: See progress and results in terminal
- 📝 **Log Files**: Detailed logs saved to `logs/` directory
- ⚙️ **Scriptable**: Perfect for automation and CI/CD
- 📊 **JSON Results**: Results saved to structured JSON files
- 🔄 **Batch Processing**: Process multiple campaigns sequentially

### Programmatic Usage

```python
from langgraph_builder import LangGraphWorkflowBuilder

# Initialize workflow
builder = LangGraphWorkflowBuilder('workflow.json')

# Execute workflow
results = builder.execute()

# Get execution summary
summary = builder.get_execution_summary()
print(f"Success rate: {summary['successful_steps']}/{summary['total_steps']}")
```

### Configuration Customization

Edit `workflow.json` to customize:

```json
{
  "config": {
    "icp": {
      "industry": ["SaaS", "Technology"],
      "employee_count": {"min": 100, "max": 1000}
    },
    "scoring": {
      "weights": {
        "company_size": 0.3,
        "industry_match": 0.25,
        "technology_stack": 0.2,
        "recent_signals": 0.25
      }
    }
  }
}
```

## 📊 Output Examples

### Prospect Search Results
```json
{
  "leads": [
    {
      "company": "TechCorp Solutions",
      "contact_name": "Sarah Johnson",
      "email": "sarah.johnson@techcorp.com",
      "title": "VP of Sales",
      "company_size": 150,
      "industry": "SaaS",
      "signals": ["recent_funding", "hiring_for_sales"]
    }
  ]
}
```

### Lead Scoring Results
```json
{
  "ranked_leads": [
    {
      "lead": {...},
      "score": 8.7,
      "priority": "high",
      "reasoning": [
        "company_size: 10/10 - Perfect company size fit",
        "recent_signals: 8/10 - Strong buying signals present"
      ]
    }
  ]
}
```

### Campaign Analytics
```json
{
  "metrics": {
    "open_rate": 0.35,
    "click_rate": 0.08,
    "reply_rate": 0.03,
    "meeting_rate": 0.015
  },
  "recommendations": [
    {
      "type": "subject_line",
      "suggestion": "Focus on problem-specific subjects",
      "confidence": 0.8
    }
  ]
}
```

## 🔍 Monitoring & Logging

### Log Files
- **Agent logs**: `logs/{agent_id}.log`
- **Workflow logs**: Console output
- **Campaign feedback**: `campaign_feedback.json`

### Google Sheets Integration
Configure Google Sheets to track:
- Campaign performance metrics
- Optimization recommendations
- Response analytics

## 🛠️ Extension Guide

### Adding New Agents

1. **Create Agent Class**:
```python
# agents/my_custom_agent.py
from .base_agent import BaseAgent, AgentRegistry

@AgentRegistry.register
class MyCustomAgent(BaseAgent):
    def execute(self, inputs):
        # Your agent logic here
        return {"result": "success"}
```

2. **Update workflow.json**:
```json
{
  "steps": [
    {
      "id": "my_custom_step",
      "agent": "MyCustomAgent",
      "inputs": {...},
      "instructions": "Description of what this agent does"
    }
  ]
}
```

3. **Update agents/__init__.py**:
```python
from .my_custom_agent import MyCustomAgent
__all__.append('MyCustomAgent')
```

### Adding New APIs

1. **Add credentials to .env**:
```bash
NEW_API_KEY=your_api_key_here
```

2. **Implement API client in agent**:
```python
def _setup_api_client(self):
    api_key = self.tool_clients.get('NewAPI', {}).get('api_key')
    if api_key:
        self.client = NewAPIClient(api_key)
```

### Custom Scoring Logic

Modify `ScoringAgent._score_*` methods:

```python
def _score_custom_criteria(self, lead_data):
    # Your custom scoring logic
    score = 0.0
    reasoning = "Custom scoring rationale"
    return score, reasoning
```

### Workflow Modifications

Edit `workflow.json` to:
- Add new steps
- Change agent flow
- Modify ICP criteria
- Adjust scoring weights
- Customize output schemas

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents.py

# Run with coverage
pytest --cov=agents
```

### Mock Mode
Set environment variables for testing:
```bash
ENABLE_MOCK_APIS=true
ENABLE_EMAIL_SENDING=false
USE_SAMPLE_DATA=true
```

## 🔒 Security Considerations

1. **API Key Protection**: Store in `.env`, never commit to repo
2. **Email Validation**: Built-in email validation prevents sending to invalid addresses
3. **Rate Limiting**: Configured rate limits prevent API quota exhaustion
4. **Data Encryption**: Sensitive data can be encrypted using `ENCRYPTION_KEY`
5. **Webhook Security**: Use `WEBHOOK_SECRET` for webhook validation

## 🐛 Troubleshooting

### Common Issues

**LangGraph not available warning**:
```bash
pip install langgraph langchain langchain-core
```

**API authentication errors**:
- Verify API keys in `.env`
- Check API key permissions and quotas

**Email sending failures**:
- Verify SendGrid API key and sender email
- Check email validation logic

**Memory issues with large datasets**:
- Reduce `DEFAULT_BATCH_SIZE` in `.env`
- Implement pagination in agents

### Debug Mode

```bash
# Enable detailed logging
export LOG_LEVEL=DEBUG
python langgraph_builder.py --verbose
```

## 📈 Performance Optimization

1. **Batch Processing**: Configure optimal batch sizes
2. **Rate Limiting**: Respect API limits
3. **Caching**: Implement response caching for repeated queries
4. **Async Processing**: Use aiohttp for concurrent API calls
5. **Database Integration**: Store results for analysis

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for all public methods
- Add unit tests for new features
- Update README for new functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check this README and inline documentation
- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions

## 🔄 Version History

### v1.0.0 (Current)
- ✅ **Complete 7-Agent Workflow** - End-to-end autonomous prospecting
- ✅ **Real-time Web Dashboard** - Live monitoring and control interface
- ✅ **Multi-API Integration** - Clay, Apollo, Explorium, Gemini, SendGrid
- ✅ **Intelligent Lead Scoring** - ICP-based qualification with buying signals
- ✅ **AI Content Generation** - Personalized emails using Gemini AI
- ✅ **Campaign Analytics** - Performance tracking and optimization
- ✅ **Flexible Execution** - Dashboard UI or headless pipeline modes

### 🗺️ Roadmap (What's Next)
- [ ] **LinkedIn Integration** - Advanced personalization with LinkedIn data
- [ ] **Multi-channel Outreach** - LinkedIn messages, Twitter DMs, SMS
- [ ] **CRM Integration** - Salesforce, HubSpot, Pipedrive connectors
- [ ] **Advanced Analytics** - A/B testing, conversion attribution
- [ ] **Team Collaboration** - Multi-user dashboard, role permissions
- [ ] **API Webhooks** - Real-time integrations with external systems

---

## 🚀 Quick Start Guide

### 🎆 30-Second Setup

```bash
# 1. Clone and setup
git clone <repository-url>
cd prospect_to_lead_workflow
python -m venv venv

# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

### 🔑 2. Configure Your API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys:
# SENDGRID_API_KEY=your_sendgrid_key_here
# SENDER_EMAIL=your_verified_email@domain.com  
# GEMINI_API_KEY=your_gemini_key_here
# etc...
```

### 🎆 3A. Run with Dashboard (Recommended)

```bash
# Start the web dashboard
python start_dashboard.py

# Open browser to: http://127.0.0.1:5000
# Click "Start Workflow" button
# Watch the magic happen in real-time! ✨
```

### 🎆 3B. Or Run Direct Pipeline

```bash
# Run the complete workflow (headless)
python langgraph_builder.py

# Results will be displayed in terminal
# Logs saved to logs/ directory
```

### 🎉 Expected Results

After execution, you should see:
- ✅ **4+ Qualified Leads** discovered from Clay/Apollo
- ✅ **Enriched Company Data** with technology stacks
- ✅ **AI Scores 8.5-9.8/10** for lead quality
- ✅ **4 Personalized Emails** generated by Gemini AI
- ✅ **Emails Successfully Sent** via SendGrid
- ✅ **Campaign Analytics** and optimization recommendations

**🎉 Congratulations!** You now have a fully autonomous B2B prospecting system that:
1. Finds qualified prospects automatically
2. Scores them intelligently 
3. Writes personalized emails
4. Sends them at scale
5. Tracks performance and optimizes

---

## 📝 Additional Resources

- 🎥 **[Complete Video Tutorial](https://www.youtube.com/watch?v=ytsB0F4D18w)** - Step-by-step setup guide
- 📚 **API Documentation** - Check individual agent files for detailed API docs
- 🐞 **Issues & Support** - Report bugs or request features on GitHub
- 📈 **Advanced Configuration** - See `workflow.json` for customization options


