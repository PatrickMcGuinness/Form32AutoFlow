"""Date manipulation utilities for form32_docling."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def format_date(exam_date: str | None) -> str:
    """Format exam date as M.D.YY with dots between numbers.

    Args:
        exam_date: Date string in various formats (e.g., MM/DD/YYYY, YYYY-MM-DD).

    Returns:
        Formatted date string like "1.23.24" or "NO_DATE" on error.
    """
    if not exam_date:
        logger.error("Exam date is None or empty")
        return "NO_DATE"

    try:
        date_str = exam_date.strip()
        # Try multiple date formats
        for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                date_obj = datetime.strptime(date_str, fmt)
                formatted = (
                    f"{date_obj.month}.{date_obj.day}.{str(date_obj.year)[-2:]}"
                )
                logger.debug(f"Formatted exam_date: {formatted}")
                return formatted
            except ValueError:
                continue

        logger.error(f"Unable to parse date: {exam_date}")
        return "NO_DATE"

    except (ValueError, AttributeError) as e:
        logger.error(f"Error formatting date: {exam_date}. Error: {e}")
        return "NO_DATE"
