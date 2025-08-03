import os
import json
from typing import List, Dict, Optional, Any
from mcp_kit import ProxyMCP, Tool
from pydantic import BaseModel
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

# --- Models ---
class ResearchProject(BaseModel):
    id: str
    title: str
    description: str
    status: str  # "active", "completed", "on_hold"
    created_date: str
    last_updated: str
    progress: float  # 0.0 to 1.0
    tags: List[str]

class ResearchTask(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    status: str  # "pending", "in_progress", "completed", "blocked"
    priority: str  # "low", "medium", "high", "urgent"
    assigned_to: Optional[str]
    due_date: Optional[str]
    estimated_hours: float
    actual_hours: Optional[float]

class ResearchNote(BaseModel):
    id: str
    project_id: str
    title: str
    content: str
    created_date: str
    last_updated: str
    tags: List[str]
    related_persons: List[str]

# --- In-memory storage for demo ---
PROJECTS = {}
TASKS = {}
NOTES = {}

# --- Tool Implementations ---
async def create_research_project(title: str, description: str, tags: List[str] = None) -> ResearchProject:
    """Create a new research project."""
    logger.info("Creating research project", title=title)
    
    project_id = f"proj_{len(PROJECTS) + 1}"
    now = datetime.now().isoformat()
    
    project = ResearchProject(
        id=project_id,
        title=title,
        description=description,
        status="active",
        created_date=now,
        last_updated=now,
        progress=0.0,
        tags=tags or []
    )
    
    PROJECTS[project_id] = project
    logger.info("Created research project", project_id=project_id)
    
    return project

async def get_research_projects(status: Optional[str] = None) -> List[ResearchProject]:
    """Get all research projects, optionally filtered by status."""
    logger.info("Getting research projects", status=status)
    
    projects = list(PROJECTS.values())
    
    if status:
        projects = [p for p in projects if p.status == status]
    
    return projects

async def update_project_status(project_id: str, status: str, progress: Optional[float] = None) -> ResearchProject:
    """Update the status and progress of a research project."""
    logger.info("Updating project status", project_id=project_id, status=status, progress=progress)
    
    if project_id not in PROJECTS:
        raise ValueError(f"Project {project_id} not found")
    
    project = PROJECTS[project_id]
    project.status = status
    project.last_updated = datetime.now().isoformat()
    
    if progress is not None:
        project.progress = max(0.0, min(1.0, progress))
    
    PROJECTS[project_id] = project
    return project

async def create_research_task(project_id: str, title: str, description: str, priority: str = "medium", 
                              estimated_hours: float = 1.0, due_date: Optional[str] = None) -> ResearchTask:
    """Create a new research task within a project."""
    logger.info("Creating research task", project_id=project_id, title=title)
    
    if project_id not in PROJECTS:
        raise ValueError(f"Project {project_id} not found")
    
    task_id = f"task_{len(TASKS) + 1}"
    now = datetime.now().isoformat()
    
    task = ResearchTask(
        id=task_id,
        project_id=project_id,
        title=title,
        description=description,
        status="pending",
        priority=priority,
        assigned_to=None,
        due_date=due_date,
        estimated_hours=estimated_hours,
        actual_hours=None
    )
    
    TASKS[task_id] = task
    logger.info("Created research task", task_id=task_id)
    
    return task

async def get_project_tasks(project_id: str, status: Optional[str] = None) -> List[ResearchTask]:
    """Get all tasks for a project, optionally filtered by status."""
    logger.info("Getting project tasks", project_id=project_id, status=status)
    
    if project_id not in PROJECTS:
        raise ValueError(f"Project {project_id} not found")
    
    tasks = [t for t in TASKS.values() if t.project_id == project_id]
    
    if status:
        tasks = [t for t in tasks if t.status == status]
    
    return tasks

async def update_task_status(task_id: str, status: str, actual_hours: Optional[float] = None) -> ResearchTask:
    """Update the status and actual hours of a research task."""
    logger.info("Updating task status", task_id=task_id, status=status, actual_hours=actual_hours)
    
    if task_id not in TASKS:
        raise ValueError(f"Task {task_id} not found")
    
    task = TASKS[task_id]
    task.status = status
    
    if actual_hours is not None:
        task.actual_hours = actual_hours
    
    TASKS[task_id] = task
    return task

async def create_research_note(project_id: str, title: str, content: str, tags: List[str] = None,
                              related_persons: List[str] = None) -> ResearchNote:
    """Create a new research note within a project."""
    logger.info("Creating research note", project_id=project_id, title=title)
    
    if project_id not in PROJECTS:
        raise ValueError(f"Project {project_id} not found")
    
    note_id = f"note_{len(NOTES) + 1}"
    now = datetime.now().isoformat()
    
    note = ResearchNote(
        id=note_id,
        project_id=project_id,
        title=title,
        content=content,
        created_date=now,
        last_updated=now,
        tags=tags or [],
        related_persons=related_persons or []
    )
    
    NOTES[note_id] = note
    logger.info("Created research note", note_id=note_id)
    
    return note

async def get_project_notes(project_id: str, tags: List[str] = None) -> List[ResearchNote]:
    """Get all notes for a project, optionally filtered by tags."""
    logger.info("Getting project notes", project_id=project_id, tags=tags)
    
    if project_id not in PROJECTS:
        raise ValueError(f"Project {project_id} not found")
    
    notes = [n for n in NOTES.values() if n.project_id == project_id]
    
    if tags:
        notes = [n for n in notes if any(tag in n.tags for tag in tags)]
    
    return notes

async def search_notes(query: str, project_id: Optional[str] = None) -> List[ResearchNote]:
    """Search notes by content or title."""
    logger.info("Searching notes", query=query, project_id=project_id)
    
    notes = list(NOTES.values())
    
    if project_id:
        notes = [n for n in notes if n.project_id == project_id]
    
    # Simple text search
    matching_notes = []
    query_lower = query.lower()
    
    for note in notes:
        if (query_lower in note.title.lower() or 
            query_lower in note.content.lower() or
            any(query_lower in tag.lower() for tag in note.tags)):
            matching_notes.append(note)
    
    return matching_notes

async def generate_research_report(project_id: str) -> Dict[str, Any]:
    """Generate a comprehensive report for a research project."""
    logger.info("Generating research report", project_id=project_id)
    
    if project_id not in PROJECTS:
        raise ValueError(f"Project {project_id} not found")
    
    project = PROJECTS[project_id]
    tasks = [t for t in TASKS.values() if t.project_id == project_id]
    notes = [n for n in NOTES.values() if n.project_id == project_id]
    
    # Calculate statistics
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == "completed"])
    pending_tasks = len([t for t in tasks if t.status == "pending"])
    in_progress_tasks = len([t for t in tasks if t.status == "in_progress"])
    
    total_estimated_hours = sum(t.estimated_hours for t in tasks)
    total_actual_hours = sum(t.actual_hours or 0 for t in tasks)
    
    # Calculate progress based on completed tasks
    progress = completed_tasks / total_tasks if total_tasks > 0 else 0.0
    
    report = {
        "project_id": project_id,
        "project_title": project.title,
        "project_description": project.description,
        "status": project.status,
        "progress": progress,
        "statistics": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "total_notes": len(notes),
            "total_estimated_hours": total_estimated_hours,
            "total_actual_hours": total_actual_hours
        },
        "recent_activity": {
            "recent_tasks": [t for t in tasks if t.status in ["in_progress", "completed"]][:5],
            "recent_notes": sorted(notes, key=lambda n: n.last_updated, reverse=True)[:5]
        },
        "recommendations": []
    }
    
    # Add recommendations based on project state
    if pending_tasks > completed_tasks:
        report["recommendations"].append("Focus on completing pending tasks to make progress")
    
    if total_actual_hours > total_estimated_hours * 1.5:
        report["recommendations"].append("Tasks are taking longer than estimated - consider adjusting timelines")
    
    if len(notes) < len(tasks):
        report["recommendations"].append("Consider adding more research notes to document findings")
    
    return report

async def get_research_timeline(project_id: str) -> List[Dict[str, Any]]:
    """Get a timeline of research activities for a project."""
    logger.info("Getting research timeline", project_id=project_id)
    
    if project_id not in PROJECTS:
        raise ValueError(f"Project {project_id} not found")
    
    project = PROJECTS[project_id]
    tasks = [t for t in TASKS.values() if t.project_id == project_id]
    notes = [n for n in NOTES.values() if n.project_id == project_id]
    
    timeline = []
    
    # Add project creation
    timeline.append({
        "date": project.created_date,
        "type": "project_created",
        "title": f"Project '{project.title}' created",
        "description": project.description
    })
    
    # Add task updates
    for task in tasks:
        timeline.append({
            "date": task.due_date or "No due date",
            "type": "task",
            "title": task.title,
            "description": f"Task: {task.description} (Status: {task.status})",
            "priority": task.priority
        })
    
    # Add note creation
    for note in notes:
        timeline.append({
            "date": note.created_date,
            "type": "note_created",
            "title": f"Note: {note.title}",
            "description": note.content[:100] + "..." if len(note.content) > 100 else note.content
        })
    
    # Sort by date
    timeline.sort(key=lambda x: x["date"])
    
    return timeline

# --- MCP Server Setup ---
proxy = ProxyMCP()

proxy.add_tool(Tool(
    name="create_research_project",
    description="Create a new research project.",
    fn=create_research_project,
    input_model=BaseModel.construct(__fields__={
        'title': (str, ...),
        'description': (str, ...),
        'tags': (List[str], None)
    }),
    output_model=ResearchProject
))

proxy.add_tool(Tool(
    name="get_research_projects",
    description="Get all research projects, optionally filtered by status.",
    fn=get_research_projects,
    input_model=BaseModel.construct(__fields__={
        'status': (Optional[str], None)
    }),
    output_model=List[ResearchProject]
))

proxy.add_tool(Tool(
    name="update_project_status",
    description="Update the status and progress of a research project.",
    fn=update_project_status,
    input_model=BaseModel.construct(__fields__={
        'project_id': (str, ...),
        'status': (str, ...),
        'progress': (Optional[float], None)
    }),
    output_model=ResearchProject
))

proxy.add_tool(Tool(
    name="create_research_task",
    description="Create a new research task within a project.",
    fn=create_research_task,
    input_model=BaseModel.construct(__fields__={
        'project_id': (str, ...),
        'title': (str, ...),
        'description': (str, ...),
        'priority': (str, "medium"),
        'estimated_hours': (float, 1.0),
        'due_date': (Optional[str], None)
    }),
    output_model=ResearchTask
))

proxy.add_tool(Tool(
    name="get_project_tasks",
    description="Get all tasks for a project, optionally filtered by status.",
    fn=get_project_tasks,
    input_model=BaseModel.construct(__fields__={
        'project_id': (str, ...),
        'status': (Optional[str], None)
    }),
    output_model=List[ResearchTask]
))

proxy.add_tool(Tool(
    name="update_task_status",
    description="Update the status and actual hours of a research task.",
    fn=update_task_status,
    input_model=BaseModel.construct(__fields__={
        'task_id': (str, ...),
        'status': (str, ...),
        'actual_hours': (Optional[float], None)
    }),
    output_model=ResearchTask
))

proxy.add_tool(Tool(
    name="create_research_note",
    description="Create a new research note within a project.",
    fn=create_research_note,
    input_model=BaseModel.construct(__fields__={
        'project_id': (str, ...),
        'title': (str, ...),
        'content': (str, ...),
        'tags': (List[str], None),
        'related_persons': (List[str], None)
    }),
    output_model=ResearchNote
))

proxy.add_tool(Tool(
    name="get_project_notes",
    description="Get all notes for a project, optionally filtered by tags.",
    fn=get_project_notes,
    input_model=BaseModel.construct(__fields__={
        'project_id': (str, ...),
        'tags': (List[str], None)
    }),
    output_model=List[ResearchNote]
))

proxy.add_tool(Tool(
    name="search_notes",
    description="Search notes by content or title.",
    fn=search_notes,
    input_model=BaseModel.construct(__fields__={
        'query': (str, ...),
        'project_id': (Optional[str], None)
    }),
    output_model=List[ResearchNote]
))

proxy.add_tool(Tool(
    name="generate_research_report",
    description="Generate a comprehensive report for a research project.",
    fn=generate_research_report,
    input_model=BaseModel.construct(__fields__={
        'project_id': (str, ...)
    }),
    output_model=Dict[str, Any]
))

proxy.add_tool(Tool(
    name="get_research_timeline",
    description="Get a timeline of research activities for a project.",
    fn=get_research_timeline,
    input_model=BaseModel.construct(__fields__={
        'project_id': (str, ...)
    }),
    output_model=List[Dict[str, Any]]
))

if __name__ == '__main__':
    logger.info("Starting Research Management MCP server...")
    proxy.run() 