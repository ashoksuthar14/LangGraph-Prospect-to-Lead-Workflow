"""
Base Agent class providing common functionality for all workflow agents.
Implements ReAct-style reasoning and structured input/output handling.
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class BaseAgent(ABC):
    """
    Abstract base class for all workflow agents.
    Provides common functionality including logging, reasoning, and API handling.
    """

    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """
        Initialize the base agent with configuration.
        
        Args:
            agent_id: Unique identifier for this agent
            config: Agent configuration dictionary
        """
        self.agent_id = agent_id
        self.config = config
        self.tools = config.get('tools', [])
        self.instructions = config.get('instructions', '')
        self.reasoning_prompt = config.get('reasoning_prompt', '')
        
        # Set up logging
        self.logger = self._setup_logging()
        
        # Initialize tool clients
        self.tool_clients = self._initialize_tools()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the agent."""
        logger = logging.getLogger(f"agent.{self.agent_id}")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler
        log_file = os.path.join(log_dir, f"{self.agent_id}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """Initialize tool clients based on configuration."""
        clients = {}
        
        for tool in self.tools:
            tool_name = tool['name']
            tool_config = tool['config']
            
            # Replace environment variable placeholders
            for key, value in tool_config.items():
                if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                    env_var = value[2:-2]  # Remove {{ and }}
                    tool_config[key] = os.getenv(env_var)
            
            clients[tool_name] = tool_config
            
        return clients
    
    def reason(self, inputs: Dict[str, Any], step: str) -> str:
        """
        Perform ReAct-style reasoning about the current step.
        
        Args:
            inputs: Current step inputs
            step: Current reasoning step (e.g., 'observation', 'thought', 'action')
            
        Returns:
            Reasoning text
        """
        timestamp = datetime.now().isoformat()
        
        reasoning = f"""
[{timestamp}] Agent: {self.agent_id}
Step: {step}

Base Reasoning: {self.reasoning_prompt}

Current Inputs: {json.dumps(inputs, indent=2)}

Instructions: {self.instructions}

Available Tools: {[tool['name'] for tool in self.tools]}
        """
        
        self.logger.info(f"Reasoning - {step}: {reasoning}")
        return reasoning.strip()
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> bool:
        """
        Validate input structure and required fields.
        
        Args:
            inputs: Input data to validate
            
        Returns:
            True if inputs are valid
        """
        try:
            # Basic validation - can be extended by subclasses
            if not isinstance(inputs, dict):
                raise ValueError("Inputs must be a dictionary")
                
            self.logger.info(f"Input validation passed for {self.agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Input validation failed: {str(e)}")
            return False
    
    def validate_outputs(self, outputs: Dict[str, Any]) -> bool:
        """
        Validate output structure against expected schema.
        
        Args:
            outputs: Output data to validate
            
        Returns:
            True if outputs are valid
        """
        try:
            # Basic validation - can be extended by subclasses
            if not isinstance(outputs, dict):
                raise ValueError("Outputs must be a dictionary")
                
            self.logger.info(f"Output validation passed for {self.agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Output validation failed: {str(e)}")
            return False
    
    def generate_execution_id(self) -> str:
        """Generate unique execution ID for tracking."""
        return f"{self.agent_id}_{uuid.uuid4().hex[:8]}"
    
    def log_execution_start(self, execution_id: str, inputs: Dict[str, Any]):
        """Log the start of agent execution."""
        self.logger.info(f"Starting execution {execution_id}")
        self.logger.info(f"Inputs: {json.dumps(inputs, indent=2)}")
    
    def log_execution_end(self, execution_id: str, outputs: Dict[str, Any], success: bool):
        """Log the end of agent execution."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Execution {execution_id} completed with status: {status}")
        if success:
            self.logger.info(f"Outputs: {json.dumps(outputs, indent=2)}")
    
    @abstractmethod
    def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main functionality.
        
        Args:
            inputs: Structured input data
            
        Returns:
            Structured output data
        """
        pass
    
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point to run the agent with full error handling and logging.
        
        Args:
            inputs: Structured input data
            
        Returns:
            Structured output data
        """
        execution_id = self.generate_execution_id()
        
        try:
            # Log execution start
            self.log_execution_start(execution_id, inputs)
            
            # Validate inputs
            if not self.validate_inputs(inputs):
                raise ValueError("Input validation failed")
            
            # Perform reasoning
            self.reason(inputs, "initial_analysis")
            
            # Execute main functionality
            outputs = self.execute(inputs)
            
            # Validate outputs
            if not self.validate_outputs(outputs):
                raise ValueError("Output validation failed")
            
            # Log success
            self.log_execution_end(execution_id, outputs, True)
            
            return outputs
            
        except Exception as e:
            self.logger.error(f"Execution {execution_id} failed: {str(e)}")
            self.log_execution_end(execution_id, {}, False)
            
            # Return error output in expected format
            return {
                "error": True,
                "message": str(e),
                "execution_id": execution_id,
                "agent_id": self.agent_id
            }


class AgentRegistry:
    """Registry to manage and create agent instances."""
    
    _agents = {}
    
    @classmethod
    def register(cls, agent_class):
        """Register an agent class."""
        cls._agents[agent_class.__name__] = agent_class
        return agent_class
    
    @classmethod
    def create_agent(cls, agent_name: str, agent_id: str, config: Dict[str, Any]) -> BaseAgent:
        """Create an agent instance by name."""
        if agent_name not in cls._agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        return cls._agents[agent_name](agent_id, config)
    
    @classmethod
    def list_agents(cls) -> List[str]:
        """List all registered agent names."""
        return list(cls._agents.keys())