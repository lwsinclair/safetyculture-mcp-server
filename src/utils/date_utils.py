"""
Date Utilities for SafetyCulture MCP Server

This module provides utility functions for working with dates.
"""

import datetime
import re
from dateutil.relativedelta import relativedelta
from typing import Tuple, Union, Optional

def parse_date_range(time_period: str) -> Tuple[datetime.datetime, datetime.datetime]:
    """
    Parse a natural language time period into start and end dates.
    
    Args:
        time_period: A string describing a time period (e.g., '3 months', 'last week', '2023-01-01 to 2023-03-31')
        
    Returns:
        A tuple containing the start and end dates
        
    Raises:
        ValueError: If the time period cannot be parsed
    """
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Check for explicit date range format (YYYY-MM-DD to YYYY-MM-DD)
    date_range_pattern = r'(\d{4}-\d{2}-\d{2})\s+to\s+(\d{4}-\d{2}-\d{2})'
    date_range_match = re.match(date_range_pattern, time_period)
    if date_range_match:
        start_str, end_str = date_range_match.groups()
        try:
            start_date = datetime.datetime.strptime(start_str, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_str, '%Y-%m-%d')
            # Set end date to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)
            return start_date, end_date
        except ValueError:
            raise ValueError(f"Could not parse date range: {time_period}")
    
    # Check for month range format (MMM-MMM YYYY)
    month_range_pattern = r'([A-Za-z]{3})-([A-Za-z]{3})\s+(\d{4})'
    month_range_match = re.match(month_range_pattern, time_period)
    if month_range_match:
        start_month_str, end_month_str, year_str = month_range_match.groups()
        try:
            start_date = datetime.datetime.strptime(f"01 {start_month_str} {year_str}", '%d %b %Y')
            # Get the last day of the end month
            if end_month_str.lower() in ['feb', 'february']:
                # Handle February specially to account for leap years
                year = int(year_str)
                last_day = 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
            else:
                # Map month abbreviations to their number of days
                days_in_month = {
                    'jan': 31, 'january': 31,
                    'feb': 28, 'february': 28,  # This will be adjusted for leap years above
                    'mar': 31, 'march': 31,
                    'apr': 30, 'april': 30,
                    'may': 31,
                    'jun': 30, 'june': 30,
                    'jul': 31, 'july': 31,
                    'aug': 31, 'august': 31,
                    'sep': 30, 'september': 30,
                    'oct': 31, 'october': 31,
                    'nov': 30, 'november': 30,
                    'dec': 31, 'december': 31
                }
                last_day = days_in_month.get(end_month_str.lower(), 30)
            
            end_date = datetime.datetime.strptime(f"{last_day} {end_month_str} {year_str}", '%d %b %Y')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            return start_date, end_date
        except ValueError:
            raise ValueError(f"Could not parse month range: {time_period}")
    
    # Handle relative time periods
    
    # Last X (days, weeks, months, years)
    last_pattern = r'last\s+(\d+)\s+(day|days|week|weeks|month|months|year|years)'
    last_match = re.match(last_pattern, time_period, re.IGNORECASE)
    if last_match or time_period.lower() == 'last day' or time_period.lower() == 'last week' or time_period.lower() == 'last month' or time_period.lower() == 'last year':
        if last_match:
            count_str, unit = last_match.groups()
            count = int(count_str)
        else:
            count = 1
            unit = time_period.lower().split(' ')[1]
        
        if unit.lower() in ['day', 'days']:
            start_date = today - datetime.timedelta(days=count)
        elif unit.lower() in ['week', 'weeks']:
            start_date = today - datetime.timedelta(weeks=count)
        elif unit.lower() in ['month', 'months']:
            start_date = today - relativedelta(months=count)
        elif unit.lower() in ['year', 'years']:
            start_date = today - relativedelta(years=count)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")
        
        return start_date, today
    
    # X (days, weeks, months, years) ago
    ago_pattern = r'(\d+)\s+(day|days|week|weeks|month|months|year|years)\s+ago'
    ago_match = re.match(ago_pattern, time_period, re.IGNORECASE)
    if ago_match:
        count_str, unit = ago_match.groups()
        count = int(count_str)
        
        if unit.lower() in ['day', 'days']:
            point_in_time = today - datetime.timedelta(days=count)
        elif unit.lower() in ['week', 'weeks']:
            point_in_time = today - datetime.timedelta(weeks=count)
        elif unit.lower() in ['month', 'months']:
            point_in_time = today - relativedelta(months=count)
        elif unit.lower() in ['year', 'years']:
            point_in_time = today - relativedelta(years=count)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")
        
        # For "ago" periods, we typically mean a point in time, so start and end are the same
        # But we'll make it a full day for usability
        start_date = point_in_time.replace(hour=0, minute=0, second=0)
        end_date = point_in_time.replace(hour=23, minute=59, second=59)
        return start_date, end_date
    
    # X (days, weeks, months, years)
    simple_pattern = r'(\d+)\s+(day|days|week|weeks|month|months|year|years)'
    simple_match = re.match(simple_pattern, time_period, re.IGNORECASE)
    if simple_match:
        count_str, unit = simple_match.groups()
        count = int(count_str)
        
        end_date = today
        
        if unit.lower() in ['day', 'days']:
            start_date = today - datetime.timedelta(days=count)
        elif unit.lower() in ['week', 'weeks']:
            start_date = today - datetime.timedelta(weeks=count)
        elif unit.lower() in ['month', 'months']:
            start_date = today - relativedelta(months=count)
        elif unit.lower() in ['year', 'years']:
            start_date = today - relativedelta(years=count)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")
        
        return start_date, end_date
    
    # This week, this month, this year
    if time_period.lower() == 'this week':
        # Start of current week (assuming Monday is the first day)
        weekday = today.weekday()
        start_date = today - datetime.timedelta(days=weekday)
        return start_date, today
    
    if time_period.lower() == 'this month':
        # Start of current month
        start_date = today.replace(day=1)
        return start_date, today
    
    if time_period.lower() == 'this year':
        # Start of current year
        start_date = today.replace(month=1, day=1)
        return start_date, today
    
    # Year-to-date (YTD)
    if time_period.lower() == 'ytd' or time_period.lower() == 'year to date':
        start_date = today.replace(month=1, day=1)
        return start_date, today
    
    # Quarter-to-date (QTD)
    if time_period.lower() == 'qtd' or time_period.lower() == 'quarter to date':
        month = today.month
        quarter_start_month = ((month - 1) // 3) * 3 + 1
        start_date = today.replace(month=quarter_start_month, day=1)
        return start_date, today
    
    # If we can't parse the time period, raise an error
    raise ValueError(f"Could not parse time period: {time_period}")

def get_date_parts(date: datetime.datetime) -> Tuple[int, int, int]:
    """
    Get the year, month, and day parts of a date.
    
    Args:
        date: A datetime object
        
    Returns:
        A tuple containing the year, month, and day
    """
    return date.year, date.month, date.day 