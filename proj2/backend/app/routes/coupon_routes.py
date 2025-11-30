from flask import Blueprint, request, jsonify, current_app, send_file
from app.models import Coupons
from app.models import CodePuzzles
from app.app import db
import random
import os
import base64

coupon_bp = Blueprint('coupon', __name__, url_prefix='/api')


@coupon_bp.route('/coupons', methods=['GET'])
def list_coupons():
    try:
        coupons = Coupons.query.filter_by(is_active=True).all()
        return jsonify({'coupons': [{'id': c.id, 'code': c.code, 'difficulty': c.difficulty, 'discount_percent': float(c.discount_percent)} for c in coupons]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@coupon_bp.route('/coupons/<string:code>', methods=['GET'])
def get_coupon(code):
    try:
        c = Coupons.query.filter_by(code=code, is_active=True).first()
        if not c:
            return jsonify({'error': 'Coupon not found'}), 404
        return jsonify({'id': c.id, 'code': c.code, 'difficulty': c.difficulty, 'discount_percent': float(c.discount_percent)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@coupon_bp.route('/coupons', methods=['POST'])
def create_coupon():
    # Minimal creation endpoint; in a real app restrict to admin/staff
    try:
        data = request.get_json() or {}
        code = data.get('code')
        difficulty = int(data.get('difficulty', 1))
        discount_percent = float(data.get('discount_percent', 0.0))
        if not code:
            return jsonify({'error': 'code is required'}), 400
        c = Coupons(code=code, difficulty=difficulty, discount_percent=discount_percent)
        db.session.add(c)
        db.session.commit()
        return jsonify({'message': 'Coupon created', 'id': c.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@coupon_bp.route('/coupons/apply', methods=['POST'])
def apply_coupon():
    try:
        data = request.get_json() or {}
        code = data.get('code')
        total = float(data.get('total', 0.0))
        skip_puzzle = bool(data.get('skip_puzzle', False))
        answer = data.get('answer')
        token = data.get('token')

        if not code:
            return jsonify({'error': 'code is required'}), 400

        c = Coupons.query.filter_by(code=code, is_active=True).first()
        if not c:
            return jsonify({'error': 'Invalid coupon code'}), 404

        # If puzzle is required and not skipped, verify answer by reading answer file
        if not skip_puzzle:
            if not token or answer is None:
                return jsonify({'error': 'Puzzle answer and token required'}), 400
            try:
                # token is a base64 encoded string produced by get_coupon_puzzle
                decoded = base64.b64decode(token.encode()).decode()
                # token format for DB puzzles: db:<id>
                if decoded.startswith('db:'):
                    try:
                        pid = int(decoded.split(':', 1)[1])
                    except Exception:
                        return jsonify({'error': 'Invalid DB puzzle token'}), 400
                    puzzle = CodePuzzles.query.get(pid)
                    if not puzzle or not puzzle.is_active:
                        return jsonify({'error': 'Puzzle not found'}), 400
                    expected_answer = (puzzle.answer or '').strip()
                    if str(answer).strip() != expected_answer:
                        return jsonify({'error': 'Incorrect puzzle answer'}), 400
                else:
                    # filesystem based token: <folder>/<name>
                    puzzle_relpath = decoded
                    # Allow test override of puzzle root
                    puzzle_root = current_app.config.get('CODE_PUZZLE_ROOT', os.path.join(current_app.root_path, 'code_puzzle'))
                    puzzle_dir = os.path.join(puzzle_root)
                    answer_path = os.path.join(puzzle_dir, puzzle_relpath + '.txt')
                    if not os.path.exists(answer_path):
                        return jsonify({'error': 'Puzzle answer file not found'}), 400
                    with open(answer_path, 'r', encoding='utf-8') as f:
                        expected_answer = f.read().strip()
                    if str(answer).strip() != expected_answer.strip():
                        return jsonify({'error': 'Incorrect puzzle answer'}), 400
            except Exception as e:
                return jsonify({'error': 'Token verification failed: ' + str(e)}), 400

        # Apply discount
        discount = float(c.discount_percent)
        discounted = max(0.0, total * (1 - discount / 100.0))
        return jsonify({'code': c.code, 'discount_percent': discount, 'new_total': round(discounted, 2)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@coupon_bp.route('/coupons/<string:code>/puzzle', methods=['GET'])
def get_coupon_puzzle(code):
    """Return a simple puzzle and a signed token encoding the expected answer.
    The client shows the puzzle and submits answer+token to /coupons/apply for verification.
    """
    try:
        c = Coupons.query.filter_by(code=code, is_active=True).first()
        if not c:
            return jsonify({'error': 'Coupon not found'}), 404

        # Choose a puzzle file from code_puzzle based on difficulty
        difficulty_level = int(max(1, min(10, int(c.difficulty))))
        # map difficulty to folder: 1-3 -> easy, 4-6 -> medium, 7-10 -> hard
        if difficulty_level <= 3:
            folder = 'easy'
        elif difficulty_level <= 6:
            folder = 'medium'
        else:
            folder = 'hard'

        # Allow tests to override the puzzle root directory via app config
        puzzle_root = current_app.config.get('CODE_PUZZLE_ROOT', os.path.join(current_app.root_path, 'code_puzzle'))
        puzzle_dir = os.path.join(puzzle_root, folder)

        if not os.path.exists(puzzle_dir):
            return jsonify({'error': 'Puzzle directory not found on server'}), 500

        # Prefer puzzles from DB that match difficulty and folder
        puzzles = CodePuzzles.query.filter_by(folder=folder, is_active=True).all()
        script_content = None
        token = None
        filename = None

        if puzzles:
            chosen = random.choice(puzzles)
            script_content = chosen.script
            token = base64.b64encode(f"db:{chosen.id}".encode()).decode()
            filename = f"{chosen.folder}/{chosen.name}.py"
            return jsonify({'puzzle_script': script_content, 'token': token, 'filename': filename}), 200

        # fallback to filesystem
        py_files = [f for f in os.listdir(puzzle_dir) if f.endswith('.py')]
        if not py_files:
            return jsonify({'error': 'No puzzles available'}), 500
        chosen_file = random.choice(py_files)
        chosen_path = os.path.join(puzzle_dir, chosen_file)
        with open(chosen_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        rel = f"{folder}/{os.path.splitext(chosen_file)[0]}"
        token = base64.b64encode(rel.encode()).decode()
        filename = chosen_file
        return jsonify({'puzzle_script': script_content, 'token': token, 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
