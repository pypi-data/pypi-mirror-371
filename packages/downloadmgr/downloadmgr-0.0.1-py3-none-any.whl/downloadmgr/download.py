import time
import json
from appPublic.dictObject import DictObject
from sqlor.dbpools import DBPools
from ahserver.serverenv import ServerEnv, get_serverenv

class DownloadMgr:
	def __init__(self,request):
		self.request = request
		self.env = request['run_ns']
		self.uapi = self.env.UAPI(request, **self.env)
		self.uappid = 'downloader'

	async def save_finished_task(self, taskid):
		db = DBPools()
		userid = await self.env.get_user()
		dbname = self.env.get_module_dbname('downloadmgr')
		async with db.sqlorContext(dbname) as sor:
			ns = {
				"id": taskid,
				"finish_time": time.time(),
			}
			await sor.U('download', ns)

	async def save_task(self, taskid):
		db = DBPools()
		userid = await self.env.get_user()
		dbname = self.env.get_module_dbname('downloadmgr')
		async with db.sqlorContext(dbname) as sor:
			ns = {
				"id": taskid,
				"userid": userid,
				"start_time": time.time()
			}
			await sor.C('download', ns)

	async def get_user_tasks(self):
		db = DBPools()
		userid = await self.env.get_user()
		dbname = self.env.get_module_dbname('downloadmgr')
		async with db.sqlorContext(dbname) as sor:
			sql = """select * from download
where userid=${userid}$
and finish_time is NULL"""
			ns = {
				'userid': userid
			}
			recs = await sor.sqlExe(sql, ns)
			return recs
		return []
		
	async def uapicall(self, apiname, ns):
		userid = await self.env.get_user()
		x = self.uapi.call(self.uappname,
					apiname,
					userid,
					ns)
		d = json.loads(x.decode('utf-8')
		return DictObject(**d)

	async download(self, url):
		try:
			d = await self.uapicall('addUrl', {'url':url})
			await self.save_task(d.result)
			return d.result
		except Exception as e:
			self.env.exception(f'{url=},{e}\n{format_exc()}')
			raise e

	async def delete_file(self, filename):
		pass

	async remove_task(self, taskid):
		await self.uapicall('remove-task', {'taskid':taskid})
		return True
	
	async def file_downloaded(self, filename):
		pass
	
	async def check_download_finished(self, status):
		s = status
		if s.totalLength == s.completedLength:
			await self.save_finished_task(s.gid)
			await self.file_downloaded(s.info.name)
			await self.remove_task(s.gid)
			await self.delete_file(s.info.name)
				
	async def get_task_status(self, tid):
		d = await self.uapicall('get_task_status', {'taskid':tid})
		await self.check_downlaod_finished(d.result)
		rzt = d.result
		rzt.filename = rzt.info.name
		return rzt

	async get_tasks_status(self):
		recs = await self.get_user_tasks(userid)
		urls = [r.id for r in recs]
		try:
			d = await self.uapicall('get_task_status', {'taskid':tid})
			await self.check_downlaod_finished(d.result)
			return d.result
		except Exception as e:
			self.env.exception(f'{e=}\n{format_exc()}')
			raise e
	

