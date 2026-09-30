"""Validate a career-study-notes delivery. Does not modify files."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image


def validate(root):
    root = Path(root).resolve()
    data = json.loads((root / '交付清单.json').read_text(encoding='utf-8-sig'))
    notes = data['notes']
    errors, hashes = [], set()
    if len(notes) != data['expected_count']:
        errors.append('篇数与预期不一致')
    if [n['id'] for n in notes] != list(range(1, len(notes) + 1)):
        errors.append('编号不连续或未排序')

    def resolve(value):
        if Path(value).is_absolute():
            raise ValueError('请使用项目相对路径: ' + value)
        dest = (root / value).resolve()
        if not dest.is_relative_to(root):
            raise ValueError('路径越出项目: ' + value)
        return dest

    count = 0
    for n in notes:
        folder = resolve(n['folder'])
        if not folder.is_dir():
            errors.append(f"{n['id']}: 缺少文件夹")
            continue
        declared = {resolve(f) for f in n['images']}
        actual = {f.resolve() for f in folder.iterdir() if f.suffix.lower() in ('.jpg', '.jpeg', '.png')}
        if actual != declared:
            errors.append(f"{n['id']}: 图片清单与文件夹不一致")
        if not n['images']:
            errors.append(f"{n['id']}: 缺少图片")
        for i, name in enumerate(n['images']):
            f = resolve(name)
            if f.parent != folder or not f.is_file():
                errors.append('图片路径错误: ' + name)
                continue
            try:
                with Image.open(f) as im:
                    if list(im.size) != data['size']:
                        errors.append('图片尺寸错误: ' + name)
                    im.verify()
            except Exception as exc:
                errors.append(f'图片无法读取: {name}: {exc}')
            if i == 0:
                digest = hashlib.sha256(f.read_bytes()).hexdigest()
                if digest in hashes:
                    errors.append('封面完全重复: ' + name)
                hashes.add(digest)
            count += 1
        for key in ('copy', 'transcript', 'sources'):
            f = resolve(n[key])
            if f.parent != folder or not f.is_file() or not f.read_text(encoding='utf-8-sig').strip():
                errors.append(f"{n['id']}: 缺失或空白 {key}")
        f = resolve(n['copy'])
        if f.is_file() and f.read_text(encoding='utf-8-sig').splitlines()[0].strip() != n['title']:
            errors.append(f"{n['id']}: 文案标题不对应")
    return {'notes': len(notes), 'images': count, 'errors': errors}


if __name__ == '__main__':
    result = validate(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(bool(result['errors']))
