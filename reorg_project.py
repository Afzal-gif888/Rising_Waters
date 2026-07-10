import os
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent

new_dirs = [
    root / 'backend',
    root / 'backend' / 'routes',
    root / 'backend' / 'services',
    root / 'backend' / 'config',
    root / 'backend' / '__pycache__',
    root / 'frontend',
    root / 'frontend' / 'templates',
    root / 'frontend' / 'static',
    root / 'frontend' / 'static' / 'css',
    root / 'frontend' / 'static' / 'js',
    root / 'frontend' / 'static' / 'images',
    root / 'ml',
    root / 'ml' / 'notebooks',
    root / 'ml' / 'utils',
    root / 'docs',
    root / 'docs' / 'screenshots',
]

for directory in new_dirs:
    directory.mkdir(parents=True, exist_ok=True)

moves = [
    ('src/app.py', 'backend/app.py'),
    ('src/routes.py', 'backend/routes/main.py'),
    ('src/prediction_service.py', 'backend/services/prediction_service.py'),
    ('src/config.py', 'backend/config/settings.py'),
    ('src/train.py', 'backend/train.py'),
    ('src/predict.py', 'backend/predict.py'),
    ('src/__init__.py', 'backend/__init__.py'),
]

for src_rel, dst_rel in moves:
    src = root / src_rel
    dst = root / dst_rel
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))

# move notebooks
src_nb = root / 'notebooks'
if src_nb.exists():
    for item in src_nb.iterdir():
        if item.is_file():
            shutil.move(str(item), str(root / 'ml' / 'notebooks' / item.name))

# move utils
src_utils = root / 'utils'
if src_utils.exists():
    for item in src_utils.iterdir():
        if item.is_file():
            shutil.move(str(item), str(root / 'ml' / 'utils' / item.name))

# move frontend templates and static
src_templates = root / 'templates'
if src_templates.exists():
    for item in src_templates.iterdir():
        if item.is_file():
            shutil.move(str(item), str(root / 'frontend' / 'templates' / item.name))

src_static = root / 'static'
if src_static.exists():
    for subdir in ('css', 'js', 'images'):
        src_sub = src_static / subdir
        dst_sub = root / 'frontend' / 'static' / subdir
        if src_sub.exists():
            for item in src_sub.iterdir():
                if item.is_file():
                    shutil.move(str(item), str(dst_sub / item.name))

# move docs
arch = root / 'reports' / 'architecture.md'
if arch.exists():
    shutil.move(str(arch), str(root / 'docs' / 'architecture.md'))

screens = root / 'reports' / 'screenshots' / 'README.md'
if screens.exists():
    shutil.move(str(screens), str(root / 'docs' / 'screenshots' / 'README.md'))

# cleanup empty directories
for directory in ['src', 'templates', 'static/css', 'static/js', 'static/images', 'static', 'utils', 'notebooks', 'reports/screenshots']:
    path = root / directory
    try:
        if path.exists() and not any(path.iterdir()):
            path.rmdir()
    except Exception:
        pass

print('Reorganization complete.')
