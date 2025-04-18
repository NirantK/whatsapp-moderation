import enum

from pydantic import BaseModel


class Labels(str, enum.Enum):
    """Enumeration for single-label text classification."""

    MALE = "male"
    FEMALE = "female"
    UNDECIDED = "undecided"


class SinglePrediction(BaseModel):
    """Class for a single class label prediction."""

    class_label: Labels
    class_probability: float 