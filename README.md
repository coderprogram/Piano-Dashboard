# 🎹 Piano Practice App

A Flask web application for practicing piano key recognition and sight reading with progress tracking and interactive charts.

## 🌟 Features

- **🎹 Key Recognition Practice**: Identify notes on treble and bass clef with response time tracking
- **📖 Sight Reading Generator**: Create custom exercises with adjustable difficulty levels
- **📊 Progress Tracking**: Monitor accuracy, response times, and improvement over time
- **⚙️ Interactive Statistics**: Detailed stats modal with progress charts
- **🌙 Dark Mode**: Toggle between light and dark themes
- **📱 Mobile Responsive**: Works great on all devices
- **📄 PDF Export**: Generate and download practice sheets
- **⏱️ Session Management**: 10-key practice sessions with completion tracking

## 🚀 Live Demo

**Live App**: [https://piano-practice-app.onrender.com](https://piano-practice-app.onrender.com)

## 📦 Installation

### Local Development

1. **Clone the repository**:
```bash
git clone https://github.com/YOUR_USERNAME/piano-practice-app.git
cd piano-practice-app
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run data migration** (if using existing data):
```bash
python data_migration.py
```

4. **Start the application**:
```bash
python app.py
```

5. **Open your browser** to `http://localhost:5000`

### Quick Deployment Check

Run the preparation script to ensure everything is ready:
```bash
python prepare_deployment.py
```

## 🌐 Deployment to Render

### Prerequisites
- GitHub account
- Git installed locally

### Steps
1. **Push to GitHub**:
```bash
git add .
git commit -m "Ready for deployment"
git push
```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Render auto-detects configuration from `render.yaml`
   - Deploy! (takes 2-5 minutes)

3. **Your app will be live** at: `https://your-app-name.onrender.com`

See the detailed [Render Deployment Guide](Render_Deployment_Guide.md) for complete instructions.

## 📁 Project Structure

```
piano-practice/
├── app.py                      # Main Flask application
├── music_utils.py              # Music theory and PDF generation
├── data_migration.py           # Data migration script
├── prepare_deployment.py       # Deployment preparation
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── templates/                  # HTML templates
│   ├── index.html              # Homepage with stats
│   ├── key_practice.html       # Key recognition practice
│   └── sight_reading.html      # Sight reading generator
├── static/                     # Static assets
│   ├── style.css               # Styles with dark mode
│   └── script.js               # JavaScript + VexFlow integration
├── data.csv                    # Practice data (auto-generated)
├── sessions.csv               # Session summaries (auto-generated)
└── exports/                   # Generated PDFs
```

## 🎮 Usage

### Key Recognition Practice
1. Click "Start Practice" to begin a 10-key session
2. Look at the note on the staff and press the corresponding letter key (C, D, E, F, G, A, B)
3. Track your accuracy and response times in real-time
4. Complete sessions to unlock progress charts

### Sight Reading
1. Choose difficulty level (Beginner/Intermediate/Advanced) and clef
2. Generate custom melodies with various key signatures and time signatures
3. Export practice sheets as PDFs for offline practice

### Statistics & Progress
1. Click the ⚙️ gear icon to view detailed statistics
2. See interactive charts showing improvement over time
3. Track accuracy by clef (treble vs bass)
4. Monitor response time trends
5. Export progress charts as images

## 🛠️ Technologies Used

- **Backend**: Flask (Python), ReportLab (PDF generation)
- **Frontend**: HTML5, CSS3 (with CSS Variables for theming), JavaScript
- **Music Notation**: VexFlow.js
- **Charts**: Chart.js
- **Data Storage**: CSV files with session management
- **Deployment**: Render (with auto-deploy from GitHub)

## 📊 Data Tracking

The app tracks comprehensive statistics:
- Individual key recognition attempts with response times
- Session summaries (10 keys each)
- Daily aggregated statistics
- Clef-specific performance metrics
- Progress trends over time

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **VexFlow** for music notation rendering
- **Chart.js** for interactive progress charts
- **Render** for free hosting platform
- **ReportLab** for PDF generation

---

**🎵 Happy practicing!** 🎹