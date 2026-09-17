from flask import Flask, render_template, request, jsonify
import json
import os
import sqlite3
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
SINS_PATH = os.path.join(DATA_DIR, 'sins.json')
DB_PATH = os.path.join(DATA_DIR, 'centres.db')

VALIDITY_HOURS = 24
GRACE_HOURS = 1


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS centres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_name TEXT NOT NULL,
            church_or_institution TEXT NOT NULL,
            location_link TEXT,
            times_json TEXT NOT NULL,
            language TEXT,
            active INTEGER NOT NULL DEFAULT 1,
            pin_hash TEXT NOT NULL,
            reports INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    ''')

    cols = [r['name'] for r in conn.execute('PRAGMA table_info(centres)').fetchall()]
    if 'expires_at' not in cols:
        conn.execute("ALTER TABLE centres ADD COLUMN expires_at TEXT NOT NULL DEFAULT '1970-01-01T00:00:00Z'")

    conn.commit()
    conn.close()


def hash_pin(pin):
    return hashlib.sha256(str(pin).encode('utf-8')).hexdigest()


def iso_now():
    return datetime.utcnow().isoformat() + 'Z'


def iso_plus_hours(hours):
    return (datetime.utcnow() + timedelta(hours=hours)).isoformat() + 'Z'


def parse_iso(s):
    try:
        return datetime.fromisoformat(s.replace('Z', '+00:00'))
    except Exception:
        return datetime(1970, 1, 1)


def row_to_dict(row):
    expires_at = row['expires_at']
    now = datetime.utcnow().replace(tzinfo=parse_iso(iso_now()).tzinfo)
    expires_dt = parse_iso(expires_at)
    seconds_left = (expires_dt - now).total_seconds()
    hours_left = max(0, seconds_left / 3600)

    return {
        'id': row['id'],
        'place_name': row['place_name'],
        'church_or_institution': row['church_or_institution'],
        'location_link': row['location_link'] or '',
        'times': json.loads(row['times_json']),
        'language': row['language'] or '',
        'active': bool(row['active']),
        'reports': row['reports'],
        'created_at': row['created_at'],
        'updated_at': row['updated_at'],
        'expires_at': expires_at,
        'hours_left': round(hours_left, 1),
        'expiring_soon': 0 < hours_left <= GRACE_HOURS,
        'expired': seconds_left <= 0,
    }


@app.route('/')
def index():
    with open(SINS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return render_template('index.html', data=data)


@app.route('/centres')
def centres_page():
    return render_template('centres.html')


@app.route('/api/centres', methods=['GET'])
def list_centres():
    conn = get_db()
    now_iso = iso_now()
    rows = conn.execute('''
        SELECT * FROM centres
        WHERE active = 1 AND expires_at > ?
        ORDER BY updated_at DESC
    ''', (now_iso,)).fetchall()
    conn.close()
    return jsonify([row_to_dict(r) for r in rows])


@app.route('/api/centres', methods=['POST'])
def create_centre():
    body = request.get_json(silent=True) or {}
    place_name = (body.get('place_name') or '').strip()
    church = (body.get('church_or_institution') or '').strip()
    location_link = (body.get('location_link') or '').strip()
    times = body.get('times') or []
    language = (body.get('language') or '').strip()
    pin = str(body.get('pin') or '').strip()

    if not place_name or not church:
        return jsonify({'error': 'Place name and church/institution are required.'}), 400
    if len(pin) < 4 or not pin.isdigit():
        return jsonify({'error': 'PIN must be at least 4 digits.'}), 400
    if not isinstance(times, list) or not times:
        return jsonify({'error': 'At least one time slot is required.'}), 400
    for slot in times:
        if not slot.get('day') or not slot.get('from') or not slot.get('to'):
            return jsonify({'error': 'Each time slot must have a day and start/end time.'}), 400

    now = iso_now()
    expires = iso_plus_hours(VALIDITY_HOURS)

    conn = get_db()
    cur = conn.execute('''
        INSERT INTO centres
        (place_name, church_or_institution, location_link, times_json,
         language, active, pin_hash, reports, created_at, updated_at, expires_at)
        VALUES (?, ?, ?, ?, ?, 1, ?, 0, ?, ?, ?)
    ''', (
        place_name, church, location_link, json.dumps(times),
        language, hash_pin(pin), now, now, expires
    ))
    conn.commit()
    new_id = cur.lastrowid
    row = conn.execute('SELECT * FROM centres WHERE id = ?', (new_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(row)), 201


@app.route('/api/centres/<int:centre_id>', methods=['PUT'])
def update_centre(centre_id):
    body = request.get_json(silent=True) or {}
    pin = str(body.get('pin') or '').strip()

    conn = get_db()
    row = conn.execute('SELECT * FROM centres WHERE id = ?', (centre_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Centre not found.'}), 404
    if hash_pin(pin) != row['pin_hash']:
        conn.close()
        return jsonify({'error': 'Incorrect PIN.'}), 403

    place_name = (body.get('place_name') or row['place_name']).strip()
    church = (body.get('church_or_institution') or row['church_or_institution']).strip()
    location_link = (body.get('location_link') or '').strip()
    times = body.get('times')
    language = (body.get('language') or '').strip()
    active = body.get('active')

    if not isinstance(times, list) or not times:
        conn.close()
        return jsonify({'error': 'At least one time slot is required.'}), 400
    for slot in times:
        if not slot.get('day') or not slot.get('from') or not slot.get('to'):
            conn.close()
            return jsonify({'error': 'Each time slot must have a day and start/end time.'}), 400

    new_active = 1 if (active is None or active) else 0
    now = iso_now()

    conn.execute('''
        UPDATE centres
        SET place_name = ?, church_or_institution = ?, location_link = ?,
            times_json = ?, language = ?, active = ?, updated_at = ?
        WHERE id = ?
    ''', (
        place_name, church, location_link, json.dumps(times),
        language, new_active, now, centre_id
    ))
    conn.commit()
    row = conn.execute('SELECT * FROM centres WHERE id = ?', (centre_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(row))


@app.route('/api/centres/<int:centre_id>/renew', methods=['POST'])
def renew_centre(centre_id):
    body = request.get_json(silent=True) or {}
    pin = str(body.get('pin') or '').strip()

    conn = get_db()
    row = conn.execute('SELECT * FROM centres WHERE id = ?', (centre_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Centre not found.'}), 404
    if hash_pin(pin) != row['pin_hash']:
        conn.close()
        return jsonify({'error': 'Incorrect PIN.'}), 403

    now = iso_now()
    new_expires = iso_plus_hours(VALIDITY_HOURS)
    conn.execute('''
        UPDATE centres
        SET updated_at = ?, expires_at = ?, active = 1
        WHERE id = ?
    ''', (now, new_expires, centre_id))
    conn.commit()
    row = conn.execute('SELECT * FROM centres WHERE id = ?', (centre_id,)).fetchone()
    conn.close()
    return jsonify(row_to_dict(row))


@app.route('/api/centres/<int:centre_id>', methods=['DELETE'])
def delete_centre(centre_id):
    body = request.get_json(silent=True) or {}
    pin = str(body.get('pin') or '').strip()

    conn = get_db()
    row = conn.execute('SELECT * FROM centres WHERE id = ?', (centre_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Centre not found.'}), 404
    if hash_pin(pin) != row['pin_hash']:
        conn.close()
        return jsonify({'error': 'Incorrect PIN.'}), 403

    conn.execute('DELETE FROM centres WHERE id = ?', (centre_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/api/centres/<int:centre_id>/report', methods=['POST'])
def report_centre(centre_id):
    conn = get_db()
    row = conn.execute('SELECT * FROM centres WHERE id = ?', (centre_id,)).fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'Centre not found.'}), 404
    conn.execute('UPDATE centres SET reports = reports + 1 WHERE id = ?', (centre_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)