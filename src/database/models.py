"""
ObjectBox entity models for the multi-agent educational platform.

This module defines the core data entities used throughout the platform:
- Student: User profile and learning preferences
- Interaction: Student interactions with the platform
- LearningProgress: Progress tracking for subjects and topics
- CurriculumContent: Educational content with basic structure

All entities use proper ObjectBox decorators and field types for database persistence.
"""

from datetime import datetime
from objectbox import Entity, Id, String, Int64, Float64, Date, Float32Vector
from objectbox.model import Property


@Entity()
class Student:
    """Student entity representing a learner in the platform."""
    id = Id
    name = String
    email = String
    learning_preferences = String
    created_at = Int64
    updated_at = Int64

def update_preferences(self, preferences: str):
        """Update learning preferences and timestamp."""
        self.learning_preferences = preferences
        self.updated_at = int(datetime.now().timestamp() * 1000)

def __str__(self):
    return f"Student(id={self.id}, name='{self.name}', email='{self.email}')"


@Entity()
class Interaction:
    """Interaction entity representing student interactions with agents."""
    id = Id
    student_id = Property(int, id=2, uid=2002, index=True)
    input_type = Property(str, id=3, uid=2003)
    input_content = Property(str, id=4, uid=2004)
    agent_response = Property(str, id=5, uid=2005)
    timestamp = Date
    session_id = Property(str, id=7, uid=2007, index=True)

    def is_multimodal(self) -> bool:
        """Check if interaction involves multimodal input."""
        return self.input_type in ['voice', 'image']

    def __str__(self):
        return f"Interaction(id={self.id}, student_id={self.student_id}, type='{self.input_type}')"


@Entity()
class LearningProgress:
    """Learning progress entity tracking student advancement."""
    id= Id(id=1, uid=3001)
    student_id= Property(int, id=2, uid=3002, index=True)
    subject = Property(str, id=3, uid=3003, index=True)
    topic= Property(str, id=4, uid=3004, index=True)
    completion_percentage = Float64(id=5, uid=3005)
    last_accessed = Date
    performance_score= Property(float, id=7, uid=3007)



@Entity()
class CurriculumContent:
    """Curriculum content entity with basic structure."""
    id= Id(id=1, uid=4001)
    title = Property(str, id=2, uid=4002, index=True)
    content = Property(str, id=3, uid=4003)
    subject = Property(str, id=4, uid=4004, index=True)
    difficulty_level = Property(int, id=5, uid=4005, index=True)
    content_type = Property(str, id=6, uid=4006)
    created_at = Property(int, id=7, uid=4007)
    updated_at = Property(int, id=8, uid=4008)
    vector_embedding: Float32Vector = Float32Vector(id=9, uid=4009)
