"""
Specific API endpoint implementations for Paymo.

This module contains high-level methods for interacting with specific
Paymo API endpoints like projects, clients, tasks, etc.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date

from client import PaymoClient
from exceptions import PaymoAPIError


class ProjectsEndpoint:
    """High-level interface for project-related operations."""
    
    def __init__(self, client: PaymoClient):
        self.client = client
    
    def list(
        self, 
        include: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List all projects.
        
        Args:
            include: List of related resources to include
            where: Filter conditions
            page: Page number for pagination
            per_page: Number of items per page
            
        Returns:
            List of project dictionaries
        """
        params = {}
        if include:
            params['include'] = ','.join(include)
        if where:
            params['where'] = self._build_where_clause(where)
        if page is not None:
            params['page'] = page
        if per_page is not None:
            params['per_page'] = per_page
        
        return self.client.get('projects', params=params)
    
    def get(self, project_id: Union[int, str]) -> Dict[str, Any]:
        """
        Get a specific project by ID.
        
        Args:
            project_id: The project ID
            
        Returns:
            Project dictionary
        """
        return self.client.get(f'projects/{project_id}')
    
    def create(
        self,
        name: str,
        client_id: Optional[int] = None,
        description: Optional[str] = None,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
        budget: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new project.
        
        Args:
            name: Project name
            client_id: Associated client ID
            description: Project description
            start_date: Project start date
            end_date: Project end date
            budget: Project budget
            **kwargs: Additional project fields
            
        Returns:
            Created project dictionary
        """
        data = {
            'name': name,
            **kwargs
        }
        
        if client_id is not None:
            data['client_id'] = client_id
        if description is not None:
            data['description'] = description
        if start_date is not None:
            data['start_date'] = self._format_date(start_date)
        if end_date is not None:
            data['end_date'] = self._format_date(end_date)
        if budget is not None:
            data['budget'] = budget
        
        return self.client.post('projects', data=data)
    
    def update(
        self,
        project_id: Union[int, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing project.
        
        Args:
            project_id: The project ID
            **kwargs: Fields to update
            
        Returns:
            Updated project dictionary
        """
        # Format date fields if present
        for field in ['start_date', 'end_date']:
            if field in kwargs and kwargs[field] is not None:
                kwargs[field] = self._format_date(kwargs[field])
        
        return self.client.put(f'projects/{project_id}', data=kwargs)
    
    def delete(self, project_id: Union[int, str]) -> bool:
        """
        Delete a project.
        
        Args:
            project_id: The project ID
            
        Returns:
            True if successful, False otherwise
        """
        return self.client.delete(f'projects/{project_id}')
    
    def _build_where_clause(self, where: Dict[str, Any]) -> str:
        """Build a where clause string from a dictionary."""
        conditions = []
        for key, value in where.items():
            if isinstance(value, str):
                conditions.append(f"{key}='{value}'")
            else:
                conditions.append(f"{key}={value}")
        return ' AND '.join(conditions)
    
    def _format_date(self, date_value: Union[str, date, datetime]) -> str:
        """Format a date value for the API."""
        if isinstance(date_value, str):
            return date_value
        elif isinstance(date_value, (date, datetime)):
            return date_value.strftime('%Y-%m-%d')
        else:
            raise ValueError(f"Invalid date format: {date_value}")


class ClientsEndpoint:
    """High-level interface for client-related operations."""
    
    def __init__(self, client: PaymoClient):
        self.client = client
    
    def list(
        self,
        include: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List all clients."""
        params = {}
        if include:
            params['include'] = ','.join(include)
        if where:
            params['where'] = self._build_where_clause(where)
        if page is not None:
            params['page'] = page
        if per_page is not None:
            params['per_page'] = per_page
        
        return self.client.get('clients', params=params)
    
    def get(self, client_id: Union[int, str]) -> Dict[str, Any]:
        """Get a specific client by ID."""
        return self.client.get(f'clients/{client_id}')
    
    def create(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new client."""
        data = {
            'name': name,
            **kwargs
        }
        
        if email is not None:
            data['email'] = email
        if phone is not None:
            data['phone'] = phone
        if address is not None:
            data['address'] = address
        
        return self.client.post('clients', data=data)
    
    def update(
        self,
        client_id: Union[int, str],
        **kwargs
    ) -> Dict[str, Any]:
        """Update an existing client."""
        return self.client.put(f'clients/{client_id}', data=kwargs)
    
    def delete(self, client_id: Union[int, str]) -> bool:
        """Delete a client."""
        return self.client.delete(f'clients/{client_id}')
    
    def _build_where_clause(self, where: Dict[str, Any]) -> str:
        """Build a where clause string from a dictionary."""
        conditions = []
        for key, value in where.items():
            if isinstance(value, str):
                conditions.append(f"{key}='{value}'")
            else:
                conditions.append(f"{key}={value}")
        return ' AND '.join(conditions)


class TasksEndpoint:
    """High-level interface for task-related operations."""
    
    def __init__(self, client: PaymoClient):
        self.client = client
    
    def list(
        self,
        project_id: Optional[Union[int, str]] = None,
        include: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by project."""
        params = {}
        if project_id is not None:
            params['project_id'] = project_id
        if include:
            params['include'] = ','.join(include)
        if where:
            params['where'] = self._build_where_clause(where)
        if page is not None:
            params['page'] = page
        if per_page is not None:
            params['per_page'] = per_page
        
        return self.client.get('tasks', params=params)
    
    def get(self, task_id: Union[int, str]) -> Dict[str, Any]:
        """Get a specific task by ID."""
        return self.client.get(f'tasks/{task_id}')
    
    def create(
        self,
        name: str,
        project_id: Union[int, str],
        description: Optional[str] = None,
        due_date: Optional[Union[str, date, datetime]] = None,
        priority: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new task."""
        data = {
            'name': name,
            'project_id': project_id,
            **kwargs
        }
        
        if description is not None:
            data['description'] = description
        if due_date is not None:
            data['due_date'] = self._format_date(due_date)
        if priority is not None:
            data['priority'] = priority
        
        return self.client.post('tasks', data=data)
    
    def update(
        self,
        task_id: Union[int, str],
        **kwargs
    ) -> Dict[str, Any]:
        """Update an existing task."""
        # Format date fields if present
        for field in ['due_date']:
            if field in kwargs and kwargs[field] is not None:
                kwargs[field] = self._format_date(kwargs[field])
        
        return self.client.put(f'tasks/{task_id}', data=kwargs)
    
    def delete(self, task_id: Union[int, str]) -> bool:
        """Delete a task."""
        return self.client.delete(f'tasks/{task_id}')
    
    def _build_where_clause(self, where: Dict[str, Any]) -> str:
        """Build a where clause string from a dictionary."""
        conditions = []
        for key, value in where.items():
            if isinstance(value, str):
                conditions.append(f"{key}='{value}'")
            else:
                conditions.append(f"{key}={value}")
        return ' AND '.join(conditions)
    
    def _format_date(self, date_value: Union[str, date, datetime]) -> str:
        """Format a date value for the API."""
        if isinstance(date_value, str):
            return date_value
        elif isinstance(date_value, (date, datetime)):
            return date_value.strftime('%Y-%m-%d')
        else:
            raise ValueError(f"Invalid date format: {date_value}")


class TimeEntriesEndpoint:
    """High-level interface for time entry operations."""
    
    def __init__(self, client: PaymoClient):
        self.client = client
    
    def list(
        self,
        project_id: Optional[Union[int, str]] = None,
        task_id: Optional[Union[int, str]] = None,
        user_id: Optional[Union[int, str]] = None,
        start_date: Optional[Union[str, date, datetime]] = None,
        end_date: Optional[Union[str, date, datetime]] = None,
        include: Optional[List[str]] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List time entries with optional filters."""
        params = {}
        
        if project_id is not None:
            params['project_id'] = project_id
        if task_id is not None:
            params['task_id'] = task_id
        if user_id is not None:
            params['user_id'] = user_id
        if start_date is not None:
            params['start_date'] = self._format_date(start_date)
        if end_date is not None:
            params['end_date'] = self._format_date(end_date)
        if include:
            params['include'] = ','.join(include)
        if page is not None:
            params['page'] = page
        if per_page is not None:
            params['per_page'] = per_page
        
        return self.client.get('entries', params=params)
    
    def get(self, time_entry_id: Union[int, str]) -> Dict[str, Any]:
        """Get a specific time entry by ID."""
        return self.client.get(f'entries/{time_entry_id}')
    
    def create(
        self,
        project_id: Union[int, str],
        task_id: Union[int, str],
        start_time: Union[str, datetime],
        end_time: Optional[Union[str, datetime]] = None,
        duration: Optional[int] = None,  # in minutes
        description: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new time entry."""
        data = {
            'project_id': project_id,
            'task_id': task_id,
            'start_time': self._format_datetime(start_time),
            **kwargs
        }
        
        if end_time is not None:
            data['end_time'] = self._format_datetime(end_time)
        if duration is not None:
            data['duration'] = duration
        if description is not None:
            data['description'] = description
        
        return self.client.post('entries', data=data)
    
    def update(
        self,
        time_entry_id: Union[int, str],
        **kwargs
    ) -> Dict[str, Any]:
        """Update an existing time entry."""
        # Format datetime fields if present
        for field in ['start_time', 'end_time']:
            if field in kwargs and kwargs[field] is not None:
                kwargs[field] = self._format_datetime(kwargs[field])
        
        return self.client.put(f'entries/{time_entry_id}', data=kwargs)
    
    def delete(self, time_entry_id: Union[int, str]) -> bool:
        """Delete a time entry."""
        return self.client.delete(f'entries/{time_entry_id}')
    
    def _format_date(self, date_value: Union[str, date, datetime]) -> str:
        """Format a date value for the API."""
        if isinstance(date_value, str):
            return date_value
        elif isinstance(date_value, (date, datetime)):
            return date_value.strftime('%Y-%m-%d')
        else:
            raise ValueError(f"Invalid date format: {date_value}")
    
    def _format_datetime(self, datetime_value: Union[str, datetime]) -> str:
        """Format a datetime value for the API."""
        if isinstance(datetime_value, str):
            return datetime_value
        elif isinstance(datetime_value, datetime):
            return datetime_value.strftime('%Y-%m-%d %H:%M:%S')
        else:
            raise ValueError(f"Invalid datetime format: {datetime_value}")
