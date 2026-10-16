import enum


class SkillType(str, enum.Enum):
    OFFERS = "OFFERS"
    WANTS = "WANTS"


class Proficiency(str, enum.Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    EXPERT = "Expert"


class MatchStatus(str, enum.Enum):
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class SessionStatus(str, enum.Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELED = "Canceled"


class InterviewType(str, enum.Enum):
    MCQ = "MCQ"
    CODING = "Coding"
    PRACTICAL = "Practical"
