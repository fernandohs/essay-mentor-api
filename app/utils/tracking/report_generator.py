"""
Report generator for token usage tracking.
Handles generation of daily usage, monthly usage, and comprehensive reports.
"""
from datetime import date
from typing import Optional, List, Dict, Any
from sqlite3 import Row

from app.models.usage import (
    DailyUsage, MonthlyUsage, UsageReport,
    Provider, Function
)


class ReportGenerator:
    """Generates various reports from token usage data."""
    
    def __init__(self, db_path: str):
        """Initialize report generator."""
        self.db_path = db_path
    
    def get_daily_usage(self, target_date: date, function: Optional[str] = None) -> List[DailyUsage]:
        """Get daily usage aggregated data."""
        query = """
            SELECT provider, function, 
                   SUM(tokens_total) as total_tokens,
                   SUM(cost_usd) as total_cost,
                   COUNT(*) as call_count,
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failure_count,
                   SUM(CASE WHEN fallback_model IS NOT NULL THEN 1 ELSE 0 END) as fallback_count,
                   AVG(response_time_ms) as avg_response_time,
                   AVG(tokens_total) as avg_tokens_per_call
            FROM token_usage
            WHERE DATE(timestamp) = ?
        """
        params = [target_date.isoformat()]
        
        if function:
            query += " AND function = ?"
            params.append(function)
        
        query += " GROUP BY provider, function"
        
        rows = self._execute_query(query, params)
        return self._parse_daily_usage_rows(rows, target_date)
    
    def get_usage_report(
        self,
        start_date: date,
        end_date: date,
        function: Optional[str] = None,
        provider: Optional[str] = None
    ) -> UsageReport:
        """Generate comprehensive usage report."""
        query = """
            SELECT provider, function,
                   SUM(tokens_total) as total_tokens,
                   SUM(cost_usd) as total_cost,
                   COUNT(*) as call_count,
                   SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as success_count,
                   SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failure_count,
                   SUM(CASE WHEN fallback_model IS NOT NULL THEN 1 ELSE 0 END) as fallback_count,
                   AVG(response_time_ms) as avg_response_time
            FROM token_usage
            WHERE DATE(timestamp) BETWEEN ? AND ?
        """
        params = [start_date.isoformat(), end_date.isoformat()]
        
        if function:
            query += " AND function = ?"
            params.append(function)
        
        if provider:
            query += " AND provider = ?"
            params.append(provider)
        
        query += " GROUP BY provider, function"
        
        rows = self._execute_query(query, params)
        return self._build_usage_report(rows, start_date, end_date)
    
    def _execute_query(self, query: str, params: tuple = ()) -> List[Row]:
        """Execute a SELECT query and return results."""
        import sqlite3
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Database query error: {e}")
            return []
    
    def _parse_daily_usage_rows(self, rows: List[Row], target_date: date) -> List[DailyUsage]:
        """Parse database rows into DailyUsage objects."""
        daily_usages = []
        for row in rows:
            daily_usage = DailyUsage(
                date=target_date,
                provider=Provider(row[0]),
                function=Function(row[1]),
                total_tokens=row[2] or 0,
                total_cost_usd=row[3] or 0.0,
                call_count=row[4] or 0,
                success_count=row[5] or 0,
                failure_count=row[6] or 0,
                fallback_count=row[7] or 0,
                avg_response_time_ms=row[8] or 0.0,
                avg_tokens_per_call=row[9] or 0.0
            )
            daily_usages.append(daily_usage)
        
        return daily_usages
    
    def _build_usage_report(self, rows: List[Row], start_date: date, end_date: date) -> UsageReport:
        """Build a comprehensive UsageReport from database rows."""
        # Calculate totals
        total_cost = sum(row[3] or 0.0 for row in rows)
        total_tokens = sum(row[2] or 0 for row in rows)
        total_calls = sum(row[4] or 0 for row in rows)
        total_success = sum(row[5] or 0 for row in rows)
        total_fallback = sum(row[7] or 0 for row in rows)
        
        success_rate = (total_success / total_calls * 100) if total_calls > 0 else 0.0
        fallback_rate = (total_fallback / total_calls * 100) if total_calls > 0 else 0.0
        avg_response_time = sum(row[8] or 0.0 for row in rows) / len(rows) if rows else 0.0
        
        # Group by function and provider
        usage_by_function = self._group_by_function(rows)
        usage_by_provider = self._group_by_provider(rows)
        
        # Calculate rates for grouped data
        self._calculate_rates(usage_by_function)
        self._calculate_rates(usage_by_provider)
        
        return UsageReport(
            period=f"{start_date} to {end_date}",
            start_date=start_date,
            end_date=end_date,
            total_cost_usd=total_cost,
            total_tokens=total_tokens,
            total_calls=total_calls,
            success_rate=success_rate,
            fallback_rate=fallback_rate,
            avg_response_time_ms=avg_response_time,
            usage_by_function=usage_by_function,
            usage_by_provider=usage_by_provider,
            cost_trend={}
        )
    
    def _group_by_function(self, rows: List[Row]) -> Dict[str, Dict[str, Any]]:
        """Group usage data by function."""
        usage_by_function = {}
        
        for row in rows:
            function_name = row[1]
            
            if function_name not in usage_by_function:
                usage_by_function[function_name] = {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "call_count": 0,
                    "success_count": 0,
                    "fallback_count": 0
                }
            
            usage_by_function[function_name]["total_tokens"] += row[2] or 0
            usage_by_function[function_name]["total_cost"] += row[3] or 0.0
            usage_by_function[function_name]["call_count"] += row[4] or 0
            usage_by_function[function_name]["success_count"] += row[5] or 0
            usage_by_function[function_name]["fallback_count"] += row[7] or 0
        
        return usage_by_function
    
    def _group_by_provider(self, rows: List[Row]) -> Dict[str, Dict[str, Any]]:
        """Group usage data by provider."""
        usage_by_provider = {}
        
        for row in rows:
            provider_name = row[0]
            
            if provider_name not in usage_by_provider:
                usage_by_provider[provider_name] = {
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "call_count": 0,
                    "success_count": 0,
                    "fallback_count": 0
                }
            
            usage_by_provider[provider_name]["total_tokens"] += row[2] or 0
            usage_by_provider[provider_name]["total_cost"] += row[3] or 0.0
            usage_by_provider[provider_name]["call_count"] += row[4] or 0
            usage_by_provider[provider_name]["success_count"] += row[5] or 0
            usage_by_provider[provider_name]["fallback_count"] += row[7] or 0
        
        return usage_by_provider
    
    def _calculate_rates(self, grouped_data: Dict[str, Dict[str, Any]]):
        """Calculate success and fallback rates for grouped data."""
        for data in grouped_data.values():
            if data["call_count"] > 0:
                data["success_rate"] = (data["success_count"] / data["call_count"]) * 100
                data["fallback_rate"] = (data["fallback_count"] / data["call_count"]) * 100
