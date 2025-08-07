# Import the main application
from dashboard_app import app, server

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050) 