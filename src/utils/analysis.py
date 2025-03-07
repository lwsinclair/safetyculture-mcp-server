"""
Analysis Utilities for SafetyCulture MCP Server

This module provides utility functions for analyzing SafetyCulture data.
"""

import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Any, Union, Tuple

def analyze_trends(
    data: List[Dict[str, Any]], 
    date_field: str = 'modified_at',
    value_field: Optional[str] = None,
    group_by: Optional[str] = None,
    start_date: Optional[datetime.datetime] = None,
    end_date: Optional[datetime.datetime] = None
) -> Dict[str, Any]:
    """
    Analyze trends in a dataset over time.
    
    Args:
        data: A list of dictionaries containing the data to analyze
        date_field: The field containing the date information
        value_field: Optional field to aggregate values from
        group_by: Optional field to group the data by
        start_date: Optional start date for filtering the data
        end_date: Optional end date for filtering the data
        
    Returns:
        A dictionary containing the analysis results
    """
    if not data:
        return {"error": "No data to analyze"}
    
    # Convert to pandas DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Ensure date_field exists in the data
    if date_field not in df.columns:
        return {"error": f"Date field '{date_field}' not found in the data"}
    
    # Convert date field to datetime
    df[date_field] = pd.to_datetime(df[date_field])
    
    # Filter by date range if provided
    if start_date:
        df = df[df[date_field] >= start_date]
    if end_date:
        df = df[df[date_field] <= end_date]
    
    # Extract date components
    df['date'] = df[date_field].dt.date
    df['year'] = df[date_field].dt.year
    df['month'] = df[date_field].dt.month
    df['day'] = df[date_field].dt.day
    df['weekday'] = df[date_field].dt.weekday
    
    # Prepare results dictionary
    results = {
        "total_count": len(df),
        "date_range": {
            "start": df[date_field].min().isoformat() if not df.empty else None,
            "end": df[date_field].max().isoformat() if not df.empty else None
        }
    }
    
    # Group by date
    date_counts = df.groupby('date').size().reset_index(name='count')
    results["by_date"] = date_counts.to_dict('records')
    
    # Group by month
    month_counts = df.groupby(['year', 'month']).size().reset_index(name='count')
    month_counts['month_year'] = month_counts.apply(lambda x: f"{x['year']}-{x['month']:02d}", axis=1)
    results["by_month"] = month_counts[['month_year', 'count']].to_dict('records')
    
    # Group by weekday
    weekday_counts = df.groupby('weekday').size().reset_index(name='count')
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_counts['weekday_name'] = weekday_counts['weekday'].apply(lambda x: weekday_names[x])
    results["by_weekday"] = weekday_counts[['weekday_name', 'count']].to_dict('records')
    
    # Group by additional field if provided
    if group_by and group_by in df.columns:
        group_counts = df.groupby(group_by).size().reset_index(name='count')
        results[f"by_{group_by}"] = group_counts.to_dict('records')
    
    # Calculate aggregates if value field provided
    if value_field and value_field in df.columns:
        # Ensure the value field is numeric
        if pd.api.types.is_numeric_dtype(df[value_field]):
            results["value_stats"] = {
                "mean": float(df[value_field].mean()),
                "median": float(df[value_field].median()),
                "min": float(df[value_field].min()),
                "max": float(df[value_field].max()),
                "std_dev": float(df[value_field].std())
            }
            
            # Calculate trend over time
            value_trend = df.groupby('date')[value_field].mean().reset_index()
            results["value_trend"] = value_trend.to_dict('records')
            
            # Calculate trend by group if provided
            if group_by and group_by in df.columns:
                group_value_trend = df.groupby([group_by, 'date'])[value_field].mean().reset_index()
                results["value_trend_by_group"] = group_value_trend.to_dict('records')
    
    return results

def compare_data_periods(
    first_period_data: List[Dict[str, Any]],
    second_period_data: List[Dict[str, Any]],
    date_field: str = 'modified_at',
    value_field: Optional[str] = None,
    group_by: Optional[str] = None,
    category_filter: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Compare data between two time periods.
    
    Args:
        first_period_data: Data from the first period
        second_period_data: Data from the second period
        date_field: The field containing the date information
        value_field: Optional field to aggregate values from
        group_by: Optional field to group the data by
        category_filter: Optional filter to apply to the data
        
    Returns:
        A dictionary containing the comparison results
    """
    if not first_period_data and not second_period_data:
        return {"error": "No data to compare"}
    
    # Convert to pandas DataFrames
    df1 = pd.DataFrame(first_period_data)
    df2 = pd.DataFrame(second_period_data)
    
    # Apply category filter if provided
    if category_filter:
        for field, value in category_filter.items():
            if field in df1.columns:
                df1 = df1[df1[field] == value]
            if field in df2.columns:
                df2 = df2[df2[field] == value]
    
    # Prepare results dictionary
    results = {
        "first_period": {
            "total_count": len(df1),
            "date_range": {
                "start": df1[date_field].min().isoformat() if date_field in df1.columns and not df1.empty else None,
                "end": df1[date_field].max().isoformat() if date_field in df1.columns and not df1.empty else None
            }
        },
        "second_period": {
            "total_count": len(df2),
            "date_range": {
                "start": df2[date_field].min().isoformat() if date_field in df2.columns and not df2.empty else None,
                "end": df2[date_field].max().isoformat() if date_field in df2.columns and not df2.empty else None
            }
        }
    }
    
    # Calculate percentage change in total count
    if results["first_period"]["total_count"] > 0:
        percent_change = ((results["second_period"]["total_count"] - results["first_period"]["total_count"]) / 
                         results["first_period"]["total_count"]) * 100
        results["total_count_percent_change"] = percent_change
    else:
        results["total_count_percent_change"] = None
    
    # Compare by group if provided
    if group_by and group_by in df1.columns and group_by in df2.columns:
        group1_counts = df1.groupby(group_by).size().reset_index(name='count')
        group2_counts = df2.groupby(group_by).size().reset_index(name='count')
        
        # Merge the group counts
        group_comparison = pd.merge(group1_counts, group2_counts, on=group_by, how='outer', suffixes=('_first', '_second'))
        group_comparison = group_comparison.fillna(0)
        
        # Calculate percentage change for each group
        group_comparison['percent_change'] = ((group_comparison['count_second'] - group_comparison['count_first']) / 
                                            group_comparison['count_first']) * 100
        group_comparison['percent_change'] = group_comparison['percent_change'].replace([np.inf, -np.inf], np.nan)
        
        results["by_group"] = group_comparison.to_dict('records')
    
    # Compare value field if provided
    if value_field and value_field in df1.columns and value_field in df2.columns:
        # Ensure the value field is numeric
        if (pd.api.types.is_numeric_dtype(df1[value_field]) and 
            pd.api.types.is_numeric_dtype(df2[value_field])):
            
            results["first_period"]["value_stats"] = {
                "mean": float(df1[value_field].mean()) if not df1.empty else None,
                "median": float(df1[value_field].median()) if not df1.empty else None,
                "min": float(df1[value_field].min()) if not df1.empty else None,
                "max": float(df1[value_field].max()) if not df1.empty else None
            }
            
            results["second_period"]["value_stats"] = {
                "mean": float(df2[value_field].mean()) if not df2.empty else None,
                "median": float(df2[value_field].median()) if not df2.empty else None,
                "min": float(df2[value_field].min()) if not df2.empty else None,
                "max": float(df2[value_field].max()) if not df2.empty else None
            }
            
            # Calculate percentage change in mean value
            if results["first_period"]["value_stats"]["mean"] is not None and results["first_period"]["value_stats"]["mean"] != 0:
                mean_percent_change = ((results["second_period"]["value_stats"]["mean"] - 
                                      results["first_period"]["value_stats"]["mean"]) / 
                                     results["first_period"]["value_stats"]["mean"]) * 100
                results["mean_value_percent_change"] = mean_percent_change
            else:
                results["mean_value_percent_change"] = None
    
    return results 