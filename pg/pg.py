import psutil
prc_ids = psutil.pids()

for idx,val in enumerate(prc_ids):
    try:
        prcs = psutil.Process(val)
        p_name = prcs.name()
        cmd = ' '.join(prcs.cmdline())
        stat = prcs.status()
        if 'python3' in p_name:
            print(f'stat: {stat}, cmd: {cmd}, name: {p_name}')
    except:
        print(f'Err: PID={val}, IDX: {idx}')
