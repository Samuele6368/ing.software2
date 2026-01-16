from .student import Student
from .course import Course
from .exam import Exam
from .registration import Registration

#definisco i nomi da esportare quando si importa il modulo
__all__ = ["Student", "Course", "Exam", "Registration"]
