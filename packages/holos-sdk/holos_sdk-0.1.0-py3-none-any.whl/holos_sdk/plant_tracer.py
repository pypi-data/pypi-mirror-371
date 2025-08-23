"""
PlantTracer - A wrapper class for tracing functionality

This module provides a PlantTracer class that simplifies tracing operations
by allowing configuration of default values during initialization.
"""

import uuid
import re
import requests
from datetime import datetime, timezone
from typing import Optional, Dict, Any, Literal
from a2a.types import Message, Task, TaskStatusUpdateEvent, AgentCard
from .types import TaskPlan


class PlantTracer:
    """
    A wrapper class for plant tracing functionality.
    
    This class allows you to configure default values for tracing operations,
    reducing the need to specify common parameters in each tracing call.
    """
    
    def __init__(
        self,
        base_url: str,
        creator_id: str,
        agent_id: Optional[str] = None,
        agent_card: Optional[AgentCard] = None,
    ):
        """
        Initialize the PlantTracer with default values.
        
        Args:
            base_url: API base URL for tracing operations
            creator_id: Default creator ID
            agent_id: Optional default agent ID
            agent_card: Optional agent card (will use agent_card.url as agent_id if provided)
        """
        self.creator_id = creator_id
        self.agent_id = agent_id
        self.api_base_url = base_url
        
        # Extract agent_id from agent_card if provided and agent_id not already set
        if agent_card and not self.agent_id:
            self.agent_id = agent_card.url
    
    def _convert_to_dict(self, obj: Any) -> Dict[str, Any]:
        """
        Convert an object to a dictionary, handling both A2A objects and regular dicts.
        
        Args:
            obj: Object to convert (A2A object or dict)
        
        Returns:
            Dictionary representation of the object
        """
        if hasattr(obj, 'model_dump'):
            return obj.model_dump(exclude_none=True)
        elif isinstance(obj, dict):
            return obj
        else:
            return obj
    
    def _create_tracing_data_entry(
        self,
        object_kind: str,
        object_data: Any,
        event_name: str,
        flow_role: Literal['producer', 'consumer', 'producer_consumer'],
        entry_id: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a tracing data entry with default values from the tracer.
        
        Args:
            object_kind: Type of object being traced
            object_data: The actual object data being traced
            event_name: Name of the event
            flow_role: Flow role ('producer', 'consumer', or 'producer_consumer')
            entry_id: Optional unique identifier (will generate if not provided)
            timestamp: Optional timestamp (will use current time if not provided)
        
        Returns:
            Dict containing the formatted tracing data entry
        """
        if not entry_id:
            entry_id = str(uuid.uuid4())
        
        if not timestamp:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        return {
            "id": entry_id,
            "creator_id": self.creator_id,
            "object_kind": object_kind,
            "object": self._convert_to_dict(object_data),
            "event_name": event_name,
            "flow_role": flow_role,
            "agent_id": self.agent_id,
            "timestamp": timestamp
        }
    
    def submit_tracing_data(self, tracing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit tracing data to the API.
        
        Args:
            tracing_data: Dictionary containing tracing data
        
        Returns:
            Dict containing the response with id, event_name, timestamp, status, and message
        """
        url = f"{self.api_base_url}/holos/plant/traces"

        try:
            response = requests.post(url, json=tracing_data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Failed to submit tracing data: {str(e)}"
            }
    
    def submit_task_plan_tracing(
        self,
        task_plan: TaskPlan,
        flow_role: Literal['producer', 'consumer', 'producer_consumer'],
        event_name: str = "Create task plan",
        entry_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit tracing data for a task plan.
        
        Args:
            task_plan: TaskPlan object containing task plan data
            flow_role: Flow role ('producer', 'consumer', or 'producer_consumer')
            event_name: Name of the event
            entry_id: Optional unique identifier
        
        Returns:
            Dict containing the response from the tracing API
        """
        tracing_data = self._create_tracing_data_entry(
            object_kind="task_plan",
            object_data=task_plan,
            event_name=event_name,
            flow_role=flow_role,
            entry_id=entry_id,
        )
        
        return self.submit_tracing_data(tracing_data)
    
    def submit_message_tracing(
        self,
        message: Message,
        flow_role: Literal['producer', 'consumer', 'producer_consumer'],
        event_name: str = "Send message",
        entry_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit tracing data for a message.
        
        Args:
            message: A2A Message object
            flow_role: Flow role ('producer', 'consumer', or 'producer_consumer')
            event_name: Name of the event
            entry_id: Optional unique identifier
        
        Returns:
            Dict containing the response from the tracing API
        """
        tracing_data = self._create_tracing_data_entry(
            object_kind="message",
            object_data=message,
            event_name=event_name,
            flow_role=flow_role,
            entry_id=entry_id,
        )
        
        return self.submit_tracing_data(tracing_data)
    
    def submit_task_tracing(
        self,
        task: Task,
        flow_role: Literal['producer', 'consumer', 'producer_consumer'],
        event_name: str = "Create task",
        entry_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit tracing data for a task.
        
        Args:
            task: A2A Task object
            flow_role: Flow role ('producer', 'consumer', or 'producer_consumer')
            event_name: Name of the event
            entry_id: Optional unique identifier
        
        Returns:
            Dict containing the response from the tracing API
        """
        tracing_data = self._create_tracing_data_entry(
            object_kind="task",
            object_data=task,
            event_name=event_name,
            flow_role=flow_role,
            entry_id=entry_id,
        )
        
        return self.submit_tracing_data(tracing_data)
    
    def submit_task_update_event_tracing(
        self,
        task_update_event: TaskStatusUpdateEvent,
        flow_role: Literal['producer', 'consumer', 'producer_consumer'],
        event_name: str = "Update task status",
        entry_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Submit tracing data for a task update event.
        
        Args:
            task_update_event: A2A TaskStatusUpdateEvent object
            flow_role: Flow role ('producer', 'consumer', or 'producer_consumer')
            event_name: Name of the event
            entry_id: Optional unique identifier
        
        Returns:
            Dict containing the response from the tracing API
        """
        tracing_data = self._create_tracing_data_entry(
            object_kind="task_update_event",
            object_data=task_update_event,
            event_name=event_name,
            flow_role=flow_role,
            entry_id=entry_id,
        )
        
        return self.submit_tracing_data(tracing_data)
    