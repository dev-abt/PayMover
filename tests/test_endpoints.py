"""
Unit tests for API endpoint implementations.

This module contains tests for the high-level endpoint classes.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, date

from paymover.endpoints import ProjectsEndpoint, ClientsEndpoint, TasksEndpoint, TimeEntriesEndpoint
from paymover.client import PaymoClient
from paymover.exceptions import PaymoAPIError


class TestProjectsEndpoint:
    """Test cases for ProjectsEndpoint."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock(spec=PaymoClient)
        self.endpoint = ProjectsEndpoint(self.mock_client)
    
    def test_list_projects(self):
        """Test listing projects."""
        # Arrange
        expected_projects = [
            {"id": 1, "name": "Project 1"},
            {"id": 2, "name": "Project 2"}
        ]
        self.mock_client.get.return_value = expected_projects
        
        # Act
        result = self.endpoint.list()
        
        # Assert
        assert result == expected_projects
        self.mock_client.get.assert_called_once_with("projects", params={})
    
    def test_list_projects_with_filters(self):
        """Test listing projects with filters."""
        # Arrange
        expected_projects = [{"id": 1, "name": "Project 1"}]
        self.mock_client.get.return_value = expected_projects
        
        # Act
        result = self.endpoint.list(
            include=["client", "tasks"],
            where={"status": "active"},
            page=1,
            per_page=10
        )
        
        # Assert
        assert result == expected_projects
        call_args = self.mock_client.get.call_args
        assert call_args[0][0] == "projects"
        params = call_args[0][1]
        assert params["include"] == "client,tasks"
        assert params["where"] == "status='active'"
        assert params["page"] == 1
        assert params["per_page"] == 10
    
    def test_get_project(self):
        """Test getting a specific project."""
        # Arrange
        expected_project = {"id": 1, "name": "Project 1"}
        self.mock_client.get.return_value = expected_project
        
        # Act
        result = self.endpoint.get(1)
        
        # Assert
        assert result == expected_project
        self.mock_client.get.assert_called_once_with("projects/1")
    
    def test_create_project(self):
        """Test creating a project."""
        # Arrange
        project_data = {
            "name": "New Project",
            "description": "Test project",
            "client_id": 123,
            "budget": 5000.0
        }
        expected_response = {"id": 2, **project_data}
        self.mock_client.post.return_value = expected_response
        
        # Act
        result = self.endpoint.create(**project_data)
        
        # Assert
        assert result == expected_response
        self.mock_client.post.assert_called_once_with("projects", data=project_data)
    
    def test_create_project_with_dates(self):
        """Test creating a project with date fields."""
        # Arrange
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        project_data = {
            "name": "New Project",
            "start_date": start_date,
            "end_date": end_date
        }
        expected_data = {
            "name": "New Project",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
        expected_response = {"id": 2, **expected_data}
        self.mock_client.post.return_value = expected_response
        
        # Act
        result = self.endpoint.create(**project_data)
        
        # Assert
        assert result == expected_response
        call_args = self.mock_client.post.call_args
        assert call_args[0][0] == "projects"
        assert call_args[0][1] == expected_data
    
    def test_update_project(self):
        """Test updating a project."""
        # Arrange
        update_data = {"name": "Updated Project", "budget": 10000.0}
        expected_response = {"id": 1, **update_data}
        self.mock_client.put.return_value = expected_response
        
        # Act
        result = self.endpoint.update(1, **update_data)
        
        # Assert
        assert result == expected_response
        self.mock_client.put.assert_called_once_with("projects/1", data=update_data)
    
    def test_delete_project(self):
        """Test deleting a project."""
        # Arrange
        self.mock_client.delete.return_value = True
        
        # Act
        result = self.endpoint.delete(1)
        
        # Assert
        assert result is True
        self.mock_client.delete.assert_called_once_with("projects/1")
    
    def test_build_where_clause(self):
        """Test where clause building."""
        # Arrange
        where_conditions = {"status": "active", "client_id": 123}
        
        # Act
        result = self.endpoint._build_where_clause(where_conditions)
        
        # Assert
        assert "status='active'" in result
        assert "client_id=123" in result
        assert " AND " in result
    
    def test_format_date(self):
        """Test date formatting."""
        # Test string date
        assert self.endpoint._format_date("2024-01-01") == "2024-01-01"
        
        # Test date object
        test_date = date(2024, 1, 1)
        assert self.endpoint._format_date(test_date) == "2024-01-01"
        
        # Test datetime object
        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        assert self.endpoint._format_date(test_datetime) == "2024-01-01"
        
        # Test invalid type
        with pytest.raises(ValueError):
            self.endpoint._format_date(123)


class TestClientsEndpoint:
    """Test cases for ClientsEndpoint."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock(spec=PaymoClient)
        self.endpoint = ClientsEndpoint(self.mock_client)
    
    def test_list_clients(self):
        """Test listing clients."""
        # Arrange
        expected_clients = [
            {"id": 1, "name": "Client 1"},
            {"id": 2, "name": "Client 2"}
        ]
        self.mock_client.get.return_value = expected_clients
        
        # Act
        result = self.endpoint.list()
        
        # Assert
        assert result == expected_clients
        self.mock_client.get.assert_called_once_with("clients", params={})
    
    def test_create_client(self):
        """Test creating a client."""
        # Arrange
        client_data = {
            "name": "New Client",
            "email": "client@example.com",
            "phone": "+1234567890"
        }
        expected_response = {"id": 1, **client_data}
        self.mock_client.post.return_value = expected_response
        
        # Act
        result = self.endpoint.create(**client_data)
        
        # Assert
        assert result == expected_response
        self.mock_client.post.assert_called_once_with("clients", data=client_data)


class TestTasksEndpoint:
    """Test cases for TasksEndpoint."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock(spec=PaymoClient)
        self.endpoint = TasksEndpoint(self.mock_client)
    
    def test_list_tasks(self):
        """Test listing tasks."""
        # Arrange
        expected_tasks = [
            {"id": 1, "name": "Task 1", "project_id": 123},
            {"id": 2, "name": "Task 2", "project_id": 123}
        ]
        self.mock_client.get.return_value = expected_tasks
        
        # Act
        result = self.endpoint.list()
        
        # Assert
        assert result == expected_tasks
        self.mock_client.get.assert_called_once_with("tasks", params={})
    
    def test_list_tasks_with_project_filter(self):
        """Test listing tasks filtered by project."""
        # Arrange
        expected_tasks = [{"id": 1, "name": "Task 1", "project_id": 123}]
        self.mock_client.get.return_value = expected_tasks
        
        # Act
        result = self.endpoint.list(project_id=123)
        
        # Assert
        assert result == expected_tasks
        call_args = self.mock_client.get.call_args
        assert call_args[0][0] == "tasks"
        assert call_args[0][1]["project_id"] == 123
    
    def test_create_task(self):
        """Test creating a task."""
        # Arrange
        task_data = {
            "name": "New Task",
            "project_id": 123,
            "description": "Task description",
            "due_date": date(2024, 12, 31)
        }
        expected_data = {
            "name": "New Task",
            "project_id": 123,
            "description": "Task description",
            "due_date": "2024-12-31"
        }
        expected_response = {"id": 1, **expected_data}
        self.mock_client.post.return_value = expected_response
        
        # Act
        result = self.endpoint.create(**task_data)
        
        # Assert
        assert result == expected_response
        call_args = self.mock_client.post.call_args
        assert call_args[0][0] == "tasks"
        assert call_args[0][1] == expected_data


class TestTimeEntriesEndpoint:
    """Test cases for TimeEntriesEndpoint."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock(spec=PaymoClient)
        self.endpoint = TimeEntriesEndpoint(self.mock_client)
    
    def test_list_time_entries(self):
        """Test listing time entries."""
        # Arrange
        expected_entries = [
            {"id": 1, "project_id": 123, "task_id": 456, "duration": 480},
            {"id": 2, "project_id": 123, "task_id": 789, "duration": 240}
        ]
        self.mock_client.get.return_value = expected_entries
        
        # Act
        result = self.endpoint.list()
        
        # Assert
        assert result == expected_entries
        self.mock_client.get.assert_called_once_with("time_entries", params={})
    
    def test_list_time_entries_with_filters(self):
        """Test listing time entries with filters."""
        # Arrange
        expected_entries = [{"id": 1, "project_id": 123, "duration": 480}]
        self.mock_client.get.return_value = expected_entries
        
        # Act
        result = self.endpoint.list(
            project_id=123,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        # Assert
        assert result == expected_entries
        call_args = self.mock_client.get.call_args
        assert call_args[0][0] == "time_entries"
        params = call_args[0][1]
        assert params["project_id"] == 123
        assert params["start_date"] == "2024-01-01"
        assert params["end_date"] == "2024-01-31"
    
    def test_create_time_entry(self):
        """Test creating a time entry."""
        # Arrange
        entry_data = {
            "project_id": 123,
            "task_id": 456,
            "start_time": datetime(2024, 1, 1, 9, 0, 0),
            "end_time": datetime(2024, 1, 1, 17, 0, 0),
            "description": "Working on project"
        }
        expected_data = {
            "project_id": 123,
            "task_id": 456,
            "start_time": "2024-01-01 09:00:00",
            "end_time": "2024-01-01 17:00:00",
            "description": "Working on project"
        }
        expected_response = {"id": 1, **expected_data}
        self.mock_client.post.return_value = expected_response
        
        # Act
        result = self.endpoint.create(**entry_data)
        
        # Assert
        assert result == expected_response
        call_args = self.mock_client.post.call_args
        assert call_args[0][0] == "time_entries"
        assert call_args[0][1] == expected_data
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        # Test string datetime
        assert self.endpoint._format_datetime("2024-01-01 09:00:00") == "2024-01-01 09:00:00"
        
        # Test datetime object
        test_datetime = datetime(2024, 1, 1, 9, 0, 0)
        assert self.endpoint._format_datetime(test_datetime) == "2024-01-01 09:00:00"
        
        # Test invalid type
        with pytest.raises(ValueError):
            self.endpoint._format_datetime(123)
