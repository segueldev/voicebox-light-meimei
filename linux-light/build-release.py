#!/usr/bin/env python3
"""Make offline release parts (< 2 GiB) with streaming tar/gzip and checksums."""
import argparse, hashlib, os, shutil, subprocess
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--payload',required=True,type=Path); p.add_argument('--output',required=True,type=Path); a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
repo=Path(__file__).resolve().parents[1]
size=sum(f.stat().st_size for f in a.payload.rglob('*') if f.is_file() and not f.is_symlink())
version=(repo/'linux-light/VERSION').read_text().strip()
glibc=subprocess.check_output(['getconf','GNU_LIBC_VERSION'],text=True).split()[1]
process=subprocess.Popen(['tar','-cf','-','-C',str(a.payload),'.'],stdout=subprocess.PIPE)
gzip=subprocess.Popen(['gzip','-1'],stdin=process.stdout,stdout=subprocess.PIPE)
process.stdout.close()
manifest=[f'{version} {size} {glibc}']
part=0; limit=1800*1024*1024
while True:
    first=gzip.stdout.read(4*1024*1024)
    if not first: break
    name=f'meimei-payload.tar.gz.part{part:03d}'; digest=hashlib.sha256(); written=0
    with (a.output/name).open('wb') as target:
        while first:
            target.write(first); digest.update(first); written+=len(first)
            if written>=limit: break
            first=gzip.stdout.read(min(4*1024*1024,limit-written))
    manifest.append(f'{digest.hexdigest()} {name}'); print(f'{name}: {written} bytes',flush=True); part+=1
assert gzip.wait()==0 and process.wait()==0
(a.output/'manifest.txt').write_text('\n'.join(manifest)+'\n')
shutil.copyfile(repo/'linux-light/installer.sh',a.output/'instalar-meimei.run'); (a.output/'instalar-meimei.run').chmod(0o755)
shutil.copyfile(repo/'README.md',a.output/'LEEME.md')
all_files=sorted(f for f in a.output.iterdir() if f.is_file() and f.name!='SHA256SUMS')
(a.output/'SHA256SUMS').write_text('\n'.join(hashlib.file_digest(f.open('rb'),'sha256').hexdigest()+'  '+f.name for f in all_files)+'\n')
print(f'Offline release ready: {a.output}',flush=True)
