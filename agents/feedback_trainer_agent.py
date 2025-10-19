"""
FeedbackTrainerAgent - Analyzes campaign performance and generates recommendations
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentRegistry

# Mock Google Sheets API for demonstration
try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    print("Warning: gspread not installed. Using mock Google Sheets integration.")


@AgentRegistry.register
class FeedbackTrainerAgent(BaseAgent):
    """
    Agent responsible for analyzing campaign performance, generating
    optimization recommendations, and logging results to Google Sheets.
    """

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """Initialize the FeedbackTrainerAgent with Google Sheets configuration."""
        super().__init__(agent_id, config)
        self._setup_sheets()

    def _setup_sheets(self):
        """Setup Google Sheets API client."""
        sheets_config = self.tool_clients.get('GoogleSheetsAPI', {})
        sheet_id = sheets_config.get('sheet_id')
        credentials_file = sheets_config.get('credentials_file')
        
        if GSPREAD_AVAILABLE and sheet_id and credentials_file:
            try:
                # In production, use actual credentials file
                # creds = Credentials.from_service_account_file(credentials_file, scopes=[...])
                # self.gc = gspread.authorize(creds)
                # self.sheet = self.gc.open_by_key(sheet_id)
                self.sheets_configured = True
                self.logger.info("Google Sheets API configured successfully (mock)")
            except Exception as e:
                self.sheets_configured = False
                self.logger.warning(f"Google Sheets API configuration failed: {e}")
        else:
            self.sheets_configured = False
            self.logger.warning("Google Sheets API not configured - using mock integration")

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate FeedbackTrainerAgent specific inputs."""
        required_fields = ['responses', 'metrics']
        
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(inputs['responses'], list):
            self.logger.error("Field 'responses' must be a list")
            return False
        
        if not isinstance(inputs['metrics'], dict):
            self.logger.error("Field 'metrics' must be a dictionary")
            return False
        
        return super().validate_inputs(inputs)

    def _analyze_performance_vs_benchmarks(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze performance against industry benchmarks.
        
        Args:
            metrics: Campaign performance metrics
            
        Returns:
            Dictionary containing benchmark analysis
        """
        # Industry benchmarks for B2B outreach
        benchmarks = {
            'open_rate': 0.25,      # 25% typical B2B open rate
            'click_rate': 0.05,     # 5% typical click rate
            'reply_rate': 0.02,     # 2% typical reply rate
            'meeting_rate': 0.01    # 1% typical meeting booking rate
        }
        
        analysis = {}
        
        for metric, benchmark in benchmarks.items():
            current_value = metrics.get(metric, 0.0)
            performance_ratio = current_value / benchmark if benchmark > 0 else 0
            
            if performance_ratio >= 1.2:
                performance_status = "above_benchmark"
                recommendation = f"Excellent {metric.replace('_', ' ')} performance - 20% above industry benchmark"
            elif performance_ratio >= 1.0:
                performance_status = "at_benchmark"
                recommendation = f"Good {metric.replace('_', ' ')} performance - meeting industry benchmark"
            elif performance_ratio >= 0.8:
                performance_status = "slightly_below"
                recommendation = f"Fair {metric.replace('_', ' ')} - consider optimization strategies"
            else:
                performance_status = "below_benchmark"
                recommendation = f"Low {metric.replace('_', ' ')} - requires immediate attention"
            
            analysis[metric] = {
                'current_value': current_value,
                'benchmark': benchmark,
                'performance_ratio': round(performance_ratio, 2),
                'status': performance_status,
                'recommendation': recommendation
            }
        
        return analysis

    def _generate_icp_recommendations(self, responses: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Generate recommendations for ICP refinement based on engagement patterns.
        
        Args:
            responses: List of email response data
            
        Returns:
            List of ICP-related recommendations
        """
        recommendations = []
        
        if not responses:
            return [{
                'type': 'icp_targeting',
                'current_value': 'Unknown',
                'suggested_value': 'Need more data',
                'reasoning': 'Insufficient response data for ICP analysis',
                'confidence': 0.1
            }]
        
        # Analyze response patterns by company characteristics
        replied_responses = [r for r in responses if r['replied']]
        positive_responses = [r for r in replied_responses if 
                            r['response_sentiment'] in ['positive', 'interested']]
        
        reply_rate = len(replied_responses) / len(responses)
        positive_rate = len(positive_responses) / len(replied_responses) if replied_responses else 0
        
        # Company size recommendations
        if reply_rate < 0.02:  # Low reply rate
            recommendations.append({
                'type': 'company_size_targeting',
                'current_value': 'Broad size range (100-2000 employees)',
                'suggested_value': 'Focus on 200-800 employees',
                'reasoning': 'Low reply rate suggests targeting may be too broad. Mid-market companies (200-800) typically have better response rates.',
                'confidence': 0.7
            })
        
        # Industry focus recommendations
        if positive_rate < 0.5 and replied_responses:  # Low positive sentiment
            recommendations.append({
                'type': 'industry_focus',
                'current_value': 'SaaS, Technology, Financial Services',
                'suggested_value': 'Focus primarily on SaaS and FinTech',
                'reasoning': 'Mixed sentiment suggests some industries may be less receptive. Consider narrowing focus.',
                'confidence': 0.6
            })
        
        # Timing recommendations
        mobile_engagement = sum(1 for r in responses if r['opened'] and 
                              r['tracking_data'].get('device_type') == 'mobile')
        if mobile_engagement > len(responses) * 0.4:  # High mobile engagement
            recommendations.append({
                'type': 'timing_optimization',
                'current_value': 'Standard business hours',
                'suggested_value': 'Include evening and weekend sends',
                'reasoning': 'High mobile engagement suggests prospects read emails outside traditional hours.',
                'confidence': 0.8
            })
        
        return recommendations

    def _generate_messaging_recommendations(self, responses: List[Dict[str, Any]], 
                                          metrics: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate recommendations for message optimization.
        
        Args:
            responses: List of email response data
            metrics: Campaign performance metrics
            
        Returns:
            List of messaging-related recommendations
        """
        recommendations = []
        
        open_rate = metrics.get('open_rate', 0.0)
        click_rate = metrics.get('click_rate', 0.0)
        reply_rate = metrics.get('reply_rate', 0.0)
        
        # Subject line recommendations
        if open_rate < 0.25:
            recommendations.append({
                'type': 'subject_line',
                'current_value': 'Generic/company-focused subjects',
                'suggested_value': 'Problem-focused, benefit-driven subjects',
                'reasoning': f'Open rate of {open_rate:.1%} is below benchmark. Try subject lines focusing on specific pain points.',
                'confidence': 0.8
            })
        
        # Email content recommendations
        if click_rate < 0.05:
            recommendations.append({
                'type': 'email_content',
                'current_value': 'Standard value proposition',
                'suggested_value': 'Include specific metrics and case studies',
                'reasoning': f'Click rate of {click_rate:.1%} suggests content lacks compelling elements. Add concrete value evidence.',
                'confidence': 0.7
            })
        
        # Personalization recommendations
        if reply_rate < 0.02:
            recommendations.append({
                'type': 'personalization',
                'current_value': 'Basic company and role personalization',
                'suggested_value': 'Deep research-based personalization',
                'reasoning': f'Reply rate of {reply_rate:.1%} indicates insufficient personalization. Reference specific company initiatives.',
                'confidence': 0.9
            })
        
        # Call-to-action recommendations
        meeting_rate = metrics.get('meeting_rate', 0.0)
        if meeting_rate < 0.01 and reply_rate > 0.02:  # Good replies, poor conversion
            recommendations.append({
                'type': 'call_to_action',
                'current_value': 'Generic meeting request',
                'suggested_value': 'Specific value-driven CTA',
                'reasoning': 'Good reply rate but low meeting conversion suggests weak call-to-action. Be more specific about meeting value.',
                'confidence': 0.8
            })
        
        return recommendations

    def _calculate_overall_score(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate overall campaign performance score.
        
        Args:
            metrics: Campaign performance metrics
            
        Returns:
            Score from 0-10
        """
        # Weighted scoring based on business impact
        weights = {
            'open_rate': 0.2,
            'click_rate': 0.2,
            'reply_rate': 0.4,
            'meeting_rate': 0.2
        }
        
        benchmarks = {
            'open_rate': 0.25,
            'click_rate': 0.05,
            'reply_rate': 0.02,
            'meeting_rate': 0.01
        }
        
        score = 0.0
        
        for metric, weight in weights.items():
            current_value = metrics.get(metric, 0.0)
            benchmark = benchmarks[metric]
            
            # Score each metric from 0-10 based on performance vs benchmark
            metric_score = min(10, (current_value / benchmark) * 10) if benchmark > 0 else 0
            score += metric_score * weight
        
        return round(score, 1)

    def _generate_key_insights(self, responses: List[Dict[str, Any]], 
                             metrics: Dict[str, Any]) -> List[str]:
        """
        Generate key insights from campaign data.
        
        Args:
            responses: List of email response data
            metrics: Campaign performance metrics
            
        Returns:
            List of key insights
        """
        insights = []
        
        if not responses:
            return ["Insufficient data for meaningful insights"]
        
        # Engagement timing insights
        engagement_times = []
        for response in responses:
            if response['opened'] and response['open_time']:
                # In production, calculate actual time patterns
                insights.append("Most engagement occurs within 24 hours of sending")
                break
        
        # Device insights
        mobile_opens = sum(1 for r in responses if r['opened'] and 
                          r['tracking_data'].get('device_type') == 'mobile')
        if mobile_opens > len([r for r in responses if r['opened']]) * 0.3:
            insights.append("High mobile engagement - ensure mobile-optimized content")
        
        # Sentiment insights
        positive_replies = sum(1 for r in responses if r['replied'] and 
                             r['response_sentiment'] in ['positive', 'interested'])
        total_replies = sum(1 for r in responses if r['replied'])
        
        if total_replies > 0:
            positive_rate = positive_replies / total_replies
            if positive_rate > 0.6:
                insights.append("High positive sentiment - messaging resonates well with target audience")
            elif positive_rate < 0.4:
                insights.append("Mixed sentiment - consider refining value proposition")
        
        # Performance insights
        open_rate = metrics.get('open_rate', 0)
        reply_rate = metrics.get('reply_rate', 0)
        
        if open_rate > 0.3 and reply_rate < 0.02:
            insights.append("Good open rates but low replies - content may not match subject line expectations")
        elif open_rate < 0.2 and reply_rate > 0.02:
            insights.append("Low opens but good reply rate - subject lines may be filtering for quality")
        
        return insights if insights else ["Campaign performance is within typical ranges"]

    def _log_to_sheets(self, recommendations: List[Dict[str, str]], 
                      performance_summary: Dict[str, Any]) -> bool:
        """
        Log recommendations and performance data to Google Sheets.
        
        Args:
            recommendations: List of optimization recommendations
            performance_summary: Summary of campaign performance
            
        Returns:
            True if successful, False otherwise
        """
        if not self.sheets_configured:
            self.logger.warning("Sheets not configured - logging locally")
            # Log to local file as fallback
            log_data = {
                'timestamp': datetime.now().isoformat(),
                'performance_summary': performance_summary,
                'recommendations': recommendations
            }
            
            try:
                with open('campaign_feedback.json', 'a') as f:
                    f.write(json.dumps(log_data) + '\n')
                self.logger.info("Feedback logged to local file: campaign_feedback.json")
                return True
            except Exception as e:
                self.logger.error(f"Failed to log to local file: {e}")
                return False
        
        # In production, write to actual Google Sheets
        try:
            # Mock implementation - replace with actual sheets API calls
            self.logger.info("Feedback logged to Google Sheets (mock implementation)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to log to Google Sheets: {e}")
            return False

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute performance analysis and generate recommendations.
        
        Args:
            inputs: Dictionary containing responses and metrics
            
        Returns:
            Dictionary containing recommendations and performance summary
        """
        responses = inputs['responses']
        metrics = inputs['metrics']
        
        self.reason(inputs, "analyzing_campaign_performance")
        
        # Analyze performance against benchmarks
        benchmark_analysis = self._analyze_performance_vs_benchmarks(metrics)
        
        # Generate recommendations
        icp_recommendations = self._generate_icp_recommendations(responses)
        messaging_recommendations = self._generate_messaging_recommendations(responses, metrics)
        
        # Combine all recommendations
        all_recommendations = icp_recommendations + messaging_recommendations
        
        # Calculate overall performance score
        overall_score = self._calculate_overall_score(metrics)
        
        # Generate key insights
        key_insights = self._generate_key_insights(responses, metrics)
        
        # Generate action items
        action_items = []
        for rec in all_recommendations[:3]:  # Top 3 recommendations
            if rec['confidence'] > 0.7:
                action_items.append(f"Implement {rec['type']}: {rec['suggested_value']}")
        
        if not action_items:
            action_items = ["Continue current approach - performance is acceptable"]
        
        # Create performance summary
        performance_summary = {
            'overall_score': overall_score,
            'key_insights': key_insights,
            'action_items': action_items,
            'benchmark_analysis': benchmark_analysis,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Log to Google Sheets
        sheets_logged = self._log_to_sheets(all_recommendations, performance_summary)
        
        self.reason({
            "overall_score": overall_score,
            "total_recommendations": len(all_recommendations),
            "high_confidence_recommendations": len([r for r in all_recommendations if r['confidence'] > 0.7]),
            "sheets_logged": sheets_logged
        }, "analysis_complete")
        
        return {
            "recommendations": all_recommendations,
            "performance_summary": performance_summary,
            "total_recommendations": len(all_recommendations),
            "high_confidence_count": len([r for r in all_recommendations if r['confidence'] > 0.7]),
            "sheets_logged": sheets_logged,
            "analysis_timestamp": datetime.now().isoformat()
        }