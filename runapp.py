from sai import app

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port, debug=True)
