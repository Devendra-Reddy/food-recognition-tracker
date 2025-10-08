#!/usr/bin/env python3
"""
Background Agent System for Food Recognition Tracker
Handles async processing, job queuing, and real-time status updates
"""

import threading
import queue
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Callable, Optional
from enum import Enum


class JobStatus(Enum):
    """Job status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job:
    """Represents a background job"""
    
    def __init__(self, job_id: str, job_type: str, data: Dict[str, Any], 
                 callback: Optional[Callable] = None):
        self.job_id = job_id
        self.job_type = job_type
        self.data = data
        self.callback = callback
        self.status = JobStatus.PENDING
        self.progress = 0
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary"""
        return {
            'job_id': self.job_id,
            'job_type': self.job_type,
            'status': self.status.value,
            'progress': self.progress,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'metadata': self.metadata
        }


class BackgroundAgent:
    """Background agent for processing jobs asynchronously"""
    
    def __init__(self, num_workers: int = 3):
        self.num_workers = num_workers
        self.job_queue = queue.Queue()
        self.jobs: Dict[str, Job] = {}
        self.workers = []
        self.running = False
        self.lock = threading.Lock()
        
        # Job handlers
        self.job_handlers: Dict[str, Callable] = {}
        
        # Statistics
        self.stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'average_processing_time': 0
        }
    
    def register_handler(self, job_type: str, handler: Callable):
        """Register a handler for a specific job type"""
        self.job_handlers[job_type] = handler
        print(f"✅ Registered handler for job type: {job_type}")
    
    def start(self):
        """Start the background agent"""
        if self.running:
            print("⚠️ Background agent already running")
            return
        
        self.running = True
        
        # Start worker threads
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker, args=(i,), daemon=True)
            worker.start()
            self.workers.append(worker)
        
        print(f"🚀 Background agent started with {self.num_workers} workers")
    
    def stop(self):
        """Stop the background agent"""
        if not self.running:
            return
        
        self.running = False
        
        # Wait for workers to finish
        for worker in self.workers:
            worker.join(timeout=5)
        
        self.workers.clear()
        print("🛑 Background agent stopped")
    
    def submit_job(self, job_type: str, data: Dict[str, Any], 
                   callback: Optional[Callable] = None) -> str:
        """
        Submit a new job for processing
        
        Args:
            job_type: Type of job to process
            data: Job data
            callback: Optional callback function to call on completion
            
        Returns:
            Job ID
        """
        job_id = str(uuid.uuid4())
        job = Job(job_id, job_type, data, callback)
        
        with self.lock:
            self.jobs[job_id] = job
            self.stats['total_jobs'] += 1
        
        self.job_queue.put(job)
        print(f"📥 Job submitted: {job_type} (ID: {job_id[:8]}...)")
        
        return job_id
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a job"""
        with self.lock:
            job = self.jobs.get(job_id)
            return job.to_dict() if job else None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job"""
        with self.lock:
            job = self.jobs.get(job_id)
            if job and job.status == JobStatus.PENDING:
                job.status = JobStatus.CANCELLED
                return True
            return False
    
    def get_all_jobs(self, status: Optional[JobStatus] = None) -> list:
        """Get all jobs, optionally filtered by status"""
        with self.lock:
            jobs = list(self.jobs.values())
            if status:
                jobs = [j for j in jobs if j.status == status]
            return [j.to_dict() for j in jobs]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        with self.lock:
            return {
                **self.stats,
                'active_jobs': sum(1 for j in self.jobs.values() if j.status == JobStatus.PROCESSING),
                'pending_jobs': self.job_queue.qsize(),
                'total_jobs_in_memory': len(self.jobs)
            }
    
    def _worker(self, worker_id: int):
        """Worker thread that processes jobs"""
        print(f"👷 Worker {worker_id} started")
        
        while self.running:
            try:
                # Get job from queue with timeout
                job = self.job_queue.get(timeout=1)
                
                # Process job
                self._process_job(job, worker_id)
                
                # Mark task as done
                self.job_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Worker {worker_id} error: {e}")
        
        print(f"👷 Worker {worker_id} stopped")
    
    def _process_job(self, job: Job, worker_id: int):
        """Process a single job"""
        try:
            # Update job status
            with self.lock:
                job.status = JobStatus.PROCESSING
                job.started_at = datetime.now()
                job.metadata['worker_id'] = worker_id
            
            print(f"⚙️ Worker {worker_id} processing: {job.job_type} (ID: {job.job_id[:8]}...)")
            
            # Get handler for job type
            handler = self.job_handlers.get(job.job_type)
            
            if not handler:
                raise ValueError(f"No handler registered for job type: {job.job_type}")
            
            # Execute handler with progress callback
            def progress_callback(progress: int, metadata: Dict[str, Any] = None):
                with self.lock:
                    job.progress = progress
                    if metadata:
                        job.metadata.update(metadata)
            
            # Call handler
            result = handler(job.data, progress_callback)
            
            # Update job status
            with self.lock:
                job.status = JobStatus.COMPLETED
                job.result = result
                job.progress = 100
                job.completed_at = datetime.now()
                
                # Update stats
                self.stats['completed_jobs'] += 1
                processing_time = (job.completed_at - job.started_at).total_seconds()
                
                # Update average processing time
                total_completed = self.stats['completed_jobs']
                current_avg = self.stats['average_processing_time']
                self.stats['average_processing_time'] = (
                    (current_avg * (total_completed - 1) + processing_time) / total_completed
                )
            
            print(f"✅ Job completed: {job.job_type} (ID: {job.job_id[:8]}...)")
            
            # Call callback if provided
            if job.callback:
                try:
                    job.callback(job)
                except Exception as e:
                    print(f"⚠️ Callback error: {e}")
            
        except Exception as e:
            print(f"❌ Job failed: {job.job_type} (ID: {job.job_id[:8]}...) - {e}")
            
            with self.lock:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = datetime.now()
                self.stats['failed_jobs'] += 1
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old completed jobs"""
        cutoff_time = datetime.now()
        removed = 0
        
        with self.lock:
            job_ids_to_remove = []
            
            for job_id, job in self.jobs.items():
                if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    if job.completed_at:
                        age_hours = (cutoff_time - job.completed_at).total_seconds() / 3600
                        if age_hours > max_age_hours:
                            job_ids_to_remove.append(job_id)
            
            for job_id in job_ids_to_remove:
                del self.jobs[job_id]
                removed += 1
        
        if removed > 0:
            print(f"🧹 Cleaned up {removed} old jobs")
        
        return removed


# Global agent instance
_agent_instance: Optional[BackgroundAgent] = None


def get_agent() -> BackgroundAgent:
    """Get global background agent instance"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = BackgroundAgent(num_workers=3)
        _agent_instance.start()
    return _agent_instance


def shutdown_agent():
    """Shutdown the global agent"""
    global _agent_instance
    if _agent_instance:
        _agent_instance.stop()
        _agent_instance = None
