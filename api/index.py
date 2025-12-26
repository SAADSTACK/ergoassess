"""
ErgoAssess - Vercel Serverless Entry Point
Landing page and basic API (without ML features)
"""
from flask import Flask, render_template, jsonify, send_from_directory
import os
from datetime import datetime

# Create Flask app
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ergoassess-secret-key')


@app.route('/')
def index():
    """Serve main landing page"""
    return render_template('index.html')


@app.route('/landing')
def landing():
    """Redirect to landing page"""
    return send_from_directory('../landing', 'index.html')


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'ErgoAssess API is running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'note': 'Full analysis requires desktop app. Download at /download'
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analysis endpoint - redirects to download"""
    return jsonify({
        'success': False,
        'error': 'Image analysis is not available in the web version.',
        'message': 'Please download the desktop app for full RULA/REBA analysis.',
        'download_url': 'https://github.com/SAADSTACK/ergoassess/releases'
    }), 503


@app.route('/download')
def download():
    """Download page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Download ErgoAssess</title>
        <meta http-equiv="refresh" content="0;url=https://github.com/SAADSTACK/ergoassess/releases">
    </head>
    <body>
        <p>Redirecting to downloads...</p>
    </body>
    </html>
    '''


# Vercel handler
def handler(request):
    return app(request)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
