import asyncio,importlib.util,os,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('runtime_memory',Path(__file__).resolve().parents[1]/'utils/runtime_memory.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RuntimeMemoryChecks(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        os.environ['VOICEBOX_LOW_MEMORY']='1'
        m._model_work_lock=asyncio.Lock()
    async def test_only_one_model_job_runs_at_a_time(self):
        active=0;peak=0
        @m.serialized_model_work
        async def work():
            nonlocal active,peak
            active+=1;peak=max(peak,active)
            await asyncio.sleep(.02)
            active-=1
        await asyncio.gather(work(),work(),work())
        self.assertEqual(peak,1)
    async def test_nested_work_in_same_task_does_not_deadlock(self):
        @m.serialized_model_work
        async def child():return 42
        @m.serialized_model_work
        async def parent():return await child()
        self.assertEqual(await asyncio.wait_for(parent(),1),42)
    async def test_cancellation_releases_resources_for_next_job(self):
        entered=asyncio.Event()
        @m.serialized_model_work
        async def interrupted():
            entered.set();await asyncio.sleep(100)
        @m.serialized_model_work
        async def next_job():return 'ready'
        task=asyncio.create_task(interrupted());await entered.wait();task.cancel()
        with self.assertRaises(asyncio.CancelledError):await task
        self.assertEqual(await asyncio.wait_for(next_job(),1),'ready')
if __name__=='__main__':unittest.main()
