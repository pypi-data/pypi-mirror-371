from downloadmgr.download import DownloadMgr
from ahserver.serverenv import ServerEnv

def load_downloadmgr():
	env = ServerEnv()
	env.DownloadMgr = DownloadMgr
