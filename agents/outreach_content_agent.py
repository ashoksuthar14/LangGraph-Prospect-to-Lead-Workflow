"""
OutreachContentAgent - Generates personalized outreach content using Gemini API
"""

import json
import os
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentRegistry

# Mock Gemini API for demonstration - replace with actual google-generativeai import
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Using mock responses.")


@AgentRegistry.register
class OutreachContentAgent(BaseAgent):
    """
    Agent responsible for generating personalized outreach messages
    using Gemini API based on prospect data and company information.
    """

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """Initialize the OutreachContentAgent with Gemini configuration."""
        super().__init__(agent_id, config)
        self._setup_gemini()

    def _setup_gemini(self):
        """Setup Gemini API client."""
        gemini_config = self.tool_clients.get('GeminiAPI', {})
        api_key = gemini_config.get('api_key')
        
        if GEMINI_AVAILABLE and api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.logger.info("Gemini API configured successfully")
        else:
            self.model = None
            self.logger.warning("Gemini API not configured - using mock responses")

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate OutreachContentAgent specific inputs."""
        required_fields = ['ranked_leads', 'persona', 'tone', 'max_length']
        
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(inputs['ranked_leads'], list):
            self.logger.error("Field 'ranked_leads' must be a list")
            return False
        
        return super().validate_inputs(inputs)

    def _generate_personalization_factors(self, lead_data: Dict[str, Any]) -> List[str]:
        """
        Extract personalization factors from lead data.
        
        Args:
            lead_data: Enriched lead data
            
        Returns:
            List of personalization factors
        """
        factors = []
        
        company_data = lead_data.get('company_data', {})
        contact = lead_data.get('contact', {})
        signals = lead_data.get('original_signals', [])
        
        # Company-based personalization
        if company_data.get('recent_news'):
            factors.append(f"Recent news: {company_data['recent_news'][0]}")
        
        if signals:
            factors.append(f"Buying signals: {', '.join(signals)}")
        
        if company_data.get('technologies'):
            tech_stack = company_data['technologies'][:3]  # Top 3 technologies
            factors.append(f"Tech stack: {', '.join(tech_stack)}")
        
        if company_data.get('funding'):
            factors.append(f"Funding stage: {company_data['funding']}")
        
        # Contact-based personalization
        if contact.get('seniority'):
            factors.append(f"Seniority: {contact['seniority']} level")
        
        if contact.get('previous_companies'):
            factors.append(f"Experience at: {', '.join(contact['previous_companies'][:2])}")
        
        return factors

    def _create_outreach_prompt(self, lead_data: Dict[str, Any], persona: str, 
                              tone: str, max_length: int, factors: List[str]) -> str:
        """
        Create a detailed prompt for Gemini to generate personalized outreach content.
        
        Args:
            lead_data: Enriched lead data
            persona: Outreach persona (e.g., "SDR")
            tone: Message tone (e.g., "friendly_professional")
            max_length: Maximum message length
            factors: Personalization factors
            
        Returns:
            Formatted prompt for Gemini
        """
        company = lead_data.get('company', 'Unknown Company')
        contact = lead_data.get('contact', {})
        contact_name = contact.get('name', 'there')
        title = contact.get('title', 'professional')
        company_data = lead_data.get('company_data', {})
        
        prompt = f"""
You are an expert {persona} writing personalized B2B outreach emails. 

PROSPECT DETAILS:
- Company: {company}
- Contact: {contact_name}
- Title: {title}
- Company Description: {company_data.get('description', 'Technology company')}
- Employee Count: {company_data.get('employee_count', 'Unknown')}
- Industry: {', '.join(company_data.get('industry_tags', ['Technology']))}

PERSONALIZATION FACTORS:
{chr(10).join(f"- {factor}" for factor in factors)}

REQUIREMENTS:
- Tone: {tone.replace('_', ' ')}
- Maximum length: {max_length} words
- Include a compelling subject line
- Focus on value proposition, not product features
- Use one specific personalization factor from the list above
- Include a clear, soft call-to-action
- Sound human and authentic, not template-like

STRUCTURE:
1. Subject Line (compelling and personalized)
2. Brief personalized opening
3. Value proposition relevant to their situation
4. Soft call-to-action

Generate a personalized outreach email that would resonate with {contact_name} at {company}.
"""
        return prompt

    def _generate_with_gemini(self, prompt: str) -> Dict[str, str]:
        """
        Generate content using Gemini API.
        
        Args:
            prompt: Formatted prompt for content generation
            
        Returns:
            Dictionary with subject_line and email_body
        """
        if self.model is None:
            return self._generate_mock_content(prompt)
        
        try:
            response = self.model.generate_content(prompt)
            content = response.text
            
            # Parse the response to extract subject and body
            lines = content.strip().split('\n')
            subject_line = ""
            email_body = ""
            
            # Find subject line
            for i, line in enumerate(lines):
                if 'subject' in line.lower() and ':' in line:
                    subject_line = line.split(':', 1)[1].strip()
                    email_body = '\n'.join(lines[i+1:]).strip()
                    break
            
            # If no clear subject line found, use first line as subject
            if not subject_line and lines:
                subject_line = lines[0].strip()
                email_body = '\n'.join(lines[1:]).strip()
            
            # Clean up the email body
            email_body = email_body.replace('Email Body:', '').strip()
            
            return {
                'subject_line': subject_line or "Quick question about your growth initiatives",
                'email_body': email_body or "I'd love to connect and discuss how we can help accelerate your growth."
            }
            
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            return self._generate_mock_content(prompt)

    def _generate_mock_content(self, prompt: str) -> Dict[str, str]:
        """
        Generate mock content when Gemini API is not available.
        
        Args:
            prompt: Input prompt (used to extract company/contact info)
            
        Returns:
            Dictionary with mock subject_line and email_body
        """
        # Extract company name from prompt for personalization
        company = "your company"
        if "Company:" in prompt:
            try:
                company_line = [line for line in prompt.split('\n') if line.strip().startswith('- Company:')][0]
                company = company_line.split(':', 1)[1].strip()
            except:
                pass
        
        mock_subjects = [
            f"Quick question about {company}'s growth strategy",
            f"Helping companies like {company} scale efficiently",
            f"15-minute chat about {company}'s initiatives?",
            f"{company} - streamlining your operations",
            f"Curious about {company}'s current challenges"
        ]
        
        mock_bodies = [
            f"Hi there,\n\nI noticed {company}'s recent growth and was impressed by your approach to innovation.\n\nWe've helped similar companies streamline their operations and accelerate growth by 30-40%.\n\nWorth a brief conversation to see if there's a fit?\n\nBest regards,\nSarah",
            f"Hello,\n\nCongratulations on {company}'s recent developments! Your team's focus on technology innovation caught my attention.\n\nWe specialize in helping companies like yours optimize their workflows and drive efficiency.\n\nWould you be open to a quick 15-minute call this week?\n\nBest,\nSarah",
            f"Hi,\n\nI've been following {company} and noticed some exciting developments in your space.\n\nWe've worked with similar organizations to help them scale more effectively while reducing operational overhead.\n\nMight be worth connecting - are you available for a brief chat?\n\nRegards,\nSarah"
        ]
        
        import random
        return {
            'subject_line': random.choice(mock_subjects),
            'email_body': random.choice(mock_bodies)
        }

    def _validate_content(self, content: Dict[str, str], max_length: int) -> Dict[str, str]:
        """
        Validate and potentially truncate generated content.
        
        Args:
            content: Generated content dictionary
            max_length: Maximum word count
            
        Returns:
            Validated content dictionary
        """
        subject_line = content.get('subject_line', '')
        email_body = content.get('email_body', '')
        
        # Count words in email body
        word_count = len(email_body.split())
        
        # Truncate if too long
        if word_count > max_length:
            words = email_body.split()
            truncated_body = ' '.join(words[:max_length])
            # Try to end on a complete sentence
            if '.' in truncated_body:
                sentences = truncated_body.split('.')
                truncated_body = '.'.join(sentences[:-1]) + '.'
            
            email_body = truncated_body
            self.logger.warning(f"Content truncated from {word_count} to {len(email_body.split())} words")
        
        return {
            'subject_line': subject_line.strip(),
            'email_body': email_body.strip()
        }

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute outreach content generation for all ranked leads.
        
        Args:
            inputs: Dictionary containing ranked_leads and generation parameters
            
        Returns:
            Dictionary containing generated messages
        """
        ranked_leads = inputs['ranked_leads']
        persona = inputs['persona']
        tone = inputs['tone']
        max_length = inputs['max_length']
        
        self.reason(inputs, "analyzing_leads_for_content_generation")
        
        generated_messages = []
        
        for i, ranked_lead in enumerate(ranked_leads):
            try:
                lead_data = ranked_lead['lead']
                company = lead_data.get('company', 'Unknown Company')
                
                # Generate personalization factors
                factors = self._generate_personalization_factors(lead_data)
                
                # Create prompt for Gemini
                prompt = self._create_outreach_prompt(
                    lead_data, persona, tone, max_length, factors
                )
                
                # Generate content
                content = self._generate_with_gemini(prompt)
                
                # Validate and clean content
                validated_content = self._validate_content(content, max_length)
                
                # Create message record
                message = {
                    'lead_id': f"lead_{i}_{company.lower().replace(' ', '_')}",
                    'subject_line': validated_content['subject_line'],
                    'email_body': validated_content['email_body'],
                    'personalization_factors': factors,
                    'generation_timestamp': self._get_timestamp(),
                    'word_count': len(validated_content['email_body'].split())
                }
                
                generated_messages.append(message)
                self.logger.info(f"Generated content for {company} (Priority: {ranked_lead.get('priority', 'unknown')})")
                
            except Exception as e:
                self.logger.error(f"Failed to generate content for lead {i}: {str(e)}")
                # Add fallback message
                generated_messages.append({
                    'lead_id': f"lead_{i}_fallback",
                    'subject_line': "Quick question about your initiatives",
                    'email_body': "Hi,\n\nI'd love to connect and discuss how we might be able to help with your current initiatives.\n\nBest regards,\nSarah",
                    'personalization_factors': ["Generic fallback message"],
                    'generation_error': str(e),
                    'generation_timestamp': self._get_timestamp(),
                    'word_count': 20
                })
        
        self.reason({
            "total_generated": len(generated_messages),
            "successful_generations": len([m for m in generated_messages if 'generation_error' not in m]),
            "average_word_count": sum(m['word_count'] for m in generated_messages) / len(generated_messages) if generated_messages else 0
        }, "content_generation_complete")
        
        return {
            "messages": generated_messages,
            "total_generated": len(generated_messages),
            "successful_generations": len([m for m in generated_messages if 'generation_error' not in m]),
            "failed_generations": len([m for m in generated_messages if 'generation_error' in m]),
            "average_word_count": sum(m['word_count'] for m in generated_messages) / len(generated_messages) if generated_messages else 0
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()