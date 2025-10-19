"""
ResponseTrackerAgent - Tracks email responses and engagement metrics
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentRegistry


@AgentRegistry.register
class ResponseTrackerAgent(BaseAgent):
    """
    Agent responsible for tracking email engagement metrics including
    opens, clicks, replies, and meeting bookings.
    """

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate ResponseTrackerAgent specific inputs."""
        required_fields = ['campaign_id', 'sent_status']
        
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(inputs['sent_status'], list):
            self.logger.error("Field 'sent_status' must be a list")
            return False
        
        return super().validate_inputs(inputs)

    def _simulate_engagement_data(self, sent_emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simulate email engagement data for demonstration.
        In production, this would query SendGrid or other email service APIs.
        
        Args:
            sent_emails: List of successfully sent emails
            
        Returns:
            List of engagement data for each email
        """
        engagement_data = []
        
        # Simulate realistic engagement rates
        open_rate = 0.35      # 35% open rate
        click_rate = 0.08     # 8% click rate (of opened emails)
        reply_rate = 0.03     # 3% reply rate
        meeting_rate = 0.015  # 1.5% meeting booking rate
        
        for email in sent_emails:
            if email['status'] != 'sent':
                continue
            
            # Simulate engagement with realistic probabilities
            opened = random.random() < open_rate
            clicked = opened and random.random() < (click_rate / open_rate)  # Only opened emails can be clicked
            replied = random.random() < reply_rate
            meeting_booked = replied and random.random() < (meeting_rate / reply_rate)
            
            # Simulate response sentiment for replied emails
            sentiment = self._generate_response_sentiment() if replied else None
            
            engagement = {
                'lead_id': email['lead_id'],
                'email': email['email'],
                'message_id': email['message_id'],
                'opened': opened,
                'clicked': clicked,
                'replied': replied,
                'meeting_booked': meeting_booked,
                'response_sentiment': sentiment,
                'open_time': self._generate_engagement_time('open') if opened else None,
                'click_time': self._generate_engagement_time('click') if clicked else None,
                'reply_time': self._generate_engagement_time('reply') if replied else None,
                'tracking_data': {
                    'user_agent': self._generate_user_agent() if opened else None,
                    'ip_location': self._generate_ip_location() if opened else None,
                    'device_type': self._generate_device_type() if opened else None
                }
            }
            
            engagement_data.append(engagement)
        
        return engagement_data

    def _generate_response_sentiment(self) -> str:
        """Generate realistic response sentiment."""
        sentiments = ['positive', 'neutral', 'negative', 'interested', 'not_interested']
        weights = [0.25, 0.35, 0.15, 0.15, 0.10]  # Realistic sentiment distribution
        return random.choices(sentiments, weights=weights)[0]

    def _generate_engagement_time(self, action_type: str) -> str:
        """
        Generate realistic engagement timestamps.
        
        Args:
            action_type: Type of engagement ('open', 'click', 'reply')
            
        Returns:
            ISO timestamp string
        """
        # Generate engagement time within realistic windows
        if action_type == 'open':
            # Opens typically happen within hours to days
            hours_delay = random.uniform(0.5, 48)
        elif action_type == 'click':
            # Clicks happen shortly after opens
            hours_delay = random.uniform(0.1, 2)
        elif action_type == 'reply':
            # Replies can take longer
            hours_delay = random.uniform(2, 72)
        else:
            hours_delay = 1
        
        engagement_time = datetime.now() + timedelta(hours=hours_delay)
        return engagement_time.isoformat()

    def _generate_user_agent(self) -> str:
        """Generate realistic user agent string."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        return random.choice(user_agents)

    def _generate_ip_location(self) -> str:
        """Generate realistic IP location."""
        locations = [
            "San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA",
            "Boston, MA", "Denver, CO", "Atlanta, GA", "Chicago, IL"
        ]
        return random.choice(locations)

    def _generate_device_type(self) -> str:
        """Generate realistic device type."""
        devices = ["desktop", "mobile", "tablet"]
        weights = [0.6, 0.35, 0.05]  # Desktop is most common for B2B
        return random.choices(devices, weights=weights)[0]

    def _calculate_metrics(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate aggregate engagement metrics.
        
        Args:
            responses: List of email response data
            
        Returns:
            Dictionary containing aggregate metrics
        """
        if not responses:
            return {
                "total_sent": 0,
                "open_rate": 0.0,
                "click_rate": 0.0,
                "reply_rate": 0.0,
                "meeting_rate": 0.0
            }
        
        total_sent = len(responses)
        opens = sum(1 for r in responses if r['opened'])
        clicks = sum(1 for r in responses if r['clicked'])
        replies = sum(1 for r in responses if r['replied'])
        meetings = sum(1 for r in responses if r['meeting_booked'])
        
        return {
            "total_sent": total_sent,
            "opens": opens,
            "clicks": clicks,
            "replies": replies,
            "meetings": meetings,
            "open_rate": opens / total_sent if total_sent > 0 else 0.0,
            "click_rate": clicks / total_sent if total_sent > 0 else 0.0,
            "reply_rate": replies / total_sent if total_sent > 0 else 0.0,
            "meeting_rate": meetings / total_sent if total_sent > 0 else 0.0,
            "click_to_open_rate": clicks / opens if opens > 0 else 0.0,
            "meeting_to_reply_rate": meetings / replies if replies > 0 else 0.0
        }

    def _analyze_performance_trends(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze performance trends and patterns.
        
        Args:
            responses: List of email response data
            
        Returns:
            Dictionary containing trend analysis
        """
        # Group responses by sentiment
        sentiment_breakdown = {}
        for response in responses:
            if response['replied']:
                sentiment = response['response_sentiment']
                sentiment_breakdown[sentiment] = sentiment_breakdown.get(sentiment, 0) + 1
        
        # Analyze device patterns
        device_breakdown = {}
        for response in responses:
            if response['opened']:
                device = response['tracking_data'].get('device_type')
                if device:
                    device_breakdown[device] = device_breakdown.get(device, 0) + 1
        
        # Calculate time to engagement metrics
        engagement_times = []
        for response in responses:
            if response['opened'] and response['open_time']:
                # In a real implementation, calculate actual time difference
                # For demo, generate sample time difference
                engagement_times.append(random.uniform(1, 48))  # Hours
        
        avg_time_to_open = sum(engagement_times) / len(engagement_times) if engagement_times else 0
        
        return {
            "sentiment_breakdown": sentiment_breakdown,
            "device_breakdown": device_breakdown,
            "average_time_to_open_hours": round(avg_time_to_open, 2),
            "best_performing_segment": self._identify_best_segment(responses),
            "improvement_opportunities": self._identify_improvements(responses)
        }

    def _identify_best_segment(self, responses: List[Dict[str, Any]]) -> str:
        """Identify the best performing segment based on engagement."""
        # Simple analysis - in practice this would be more sophisticated
        reply_rate = sum(1 for r in responses if r['replied']) / len(responses) if responses else 0
        
        if reply_rate > 0.05:
            return "high_engagement_segment"
        elif reply_rate > 0.02:
            return "medium_engagement_segment"
        else:
            return "low_engagement_segment"

    def _identify_improvements(self, responses: List[Dict[str, Any]]) -> List[str]:
        """Identify areas for improvement based on engagement data."""
        improvements = []
        
        if not responses:
            return ["No data available for analysis"]
        
        open_rate = sum(1 for r in responses if r['opened']) / len(responses)
        click_rate = sum(1 for r in responses if r['clicked']) / len(responses)
        reply_rate = sum(1 for r in responses if r['replied']) / len(responses)
        
        if open_rate < 0.25:
            improvements.append("Consider improving subject lines to increase open rates")
        
        if click_rate < 0.05:
            improvements.append("Add more compelling call-to-action to increase click rates")
        
        if reply_rate < 0.02:
            improvements.append("Personalize messages further to increase response rates")
        
        # Analyze device patterns for mobile optimization
        mobile_opens = sum(1 for r in responses if r['opened'] and 
                          r['tracking_data'].get('device_type') == 'mobile')
        if mobile_opens > len(responses) * 0.3:
            improvements.append("Optimize email formatting for mobile devices")
        
        return improvements if improvements else ["Performance is within expected ranges"]

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute response tracking and metric analysis.
        
        Args:
            inputs: Dictionary containing campaign_id and sent_status
            
        Returns:
            Dictionary containing engagement responses and metrics
        """
        campaign_id = inputs['campaign_id']
        sent_status = inputs['sent_status']
        
        self.reason(inputs, "analyzing_campaign_engagement")
        
        # Filter to only successfully sent emails
        sent_emails = [email for email in sent_status if email['status'] == 'sent']
        
        if not sent_emails:
            self.logger.warning("No successfully sent emails to track")
            return {
                "responses": [],
                "metrics": self._calculate_metrics([]),
                "campaign_id": campaign_id,
                "tracking_timestamp": datetime.now().isoformat(),
                "analysis": {
                    "sentiment_breakdown": {},
                    "device_breakdown": {},
                    "average_time_to_open_hours": 0,
                    "best_performing_segment": "no_data",
                    "improvement_opportunities": ["No sent emails to analyze"]
                }
            }
        
        # Simulate engagement data (in production, query actual email service APIs)
        responses = self._simulate_engagement_data(sent_emails)
        
        # Calculate aggregate metrics
        metrics = self._calculate_metrics(responses)
        
        # Perform trend analysis
        analysis = self._analyze_performance_trends(responses)
        
        self.reason({
            "campaign_id": campaign_id,
            "total_tracked": len(responses),
            "open_rate": f"{metrics['open_rate']:.1%}",
            "reply_rate": f"{metrics['reply_rate']:.1%}",
            "meeting_rate": f"{metrics['meeting_rate']:.1%}"
        }, "tracking_analysis_complete")
        
        return {
            "responses": responses,
            "metrics": metrics,
            "campaign_id": campaign_id,
            "tracking_timestamp": datetime.now().isoformat(),
            "analysis": analysis,
            "total_tracked_emails": len(responses)
        }