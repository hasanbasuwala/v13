import asyncio
from core.state.registry import Global_Registry
from core.state.models import Stage
from core.downloader.manager import process_download
from core.ui.notifications import update_job_card, send_failure_log

async def download_worker(queue, app):
    """
    Background worker that pulls jobs from the download_queue and 
    delegates them to the DownloadManager.
    """
    while True:
        # 1. Pull the job from the queue
        job = await queue.get()
        
        try:
            # 2. Update state to downloading
            await Global_Registry.update_job(job.job_id, {"stage": Stage.DOWNLOADING})
            
            # 3. Delegate to Downloader Manager (the "brain")
            success = await process_download(job)
            
            if success:
                # 4. Route to next stage (Encoding)
                await Global_Registry.update_job(job.job_id, {"stage": Stage.DOWNLOADED})
                # Add to encode_queue here when implemented
            else:
                await Global_Registry.update_job(job.job_id, {"stage": Stage.FAILED})
                await send_failure_log(app, job, "Download Manager reported failure.")
                
        except Exception as e:
            await Global_Registry.update_job(job.job_id, {"stage": Stage.FAILED})
            await send_failure_log(app, job, str(e))
            
        finally:
            # 5. Mark task as done
            queue.task_done()
