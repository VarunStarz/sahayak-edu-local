"""
Repository pattern implementation for ObjectBox entities.

This module provides:
- Base repository class with common CRUD operations
- Specific repositories for each entity type
- Query builders and filtering capabilities
- Transaction management for complex operations
"""

import logging
from typing import List, Optional, Dict, Any, TypeVar, Generic, Type
from abc import ABC, abstractmethod
from datetime import datetime

from .models import Student, Interaction, LearningProgress, CurriculumContent
from .connection import get_database, database_transaction

logger = logging.getLogger(__name__)

# Generic type for entity models
T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """Base repository class providing common CRUD operations."""
    
    def __init__(self, entity_class: Type[T]):
        self.entity_class = entity_class
        self._store = None
        self._box = None
    
    @property
    def store(self):
        """Get ObjectBox Store instance."""
        if self._store is None:
            self._store = get_database()
        return self._store
    
    @property
    def box(self):
        """Get ObjectBox Box instance for the entity."""
        if self._box is None:
            self._box = self.store.box(self.entity_class)
        return self._box
    
    def create(self, entity: T) -> T:
        """
        Create a new entity in the database.
        
        Args:
            entity: Entity instance to create
            
        Returns:
            Created entity with assigned ID
        """
        try:
            with database_transaction():
                entity_id = self.box.put(entity)
                entity.id = entity_id
                logger.debug(f"Created {self.entity_class.__name__} with ID {entity_id}")
                return entity
        except Exception as e:
            logger.error(f"Failed to create {self.entity_class.__name__}: {e}")
            raise
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Retrieve entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity instance or None if not found
        """
        try:
            return self.box.get(entity_id)
        except Exception as e:
            logger.error(f"Failed to get {self.entity_class.__name__} by ID {entity_id}: {e}")
            return None
    
    def get_all(self) -> List[T]:
        """
        Retrieve all entities.
        
        Returns:
            List of all entities
        """
        try:
            return self.box.get_all()
        except Exception as e:
            logger.error(f"Failed to get all {self.entity_class.__name__}: {e}")
            return []
    
    def update(self, entity: T) -> T:
        """
        Update an existing entity.
        
        Args:
            entity: Entity instance to update
            
        Returns:
            Updated entity
        """
        try:
            with database_transaction():
                self.box.put(entity)
                logger.debug(f"Updated {self.entity_class.__name__} with ID {entity.id}")
                return entity
        except Exception as e:
            logger.error(f"Failed to update {self.entity_class.__name__}: {e}")
            raise
    
    def delete(self, entity_id: int) -> bool:
        """
        Delete entity by ID.
        
        Args:
            entity_id: Entity ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            with database_transaction():
                return self.box.remove(entity_id)
        except Exception as e:
            logger.error(f"Failed to delete {self.entity_class.__name__} with ID {entity_id}: {e}")
            return False
    
    def count(self) -> int:
        """
        Get total count of entities.
        
        Returns:
            Total number of entities
        """
        try:
            return self.box.count()
        except Exception as e:
            logger.error(f"Failed to count {self.entity_class.__name__}: {e}")
            return 0

    def create_many(self, entities: List[T]) -> List[T]:
        """
        Create multiple new entities in the database.
        
        Args:
            entities: List of entity instances to create
            
        Returns:
            List of created entities with assigned IDs
        """
        try:
            with database_transaction():
                self.box.put(entities)
                logger.debug(f"Created {len(entities)} {self.entity_class.__name__} entities")
                return entities
        except Exception as e:
            logger.error(f"Failed to create multiple {self.entity_class.__name__} entities: {e}")
            raise
    
    def delete_many(self, entity_ids: List[int]) -> bool:
        """
        Delete multiple entities by ID.
        
        Args:
            entity_ids: List of entity IDs to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            with database_transaction():
                self.box.remove(entity_ids)
                logger.debug(f"Deleted {len(entity_ids)} {self.entity_class.__name__} entities")
                return True
        except Exception as e:
            logger.error(f"Failed to delete multiple {self.entity_class.__name__} entities: {e}")
            return False


class StudentRepository(BaseRepository[Student]):
    """Repository for Student entities with specific query methods."""
    
    def __init__(self):
        super().__init__(Student)
    
    def find_by_email(self, email: str) -> Optional[Student]:
        """
        Find student by email address.
        
        Args:
            email: Student email
            
        Returns:
            Student instance or None if not found
        """
        try:
            query = self.box.query(Student.email.equals(email)).build()
            return query.find_first()
        except Exception as e:
            logger.error(f"Failed to find student by email {email}: {e}")
            return None
    
    def find_by_name_pattern(self, name_pattern: str) -> List[Student]:
        """
        Find students by name pattern (case-insensitive).
        
        Args:
            name_pattern: Name pattern to search for
            
        Returns:
            List of matching students
        """
        try:
            query = self.box.query(Student.name.contains(name_pattern)).build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find students by name pattern {name_pattern}: {e}")
            return []


class InteractionRepository(BaseRepository[Interaction]):
    """Repository for Interaction entities with specific query methods."""
    
    def __init__(self):
        super().__init__(Interaction)
    
    def find_by_student_id(self, student_id: int) -> List[Interaction]:
        """
        Find all interactions for a specific student.
        
        Args:
            student_id: Student ID
            
        Returns:
            List of interactions for the student
        """
        try:
            query = self.box.query(Interaction.student_id.equals(student_id)).build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find interactions for student {student_id}: {e}")
            return []
    
    def find_by_session_id(self, session_id: str) -> List[Interaction]:
        """
        Find all interactions in a specific session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of interactions in the session
        """
        try:
            query = self.box.query(Interaction.session_id.equals(session_id)).build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find interactions for session {session_id}: {e}")
            return []
    
    def find_multimodal_interactions(self, student_id: Optional[int] = None) -> List[Interaction]:
        """
        Find multimodal interactions (voice/image input).
        
        Args:
            student_id: Optional student ID to filter by
            
        Returns:
            List of multimodal interactions
        """
        try:
            query_builder = self.box.query()
            query_builder.any_of([Interaction.input_type.equals('voice'), Interaction.input_type.equals('image')])
            if student_id is not None:
                query_builder.and_(Interaction.student_id.equals(student_id))
            query = query_builder.build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find multimodal interactions: {e}")
            return []


class LearningProgressRepository(BaseRepository[LearningProgress]):
    """Repository for LearningProgress entities with specific query methods."""
    
    def __init__(self):
        super().__init__(LearningProgress)
    
    def find_by_student_id(self, student_id: int) -> List[LearningProgress]:
        """
        Find all learning progress records for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            List of learning progress records
        """
        try:
            query = self.box.query(LearningProgress.student_id.equals(student_id)).build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find progress for student {student_id}: {e}")
            return []
    
    def find_by_subject(self, subject: str, student_id: Optional[int] = None) -> List[LearningProgress]:
        """
        Find learning progress by subject.
        
        Args:
            subject: Subject name
            student_id: Optional student ID to filter by
            
        Returns:
            List of learning progress records
        """
        try:
            query_builder = self.box.query(LearningProgress.subject.equals(subject))
            if student_id is not None:
                query_builder.and_(LearningProgress.student_id.equals(student_id))
            query = query_builder.build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find progress for subject {subject}: {e}")
            return []
    
    def find_completed_topics(self, student_id: int) -> List[LearningProgress]:
        """
        Find completed topics for a student.
        
        Args:
            student_id: Student ID
            
        Returns:
            List of completed learning progress records
        """
        try:
            student_progress = self.find_by_student_id(student_id)
            return [p for p in student_progress if p.is_completed()]
        except Exception as e:
            logger.error(f"Failed to find completed topics for student {student_id}: {e}")
            return []


class CurriculumContentRepository(BaseRepository[CurriculumContent]):
    """Repository for CurriculumContent entities with specific query methods."""
    
    def __init__(self):
        super().__init__(CurriculumContent)
    
    def find_by_subject(self, subject: str) -> List[CurriculumContent]:
        """
        Find curriculum content by subject.
        
        Args:
            subject: Subject name
            
        Returns:
            List of curriculum content for the subject
        """
        try:
            query = self.box.query(CurriculumContent.subject.equals(subject)).build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find content for subject {subject}: {e}")
            return []
    
    def find_by_difficulty_level(self, min_level: int, max_level: int) -> List[CurriculumContent]:
        """
        Find curriculum content by difficulty level range.
        
        Args:
            min_level: Minimum difficulty level
            max_level: Maximum difficulty level
            
        Returns:
            List of curriculum content in the difficulty range
        """
        try:
            query = self.box.query(
                CurriculumContent.difficulty_level.between(min_level, max_level)
            ).build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find content by difficulty level: {e}")
            return []
    
    def find_advanced_content(self, subject: Optional[str] = None) -> List[CurriculumContent]:
        """
        Find advanced curriculum content (difficulty > 7).
        
        Args:
            subject: Optional subject to filter by
            
        Returns:
            List of advanced curriculum content
        """
        try:
            query_builder = self.box.query(CurriculumContent.difficulty_level.greater(7))
            if subject is not None:
                query_builder.and_(CurriculumContent.subject.equals(subject))
            query = query_builder.build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find advanced content: {e}")
            return []
    
    def find_with_embeddings(self) -> List[CurriculumContent]:
        """
        Find curriculum content that has vector embeddings.
        
        Returns:
            List of curriculum content with embeddings
        """
        try:
            # ObjectBox automatically handles non-null checks for vector properties
            # We can query for entities where the vector_embedding property is not null
            query = self.box.query(CurriculumContent.vector_embedding.not_null()).build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find content with embeddings: {e}")
            return []
    
    def find_similar_content(self, query_vector: List[float], max_results: int = 10) -> List[CurriculumContent]:
        """
        Find curriculum content similar to the query vector using vector search.
        
        Args:
            query_vector: Query vector for similarity search
            max_results: Maximum number of results to return
            
        Returns:
            List of similar curriculum content ordered by similarity
        """
        try:
            # Use ObjectBox vector search capabilities
            # The nearest_neighbor method performs the vector similarity search
            query = self.box.query(CurriculumContent.vector_embedding.nearest_neighbor(query_vector, max_results)).build()
            return query.find()
        except Exception as e:
            logger.error(f"Failed to find similar content: {e}")
            return []





# Repository instances (singletons)
student_repository = StudentRepository()
interaction_repository = InteractionRepository()
learning_progress_repository = LearningProgressRepository()
curriculum_content_repository = CurriculumContentRepository()