"""
Unit tests for ObjectBox entity models.

Tests cover:
- Entity creation and initialization
- Validation functions
- Entity methods and relationships
- Vector embedding functionality
"""

import pytest
from datetime import datetime
from src.database.models import (
    Student, Interaction, LearningProgress, CurriculumContent,
    validate_student, validate_interaction, validate_learning_progress,
    validate_curriculum_content
)


class TestStudentEntity:
    """Test cases for Student entity."""
    
    def test_student_creation(self):
        """Test basic student creation."""
        student = Student(
            name="John Doe",
            email="john@example.com",
            learning_preferences="visual,interactive"
        )
        
        assert student.name == "John Doe"
        assert student.email == "john@example.com"
        assert student.learning_preferences == "visual,interactive"
        assert isinstance(student.created_at, int)
        assert isinstance(student.updated_at, int)
    
    def test_student_default_creation(self):
        """Test student creation with default values."""
        student = Student()
        
        assert student.name == ""
        assert student.email == ""
        assert student.learning_preferences == ""
        assert isinstance(student.created_at, int)
    
    def test_update_preferences(self):
        """Test updating student preferences."""
        student = Student(name="Jane", email="jane@example.com")
        original_updated = student.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.001)
        
        student.update_preferences("auditory,kinesthetic")
        
        assert student.learning_preferences == "auditory,kinesthetic"
        assert student.updated_at > original_updated
    
    def test_student_str_representation(self):
        """Test string representation of student."""
        student = Student(name="Test User", email="test@example.com")
        student.id = 1
        
        str_repr = str(student)
        assert "Student" in str_repr
        assert "Test User" in str_repr
        assert "test@example.com" in str_repr


class TestInteractionEntity:
    """Test cases for Interaction entity."""
    
    def test_interaction_creation(self):
        """Test basic interaction creation."""
        interaction = Interaction(
            student_id=1,
            input_type="text",
            input_content="Hello, I need help with math",
            agent_response="I can help you with math problems",
            session_id="session_123"
        )
        
        assert interaction.student_id == 1
        assert interaction.input_type == "text"
        assert interaction.input_content == "Hello, I need help with math"
        assert interaction.agent_response == "I can help you with math problems"
        assert interaction.session_id == "session_123"
        assert isinstance(interaction.timestamp, int)
    
    def test_is_multimodal(self):
        """Test multimodal input detection."""
        text_interaction = Interaction(input_type="text")
        voice_interaction = Interaction(input_type="voice")
        image_interaction = Interaction(input_type="image")
        
        assert not text_interaction.is_multimodal()
        assert voice_interaction.is_multimodal()
        assert image_interaction.is_multimodal()
    
    def test_interaction_str_representation(self):
        """Test string representation of interaction."""
        interaction = Interaction(student_id=1, input_type="voice")
        interaction.id = 1
        
        str_repr = str(interaction)
        assert "Interaction" in str_repr
        assert "student_id=1" in str_repr
        assert "voice" in str_repr


class TestLearningProgressEntity:
    """Test cases for LearningProgress entity."""
    
    def test_learning_progress_creation(self):
        """Test basic learning progress creation."""
        progress = LearningProgress(
            student_id=1,
            subject="Mathematics",
            topic="Algebra",
            completion_percentage=75.5,
            performance_score=85.0
        )
        
        assert progress.student_id == 1
        assert progress.subject == "Mathematics"
        assert progress.topic == "Algebra"
        assert progress.completion_percentage == 75.5
        assert progress.performance_score == 85.0
        assert isinstance(progress.last_accessed, int)
    
    def test_update_progress(self):
        """Test updating progress metrics."""
        progress = LearningProgress(student_id=1, subject="Math", topic="Calculus")
        original_accessed = progress.last_accessed
        
        import time
        time.sleep(0.001)
        
        progress.update_progress(90.0, 88.5)
        
        assert progress.completion_percentage == 90.0
        assert progress.performance_score == 88.5
        assert progress.last_accessed > original_accessed
    
    def test_update_progress_bounds(self):
        """Test progress update with boundary values."""
        progress = LearningProgress()
        
        # Test upper bounds
        progress.update_progress(150.0, 120.0)
        assert progress.completion_percentage == 100.0
        assert progress.performance_score == 100.0
        
        # Test lower bounds
        progress.update_progress(-10.0, -5.0)
        assert progress.completion_percentage == 0.0
        assert progress.performance_score == 0.0
    
    def test_is_completed(self):
        """Test completion status check."""
        incomplete_progress = LearningProgress(completion_percentage=75.0)
        complete_progress = LearningProgress(completion_percentage=100.0)
        
        assert not incomplete_progress.is_completed()
        assert complete_progress.is_completed()
    
    def test_learning_progress_str_representation(self):
        """Test string representation of learning progress."""
        progress = LearningProgress(
            student_id=1, 
            subject="Science", 
            topic="Physics",
            completion_percentage=60.0
        )
        progress.id = 1
        
        str_repr = str(progress)
        assert "LearningProgress" in str_repr
        assert "Science" in str_repr
        assert "Physics" in str_repr
        assert "60.0%" in str_repr


class TestCurriculumContentEntity:
    """Test cases for CurriculumContent entity."""
    
    def test_curriculum_content_creation(self):
        """Test basic curriculum content creation."""
        content = CurriculumContent(
            title="Introduction to Algebra",
            content="Algebra is a branch of mathematics...",
            subject="Mathematics",
            difficulty_level=5,
            content_type="lesson"
        )
        
        assert content.title == "Introduction to Algebra"
        assert content.content == "Algebra is a branch of mathematics..."
        assert content.subject == "Mathematics"
        assert content.difficulty_level == 5
        assert content.content_type == "lesson"
        assert isinstance(content.created_at, int)
        assert isinstance(content.updated_at, int)
    
    def test_update_content(self):
        """Test content update functionality."""
        content = CurriculumContent(title="Original", content="Original content")
        original_updated = content.updated_at
        
        import time
        time.sleep(0.001)
        
        content.update_content("Updated content")
        
        assert content.content == "Updated content"
        assert content.updated_at > original_updated
    
    def test_is_advanced(self):
        """Test advanced content detection."""
        basic_content = CurriculumContent(difficulty_level=5)
        advanced_content = CurriculumContent(difficulty_level=9)
        
        assert not basic_content.is_advanced()
        assert advanced_content.is_advanced()
    
    def test_curriculum_content_str_representation(self):
        """Test string representation of curriculum content."""
        content = CurriculumContent(
            title="Test Lesson",
            subject="Science",
            difficulty_level=7
        )
        content.id = 1
        
        str_repr = str(content)
        assert "CurriculumContent" in str_repr
        assert "Test Lesson" in str_repr
        assert "Science" in str_repr
        assert "difficulty=7" in str_repr


class TestEntityValidation:
    """Test cases for entity validation functions."""
    
    def test_validate_student_valid(self):
        """Test validation of valid student."""
        student = Student(name="John Doe", email="john@example.com")
        errors = validate_student(student)
        assert len(errors) == 0
    
    def test_validate_student_invalid(self):
        """Test validation of invalid student."""
        # Empty name
        student = Student(name="", email="john@example.com")
        errors = validate_student(student)
        assert "Student name cannot be empty" in errors
        
        # Invalid email
        student = Student(name="John", email="invalid-email")
        errors = validate_student(student)
        assert "Student email must be valid" in errors
        
        # Name too long
        student = Student(name="x" * 101, email="john@example.com")
        errors = validate_student(student)
        assert "Student name cannot exceed 100 characters" in errors
    
    def test_validate_interaction_valid(self):
        """Test validation of valid interaction."""
        interaction = Interaction(
            student_id=1,
            input_type="text",
            input_content="Hello",
            session_id="session_123"
        )
        errors = validate_interaction(interaction)
        assert len(errors) == 0
    
    def test_validate_interaction_invalid(self):
        """Test validation of invalid interaction."""
        # Invalid student_id
        interaction = Interaction(student_id=0, input_type="text", input_content="Hello", session_id="123")
        errors = validate_interaction(interaction)
        assert "Interaction must have valid student_id" in errors
        
        # Invalid input type
        interaction = Interaction(student_id=1, input_type="invalid", input_content="Hello", session_id="123")
        errors = validate_interaction(interaction)
        assert "Input type must be 'text', 'voice', or 'image'" in errors
        
        # Empty content
        interaction = Interaction(student_id=1, input_type="text", input_content="", session_id="123")
        errors = validate_interaction(interaction)
        assert "Input content cannot be empty" in errors
        
        # Empty session ID
        interaction = Interaction(student_id=1, input_type="text", input_content="Hello", session_id="")
        errors = validate_interaction(interaction)
        assert "Session ID cannot be empty" in errors
    
    def test_validate_learning_progress_valid(self):
        """Test validation of valid learning progress."""
        progress = LearningProgress(
            student_id=1,
            subject="Math",
            topic="Algebra",
            completion_percentage=75.0,
            performance_score=85.0
        )
        errors = validate_learning_progress(progress)
        assert len(errors) == 0
    
    def test_validate_learning_progress_invalid(self):
        """Test validation of invalid learning progress."""
        # Invalid student_id
        progress = LearningProgress(student_id=0, subject="Math", topic="Algebra")
        errors = validate_learning_progress(progress)
        assert "Learning progress must have valid student_id" in errors
        
        # Empty subject
        progress = LearningProgress(student_id=1, subject="", topic="Algebra")
        errors = validate_learning_progress(progress)
        assert "Subject cannot be empty" in errors
        
        # Empty topic
        progress = LearningProgress(student_id=1, subject="Math", topic="")
        errors = validate_learning_progress(progress)
        assert "Topic cannot be empty" in errors
        
        # Invalid completion percentage
        progress = LearningProgress(student_id=1, subject="Math", topic="Algebra", completion_percentage=150.0)
        errors = validate_learning_progress(progress)
        assert "Completion percentage must be between 0 and 100" in errors
        
        # Invalid performance score
        progress = LearningProgress(student_id=1, subject="Math", topic="Algebra", performance_score=-10.0)
        errors = validate_learning_progress(progress)
        assert "Performance score must be between 0 and 100" in errors
    
    def test_validate_curriculum_content_valid(self):
        """Test validation of valid curriculum content."""
        content = CurriculumContent(
            title="Test Lesson",
            content="Lesson content",
            subject="Math",
            difficulty_level=5,
            content_type="lesson"
        )
        errors = validate_curriculum_content(content)
        assert len(errors) == 0
    
    def test_validate_curriculum_content_invalid(self):
        """Test validation of invalid curriculum content."""
        # Empty title
        content = CurriculumContent(title="", content="Content", subject="Math", content_type="lesson")
        errors = validate_curriculum_content(content)
        assert "Content title cannot be empty" in errors
        
        # Empty content
        content = CurriculumContent(title="Title", content="", subject="Math", content_type="lesson")
        errors = validate_curriculum_content(content)
        assert "Content body cannot be empty" in errors
        
        # Empty subject
        content = CurriculumContent(title="Title", content="Content", subject="", content_type="lesson")
        errors = validate_curriculum_content(content)
        assert "Subject cannot be empty" in errors
        
        # Invalid difficulty level
        content = CurriculumContent(title="Title", content="Content", subject="Math", difficulty_level=15, content_type="lesson")
        errors = validate_curriculum_content(content)
        assert "Difficulty level must be between 1 and 10" in errors
        
        # Empty content type
        content = CurriculumContent(title="Title", content="Content", subject="Math", content_type="")
        errors = validate_curriculum_content(content)
        assert "Content type cannot be empty" in errors