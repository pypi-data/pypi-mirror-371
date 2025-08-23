from logging import Logger
import multiprocessing
import queue
import threading

# import agentflow.core.agent as aa


import logging, os
logger = logging.getLogger(os.getenv('LOGGER_NAME'))



# Define the Strategy interface
class Worker:
    def __init__(self, initiator_agent):
        if not multiprocessing.get_start_method(allow_none=True):
            multiprocessing.set_start_method('spawn')        
        self.initiator_agent = initiator_agent
        self.work_process = None
        self.work_thread = None
        
        
    def create_event(self):
        return None
    
    
    def is_working(self):
        if self.work_process:
            return self.work_process.is_alive()
        elif self.work_thread:
            return self.work_thread.is_alive()
        else:
            return False


    def send_data(self, data):
        pass

    
    def start(self):
        pass
    
    
    def stop(self):
        pass



# Concrete strategy for using processes
class ProcessWorker(Worker):
    def __init__(self, initiator_agent):
        super().__init__(initiator_agent)
        
        
    def create_event(self):
        return multiprocessing.Event()
        

    def start(self):
        logger.debug(self.initiator_agent.M(f"self.initiator_agent: {self.initiator_agent}"))
        self.work_queue = multiprocessing.Queue()
        # self.terminate_event = multiprocessing.Event()
        
        cfg = self.initiator_agent.config
        cfg['work_queue'] = self.work_queue
        # cfg['terminate_event'] = self.terminate_event
        self.process = multiprocessing.Process(target=self.initiator_agent._activate, args=(cfg,))
        self.work_process = self.process.start()
        
        return self.process


    def send_data(self, data):
        self.work_queue.put(data)


    def stop(self):
        logger.debug(self.initiator_agent.M("Stopping.."))
        self.send_data('terminate')
        self.process.join()  # Wait for the process to finish
        logger.debug(self.initiator_agent.M("Stopped."))



# Concrete strategy for using threads
class ThreadWorker(Worker):
    def __init__(self, initiator_agent):
        super().__init__(initiator_agent)
        
        
    def create_event(self):
        return threading.Event()


    def start(self):
        logger.debug("Thread worker")
        self.work_queue = queue.Queue()
        # self.terminate_event = threading.Event()
        
        cfg = self.initiator_agent.config
        cfg['work_queue'] = self.work_queue
        # cfg['terminate_event'] = self.terminate_event
        self.work_thread = threading.Thread(target=self.initiator_agent._activate, args=(cfg,))
        self.work_thread.start()
        
        return self.work_thread


    def send_data(self, data):
        logger.debug(self.initiator_agent.M(f"data: {data}"))
        self.work_queue.put(data)


    def stop(self):
        logger.debug(self.initiator_agent.M("Stopping.."))
        self.send_data('terminate')
        self.work_thread.join()  # Wait for the process to finish
        logger.debug(self.initiator_agent.M("Stopped."))
