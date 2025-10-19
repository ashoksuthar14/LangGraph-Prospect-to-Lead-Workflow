"""
DataEnrichmentAgent - Enriches lead data using Explorium API
"""

import requests
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentRegistry


@AgentRegistry.register
class DataEnrichmentAgent(BaseAgent):
    """
    Agent responsible for enriching basic lead data with comprehensive company
    and contact information using Explorium API.
    """

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate DataEnrichmentAgent specific inputs."""
        if 'leads' not in inputs:
            self.logger.error("Missing required field: leads")
            return False
        
        if not isinstance(inputs['leads'], list):
            self.logger.error("Field 'leads' must be a list")
            return False
        
        return super().validate_inputs(inputs)

    def _search_business_by_domain(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Search for businesses using Explorium API based on company name.
        
        Args:
            company_name: Name of the company to search
            
        Returns:
            List of matching businesses from Explorium
        """
        explorium_config = self.tool_clients.get('ExploriumAPI', {})
        api_key = explorium_config.get('api_key')
        base_url = explorium_config.get('endpoint', 'https://api.explorium.ai/v1')
        
        if not api_key:
            self.logger.warning("Explorium API not configured, using mock data")
            return []
        
        headers = {
            "API_KEY": api_key,
            "Content-Type": "application/json"
        }
        
        # Search for businesses matching the company name
        payload = {
            "mode": "full",
            "size": 10,
            "page_size": 10,
            "page": 1,
            "filters": {
                "name": {
                    "type": "includes",
                    "values": [company_name]
                }
            }
        }
        
        try:
            response = requests.post(f"{base_url}/businesses", headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                self.logger.error(f"Explorium business search failed: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Explorium API error: {str(e)}")
            return []
    
    def _get_prospects_for_business(self, business_id: str) -> List[Dict[str, Any]]:
        """
        Get prospects (contacts) for a specific business using Explorium API.
        
        Args:
            business_id: Business ID from Explorium
            
        Returns:
            List of prospects from the business
        """
        explorium_config = self.tool_clients.get('ExploriumAPI', {})
        api_key = explorium_config.get('api_key')
        base_url = explorium_config.get('endpoint', 'https://api.explorium.ai/v1')
        
        if not api_key:
            return []
        
        headers = {
            "API_KEY": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "mode": "full",
            "size": 50,
            "page_size": 50,
            "page": 1,
            "filters": {
                "business_id": {
                    "type": "includes",
                    "values": [business_id]
                },
                "job_department": {
                    "type": "includes",
                    "values": ["marketing", "sales", "business development", "executive"]
                },
                "has_email": {
                    "type": "exists",
                    "value": True
                }
            }
        }
        
        try:
            response = requests.post(f"{base_url}/prospects", headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                self.logger.error(f"Explorium prospects search failed: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Explorium prospects API error: {str(e)}")
            return []
    
    def _enrich_contact_info(self, prospect_id: str) -> Dict[str, Any]:
        """
        Enrich contact information using Explorium Contact Information API.
        
        Args:
            prospect_id: Prospect ID from Explorium
            
        Returns:
            Enriched contact information
        """
        explorium_config = self.tool_clients.get('ExploriumAPI', {})
        api_key = explorium_config.get('api_key')
        base_url = explorium_config.get('endpoint', 'https://api.explorium.ai/v1')
        
        if not api_key:
            return {}
        
        headers = {
            "API_KEY": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prospect_id": prospect_id
        }
        
        try:
            response = requests.post(f"{base_url}/prospects/contacts_information/enrich", 
                                   headers=headers, json=payload)
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {})
            else:
                self.logger.error(f"Explorium contact enrichment failed: {response.status_code}")
                return {}
        except Exception as e:
            self.logger.error(f"Explorium contact enrichment error: {str(e)}")
            return {}


    def _determine_seniority(self, title: str) -> str:
        """Determine seniority level from job title."""
        title_lower = title.lower()
        
        if any(keyword in title_lower for keyword in ['ceo', 'cto', 'cfo', 'chief', 'president']):
            return 'executive'
        elif any(keyword in title_lower for keyword in ['vp', 'vice president', 'director']):
            return 'senior'
        elif any(keyword in title_lower for keyword in ['manager', 'lead', 'head']):
            return 'mid'
        else:
            return 'entry'

    def _get_mock_tech_stack(self, industry: str) -> List[str]:
        """Generate mock technology stack based on industry."""
        base_tech = ["Salesforce", "HubSpot", "Slack", "Zoom", "Microsoft 365"]
        
        if industry.lower() == 'saas':
            return base_tech + ["AWS", "Docker", "React", "Python", "PostgreSQL"]
        elif industry.lower() == 'financial services':
            return base_tech + ["Snowflake", "Tableau", "Java", "Oracle", "Workday"]
        else:
            return base_tech + ["Google Cloud", "Kubernetes", "JavaScript", "MongoDB"]

    def _determine_funding_stage(self, employee_count: int) -> str:
        """Estimate funding stage based on employee count."""
        if employee_count < 50:
            return "Seed"
        elif employee_count < 150:
            return "Series A"
        elif employee_count < 500:
            return "Series B"
        else:
            return "Series C+"

    def _estimate_revenue(self, employee_count: int) -> int:
        """Estimate annual revenue based on employee count."""
        # Rough estimate: $200k revenue per employee
        return employee_count * 200000

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute data enrichment using Explorium API workflow:
        1. Search for businesses by company name
        2. Get prospects for each business
        3. Enrich contact information for key prospects
        
        Args:
            inputs: Dictionary containing list of leads to enrich
            
        Returns:
            Dictionary containing enriched leads data
        """
        leads = inputs['leads']
        
        self.reason(inputs, "analyzing_leads_for_explorium_enrichment")
        
        enriched_leads = []
        
        for lead in leads:
            try:
                company_name = lead.get('company', '')
                self.logger.info(f"Starting Explorium enrichment for {company_name}")
                
                # Step 1: Search for the business in Explorium
                businesses = self._search_business_by_domain(company_name)
                
                if not businesses:
                    # Fallback to mock data if no business found
                    enriched_lead = self._create_fallback_enrichment(lead)
                    enriched_leads.append(enriched_lead)
                    continue
                
                # Use the first matching business
                business = businesses[0]
                business_id = business.get('business_id')
                
                # Step 2: Get prospects for this business
                prospects = self._get_prospects_for_business(business_id) if business_id else []
                
                # Step 3: Enrich contact information for the best matching prospect
                best_prospect = self._find_best_matching_prospect(prospects, lead)
                
                if best_prospect:
                    prospect_id = best_prospect.get('prospect_id')
                    enriched_contact_info = self._enrich_contact_info(prospect_id) if prospect_id else {}
                    
                    # Combine all enriched data
                    enriched_lead = {
                        "company": company_name,
                        "contact": {
                            "name": best_prospect.get('full_name', lead.get('contact_name', '')),
                            "email": self._extract_best_email(enriched_contact_info, lead),
                            "title": best_prospect.get('job_title', lead.get('title', '')),
                            "linkedin": lead.get('linkedin', ''),
                            "seniority": self._determine_seniority(best_prospect.get('job_title', '')),
                            "phone": enriched_contact_info.get('phone_numbers', ''),
                            "mobile_phone": enriched_contact_info.get('mobile_phone', ''),
                            "department": best_prospect.get('job_department', '')
                        },
                        "company_data": {
                            "description": business.get('description', f"{company_name} business information"),
                            "domain": business.get('domain', ''),
                            "employee_count": self._parse_employee_range(business.get('number_of_employees_range', '')),
                            "country": business.get('country_name', ''),
                            "industry_tags": [business.get('google_category', lead.get('industry', 'Technology'))],
                            "technologies": self._get_mock_tech_stack(lead.get('industry', '')),
                            "funding": self._determine_funding_stage(self._parse_employee_range(business.get('number_of_employees_range', ''))),
                            "annual_revenue": self._estimate_revenue(self._parse_employee_range(business.get('number_of_employees_range', ''))),
                            "founded": business.get('founded_year', 2015),
                            "business_id": business_id
                        },
                        "original_signals": lead.get('signals', []),
                        "enrichment_source": "explorium",
                        "enrichment_timestamp": self._get_timestamp(),
                        "prospects_found": len(prospects)
                    }
                else:
                    # Use business data but fallback contact info
                    enriched_lead = self._create_business_only_enrichment(lead, business)
                
                enriched_leads.append(enriched_lead)
                self.logger.info(f"Successfully enriched {company_name} with Explorium data")
                
            except Exception as e:
                self.logger.error(f"Explorium enrichment failed for {lead.get('company', 'Unknown')}: {str(e)}")
                # Fallback enrichment
                fallback_enrichment = self._create_fallback_enrichment(lead)
                fallback_enrichment["enrichment_error"] = str(e)
                enriched_leads.append(fallback_enrichment)
        
        self.reason({
            "total_processed": len(leads),
            "explorium_enrichments": len([l for l in enriched_leads if l.get('enrichment_source') == 'explorium']),
            "fallback_enrichments": len([l for l in enriched_leads if l.get('enrichment_source') != 'explorium'])
        }, "explorium_enrichment_complete")
        
        return {
            "enriched_leads": enriched_leads,
            "total_processed": len(leads),
            "successful_enrichments": len([l for l in enriched_leads if 'enrichment_error' not in l]),
            "failed_enrichments": len([l for l in enriched_leads if 'enrichment_error' in l]),
            "explorium_enrichments": len([l for l in enriched_leads if l.get('enrichment_source') == 'explorium'])
        }

    def _find_best_matching_prospect(self, prospects: List[Dict[str, Any]], original_lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find the best matching prospect from Explorium results.
        
        Args:
            prospects: List of prospects from Explorium
            original_lead: Original lead data
            
        Returns:
            Best matching prospect or None
        """
        if not prospects:
            return None
        
        # Prioritize by job department and title similarity
        target_departments = ['sales', 'marketing', 'business development', 'executive']
        original_title = original_lead.get('title', '').lower()
        
        for prospect in prospects:
            job_dept = prospect.get('job_department', '').lower()
            job_title = prospect.get('job_title', '').lower()
            
            # High priority match
            if job_dept in target_departments:
                return prospect
            
            # Title similarity match
            if original_title and any(word in job_title for word in original_title.split()):
                return prospect
        
        # Return first prospect if no perfect match
        return prospects[0]
    
    def _extract_best_email(self, enriched_contact_info: Dict[str, Any], original_lead: Dict[str, Any]) -> str:
        """
        Extract the best email from enriched contact information.
        
        Args:
            enriched_contact_info: Contact info from Explorium enrichment
            original_lead: Original lead data
            
        Returns:
            Best email address
        """
        # Try professional email first
        if enriched_contact_info.get('professions_email'):
            return enriched_contact_info['professions_email']
        
        # Try emails array
        emails = enriched_contact_info.get('emails', [])
        if emails and isinstance(emails, list):
            return emails[0]
        
        # Fallback to original email
        return original_lead.get('email', '')
    
    def _parse_employee_range(self, employee_range: str) -> int:
        """
        Parse employee range string to approximate number.
        
        Args:
            employee_range: String like "11-50" or "51-200"
            
        Returns:
            Approximate employee count
        """
        if not employee_range:
            return 100
        
        try:
            if '-' in employee_range:
                parts = employee_range.split('-')
                min_employees = int(parts[0])
                max_employees = int(parts[1])
                return (min_employees + max_employees) // 2
            else:
                return int(employee_range)
        except (ValueError, IndexError):
            return 100
    
    def _create_fallback_enrichment(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create fallback enrichment when Explorium data is not available.
        
        Args:
            lead: Original lead data
            
        Returns:
            Fallback enriched lead data
        """
        company_name = lead.get('company', '')
        return {
            "company": company_name,
            "contact": {
                "name": lead.get('contact_name', ''),
                "email": lead.get('email', ''),
                "title": lead.get('title', ''),
                "linkedin": lead.get('linkedin', ''),
                "seniority": self._determine_seniority(lead.get('title', '')),
                "phone": '',
                "mobile_phone": '',
                "department": ''
            },
            "company_data": {
                "description": f"{company_name} is a technology company.",
                "domain": '',
                "employee_count": lead.get('company_size', 100),
                "country": 'United States',
                "industry_tags": [lead.get('industry', 'Technology')],
                "technologies": self._get_mock_tech_stack(lead.get('industry', '')),
                "funding": self._determine_funding_stage(lead.get('company_size', 100)),
                "annual_revenue": self._estimate_revenue(lead.get('company_size', 100)),
                "founded": 2015,
                "business_id": ''
            },
            "original_signals": lead.get('signals', []),
            "enrichment_source": "fallback",
            "enrichment_timestamp": self._get_timestamp(),
            "prospects_found": 0
        }
    
    def _create_business_only_enrichment(self, lead: Dict[str, Any], business: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create enrichment using business data but fallback contact info.
        
        Args:
            lead: Original lead data
            business: Business data from Explorium
            
        Returns:
            Business-enriched lead data
        """
        company_name = lead.get('company', '')
        return {
            "company": company_name,
            "contact": {
                "name": lead.get('contact_name', ''),
                "email": lead.get('email', ''),
                "title": lead.get('title', ''),
                "linkedin": lead.get('linkedin', ''),
                "seniority": self._determine_seniority(lead.get('title', '')),
                "phone": '',
                "mobile_phone": '',
                "department": ''
            },
            "company_data": {
                "description": business.get('description', f"{company_name} business information"),
                "domain": business.get('domain', ''),
                "employee_count": self._parse_employee_range(business.get('number_of_employees_range', '')),
                "country": business.get('country_name', ''),
                "industry_tags": [business.get('google_category', lead.get('industry', 'Technology'))],
                "technologies": self._get_mock_tech_stack(lead.get('industry', '')),
                "funding": self._determine_funding_stage(self._parse_employee_range(business.get('number_of_employees_range', ''))),
                "annual_revenue": self._estimate_revenue(self._parse_employee_range(business.get('number_of_employees_range', ''))),
                "founded": business.get('founded_year', 2015),
                "business_id": business.get('business_id', '')
            },
            "original_signals": lead.get('signals', []),
            "enrichment_source": "explorium_business_only",
            "enrichment_timestamp": self._get_timestamp(),
            "prospects_found": 0
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
