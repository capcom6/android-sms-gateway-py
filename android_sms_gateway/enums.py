import enum


class ProcessState(enum.Enum):
    Pending = "Pending"
    Processed = "Processed"
    Sent = "Sent"
    Delivered = "Delivered"
    Failed = "Failed"
