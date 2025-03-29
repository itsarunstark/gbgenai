from threading import Thread, Lock
from uuid import UUID
from typing_extensions import AnyStr, Callable, Any
import uuid
from enum import Enum
from queue import Queue
import time

Bool = bool

class Priority(Enum):
    PRIORITY_HIGH = 0x03
    PRIORITY_MID = 0x02
    PRIORITY_LOW = 0x01

jobFamily = {

}

class Schedular(object):
    def __init__(self):
        self.jobs = {
            Priority.PRIORITY_HIGH: Queue(),
            Priority.PRIORITY_MID: Queue(),
            Priority.PRIORITY_LOW: Queue()
        }

        self.schedular_lock = Lock()
        self.running = False
    
    def process_queue(self):
        print("Invoked BACKEND ENGINE.......")

        while(not self.jobs[Priority.PRIORITY_HIGH].empty()):
            with self.schedular_lock:
                job = self.jobs[Priority.PRIORITY_HIGH].get_nowait()
            job.execute()
        
        while(not self.jobs[Priority.PRIORITY_MID].empty()):
            with self.schedular_lock:
                job = self.jobs[Priority.PRIORITY_MID].get_nowait()
            job.execute()
        
        while(not self.jobs[Priority.PRIORITY_LOW].empty()):
            with self.schedular_lock:
                job = self.jobs[Priority.PRIORITY_LOW].get_nowait()
            job.execute()
        
        self.running = False
    
    def queue_job(self, job, priority: Priority) -> UUID:
        with self.schedular_lock:
            self.jobs[priority].put_nowait(job)
        if(not self.running):
            self.start_schedular()
        
        return job.job_id
            


    def start_schedular(self):
        self.running = True
        self.running_thread = Thread(target=self.process_queue)
        self.running_thread.start()



class Job(object):
    job_id : UUID = None
    job_title : AnyStr = None
    job_function : Callable = None
    data : Any = None
    running : Bool = False
    finished : Bool = False
    started : Bool = False
    results : Any = None
    remarks: AnyStr = ''

    def __init__(self, data: Any, job_function: Callable):
        self.job_id = uuid.uuid4()
        self.job_function = job_function
        self.data = data
        jobFamily[self.job_id] = self
    
    def schedule_job(self, schedular:Schedular, priority_level):
        self.running = False
        self.finished = False
        self.started  = False
        return schedular.queue_job(self, priority_level)

    
    def execute(self):
        self.started = True
        self.running = True
        results = self.job_function(self.data)
        self.running = False
        self.finished = True
        self.results = results

def placeholder(text):
    for i in range(10):
        print(text)
    return "finished"

if __name__ == '__main__':
    schedular  = Schedular()
    job1 = Job("Data here", placeholder)
    job_id = job1.schedule_job(schedular, Priority.PRIORITY_LOW)
    print("JOB ID IS .. {}".format(job_id))
    while(not job1.finished):...
        # print("Waiting for job to finsihed .................")
    print(job1.finished)
    print(job1.results)
    time.sleep(3)
    job2 = Job("Data here Done", placeholder)
    job_id = job2.schedule_job(schedular, Priority.PRIORITY_LOW)
    print("JOB ID IS .. {}".format(job_id))
    print(jobFamily)

