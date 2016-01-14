# coding: utf-8
import string, sys, os, time
import threading
import Queue, traceback
import logging

TASK_NORET = 0
TASK_RET   = 1
TASK_NOTIFY_RET = 2

log = logging.getLogger()

class ThreadPool:
    def __init__(self, num, qsize=0):
        self.queue   = Queue.Queue(qsize)
        self.result  = {} 
        self.threads = []
        self.count   = num
        #self.mutex   = threading.Lock() 

        self.isrunning  = False
        self.task_done  = 0
        self.task_error = 0
        # 正在执行任务的线程数
        self.thread_running = 0

    def start(self):
        # 如果标记为已经在运行就不能再创建新的线程池运行了
        if self.isrunning:
            return
        for i in range(0, self.count):
            t = threading.Thread(target=self._run)
            self.threads.append(t)
            t.setDaemon(True)
        
        self.isrunning = True
        for th in self.threads:
            th.start()

    def stop(self):
        self.isrunning = False
        # 等待其他线程退出
        while True:
            #self.mutex.acquire()
            #tr = self.thread_running
            #self.mutex.release()
            #if tr == 0:
            if self.thread_running == 0:
                break
            time.sleep(1)
        
    def _run(self):
        while True:
            task = None
            while True:
                if not self.isrunning:
                    log.info('stop!')
                    return
                try:
                    task = self.queue.get(timeout=1)
                except Exception, e:
                    #log.info('get timeout, self.queue.get:',  str(e))
                    continue
                break
            self.do_task(task)


    def do_task(self, task):
        if not task:
            log.error('get task none: %s' % (task.name))
            return

        log.info('get task: %s' % (task.name))
        self.thread_running += 1

        try:
            ret = task.run()
        except Exception, e:
            log.error('task %s run error: %s' % (task.name, str(e)))
            #traceback.print_exc(file=sys.stdout)
            log.error(traceback.format_exc())
            self.thread_running -= 1
            self.task_error += 1
            return
        
        self.task_done += 1
        self.thread_running -= 1

        if not ret is None:
            task.set_result(ret)

        log.info('task %s run complete' % task.name)

    def add(self, task):
        self.queue.put(task) 

    def info(self):
        return (self.task_done, self.task_error)


class Task(object):
    def __init__(self, func=None, *args, **kwargs):
        self.name = self.__class__.__name__
        self._func = func
        self._args = args
        self._kwargs = kwargs

        self._result  = None
        self._event = threading.Event()

    def run(self):
        return self._func(self, *self._args, **self._kwargs)

    def set_result(self, result):
        self._result = result
        self._event.set()

    def get_result(self, timeout=1):
        try:
            log.info('wait ...')
            self._event.wait(timeout)
            log.info('wait timeout ...')
        except:
            return None
        return self._result

class SimpleTask(Task):
    def __init__(self, n, a=None):
        self.name = n
        super(SimpleTask, self).__init__(a)
    
    def run(self):
        #log.info('in task run, ', self.name)
        time.sleep(1)
        #log.info('ok, end task run', self.name)

        return self.name

def test():
    from qfcommon.base import logger
    global log
    log = logger.install('ScreenLogger')
    tp = ThreadPool(10)

    for i in range(0, 100):
        t = SimpleTask(str(i))
        tp.add(t)
    
    tp.start()
    while True: 
        done, error = tp.info()
        log.info('applys:', done, error)
        cc = done + error
        time.sleep(1)
        if cc == 100:
            break
    tp.stop()
    log.info('end')

def test1():
    from qfcommon.base import logger
    global log
    log = logger.install('stdout')
    log.info('init')
    tp = ThreadPool(10)
    tp.start()

    class SimpleTask2(Task):
        def __init__(self, n, a=None):
            self.name = n
            super(SimpleTask2, self).__init__(a)
        
        def run(self):
            log.info('in task run, %s', self.name)
            time.sleep(2)
            log.info('ok, end task run %s', self.name)
            return self.name + '!!!'

    t = SimpleTask2('haha')
    log.info('add ...')
    tp.add(t)
    
    log.info('result:%s', t.get_result(1000))

    tp.stop()

def test2():
    from qfcommon.base import logger
    global log
    log = logger.install('stdout')
    log.info('init')
    tp = ThreadPool(10)
    tp.start()

    def run(obj, name):
        log.info('in task run, %s', name)
        time.sleep(1)
        log.info('ok, end task run %s', name)
        return name + '!!!'

    log.info('add ...')
    t = Task(func=run, name='haha')
    tp.add(t)
    
    log.info('result:%s', t.get_result(1000))

    tp.stop()


        
if __name__ == '__main__':
    test2()



