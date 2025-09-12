from dataclasses import dataclass

@dataclass
class ExcelPivot:
    date_range: str
    average_review_rating: float
    average_review_count_per_day: float
    review_count_in_past_month: int
    options_count: dict