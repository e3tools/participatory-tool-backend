import enum

class EngagementStatusEnum(enum.Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    CANCELLED = "Cancelled"

class EngagementActionTaskUpdateTypeEnum(enum.Enum):
    GENERAL = "General"
    PERCENTAGE_PROGRESS = "Percentage Progress"
    TASK_STATUS = "Task Status"
    START_DATE = "Start Date"
    END_DATE = "End Date"
    BULK = "Multiple Fields At Once"


class TechnicalAnalysisTypeEnum(enum.Enum):
    TEXT = "Text"
    NUMERIC = "Numeric"
    DATE = "Date"

class DefaultRolesEnum(enum.Enum):
    GUEST = "Guest"
    DATA_CAPTURE = "Data Capture" 
    FORM_DESIGNER_USER = "Form Design User"
    FORM_DESIGNER_MANAGER = "Form Design Manager"
    TECHNICAL_DATA_USER = "Technical Data User"
    TECHNICAL_DATA_MANAGER = "Technical Data Manager"