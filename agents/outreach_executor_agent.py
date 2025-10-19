"""
OutreachExecutorAgent - Executes outreach campaigns using SendGrid API
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentRegistry

# Mock SendGrid API for demonstration
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    print("Warning: sendgrid not installed. Using mock email sending.")


@AgentRegistry.register
class OutreachExecutorAgent(BaseAgent):
    """
    Agent responsible for executing outreach campaigns by sending
    personalized emails using SendGrid API.
    """

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """Initialize the OutreachExecutorAgent with SendGrid configuration."""
        super().__init__(agent_id, config)
        self._setup_sendgrid()

    def _setup_sendgrid(self):
        """Setup SendGrid API client."""
        sendgrid_config = self.tool_clients.get('SendGridAPI', {})
        api_key = sendgrid_config.get('api_key')
        self.from_email = sendgrid_config.get('from_email', 'sarah@yourcompany.com')
        
        self.logger.info(f"SendGrid config loaded: api_key={'*' * 10 if api_key else 'None'}, from_email={self.from_email}")
        
        if SENDGRID_AVAILABLE and api_key:
            self.sg = sendgrid.SendGridAPIClient(api_key=api_key)
            self.logger.info("SendGrid API configured successfully")
        else:
            self.sg = None
            self.logger.warning(f"SendGrid API not configured - SENDGRID_AVAILABLE={SENDGRID_AVAILABLE}, api_key={'set' if api_key else 'missing'}")

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate OutreachExecutorAgent specific inputs."""
        required_fields = ['messages', 'ranked_leads']
        
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(inputs['messages'], list):
            self.logger.error("Field 'messages' must be a list")
            return False
        
        if not isinstance(inputs['ranked_leads'], list):
            self.logger.error("Field 'ranked_leads' must be a list")
            return False
        
        return super().validate_inputs(inputs)

    def _create_campaign_id(self) -> str:
        """Generate unique campaign ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"campaign_{timestamp}_{uuid.uuid4().hex[:8]}"

    def _get_lead_email(self, lead_id: str, ranked_leads: List[Dict[str, Any]]) -> str:
        """
        Extract email address for a lead.
        
        Args:
            lead_id: Lead identifier
            ranked_leads: List of ranked lead data
            
        Returns:
            Email address or empty string if not found
        """
        try:
            # Extract lead index from lead_id
            if 'lead_' in lead_id:
                lead_index = int(lead_id.split('_')[1])
                if lead_index < len(ranked_leads):
                    lead_data = ranked_leads[lead_index]['lead']
                    contact = lead_data.get('contact', {})
                    return contact.get('email', '')
        except (ValueError, IndexError, KeyError):
            pass
        
        return ''

    def _send_email_sendgrid(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Send email using SendGrid API.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            Dictionary with send status information
        """
        # Check if email sending is enabled in environment
        import os
        email_sending_enabled = os.getenv('ENABLE_EMAIL_SENDING', 'false').lower() == 'true'
        
        if not self.sg or not email_sending_enabled:
            self.logger.info(f"Email sending disabled (ENABLE_EMAIL_SENDING={email_sending_enabled}) - using mock")
            return self._send_email_mock(to_email, subject, body)
        
        try:
            # Use the direct API approach like in our working test
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.sg.api_key}',
                'Content-Type': 'application/json'
            }
            
            email_data = {
                "personalizations": [{
                    "to": [{"email": to_email}],
                    "subject": subject
                }],
                "from": {"email": self.from_email},
                "content": [{
                    "type": "text/plain",
                    "value": body
                }]
            }
            
            self.logger.info(f"Attempting to send email via SendGrid: {to_email}")
            response = requests.post('https://api.sendgrid.com/v3/mail/send', 
                                   headers=headers, 
                                   json=email_data)
            
            self.logger.info(f"SendGrid response: status={response.status_code}")
            
            if response.status_code == 202:
                return {
                    'status': 'sent',
                    'status_code': response.status_code,
                    'message_id': response.headers.get('X-Message-Id', ''),
                    'sent_at': datetime.now().isoformat(),
                    'error': None
                }
            else:
                error_msg = f"HTTP Error {response.status_code}: {response.text}"
                self.logger.error(f"SendGrid send failed: {error_msg}")
                return {
                    'status': 'failed',
                    'status_code': response.status_code,
                    'message_id': '',
                    'sent_at': datetime.now().isoformat(),
                    'error': error_msg
                }
            
        except Exception as e:
            self.logger.error(f"SendGrid send exception: {str(e)}")
            return {
                'status': 'failed',
                'status_code': 500,
                'message_id': '',
                'sent_at': datetime.now().isoformat(),
                'error': str(e)
            }

    def _send_email_mock(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Mock email sending for demonstration.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body
            
        Returns:
            Dictionary with mock send status
        """
        # Simulate success/failure rates
        import random
        success_rate = 0.95  # 95% success rate for demo
        
        if random.random() < success_rate:
            status = 'sent'
            message_id = f"mock_{uuid.uuid4().hex[:12]}"
            error = None
        else:
            status = 'failed'
            message_id = ''
            error = 'Mock delivery failure (5% failure rate for demo)'
        
        return {
            'status': status,
            'status_code': 200 if status == 'sent' else 400,
            'message_id': message_id,
            'sent_at': datetime.now().isoformat(),
            'error': error
        }

    def _validate_email_address(self, email: str) -> bool:
        """
        Basic email validation.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email appears valid
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _create_tracking_metadata(self, lead_id: str, campaign_id: str) -> Dict[str, str]:
        """
        Create metadata for tracking email engagement.
        
        Args:
            lead_id: Lead identifier
            campaign_id: Campaign identifier
            
        Returns:
            Dictionary with tracking metadata
        """
        return {
            'campaign_id': campaign_id,
            'lead_id': lead_id,
            'sent_timestamp': datetime.now().isoformat(),
            'tracking_id': f"{campaign_id}_{lead_id}_{uuid.uuid4().hex[:6]}"
        }

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute outreach campaign by sending personalized emails.
        
        Args:
            inputs: Dictionary containing messages and ranked_leads
            
        Returns:
            Dictionary containing campaign execution results
        """
        messages = inputs['messages']
        ranked_leads = inputs['ranked_leads']
        
        # Generate campaign ID
        campaign_id = self._create_campaign_id()
        
        self.reason(inputs, "preparing_outreach_campaign")
        
        sent_status = []
        successful_sends = 0
        failed_sends = 0
        
        for message in messages:
            try:
                lead_id = message['lead_id']
                subject = message['subject_line']
                body = message['email_body']
                
                # Get recipient email
                to_email = self._get_lead_email(lead_id, ranked_leads)
                
                if not to_email:
                    self.logger.error(f"No email found for lead {lead_id}")
                    sent_status.append({
                        'lead_id': lead_id,
                        'email': '',
                        'status': 'failed',
                        'sent_at': datetime.now().isoformat(),
                        'message_id': '',
                        'error': 'No email address found'
                    })
                    failed_sends += 1
                    continue
                
                # Validate email
                if not self._validate_email_address(to_email):
                    self.logger.error(f"Invalid email address: {to_email}")
                    sent_status.append({
                        'lead_id': lead_id,
                        'email': to_email,
                        'status': 'failed',
                        'sent_at': datetime.now().isoformat(),
                        'message_id': '',
                        'error': 'Invalid email address'
                    })
                    failed_sends += 1
                    continue
                
                # Send email
                send_result = self._send_email_sendgrid(to_email, subject, body)
                
                # Create tracking metadata
                tracking_metadata = self._create_tracking_metadata(lead_id, campaign_id)
                
                # Create status record
                status_record = {
                    'lead_id': lead_id,
                    'email': to_email,
                    'status': send_result['status'],
                    'sent_at': send_result['sent_at'],
                    'message_id': send_result['message_id'],
                    'tracking_metadata': tracking_metadata
                }
                
                if send_result['error']:
                    status_record['error'] = send_result['error']
                    failed_sends += 1
                else:
                    successful_sends += 1
                
                sent_status.append(status_record)
                
                self.logger.info(f"Email {send_result['status']} for {to_email} (Lead: {lead_id})")
                
            except Exception as e:
                self.logger.error(f"Failed to send email for message {message.get('lead_id', 'unknown')}: {str(e)}")
                sent_status.append({
                    'lead_id': message.get('lead_id', 'unknown'),
                    'email': '',
                    'status': 'failed',
                    'sent_at': datetime.now().isoformat(),
                    'message_id': '',
                    'error': str(e)
                })
                failed_sends += 1
        
        self.reason({
            "campaign_id": campaign_id,
            "total_emails": len(messages),
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
            "success_rate": f"{(successful_sends/len(messages)*100):.1f}%" if messages else "0%"
        }, "campaign_execution_complete")
        
        return {
            "sent_status": sent_status,
            "campaign_id": campaign_id,
            "total_emails": len(messages),
            "successful_sends": successful_sends,
            "failed_sends": failed_sends,
            "success_rate": successful_sends / len(messages) if messages else 0.0,
            "execution_timestamp": datetime.now().isoformat()
        }