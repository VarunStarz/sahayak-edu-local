"""
ObjectBox entity models for the multi-agent educational platform.

This module defines the core data entities used throughout the platform:
- Student: User profile and learning preferences
- Interaction: Student interactions with the platform
- LearningProgress: Progress tracking for subjects and topics
- CurriculumContent: Educational content with basic structure

All entities use proper ObjectBox decorators and field types for database persistence.
"""

import re
from datetime import datetime
from typing import List, Optional
from objectbox import Entity, Id, String, Int64, Float64, Date, Float32Vector
from objectbox.model import Property


@Entity
class Student:
    """Student entity representing a learner in the platform."""
    id: int = Id(id=1, uid=1001)
    name: str = Property(str, id=2, uid=1002, index=True)
    email: str = Property(str, id=3, uid=1003, index=True)
    learning_preferences: str = Property(str, id=4, uid=1004)
    created_at: int = Property(int, id=5, uid=1005)
    updated_at: int = Property(int, id=6, uid=1006)

    def update_preferences(self, preferences: str):
        """Update learning preferences and timestamp."""
        self.learning_preferences = preferences
        self.updated_at = int(datetime.now().timestamp() * 1000)

    def __str__(self):
        return f"Student(id={self.id}, name='{self.name}', email='{self.email}')"


@Entity
class Interaction:
    """Interaction entity representing student interactions with agents."""
    id: int = Id(id=1, uid=2001)
    student_id: int = Property(int, id=2, uid=2002, index=True)
    input_type: str = Property(str, id=3, uid=2003)
    input_content: str = Property(str, id=4, uid=2004)
    agent_response: str = Property(str, id=5, uid=2005)
    timestamp: int = Property(int, id=6, uid=2006, index=True)
    session_id: str = Property(str, id=7, uid=2007, index=True)

    def is_multimodal(self) -> bool:
        """Check if interaction involves multimodal input."""
        return self.input_type in ['voice', 'image']

    def __str__(self):
        return f"Interaction(id={self.id}, student_id={self.student_id}, type='{self.input_type}')"


@Entity
class LearningProgress:
    """Learning progress entity tracking student advancement."""
    id: int = Id(id=1, uid=3001)
    student_id: int = Property(int, id=2, uid=3002, index=True)
    subject: str = Property(str, id=3, uid=3003, index=True)
    topic: str = Property(str, id=4, uid=3004, index=True)
    completion_percentage: float = Property(float, id=5, uid=3005)
    last_accessed: int = Property(int, id=6, uid=3006)
    performance_score: float = Property(float, id=7, uid=3007)

    def update_progress(self, completion: float, score: float):
        """Update progress metrics and timestamp."""
        self.completion_percentage = max(0.0, min(100.0, completion))
        self.performance_score = max(0.0, min(100.0, score))
        self.last_accessed = int(datetime.now().timestamp() * 1000)

    def is_completed(self) -> bool:
        """Check if topic is completed."""
        return self.completion_percentage >= 100.0

    def __str__(self):
        return f"LearningProgress(id={self.id}, student_id={self.student_id}, subject='{self.subject}', topic='{self.topic}', completion={self.completion_percentage}%)"


@Entity
class CurriculumContent:
    """Curriculum content entity with basic structure."""
    id: int = Id(id=1, uid=4001)
    title: str = Property(str, id=2, uid=4002, index=True)
    content: str = Property(str, id=3, uid=4003)
    subject: str = Property(str, id=4, uid=4004, index=True)
    difficulty_level: int = Property(int, id=5, uid=4005, index=True)
    content_type: str = Property(str, id=6, uid=4006)
    created_at: int = Property(int, id=7, uid=4007)
    updated_at: int = Property(int, id=8, uid=4008)
    vector_embedding: Float32Vector = Float32Vector(id=9, uid=4009)

    def update_content(self, content: str):
        """Update content and timestamp."""
        self.content = content
        self.updated_at = int(datetime.now().timestamp() * 1000)

    def is_advanced(self) -> bool:
        """Check if content is advanced level (difficulty > 7)."""
        return self.difficulty_level > 7
    
    def get_vector_embedding(self) -> Optional[List[float]]:
        """Get the vector embedding of the content."""
        return self.vector_embedding

    def __str__(self):
        return f"CurriculumContent(id={self.id}, title='{self.title}', subject='{self.subject}', difficulty={self.difficulty_level})"


