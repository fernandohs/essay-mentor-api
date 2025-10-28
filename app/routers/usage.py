"""
Usage reporting API endpoints.
"""
from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.utils.token_tracker import get_token_tracker
from app.models.usage import UsageReport, DailyUsage

router = APIRouter(prefix="/admin/usage", tags=["usage"])


@router.get("/daily", response_model=List[DailyUsage])
def get_daily_usage(
    target_date: Optional[date] = Query(None, description="Target date (defaults to today)"),
    function: Optional[str] = Query(None, description="Filter by function")
):
    """
    Get daily usage aggregated data.
    
    Args:
        target_date: Date to get usage for (defaults to today)
        function: Optional function filter (ai_detection, feedback, guidance, section_check)
    """
    if target_date is None:
        target_date = date.today()
    
    tracker = get_token_tracker()
    try:
        daily_usages = tracker.get_daily_usage(target_date, function)
        return daily_usages
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving daily usage: {str(e)}")


@router.get("/report", response_model=UsageReport)
def get_usage_report(
    start_date: date = Query(..., description="Start date for report"),
    end_date: date = Query(..., description="End date for report"),
    function: Optional[str] = Query(None, description="Filter by function"),
    provider: Optional[str] = Query(None, description="Filter by provider")
):
    """
    Get comprehensive usage report for a date range.
    
    Args:
        start_date: Start date for report
        end_date: End date for report
        function: Optional function filter
        provider: Optional provider filter
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="Date range cannot exceed 365 days")
    
    tracker = get_token_tracker()
    try:
        report = tracker.get_usage_report(start_date, end_date, function, provider)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating usage report: {str(e)}")


@router.get("/costs")
def get_cost_summary(
    days: int = Query(7, ge=1, le=365, description="Number of days to analyze"),
    function: Optional[str] = Query(None, description="Filter by function")
):
    """
    Get cost summary for the last N days.
    
    Args:
        days: Number of days to analyze (1-365)
        function: Optional function filter
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days-1)
    
    tracker = get_token_tracker()
    try:
        report = tracker.get_usage_report(start_date, end_date, function)
        
        return {
            "period": f"{start_date} to {end_date}",
            "days_analyzed": days,
            "total_cost_usd": report.total_cost_usd,
            "total_tokens": report.total_tokens,
            "total_calls": report.total_calls,
            "avg_cost_per_day": report.total_cost_usd / days,
            "avg_tokens_per_day": report.total_tokens / days,
            "avg_calls_per_day": report.total_calls / days,
            "success_rate": report.success_rate,
            "fallback_rate": report.fallback_rate,
            "cost_by_function": report.usage_by_function,
            "cost_by_provider": report.usage_by_provider
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cost summary: {str(e)}")


@router.get("/trends")
def get_usage_trends(
    days: int = Query(30, ge=7, le=90, description="Number of days to analyze"),
    function: Optional[str] = Query(None, description="Filter by function")
):
    """
    Get usage trends for the last N days.
    
    Args:
        days: Number of days to analyze (7-90)
        function: Optional function filter
    """
    tracker = get_token_tracker()
    trends = []
    
    try:
        for i in range(days):
            target_date = date.today() - timedelta(days=i)
            daily_usages = tracker.get_daily_usage(target_date, function)
            
            day_total_cost = sum(usage.total_cost_usd for usage in daily_usages)
            day_total_tokens = sum(usage.total_tokens for usage in daily_usages)
            day_total_calls = sum(usage.call_count for usage in daily_usages)
            
            trends.append({
                "date": target_date.isoformat(),
                "cost_usd": day_total_cost,
                "tokens": day_total_tokens,
                "calls": day_total_calls,
                "functions": {
                    usage.function.value: {
                        "cost_usd": usage.total_cost_usd,
                        "tokens": usage.total_tokens,
                        "calls": usage.call_count
                    }
                    for usage in daily_usages
                }
            })
        
        # Reverse to get chronological order (oldest first)
        trends.reverse()
        
        return {
            "period_days": days,
            "trends": trends,
            "summary": {
                "total_cost": sum(trend["cost_usd"] for trend in trends),
                "total_tokens": sum(trend["tokens"] for trend in trends),
                "total_calls": sum(trend["calls"] for trend in trends),
                "avg_daily_cost": sum(trend["cost_usd"] for trend in trends) / days,
                "avg_daily_tokens": sum(trend["tokens"] for trend in trends) / days,
                "avg_daily_calls": sum(trend["calls"] for trend in trends) / days
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating usage trends: {str(e)}")


@router.get("/export/csv")
def export_usage_csv(
    start_date: date = Query(..., description="Start date for export"),
    end_date: date = Query(..., description="End date for export"),
    function: Optional[str] = Query(None, description="Filter by function")
):
    """
    Export usage data as CSV.
    
    Args:
        start_date: Start date for export
        end_date: End date for export
        function: Optional function filter
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if (end_date - start_date).days > 90:
        raise HTTPException(status_code=400, detail="Export range cannot exceed 90 days")
    
    tracker = get_token_tracker()
    
    try:
        # Get daily usage for each day in range
        csv_data = []
        csv_data.append("date,provider,function,total_tokens,total_cost_usd,call_count,success_count,failure_count,fallback_count,avg_response_time_ms")
        
        current_date = start_date
        while current_date <= end_date:
            daily_usages = tracker.get_daily_usage(current_date, function)
            
            if not daily_usages:
                # Add empty row for days with no usage
                csv_data.append(f"{current_date.isoformat()},,,,,,,,,")
            else:
                for usage in daily_usages:
                    csv_data.append(
                        f"{usage.date.isoformat()},"
                        f"{usage.provider.value},"
                        f"{usage.function.value},"
                        f"{usage.total_tokens},"
                        f"{usage.total_cost_usd:.4f},"
                        f"{usage.call_count},"
                        f"{usage.success_count},"
                        f"{usage.failure_count},"
                        f"{usage.fallback_count},"
                        f"{usage.avg_response_time_ms:.2f}"
                    )
            
            current_date += timedelta(days=1)
        
        csv_content = "\n".join(csv_data)
        
        return JSONResponse(
            content={"csv_data": csv_content},
            headers={
                "Content-Disposition": f"attachment; filename=usage_report_{start_date}_{end_date}.csv"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting usage data: {str(e)}")


@router.get("/health")
def usage_tracking_health():
    """Check health of usage tracking system."""
    try:
        tracker = get_token_tracker()
        
        # Try to get today's usage to test database connection
        today = date.today()
        daily_usages = tracker.get_daily_usage(today)
        
        return {
            "status": "healthy",
            "database_path": tracker.db_path,
            "today_records": len(daily_usages),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Usage tracking system error: {str(e)}")
