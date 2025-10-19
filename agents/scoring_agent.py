"""
ScoringAgent - Scores and ranks leads based on ICP criteria and buying signals
"""

import json
from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent, AgentRegistry


@AgentRegistry.register
class ScoringAgent(BaseAgent):
    """
    Agent responsible for scoring leads based on ICP fit, buying signals,
    and company data to prioritize outreach efforts.
    """

    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """Validate ScoringAgent specific inputs."""
        required_fields = ['enriched_leads', 'scoring_criteria']
        
        for field in required_fields:
            if field not in inputs:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        if not isinstance(inputs['enriched_leads'], list):
            self.logger.error("Field 'enriched_leads' must be a list")
            return False
        
        return super().validate_inputs(inputs)

    def _score_company_size(self, employee_count: int, criteria: Dict[str, Any]) -> Tuple[float, str]:
        """
        Score based on company size alignment with ICP.
        
        Args:
            employee_count: Number of employees
            criteria: Scoring criteria configuration
            
        Returns:
            Tuple of (score, reasoning)
        """
        # Ideal range scoring
        if 100 <= employee_count <= 500:
            score = 10.0
            reasoning = "Perfect company size fit for our ICP"
        elif 50 <= employee_count <= 1000:
            score = 8.0
            reasoning = "Good company size fit"
        elif employee_count > 1000:
            score = 6.0
            reasoning = "Large company - may have longer sales cycles"
        else:
            score = 4.0
            reasoning = "Small company - may have limited budget"
        
        return score, reasoning

    def _score_industry_match(self, industry: str, target_industries: List[str]) -> Tuple[float, str]:
        """
        Score based on industry alignment.
        
        Args:
            industry: Company industry
            target_industries: List of target industries
            
        Returns:
            Tuple of (score, reasoning)
        """
        if industry in target_industries:
            score = 10.0
            reasoning = f"Perfect industry match - {industry} is a target vertical"
        elif any(target.lower() in industry.lower() for target in target_industries):
            score = 7.0
            reasoning = f"Close industry match - {industry} is adjacent to our targets"
        else:
            score = 3.0
            reasoning = f"Industry {industry} is not in our primary targets"
        
        return score, reasoning

    def _score_technology_stack(self, technologies: List[str]) -> Tuple[float, str]:
        """
        Score based on technology stack compatibility.
        
        Args:
            technologies: List of technologies used by the company
            
        Returns:
            Tuple of (score, reasoning)
        """
        # Define ideal and compatible technologies
        ideal_tech = {"Salesforce", "HubSpot", "AWS", "Microsoft 365"}
        compatible_tech = {"Google Cloud", "Slack", "Zoom", "PostgreSQL", "MongoDB"}
        
        tech_set = set(tech.lower() for tech in technologies)
        
        ideal_matches = len(ideal_tech.intersection(tech_set))
        compatible_matches = len(compatible_tech.intersection(tech_set))
        
        if ideal_matches >= 2:
            score = 10.0
            reasoning = f"Excellent tech stack compatibility - uses {ideal_matches} ideal technologies"
        elif ideal_matches >= 1 or compatible_matches >= 2:
            score = 7.0
            reasoning = "Good tech stack compatibility"
        elif compatible_matches >= 1:
            score = 5.0
            reasoning = "Some tech stack compatibility"
        else:
            score = 2.0
            reasoning = "Limited tech stack visibility or compatibility"
        
        return score, reasoning

    def _score_recent_signals(self, signals: List[str]) -> Tuple[float, str]:
        """
        Score based on buying signals and recent activity.
        
        Args:
            signals: List of buying signals
            
        Returns:
            Tuple of (score, reasoning)
        """
        # Define signal priorities
        high_priority_signals = {"recent_funding", "new_leadership", "hiring_for_sales"}
        medium_priority_signals = {"product_launch", "expansion", "hiring"}
        
        high_matches = len(set(signals).intersection(high_priority_signals))
        medium_matches = len(set(signals).intersection(medium_priority_signals))
        
        if high_matches >= 2:
            score = 10.0
            reasoning = f"Multiple high-priority buying signals: {', '.join(signals)}"
        elif high_matches >= 1:
            score = 8.0
            reasoning = f"Strong buying signal present: {', '.join(signals)}"
        elif medium_matches >= 2:
            score = 6.0
            reasoning = f"Multiple medium-priority signals: {', '.join(signals)}"
        elif medium_matches >= 1:
            score = 4.0
            reasoning = f"Some buying signals present: {', '.join(signals)}"
        else:
            score = 2.0
            reasoning = "Limited buying signals detected"
        
        return score, reasoning

    def _score_contact_seniority(self, seniority: str) -> Tuple[float, str]:
        """
        Score based on contact seniority and decision-making power.
        
        Args:
            seniority: Contact seniority level
            
        Returns:
            Tuple of (score, reasoning)
        """
        seniority_scores = {
            'executive': (10.0, "Executive level - high decision-making power"),
            'senior': (8.0, "Senior level - significant influence on decisions"),
            'mid': (6.0, "Mid-level - may influence but needs executive buy-in"),
            'entry': (3.0, "Entry-level - limited decision-making authority"),
            'unknown': (4.0, "Unknown seniority level")
        }
        
        return seniority_scores.get(seniority.lower(), (4.0, "Unknown seniority level"))

    def _score_funding_stage(self, funding: str) -> Tuple[float, str]:
        """
        Score based on company funding stage.
        
        Args:
            funding: Company funding stage
            
        Returns:
            Tuple of (score, reasoning)
        """
        funding_scores = {
            'series a': (9.0, "Series A - growing with established product-market fit"),
            'series b': (10.0, "Series B - scaling rapidly with proven revenue model"),
            'series c': (8.0, "Series C - mature company with substantial resources"),
            'series c+': (7.0, "Late stage - established but may have complex decision processes"),
            'seed': (6.0, "Seed stage - early but may have limited budget"),
            'unknown': (5.0, "Unknown funding stage"),
        }
        
        return funding_scores.get(funding.lower(), (5.0, "Unknown funding stage"))

    def _calculate_composite_score(self, scores: Dict[str, Tuple[float, str]], 
                                 weights: Dict[str, float]) -> Tuple[float, List[str]]:
        """
        Calculate weighted composite score.
        
        Args:
            scores: Dictionary of individual scores
            weights: Scoring weights configuration
            
        Returns:
            Tuple of (composite_score, reasoning_list)
        """
        composite_score = 0.0
        reasoning_list = []
        
        # Calculate weighted score
        for factor, (score, reasoning) in scores.items():
            weight = weights.get(factor, 0.0)
            weighted_score = score * weight
            composite_score += weighted_score
            reasoning_list.append(f"{factor}: {score}/10 (weight: {weight}) - {reasoning}")
        
        return composite_score, reasoning_list

    def _determine_priority(self, score: float, thresholds: Dict[str, float]) -> str:
        """
        Determine lead priority based on score and thresholds.
        
        Args:
            score: Composite lead score
            thresholds: Score thresholds configuration
            
        Returns:
            Priority level string
        """
        if score >= thresholds.get('high_priority', 9.0):
            return 'high'
        elif score >= thresholds.get('min_score', 7.0):
            return 'medium'
        else:
            return 'low'

    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute lead scoring for all enriched leads.
        
        Args:
            inputs: Dictionary containing enriched_leads and scoring_criteria
            
        Returns:
            Dictionary containing ranked leads with scores
        """
        enriched_leads = inputs['enriched_leads']
        scoring_criteria = inputs['scoring_criteria']
        
        weights = scoring_criteria.get('weights', {})
        thresholds = scoring_criteria.get('thresholds', {})
        
        self.reason(inputs, "analyzing_leads_for_scoring")
        
        ranked_leads = []
        
        for lead in enriched_leads:
            try:
                company_data = lead.get('company_data', {})
                contact_data = lead.get('contact', {})
                signals = lead.get('original_signals', [])
                
                # Calculate individual scores
                scores = {}
                
                # Company size score
                scores['company_size'] = self._score_company_size(
                    company_data.get('employee_count', 0), 
                    scoring_criteria
                )
                
                # Industry match score
                scores['industry_match'] = self._score_industry_match(
                    company_data.get('industry_tags', [''])[0] if company_data.get('industry_tags') else '',
                    ['SaaS', 'Technology', 'Financial Services']  # From ICP
                )
                
                # Technology stack score
                scores['technology_stack'] = self._score_technology_stack(
                    company_data.get('technologies', [])
                )
                
                # Recent signals score
                scores['recent_signals'] = self._score_recent_signals(signals)
                
                # Bonus factors
                scores['contact_seniority'] = self._score_contact_seniority(
                    contact_data.get('seniority', 'unknown')
                )
                
                scores['funding_stage'] = self._score_funding_stage(
                    company_data.get('funding', 'unknown')
                )
                
                # Calculate composite score
                # Default weights if not provided
                default_weights = {
                    'company_size': 0.20,
                    'industry_match': 0.25, 
                    'technology_stack': 0.15,
                    'recent_signals': 0.20,
                    'contact_seniority': 0.10,
                    'funding_stage': 0.10
                }
                effective_weights = {**default_weights, **weights}
                composite_score, reasoning_list = self._calculate_composite_score(scores, effective_weights)
                
                # Determine priority
                priority = self._determine_priority(composite_score, thresholds)
                
                # Create scored lead
                scored_lead = {
                    'lead': lead,
                    'score': round(composite_score, 2),
                    'priority': priority,
                    'reasoning': reasoning_list,
                    'individual_scores': {k: v[0] for k, v in scores.items()},
                    'scoring_timestamp': self._get_timestamp()
                }
                
                ranked_leads.append(scored_lead)
                self.logger.info(f"Scored {lead.get('company', 'Unknown')}: {composite_score:.2f} ({priority})")
                
            except Exception as e:
                self.logger.error(f"Failed to score lead {lead.get('company', 'Unknown')}: {str(e)}")
                # Add with minimal score
                ranked_leads.append({
                    'lead': lead,
                    'score': 0.0,
                    'priority': 'low',
                    'reasoning': [f"Scoring error: {str(e)}"],
                    'individual_scores': {},
                    'scoring_error': str(e),
                    'scoring_timestamp': self._get_timestamp()
                })
        
        # Sort by score (highest first)
        ranked_leads.sort(key=lambda x: x['score'], reverse=True)
        
        self.reason({
            "total_scored": len(ranked_leads),
            "high_priority": len([l for l in ranked_leads if l['priority'] == 'high']),
            "medium_priority": len([l for l in ranked_leads if l['priority'] == 'medium']),
            "low_priority": len([l for l in ranked_leads if l['priority'] == 'low'])
        }, "scoring_complete")
        
        return {
            "ranked_leads": ranked_leads,
            "total_scored": len(ranked_leads),
            "priority_distribution": {
                "high": len([l for l in ranked_leads if l['priority'] == 'high']),
                "medium": len([l for l in ranked_leads if l['priority'] == 'medium']),
                "low": len([l for l in ranked_leads if l['priority'] == 'low'])
            },
            "average_score": sum(l['score'] for l in ranked_leads) / len(ranked_leads) if ranked_leads else 0
        }

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()