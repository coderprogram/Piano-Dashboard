from flask import Flask, render_template, request, jsonify, send_file, session
import csv
import os
from datetime import datetime, timedelta
import uuid
import json
import music_utils

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# CSV files for data storage
CSV_FILE = 'data.csv'
SESSIONS_FILE = 'sessions.csv'
STATS_FILE = 'daily_stats.csv'

def init_csv_files():
    """Initialize all CSV files if they don't exist."""
    # Main practice data
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'type', 'score', 'difficulty', 'clef', 
                           'correct_answer', 'user_answer', 'key_signature', 
                           'time_signature', 'session_id', 'response_time_ms', 'notes'])
    
    # Session summaries
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['session_id', 'start_time', 'end_time', 'session_type', 
                           'total_questions', 'correct_answers', 'accuracy', 
                           'avg_response_time', 'difficulty', 'clef'])
    
    # Daily aggregated stats
    if not os.path.exists(STATS_FILE):
        with open(STATS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'total_sessions', 'total_questions', 'accuracy',
                           'avg_response_time', 'practice_time_minutes'])

def get_session_id():
    """Get or create session ID for tracking practice sessions."""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())[:8]
        session['session_start'] = datetime.now().isoformat()
        session['session_questions'] = 0
        session['session_correct'] = 0
        session['session_times'] = []
    return session['session_id']

def end_session():
    """End current session and save summary."""
    if 'session_id' in session and session['session_questions'] > 0:
        accuracy = (session['session_correct'] / session['session_questions']) * 100
        avg_time = sum(session['session_times']) / len(session['session_times']) if session['session_times'] else 0
        
        # Save session summary
        with open(SESSIONS_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                session['session_id'],
                session['session_start'],
                datetime.now().isoformat(),
                'key_practice',
                session['session_questions'],
                session['session_correct'],
                round(accuracy, 1),
                round(avg_time, 0),
                'mixed',  # difficulty
                'mixed'   # clef
            ])
        
        # Clear session
        session.pop('session_id', None)
        session.pop('session_start', None)
        session.pop('session_questions', None)
        session.pop('session_correct', None)
        session.pop('session_times', None)

def log_practice(practice_type, score, difficulty='', clef='', correct_answer='', 
                user_answer='', key_signature='', time_signature='', session_id='', 
                response_time_ms=0, notes=''):
    """Log practice session to CSV."""
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            practice_type,
            score,
            difficulty,
            clef,
            correct_answer,
            user_answer,
            key_signature,
            time_signature,
            session_id or get_session_id(),
            response_time_ms,
            notes
        ])

def parse_csv_safely():
    """Parse CSV handling both old and new formats."""
    sessions = []
    if not os.path.exists(CSV_FILE):
        return sessions
    
    with open(CSV_FILE, 'r', newline='') as f:
        content = f.read().strip()
        if not content:
            return sessions
            
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if i == 0:  # Skip header
                continue
            
            parts = line.split(',')
            if len(parts) >= 5:  # Minimum required fields
                # Create a standardized record
                record = {
                    'timestamp': parts[0] if len(parts) > 0 else '',
                    'type': parts[1] if len(parts) > 1 else '',
                    'score': parts[2] if len(parts) > 2 else '0',
                    'difficulty': parts[3] if len(parts) > 3 else '',
                    'clef': parts[4] if len(parts) > 4 else '',
                    'correct_answer': parts[5] if len(parts) > 5 else '',
                    'user_answer': parts[6] if len(parts) > 6 else '',
                    'key_signature': parts[7] if len(parts) > 7 else '',
                    'time_signature': parts[8] if len(parts) > 8 else '',
                    'session_id': parts[9] if len(parts) > 9 else '',
                    'response_time_ms': parts[10] if len(parts) > 10 else '0',
                    'notes': parts[11] if len(parts) > 11 else ''
                }
                sessions.append(record)
    
    return sessions

# Initialize CSV files on startup
init_csv_files()

# Global variable to store current key for practice
current_key = None
key_start_time = None

@app.route('/')
def index():
    """Main page with navigation."""
    return render_template('index.html')

@app.route('/key-practice')
def key_practice():
    """Key recognition practice page."""
    return render_template('key_practice.html')

@app.route('/sight-reading')
def sight_reading():
    """Sight reading practice page."""
    return render_template('sight_reading.html')

@app.route('/api/key/new')
def new_key():
    """Generate a new random key for practice."""
    global current_key, key_start_time
    current_key = music_utils.generate_random_key()
    key_start_time = datetime.now()
    return jsonify(current_key)

@app.route('/api/key/check', methods=['POST'])
def check_key():
    """Check user's key recognition answer."""
    global current_key, key_start_time
    
    if not current_key or not key_start_time:
        return jsonify({'error': 'No current key'}), 400
    
    user_answer = request.json.get('answer', '').strip()
    correct = music_utils.check_key_answer(current_key['note'], user_answer)
    
    # Calculate response time
    response_time = (datetime.now() - key_start_time).total_seconds() * 1000
    
    # Update session counters
    if 'session_questions' in session:
        session['session_questions'] += 1
        session['session_times'].append(response_time)
        if correct:
            session['session_correct'] += 1
    
    # Log the practice session with detailed info
    score = 1 if correct else 0
    log_practice(
        practice_type='key_practice',
        score=score,
        difficulty='beginner',
        clef=current_key['clef'],
        correct_answer=current_key['display_name'],
        user_answer=user_answer,
        response_time_ms=round(response_time),
        notes=f"Octave: {current_key['octave']}"
    )
    
    # Check if session should end (10 questions)
    session_complete = False
    if session.get('session_questions', 0) >= 10:
        end_session()
        session_complete = True
    
    response = {
        'correct': correct,
        'correct_answer': current_key['display_name'],
        'user_answer': user_answer,
        'response_time': round(response_time),
        'session_complete': session_complete,
        'session_progress': f"{session.get('session_questions', 0)}/10"
    }
    
    return jsonify(response)

@app.route('/api/melody/generate', methods=['POST'])
def generate_melody():
    """Generate a melody for sight reading practice."""
    data = request.json
    difficulty = data.get('difficulty', 'beginner')
    clef = data.get('clef', 'treble')
    
    melody = music_utils.generate_melody(difficulty, clef)
    
    # Log the generation with detailed info
    log_practice(
        practice_type='sight_reading_generated',
        score=1,
        difficulty=difficulty,
        clef=clef,
        key_signature=melody['key_signature'],
        time_signature=melody['time_signature'],
        notes=f"{len(melody['melody'])} notes, {melody.get('measures', 4)} measures"
    )
    
    return jsonify(melody)

@app.route('/api/melody/export', methods=['POST'])
def export_melody():
    """Export melody as PDF."""
    melody_data = request.json
    
    if not melody_data:
        return jsonify({'error': 'No melody data provided'}), 400
    
    # Create exports directory if it doesn't exist
    os.makedirs('exports', exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"practice_sheet_{timestamp}.pdf"
    
    try:
        # Create PDF
        music_utils.create_practice_pdf(melody_data, filename)
        
        # Log the export with detailed info
        log_practice(
            practice_type='pdf_export',
            score=1,
            difficulty=melody_data.get('difficulty', ''),
            clef=melody_data.get('clef', ''),
            key_signature=melody_data.get('key_signature', ''),
            time_signature=melody_data.get('time_signature', ''),
            notes=f"Exported: {filename}"
        )
        
        return send_file(f'exports/{filename}', as_attachment=True, download_name=filename)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def get_stats():
    """Get practice statistics."""
    try:
        sessions = parse_csv_safely()
        
        if not sessions:
            return jsonify({
                'total_sessions': 0,
                'key_practice_accuracy': 0,
                'treble_accuracy': 0,
                'bass_accuracy': 0,
                'avg_response_time': 0,
                'current_session_progress': session.get('session_questions', 0),
                'recent_sessions': []
            })
        
        # Filter different types of sessions
        key_practice_sessions = [s for s in sessions if s['type'] == 'key_practice']
        treble_sessions = [s for s in key_practice_sessions if s['clef'] == 'treble']
        bass_sessions = [s for s in key_practice_sessions if s['clef'] == 'bass']
        
        # Calculate overall statistics
        stats = {
            'total_sessions': len([s for s in sessions if s['type'] != 'session_start']),
            'key_practice_accuracy': 0,
            'treble_accuracy': 0,
            'bass_accuracy': 0,
            'avg_response_time': 0,
            'sight_reading_generated': len([s for s in sessions if s['type'] == 'sight_reading_generated']),
            'pdfs_exported': len([s for s in sessions if s['type'] == 'pdf_export']),
            'current_session_id': get_session_id(),
            'current_session_progress': session.get('session_questions', 0),
            'recent_sessions': []
        }
        
        # Calculate accuracy metrics
        if key_practice_sessions:
            correct_answers = sum(1 for s in key_practice_sessions if s['score'] and float(s['score']) == 1)
            stats['key_practice_accuracy'] = round((correct_answers / len(key_practice_sessions)) * 100, 1)
        
        if treble_sessions:
            treble_correct = sum(1 for s in treble_sessions if s['score'] and float(s['score']) == 1)
            stats['treble_accuracy'] = round((treble_correct / len(treble_sessions)) * 100, 1)
        
        if bass_sessions:
            bass_correct = sum(1 for s in bass_sessions if s['score'] and float(s['score']) == 1)
            stats['bass_accuracy'] = round((bass_correct / len(bass_sessions)) * 100, 1)
        
        # Calculate average response time
        times = [float(s['response_time_ms']) for s in key_practice_sessions 
                if s['response_time_ms'] and s['response_time_ms'].replace('.', '').isdigit()]
        if times:
            stats['avg_response_time'] = round(sum(times) / len(times), 0)
        
        # Get recent sessions (last 10, excluding session_start)
        recent = [s for s in sessions if s['type'] != 'session_start'][-10:]
        for session_data in recent:
            stats['recent_sessions'].append({
                'timestamp': session_data['timestamp'],
                'type': session_data['type'],
                'score': session_data['score'],
                'difficulty': session_data.get('difficulty', ''),
                'clef': session_data.get('clef', ''),
                'correct_answer': session_data.get('correct_answer', ''),
                'user_answer': session_data.get('user_answer', ''),
                'response_time': session_data.get('response_time_ms', ''),
                'notes': session_data.get('notes', '')
            })
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions')
def get_sessions():
    """Get session summaries for graphing."""
    try:
        sessions = []
        if os.path.exists(SESSIONS_FILE):
            with open(SESSIONS_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                sessions = list(reader)
        
        # Also get current live session data
        live_sessions = parse_csv_safely()
        key_sessions = [s for s in live_sessions if s['type'] == 'key_practice']
        
        # Group by session_id for live data
        session_groups = {}
        for s in key_sessions:
            sid = s.get('session_id', 'unknown')
            if sid not in session_groups:
                session_groups[sid] = []
            session_groups[sid].append(s)
        
        # Convert to session summaries
        for sid, questions in session_groups.items():
            if len(questions) >= 5:  # Only include substantial sessions
                correct = sum(1 for q in questions if q['score'] and float(q['score']) == 1)
                accuracy = (correct / len(questions)) * 100
                times = [float(q['response_time_ms']) for q in questions 
                        if q.get('response_time_ms') and str(q['response_time_ms']).replace('.', '').isdigit()]
                avg_time = sum(times) / len(times) if times else 0
                
                sessions.append({
                    'session_id': sid,
                    'start_time': questions[0]['timestamp'],
                    'end_time': questions[-1]['timestamp'],
                    'session_type': 'key_practice',
                    'total_questions': len(questions),
                    'correct_answers': correct,
                    'accuracy': round(accuracy, 1),
                    'avg_response_time': round(avg_time, 0),
                    'difficulty': 'mixed',
                    'clef': 'mixed'
                })
        
        return jsonify(sessions)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graph-data')
def get_graph_data():
    """Get data formatted for graphs."""
    try:
        sessions = []
        if os.path.exists(SESSIONS_FILE):
            with open(SESSIONS_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                sessions = list(reader)
        
        # Format for chart
        chart_data = []
        for i, session in enumerate(sessions):
            chart_data.append({
                'session': i + 1,
                'accuracy': float(session.get('accuracy', 0)),
                'response_time': float(session.get('avg_response_time', 0)),
                'date': session.get('start_time', '')[:10] if session.get('start_time') else ''
            })
        
        return jsonify(chart_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable (Render sets this)
    port = int(os.environ.get('PORT', 5000))
    # Run app on all interfaces for Render
    app.run(host='0.0.0.0', port=port, debug=False)