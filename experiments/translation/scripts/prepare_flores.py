"""Extract the English and Sinhala FLORES-200 files from the downloaded archive (CC BY-SA 4.0)."""

import hashlib
import tarfile

from common import FLORES, FLORES_SHA256

archive = FLORES / 'flores200_dataset.tar.gz'
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
assert digest == FLORES_SHA256, f'unexpected archive checksum {digest}'

with tarfile.open(archive) as tar:
    for split in ('dev', 'devtest'):
        for code, short in (('eng_Latn', 'en'), ('sin_Sinh', 'si')):
            member = tar.extractfile(f'./flores200_dataset/{split}/{code}.{split}')
            (FLORES / f'{split}.{short}').write_bytes(member.read())
    readme = tar.extractfile('./flores200_dataset/README')
    (FLORES / 'README').write_bytes(readme.read())

for split in ('dev', 'devtest'):
    en = (FLORES / f'{split}.en').read_text(encoding='utf-8').rstrip('\n').split('\n')
    si = (FLORES / f'{split}.si').read_text(encoding='utf-8').rstrip('\n').split('\n')
    assert len(en) == len(si), split
    print(f'{split}: {len(en)} sentence pairs')
