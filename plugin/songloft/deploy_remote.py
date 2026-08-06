#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""远程一键部署「多源音乐桥」SongLoft 插件到远程宿主。

zip 来源（PLUGIN_SRC，默认同级源码仓的 plugin/songloft）：
  - 默认：脚本所在目录往上两级 + '../pcyear-bridge/plugin/songloft'
          （即与 pcyear-bridge-release 同级的 pcyear-bridge/plugin/songloft/dist）
  - 可用环境变量 PLUGIN_SRC 覆盖为任意插件源码/产物目录
    （需含 dist/pcyear-bridge.jsplugin.zip）

部署目标（环境变量可覆盖）：
  DEPLOY_HOST  必填（不内置默认）
  DEPLOY_USER  必填（不内置默认）
  DEPLOY_PASS  必填（不内置默认）

用法：
  python plugin/songloft/deploy_remote.py
  PLUGIN_SRC=/abs/path/to/plugin python plugin/songloft/deploy_remote.py
  DEPLOY_HOST=https://host:1024 DEPLOY_USER=user DEPLOY_PASS=pass python plugin/songloft/deploy_remote.py
"""
import urllib.request, urllib.parse, json, os, ssl, sys, time

HOST = os.environ.get('DEPLOY_HOST', 'https://<宿主地址>:<端口>')
USER = os.environ.get('DEPLOY_USER')
PASS = os.environ.get('DEPLOY_PASS')
BASE = '/api/v1/jsplugin/pcyear-bridge'

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.normpath(os.path.join(HERE, '..', '..', 'pcyear-bridge', 'plugin', 'songloft'))
PLUGIN_SRC = os.environ.get('PLUGIN_SRC') or DEFAULT_SRC
ZIP = os.path.join(PLUGIN_SRC, 'dist', 'pcyear-bridge.jsplugin.zip')

CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE
TOKEN=None

def req(p, data=None, method=None, raw=False, headers=None, files=None, timeout=90):
    global TOKEN
    url = HOST + p
    h = dict(headers or {})
    if TOKEN: h['Authorization']='Bearer '+TOKEN
    body=None
    if files:
        boundary='----bnd'+str(os.getpid())
        h['Content-Type']='multipart/form-data; boundary='+boundary
        parts=[]
        for name,fn,ct,content in files:
            parts.append(('--'+boundary).encode())
            parts.append(('Content-Disposition: form-data; name="%s"; filename="%s"'%(name,fn)).encode())
            parts.append(('Content-Type: %s'%ct).encode()); parts.append(b''); parts.append(content if isinstance(content,bytes) else content.encode())
        parts.append(('--'+boundary+'--').encode()); parts.append(b'')
        body=b'\r\n'.join(parts)
    elif data is not None:
        body=json.dumps(data,ensure_ascii=False).encode(); h['Content-Type']='application/json'
    r=urllib.request.Request(url,data=body,headers=h,method=method or ('POST' if body else 'GET'))
    try:
        with urllib.request.urlopen(r,timeout=timeout,context=CTX) as resp:
            return resp.status,(resp.read() if raw else resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code,e.read().decode()[:600]
    except Exception as e:
        return -1,repr(e)[:300]

print('== 准备 zip ==')
print('PLUGIN_SRC =', PLUGIN_SRC)
print('ZIP        =', ZIP)
if not os.path.isfile(ZIP):
    print('!! 找不到 zip：', ZIP)
    print('   请先构建插件（在源码仓 pcyear-bridge/plugin/songloft 执行 npm run build），')
    print('   或用环境变量 PLUGIN_SRC 指向含 dist/pcyear-bridge.jsplugin.zip 的目录。')
    sys.exit(1)

print('== login ==')
s,b=req('/api/v1/auth/login',{'username':USER,'password':PASS})
print(s,b[:160])
if s!=200: print('LOGIN FAIL'); sys.exit(1)
TOKEN=json.loads(b)['access_token']

print('== upload ==')
with open(ZIP,'rb') as f: content=f.read()
s,ub=req('/api/v1/jsplugins/upload',files=[('file','pcyear-bridge.jsplugin.zip','application/zip',content)])
print('upload',s,ub[:300])

pid=None
try:
    upj=json.loads(ub); results=upj.get('results',[]) if isinstance(upj,dict) else []
    for r in results:
        pl=r.get('plugin') if isinstance(r,dict) else None
        if pl and (pl.get('entryPath') or pl.get('entry_path'))=='pcyear-bridge': pid=pl.get('id'); break
except Exception as e: print('parse',e)
if pid is None:
    try:
        s,b=req('/api/v1/jsplugins'); j=json.loads(b); arr=j.get('data',j) if isinstance(j,dict) else j
        if isinstance(arr,dict): arr=list(arr.values())
        for pl in arr:
            if isinstance(pl,dict) and (pl.get('entryPath') or pl.get('entry_path'))=='pcyear-bridge': pid=pl.get('id'); break
    except Exception as e: print('list',e)
print('plugin id =',pid)
if pid is None: print('!! 未确定 plugin id，跳过重载'); sys.exit(1)
req('/api/v1/jsplugins/%s/disable'%pid,method='POST')
req('/api/v1/jsplugins/%s/enable'%pid,method='POST')
print('reloaded',pid)

# 找 webdav 源
s,b=req(BASE+'/sources'); arr=json.loads(b).get('data',[])
wd=[x for x in arr if x.get('type')=='webdav']
print('webdav 源:',[(x.get('id'),x.get('name')) for x in wd])
if not wd: print('无 webdav 源'); sys.exit(0)
SID=wd[0]['id']

print('== /albums (验证专辑封面 coverId 是否解析) ==')
s,b=req(BASE+'/albums?sourceId=%s&limit=40&refresh=1'%urllib.parse.quote(SID),method='GET')
print('albums status',s)
try:
    ad=json.loads(b); al=ad.get('list',[])
    ok=sum(1 for a in al if a.get('coverId'));
    print(f'专辑封面: 有coverId {ok} / 共 {len(al)}')
    for a in al[:12]:
        print(f"  album={a.get('name')!r:30} coverId={a.get('coverId')!r}")
except Exception as e:
    print('parse',e,b[:200])

# 不触发全量扫描：直接用已知曲目路径探封面解析
print('\n== /cover-data 直接探封面（不触发全量扫描）==')
KNOWN = '有声书1.mp3'
for attempt in range(3):
    s,b=req(BASE+'/cover-data?sourceId=%s&coverId=%s'%(urllib.parse.quote(SID),urllib.parse.quote(KNOWN)),method='GET',timeout=60)
    print(f'  try {attempt+1}: cover-data({KNOWN!r}) -> HTTP {s}')
    if s==200:
        try:
            j=json.loads(b); print('    ok=',j.get('ok'),'contentType=',j.get('contentType'),'len=',len(b))
        except: print('    body:',b[:120])
        break
    time.sleep(3)
print('DONE')
