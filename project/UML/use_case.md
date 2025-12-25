# Use Case Diagram

```mermaid
---
title: StudentExamManager Use Cases
---
usecaseDiagram
actor Admin as "Admin"
actor Student as "Student"

rectangle StudentExamManager {
  (Manage students) as UC1
  (Manage courses) as UC2
  (Manage exams) as UC3
  (Enroll students) as UC4
  (Record grades) as UC5
  (View transcript) as UC6
  (Delete student) as UC7
  (Delete course) as UC8
  (Delete exam) as UC9
  (Delete enrollment) as UC10
  (Reset grade) as UC11

  Admin --> UC1
  Admin --> UC2
  Admin --> UC3
  Admin --> UC4
  Admin --> UC5
  Admin --> UC7
  Admin --> UC8
  Admin --> UC9
  Admin --> UC10
  Admin --> UC11
  Student --> UC6
}
```
