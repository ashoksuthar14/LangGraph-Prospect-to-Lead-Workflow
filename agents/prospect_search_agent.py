"""
ProspectSearchAgent - Searches for prospects using Clay and Apollo APIs
"""

import requests
import json
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentRegistry


@AgentRegistry.register
class ProspectSearchAgent(BaseAgent):
    """
    Agent responsible for searching and identifying prospects using external APIs.
    Uses Clay and Apollo APIs to find companies and contacts matching ICP criteria.
    """

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate ProspectSearchAgent specific inputs."""
        required_fields = ['icp', 'signals', 'limit']
        
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        # Validate ICP structure
        icp = inputs['icp']
        required_icp_fields = ['industry', 'location', 'employee_count', 'revenue']
        for field in required_icp_fields:
            if field not in icp:
                self.logger.error(f"Missing required ICP field: {field}")
                return False
        
        return super().validate_inputs(inputs)

    def _search_clay_api(self, icp: Dict[str, Any], signals: List[str], limit: int) -> List[Dict[str, Any]]:
        """
        Search for prospects using Clay API.
        
        Args:
            icp: Ideal Customer Profile criteria
            signals: List of buying signals to look for
            limit: Maximum number of results to return
            
        Returns:
            List of prospect data from Clay API
        """
        clay_config = self.tool_clients.get('ClayAPI', {})
        api_key = clay_config.get('api_key')
        endpoint = clay_config.get('endpoint')
        
        if not api_key or not endpoint:
            self.logger.warning("Clay API not configured, skipping Clay search")
            return []
        
        # Mock Clay API implementation (replace with actual API calls)
        self.logger.info("Searching Clay API for prospects...")
        
        # Simulate API call results
        mock_clay_results = [
            {
                "company": "TechCorp Solutions",
                "contact_name": "Sarah Johnson",
                "email": "sarah.johnson@techcorp.com",
                "title": "VP of Sales",
                "linkedin": "https://linkedin.com/in/sarahjohnson",
                "company_size": 150,
                "industry": "SaaS",
                "signals": ["recent_funding", "hiring_for_sales"]
            },
            {
                "company": "DataFlow Inc",
                "contact_name": "Michael Chen",
                "email": "m.chen@dataflow.com",
                "title": "Director of Marketing",
                "linkedin": "https://linkedin.com/in/michaelchen",
                "company_size": 200,
                "industry": "Technology",
                "signals": ["product_launch"]
            }
        ]
        
        self.logger.info(f"Clay API returned {len(mock_clay_results)} results")
        return mock_clay_results[:limit//2]  # Return half from Clay

    def _search_apollo_api(self, icp: Dict[str, Any], signals: List[str], limit: int) -> List[Dict[str, Any]]:
        """
        Search for prospects using Apollo API.
        
        Args:
            icp: Ideal Customer Profile criteria
            signals: List of buying signals to look for
            limit: Maximum number of results to return
            
        Returns:
            List of prospect data from Apollo API
        """
        apollo_config = self.tool_clients.get('ApolloAPI', {})
        api_key = apollo_config.get('api_key')
        endpoint = apollo_config.get('endpoint')
        
        if not api_key or not endpoint:
            self.logger.warning("Apollo API not configured, skipping Apollo search")
            return []
        
        # Mock Apollo API implementation (replace with actual API calls)
        self.logger.info("Searching Apollo API for prospects...")
        
        # Simulate API call results
        mock_apollo_results = [
            {
                "company": "CloudScale Systems",
                "contact_name": "Jennifer Martinez",
                "email": "jennifer.martinez@cloudscale.com",
                "title": "Chief Revenue Officer",
                "linkedin": "https://linkedin.com/in/jennifermartinez",
                "company_size": 300,
                "industry": "SaaS",
                "signals": ["new_leadership", "recent_funding"]
            },
            {
                "company": "FinTech Innovations",
                "contact_name": "Robert Kim",
                "email": "robert.kim@fintech-innov.com",
                "title": "VP of Business Development",
                "linkedin": "https://linkedin.com/in/robertkim",
                "company_size": 180,
                "industry": "Financial Services",
                "signals": ["hiring_for_sales"]
            }
        ]
        
        self.logger.info(f"Apollo API returned {len(mock_apollo_results)} results")
        return mock_apollo_results[:limit//2]  # Return half from Apollo

    def _deduplicate_leads(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate leads based on email address.
        
        Args:
            leads: List of lead data
            
        Returns:
            Deduplicated list of leads
        """
        seen_emails = set()
        unique_leads = []
        
        for lead in leads:
            email = lead.get('email', '').lower()
            if email and email not in seen_emails:
                seen_emails.add(email)
                unique_leads.append(lead)
                
        self.logger.info(f"Deduplicated {len(leads)} leads to {len(unique_leads)} unique leads")
        return unique_leads

    def _filter_by_icp(self, leads: List[Dict[str, Any]], icp: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter leads based on ICP criteria.
        
        Args:
            leads: List of lead data
            icp: Ideal Customer Profile criteria
            
        Returns:
            Filtered list of leads
        """
        filtered_leads = []
        
        for lead in leads:
            # Check industry match
            if lead.get('industry') not in icp.get('industry', []):
                continue
                
            # Check company size
            company_size = lead.get('company_size', 0)
            size_criteria = icp.get('employee_count', {})
            if not (size_criteria.get('min', 0) <= company_size <= size_criteria.get('max', float('inf'))):
                continue
                
            filtered_leads.append(lead)
            
        self.logger.info(f"Filtered {len(leads)} leads to {len(filtered_leads)} ICP-matching leads")
        return filtered_leads

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute prospect search using Clay and Apollo APIs.
        
        Args:
            inputs: Dictionary containing icp, signals, and limit
            
        Returns:
            Dictionary containing list of found leads
        """
        icp = inputs['icp']
        signals = inputs['signals']
        limit = inputs['limit']
        
        self.reason(inputs, "planning_search")
        
        # Search Clay API
        clay_leads = self._search_clay_api(icp, signals, limit)
        
        # Search Apollo API
        apollo_leads = self._search_apollo_api(icp, signals, limit)
        
        # Combine results
        all_leads = clay_leads + apollo_leads
        self.logger.info(f"Combined results: {len(all_leads)} total leads")
        
        # Deduplicate
        unique_leads = self._deduplicate_leads(all_leads)
        
        # Filter by ICP
        filtered_leads = self._filter_by_icp(unique_leads, icp)
        
        # Limit results
        final_leads = filtered_leads[:limit]
        
        self.reason({"leads_found": len(final_leads)}, "search_complete")
        
        return {
            "leads": final_leads,
            "total_found": len(final_leads),
            "sources": {
                "clay": len(clay_leads),
                "apollo": len(apollo_leads)
            }
        }