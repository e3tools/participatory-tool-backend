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

