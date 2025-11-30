import base64
import os
from app.models import Coupons, CodePuzzles


def test_get_coupon_puzzle_filesystem_fallback(app, client, sample_theatre, tmp_path):
    # Ensure a coupon exists that maps to easy difficulty
    with app.app_context():
        c = Coupons(code='TESTFS', difficulty=1, discount_percent=10.0, is_active=True)
        from app.app import db
        db.session.add(c)
        db.session.commit()

        # Create test-only puzzle files under tests/test_code_puzzle/easy and configure app to use it
        test_root = os.path.join(app.root_path, '..', 'tests', 'test_code_puzzle')
        puzzle_dir = os.path.join(test_root, 'easy')
        os.makedirs(puzzle_dir, exist_ok=True)
        sample_py = os.path.join(puzzle_dir, 'sample_fs.py')
        sample_txt = os.path.join(puzzle_dir, 'sample_fs.txt')
        with open(sample_py, 'w', encoding='utf-8') as f:
            f.write('# sample puzzle')
        with open(sample_txt, 'w', encoding='utf-8') as f:
            f.write('answer42')
        # point the app at the test puzzle root
        app.config['CODE_PUZZLE_ROOT'] = test_root

    res = client.get('/api/coupons/TESTFS/puzzle')
    assert res.status_code == 200
    data = res.get_json()
    assert 'token' in data and 'puzzle_script' in data


def test_apply_coupon_with_filesystem_token(app, client):
    # Create coupon and a filesystem puzzle, then apply with correct answer
    with app.app_context():
        from app.app import db
        c = Coupons(code='APPLYFS', difficulty=1, discount_percent=50.0, is_active=True)
        db.session.add(c)
        db.session.commit()
        # create puzzle files in tests/test_code_puzzle and configure app to use it
        test_root = os.path.join(app.root_path, '..', 'tests', 'test_code_puzzle')
        puzzle_dir = os.path.join(test_root, 'easy')
        os.makedirs(puzzle_dir, exist_ok=True)
        with open(os.path.join(puzzle_dir, 'fs_apply.py'), 'w', encoding='utf-8') as f:
            f.write('# no-op')
        with open(os.path.join(puzzle_dir, 'fs_apply.txt'), 'w', encoding='utf-8') as f:
            f.write('right')
        app.config['CODE_PUZZLE_ROOT'] = test_root

    token = base64.b64encode(b'easy/fs_apply').decode()
    payload = {'code': 'APPLYFS', 'total': 20.0, 'token': token, 'answer': 'right', 'skip_puzzle': False}
    res = client.post('/api/coupons/apply', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['code'] == 'APPLYFS'
    assert data['discount_percent'] == 50.0
    assert data['new_total'] == 10.0


def test_apply_coupon_missing_token_returns_400(app, client):
    with app.app_context():
        from app.app import db
        c = Coupons(code='NEEDTOKEN', difficulty=1, discount_percent=10.0, is_active=True)
        db.session.add(c)
        db.session.commit()

    payload = {'code': 'NEEDTOKEN', 'total': 10.0}
    res = client.post('/api/coupons/apply', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert 'error' in data
