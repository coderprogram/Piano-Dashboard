import random
import uuid
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Musical constants
NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
ACCIDENTALS = ['', '#', 'b']
CLEFS = ['treble', 'bass']

# Key signatures
MAJOR_KEYS = {
    'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6,
    'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6
}

MINOR_KEYS = {
    'A': 0, 'E': 1, 'B': 2, 'F#': 3, 'C#': 4, 'G#': 5, 'D#': 6,
    'D': -1, 'G': -2, 'C': -3, 'F': -4, 'Bb': -5, 'Eb': -6
}

# Difficulty settings
DIFFICULTY_SETTINGS = {
    'beginner': {
        'time_signatures': ['4/4', '3/4'],
        'key_signatures': ['C', 'G', 'F', 'Am'],
        'note_range': ['C4', 'C5'],
        'rhythms': ['quarter', 'half', 'whole'],
        'measures': 4
    },
    'intermediate': {
        'time_signatures': ['4/4', '3/4', '2/4', '6/8'],
        'key_signatures': ['C', 'G', 'D', 'A', 'F', 'Bb', 'Em', 'Bm', 'Dm'],
        'note_range': ['C4', 'C6'],
        'rhythms': ['eighth', 'quarter', 'half', 'dotted_quarter'],
        'measures': 8
    },
    'advanced': {
        'time_signatures': ['4/4', '3/4', '2/4', '6/8', '5/4', '7/8'],
        'key_signatures': list(MAJOR_KEYS.keys()) + list(MINOR_KEYS.keys()),
        'note_range': ['C3', 'C6'],
        'rhythms': ['sixteenth', 'eighth', 'quarter', 'half', 'triplet', 'syncopated'],
        'measures': 16
    }
}

def generate_random_key():
    """Generate a random key with clef for key recognition practice."""
    note = random.choice(NOTES)
    accidental = random.choice(['', '#', 'b']) if note in ['C', 'D', 'F', 'G', 'A'] else ''
    clef = random.choice(CLEFS)
    
    # Choose appropriate octave for each clef
    if clef == 'treble':
        octave = random.choice([4, 5])  # C4 to B5 range for treble
    else:  # bass clef
        octave = random.choice([2, 3])  # C2 to B3 range for bass
    
    return {
        'note': note,
        'accidental': accidental,
        'clef': clef,
        'octave': octave,
        'display_name': f"{note}{accidental}"
    }

def check_key_answer(correct_note, user_input):
    """Check if user's key recognition answer is correct."""
    return correct_note.upper() == user_input.upper()

def generate_melody(difficulty='beginner', clef='treble'):
    """Generate a simple melody based on difficulty level."""
    settings = DIFFICULTY_SETTINGS[difficulty]
    
    # Choose random key and time signature
    key_sig = random.choice(settings['key_signatures'])
    time_sig = random.choice(settings['time_signatures'])
    measures = settings['measures']
    
    # Generate scale for the key
    scale = generate_scale(key_sig)
    
    # Generate melody notes
    melody = []
    for measure in range(measures):
        notes_in_measure = get_notes_per_measure(time_sig)
        for i in range(notes_in_measure):
            note = random.choice(scale)
            rhythm = random.choice(settings['rhythms'])
            melody.append({
                'note': note,
                'rhythm': rhythm,
                'measure': measure + 1
            })
    
    return {
        'key_signature': key_sig,
        'time_signature': time_sig,
        'clef': clef,
        'melody': melody,
        'difficulty': difficulty
    }

def generate_scale(key_signature):
    """Generate a scale for a given key signature."""
    # Simplified - just return basic scale notes
    if key_signature in ['C', 'Am']:
        return ['C', 'D', 'E', 'F', 'G', 'A', 'B']
    elif key_signature in ['G', 'Em']:
        return ['G', 'A', 'B', 'C', 'D', 'E', 'F#']
    elif key_signature in ['F', 'Dm']:
        return ['F', 'G', 'A', 'Bb', 'C', 'D', 'E']
    else:
        # Default to C major for other keys
        return ['C', 'D', 'E', 'F', 'G', 'A', 'B']

def get_notes_per_measure(time_signature):
    """Get typical number of notes per measure for time signature."""
    if time_signature == '4/4':
        return 4
    elif time_signature == '3/4':
        return 3
    elif time_signature == '2/4':
        return 2
    elif time_signature == '6/8':
        return 6
    else:
        return 4  # default

def create_practice_pdf(melody_data, filename):
    """Create a PDF of the generated melody (simplified version)."""
    c = canvas.Canvas(f"exports/{filename}", pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Music Practice Sheet")
    
    # Key and time signature info
    c.setFont("Helvetica", 12)
    y_pos = height - 100
    c.drawString(50, y_pos, f"Key: {melody_data['key_signature']}")
    c.drawString(150, y_pos, f"Time: {melody_data['time_signature']}")
    c.drawString(250, y_pos, f"Clef: {melody_data['clef'].title()}")
    c.drawString(350, y_pos, f"Difficulty: {melody_data['difficulty'].title()}")
    
    # Notes (simplified text representation)
    c.setFont("Helvetica", 10)
    y_pos -= 50
    c.drawString(50, y_pos, "Notes:")
    
    y_pos -= 30
    measure_notes = {}
    for note_data in melody_data['melody']:
        measure = note_data['measure']
        if measure not in measure_notes:
            measure_notes[measure] = []
        measure_notes[measure].append(f"{note_data['note']}({note_data['rhythm']})")
    
    for measure, notes in measure_notes.items():
        c.drawString(50, y_pos, f"Measure {measure}: {' | '.join(notes)}")
        y_pos -= 20
        if y_pos < 100:  # Start new page if needed
            c.showPage()
            y_pos = height - 50
    
    c.save()
    return filename