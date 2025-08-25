"""
NovaTrace API - FastAPI endpoints for web interface
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
from .database.model import Session as DBSession, Project, Trace, TraceTypes, sessionmaker
from .database.model import engine as default_engine
from .system_info import get_system_metrics, get_simple_metrics

# Create FastAPI app
app = FastAPI(title="NovaTrace API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    """Get database session"""
    SessionLocal = sessionmaker(bind=default_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "NovaTrace API is running", "status": "healthy"}

@app.get("/api/sessions")
async def get_sessions(db: Session = Depends(get_db)):
    """Get all sessions"""
    try:
        sessions = db.query(DBSession).order_by(desc(DBSession.created_at)).all()
        return {
            "sessions": [
                {
                    "id": session.id,
                    "name": session.name,
                    "created_at": session.created_at.isoformat(),
                    "project_count": len(session.projects) if hasattr(session, 'projects') else 0
                }
                for session in sessions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")

@app.get("/api/projects")
async def get_projects(session_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all projects, optionally filtered by session"""
    try:
        query = db.query(Project)
        if session_id:
            query = query.filter(Project.session_id == session_id)
        
        projects = query.order_by(desc(Project.created_at)).all()
        
        result = []
        for project in projects:
            # Calculate metrics for each project
            traces = db.query(Trace).filter(Trace.project_id == project.id).all()
            
            total_cost = sum(trace.call_cost or 0 for trace in traces)
            total_tokens = sum((trace.input_tokens or 0) + (trace.output_tokens or 0) for trace in traces)
            avg_duration = sum(trace.duration_ms or 0 for trace in traces) / len(traces) if traces else 0
            
            # Get recent activity (last 24 hours)
            recent_activity = db.query(Trace).filter(
                Trace.project_id == project.id,
                Trace.created_at >= datetime.now() - timedelta(hours=24)
            ).count()
            
            # Determine status based on recent activity
            status = "active" if recent_activity > 0 else "inactive"
            if recent_activity > 10:
                status = "running"
            elif recent_activity > 0:
                status = "idle"
            else:
                status = "stopped"
            
            result.append({
                "id": project.id,
                "name": project.name,
                "description": f"Project with {len(traces)} traces",
                "status": status,
                "type": "llm_project",
                "created": project.created_at.isoformat(),
                "lastModified": max(trace.created_at for trace in traces).isoformat() if traces else project.created_at.isoformat(),
                "metrics": {
                    "total_traces": len(traces),
                    "total_cost": round(total_cost, 4),
                    "total_tokens": total_tokens,
                    "avg_duration_ms": round(avg_duration, 2),
                    "recent_activity": recent_activity
                },
                "cpu": min(recent_activity * 2, 100),  # Simulate CPU based on activity
                "memory": min(len(traces) * 10, 1000),  # Simulate memory based on traces
            })
        
        return {"projects": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {str(e)}")

@app.get("/api/projects/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get specific project details"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        traces = db.query(Trace).filter(Trace.project_id == project_id).all()
        
        # Get all session names in a single query
        session_ids = [trace.session_id for trace in traces if trace.session_id]
        sessions_dict = {}
        if session_ids:
            sessions = db.query(DBSession).filter(DBSession.id.in_(session_ids)).all()
            sessions_dict = {session.id: session.name for session in sessions}
        
        # Calculate detailed metrics
        total_cost = sum(trace.call_cost or 0 for trace in traces)
        total_tokens = sum((trace.input_tokens or 0) + (trace.output_tokens or 0) for trace in traces)
        
        # Group by trace type
        trace_types = {}
        for trace in traces:
            trace_type = db.query(TraceTypes).filter(TraceTypes.id == trace.type_id).first()
            type_name = trace_type.name if trace_type else "Unknown"
            
            if type_name not in trace_types:
                trace_types[type_name] = {"count": 0, "cost": 0, "tokens": 0}
            
            trace_types[type_name]["count"] += 1
            trace_types[type_name]["cost"] += trace.call_cost or 0
            trace_types[type_name]["tokens"] += (trace.input_tokens or 0) + (trace.output_tokens or 0)
        
        return {
            "id": project.id,
            "name": project.name,
            "created": project.created_at.isoformat(),
            "metrics": {
                "total_traces": len(traces),
                "total_cost": round(total_cost, 4),
                "total_tokens": total_tokens,
                "trace_types": trace_types
            },
            "traces": [
                {
                    "id": trace.id,
                    "trace_id": f"trace_{trace.id}",
                    "type": trace.type_id,
                    "created_at": trace.created_at.isoformat(),
                    "timestamp": trace.created_at.isoformat(),
                    "duration_ms": trace.duration_ms,
                    "cost": trace.call_cost,
                    "tokens": (trace.input_tokens or 0) + (trace.output_tokens or 0),
                    "input_tokens": trace.input_tokens,
                    "output_tokens": trace.output_tokens,
                    "user_id": trace.user_external_id,
                    "user_name": trace.user_external_name,
                    "session_id": trace.session_id,
                    "session_name": sessions_dict.get(trace.session_id, None) if trace.session_id else None,
                    "model_provider": trace.model_provider,
                    "model_name": trace.model_name,
                    "input_data": trace.input_data,
                    "output_data": trace.output_data,
                    "status": "completed"  # Default status for existing traces
                }
                for trace in traces[-50:]  # Last 50 traces
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching project: {str(e)}")

@app.get("/api/projects/{project_id}/metrics")
async def get_project_metrics(project_id: int, db: Session = Depends(get_db)):
    """Get project metrics and historical data"""
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        traces = db.query(Trace).filter(Trace.project_id == project_id).all()
        
        # Calculate metrics by hour for the last 24 hours
        hourly_data = {}
        for trace in traces:
            hour = trace.created_at.replace(minute=0, second=0, microsecond=0)
            hour_str = hour.isoformat()
            
            if hour_str not in hourly_data:
                hourly_data[hour_str] = {
                    "traces": 0,
                    "cost": 0,
                    "tokens": 0,
                    "avg_duration": 0,
                    "durations": []
                }
            
            hourly_data[hour_str]["traces"] += 1
            hourly_data[hour_str]["cost"] += trace.call_cost or 0
            hourly_data[hour_str]["tokens"] += (trace.input_tokens or 0) + (trace.output_tokens or 0)
            hourly_data[hour_str]["durations"].append(trace.duration_ms or 0)
        
        # Calculate averages
        for hour_data in hourly_data.values():
            if hour_data["durations"]:
                hour_data["avg_duration"] = sum(hour_data["durations"]) / len(hour_data["durations"])
            del hour_data["durations"]  # Remove raw data
        
        return {
            "project_id": project_id,
            "hourly_data": hourly_data,
            "summary": {
                "total_traces": len(traces),
                "total_cost": sum(trace.call_cost or 0 for trace in traces),
                "total_tokens": sum((trace.input_tokens or 0) + (trace.output_tokens or 0) for trace in traces),
                "avg_duration": sum(trace.duration_ms or 0 for trace in traces) / len(traces) if traces else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching project metrics: {str(e)}")

@app.get("/api/system/metrics")
async def get_system_metrics_endpoint():
    """Get current system metrics"""
    try:
        metrics = get_system_metrics()
        return {
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Fallback to simulated data if system monitoring fails
        import random
        return {
            "metrics": {
                "cpu": {"usage": random.randint(20, 80)},
                "memory": {"percent": random.randint(40, 90)},
                "disk": {"percent": random.randint(30, 85)},
                "network": {"bytes_sent": random.randint(1000, 10000)}
            },
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/api/system/simple-metrics")
async def get_simple_system_metrics():
    """Get simplified system metrics for dashboard"""
    try:
        metrics = get_simple_metrics()
        return {
            "cpu_usage": metrics["cpu_usage"],
            "memory_usage": metrics["memory_usage"], 
            "disk_usage": metrics["disk_usage"],
            "uptime": metrics["uptime"],
            "process_memory": metrics["process_memory"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Return fallback values instead of error
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "uptime": 0,
            "process_memory": 0.0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/api/system/status")
async def get_system_status(db: Session = Depends(get_db)):
    """Get system status information"""
    try:
        # Count totals
        total_sessions = db.query(DBSession).count()
        total_projects = db.query(Project).count()
        total_traces = db.query(Trace).count()
        
        # Recent activity (last 24 hours)
        recent_traces = db.query(Trace).filter(
            Trace.created_at >= datetime.now() - timedelta(hours=24)
        ).count()
        
        return {
            "uptime": "15 days, 8 hours",  # TODO: Calculate real uptime
            "active_processes": 247,  # TODO: Get real process count
            "load_average": "1.24, 1.18, 1.09",  # TODO: Get real load
            "free_memory": "2.4 GB",  # TODO: Get real memory
            "free_disk": "145.2 GB",  # TODO: Get real disk space
            "statistics": {
                "total_sessions": total_sessions,
                "total_projects": total_projects,
                "total_traces": total_traces,
                "recent_activity": recent_traces
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4445)
