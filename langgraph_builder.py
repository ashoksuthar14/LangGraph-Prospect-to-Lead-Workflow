"""
LangGraph Builder - Dynamically constructs and executes workflow from JSON configuration
"""

import json
import os
import logging
from typing import Dict, Any, List
from datetime import datetime

# LangGraph imports
try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    print("Warning: langgraph not installed. Using mock graph execution.")

# Import agents
from agents import AgentRegistry


class WorkflowState:
    """State management for the LangGraph workflow."""
    
    def __init__(self):
        self.data = {}
        self.execution_history = []
        self.current_step = None
        self.error = None
        
    def update(self, step_id: str, output: Dict[str, Any]):
        """Update state with step output."""
        self.data[step_id] = output
        self.execution_history.append({
            'step_id': step_id,
            'timestamp': datetime.now().isoformat(),
            'output_keys': list(output.keys()),
            'success': 'error' not in output
        })
        self.current_step = step_id
    
    def get_input_data(self, input_spec: str, config: Dict[str, Any]) -> Any:
        """Resolve input data from state or config."""
        if isinstance(input_spec, str) and input_spec.startswith('{{') and input_spec.endswith('}}'):
            # Extract reference path (e.g., "{{prospect_search.output.leads}}")
            ref_path = input_spec[2:-2].strip()
            
            if ref_path.startswith('config.'):
                # Reference to config
                config_key = ref_path[7:]  # Remove 'config.'
                return self._get_nested_value(config, config_key)
            else:
                # Reference to previous step output
                parts = ref_path.split('.')
                if len(parts) >= 1:
                    step_id = parts[0]
                    if step_id in self.data:
                        value = self.data[step_id]
                        
                        # Handle the ".output." pattern specially
                        if len(parts) > 1 and parts[1] == 'output':
                            # Skip the "output" part since our agents return data directly
                            for part in parts[2:]:
                                if isinstance(value, dict) and part in value:
                                    value = value[part]
                                else:
                                    # If specific field not found, return None
                                    return None
                        else:
                            # Legacy path navigation for older references
                            for part in parts[1:]:
                                if isinstance(value, dict) and part in value:
                                    value = value[part]
                                else:
                                    # If path doesn't exist, return None
                                    return None
                        
                        return value
                    else:
                        # Step not found
                        return None
        
        return input_spec
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        keys = path.split('.')
        current = obj
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current


class LangGraphWorkflowBuilder:
    """Builds and executes LangGraph workflows from JSON configuration."""
    
    def __init__(self, config_path: str):
        """
        Initialize the workflow builder.
        
        Args:
            config_path: Path to the workflow.json configuration file
        """
        self.config_path = config_path
        self.config = None
        self.workflow_state = WorkflowState()
        self.logger = self._setup_logging()
        
        # Load configuration
        self._load_config()
        
        # Import and register all agents
        self._import_agents()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the workflow builder."""
        logger = logging.getLogger("langgraph_builder")
        logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_config(self):
        """Load workflow configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
            self.logger.info(f"Loaded workflow configuration: {self.config['workflow_name']}")
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {self.config_path}: {e}")
            raise
    
    def _import_agents(self):
        """Import all agent modules to register them."""
        # Agents are already imported and registered via the @AgentRegistry.register decorator
        registered_agents = AgentRegistry.list_agents()
        self.logger.info(f"Registered agents: {registered_agents}")
    
    def _create_node_function(self, step_config: Dict[str, Any]):
        """
        Create a node function for LangGraph from step configuration.
        
        Args:
            step_config: Step configuration from workflow.json
            
        Returns:
            Function that can be used as a LangGraph node
        """
        def node_function(state: WorkflowState) -> WorkflowState:
            step_id = step_config['id']
            agent_name = step_config['agent']
            
            self.logger.info(f"Executing step: {step_id} with agent: {agent_name}")
            
            try:
                # Create agent instance
                agent = AgentRegistry.create_agent(agent_name, step_id, step_config)
                
                # Resolve inputs
                inputs = {}
                for key, value in step_config.get('inputs', {}).items():
                    resolved_value = state.get_input_data(value, self.config.get('config', {}))
                    inputs[key] = resolved_value
                
                # Execute agent
                output = agent.run(inputs)
                
                # Update state
                state.update(step_id, output)
                
                self.logger.info(f"Step {step_id} completed successfully")
                
            except Exception as e:
                self.logger.error(f"Step {step_id} failed: {e}")
                error_output = {
                    'error': True,
                    'message': str(e),
                    'step_id': step_id
                }
                state.update(step_id, error_output)
            
            return state
        
        return node_function
    
    def _build_langgraph(self) -> Any:
        """
        Build LangGraph workflow from configuration.
        
        Returns:
            Compiled LangGraph workflow
        """
        if not LANGGRAPH_AVAILABLE:
            self.logger.warning("LangGraph not available - using mock execution")
            return None
        
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each step
        for step in self.config['steps']:
            step_id = step['id']
            node_function = self._create_node_function(step)
            workflow.add_node(step_id, node_function)
        
        # Add edges based on flow configuration
        flow = self.config.get('flow', {})
        start_node = flow.get('start')
        
        if start_node:
            workflow.set_entry_point(start_node)
        
        # Add edges between nodes
        for edge in flow.get('edges', []):
            from_node = edge['from']
            to_node = edge['to']
            workflow.add_edge(from_node, to_node)
        
        # Set end node
        end_node = flow.get('end')
        if end_node:
            workflow.add_edge(end_node, END)
        
        # Compile workflow
        checkpointer = MemorySaver()
        compiled_workflow = workflow.compile(checkpointer=checkpointer)
        
        return compiled_workflow
    
    def _execute_mock_workflow(self) -> Dict[str, Any]:
        """
        Execute workflow without LangGraph (mock execution).
        
        Returns:
            Final workflow state data
        """
        self.logger.info("Starting mock workflow execution")
        
        # Execute steps in order based on flow
        flow = self.config.get('flow', {})
        start_step = flow.get('start')
        
        if not start_step:
            raise ValueError("No start step defined in workflow flow")
        
        # Create a mapping of step IDs to step configs
        step_configs = {step['id']: step for step in self.config['steps']}
        
        # Execute steps sequentially based on edges
        current_step = start_step
        executed_steps = set()
        
        while current_step and current_step not in executed_steps:
            if current_step not in step_configs:
                self.logger.error(f"Step {current_step} not found in configuration")
                break
            
            step_config = step_configs[current_step]
            
            # Execute the step
            node_function = self._create_node_function(step_config)
            self.workflow_state = node_function(self.workflow_state)
            
            # Check for errors
            if self.workflow_state.error:
                self.logger.error(f"Workflow failed at step {current_step}")
                break
            
            executed_steps.add(current_step)
            
            # Find next step
            next_step = None
            for edge in flow.get('edges', []):
                if edge['from'] == current_step:
                    next_step = edge['to']
                    break
            
            current_step = next_step
        
        self.logger.info("Mock workflow execution completed")
        return self.workflow_state.data
    
    def execute(self, initial_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the workflow.
        
        Args:
            initial_state: Optional initial state data
            
        Returns:
            Final workflow execution results
        """
        self.logger.info(f"Starting workflow execution: {self.config['workflow_name']}")
        
        if initial_state:
            self.workflow_state.data.update(initial_state)
        
        if LANGGRAPH_AVAILABLE:
            # Execute with LangGraph
            workflow = self._build_langgraph()
            
            if workflow:
                try:
                    # Execute workflow
                    thread = {"configurable": {"thread_id": "1"}}
                    result = workflow.invoke(self.workflow_state, thread)
                    
                    return result.data if hasattr(result, 'data') else result
                    
                except Exception as e:
                    self.logger.error(f"LangGraph execution failed: {e}")
                    # Fall back to mock execution
                    return self._execute_mock_workflow()
            else:
                return self._execute_mock_workflow()
        else:
            # Execute mock workflow
            return self._execute_mock_workflow()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get summary of workflow execution.
        
        Returns:
            Dictionary containing execution summary
        """
        return {
            'workflow_name': self.config.get('workflow_name', 'Unknown'),
            'total_steps': len(self.config.get('steps', [])),
            'executed_steps': len(self.workflow_state.execution_history),
            'successful_steps': len([h for h in self.workflow_state.execution_history if h['success']]),
            'failed_steps': len([h for h in self.workflow_state.execution_history if not h['success']]),
            'execution_history': self.workflow_state.execution_history,
            'current_step': self.workflow_state.current_step,
            'has_errors': self.workflow_state.error is not None
        }


def main():
    """Main entry point for the LangGraph workflow builder."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Execute LangGraph workflow from JSON configuration')
    parser.add_argument('--config', default='workflow.json', 
                       help='Path to workflow configuration file')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Create and execute workflow
        builder = LangGraphWorkflowBuilder(args.config)
        results = builder.execute()
        
        # Print results
        print("\n" + "="*50)
        print("WORKFLOW EXECUTION COMPLETE")
        print("="*50)
        
        summary = builder.get_execution_summary()
        print(f"Workflow: {summary['workflow_name']}")
        print(f"Steps executed: {summary['executed_steps']}/{summary['total_steps']}")
        print(f"Success rate: {summary['successful_steps']}/{summary['executed_steps']}")
        
        if summary['has_errors']:
            print("\nErrors occurred during execution. Check logs for details.")
        else:
            print("\nWorkflow completed successfully!")
        
        # Print final results (last step output)
        if results:
            final_step = summary['current_step']
            if final_step and final_step in results:
                print(f"\nFinal output from {final_step}:")
                print(json.dumps(results[final_step], indent=2))
        
    except Exception as e:
        print(f"Error executing workflow: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())