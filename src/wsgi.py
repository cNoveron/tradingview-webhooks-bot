try:
    # Try importing from current directory (when running from src/)
    from main import app
except ImportError:
    # Try importing from src directory (when running from project root)
    from src.main import app

if __name__ == '__main__':
    app.run()