"""Re-run the unchanged historical suites in isolated subprocesses."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess,sys,time,json,os
root=Path(__file__).resolve().parent
def run(name):
    start=time.time();p=root/'evidence'/f'{name}.log'
    with p.open('w') as f:
        r=subprocess.run([sys.executable,name+'.py'],cwd=root/'kernel/clean',stdout=f,stderr=subprocess.STDOUT,
            env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0'))
    lines=p.read_text().splitlines()
    result={'script':name,'exit_code':r.returncode,'seconds':round(time.time()-start,3),
        'pass_lines':sum(x.startswith('PASS') for x in lines),'fail_lines':[x for x in lines if x.startswith('FAIL')], 'tail':lines[-3:]}
    (root/'evidence'/f'{name}.result.json').write_text(json.dumps(result,indent=2))
    return result
if __name__=='__main__':
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(run,['verify_v5','verify_v3','verify_canon','verify_v5_2','verify_a37']): print(json.dumps(result),flush=True)
