import os
import logging

# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to console
    ]
)

# Default tags for initial apps
DEFAULT_TAGS = {
    'cashgiraffe.app': {
        'bug': ['crash', 'bug', 'error', 'glitch', 'freeze', 'not working', 'broken'],
        'feature-request': ['add', 'wish', 'feature', 'please include', 'need', 'want'],
        'ui': ['interface', 'design', 'layout', 'look', 'navigation', 'confusing'],
        'performance': ['slow', 'lag', 'fast', 'speed', 'loading', 'delay'],
        'payment': ['payment', 'payout', 'money', 'cash', 'withdraw', 'transaction', 'paid'],
        'rewards': ['reward', 'points', 'bonus', 'earn', 'incentive', 'credit'],
        'gameplay': ['game', 'level', 'task', 'challenge', 'play', 'mission', 'quest'],
        'difficulty': ['difficult', 'hard', 'easy', 'challenging', 'tough', 'simple'],
        'fun': ['fun', 'enjoy', 'enjoyable', 'entertaining', 'awesome'],
        'scam': ['scam', 'fake', 'fraud', 'not paying', 'cheat'],
        'positive': ['great', 'awesome', 'love', 'excellent', 'amazing', 'fantastic'],
        'negative': ['bad', 'terrible', 'hate', 'awful', 'horrible', 'disappointed']
    },
    'com.whatsapp': {
        'privacy': ['privacy', 'secure', 'encryption', 'data', 'leak'],
        'chat': ['chat', 'message', 'group', 'conversation', 'talk'],
        'call': ['call', 'voice', 'video', 'audio', 'ring'],
        'connection': ['connection', 'network', 'offline', 'internet', 'disconnected'],
        'notification': ['notification', 'alert', 'ping', 'sound', 'silent'],
        'media': ['photo', 'video', 'file', 'share', 'attachment'],
        'bug': ['crash', 'bug', 'error', 'glitch', 'freeze'],
        'feature-request': ['add', 'wish', 'feature', 'need', 'want'],
        'ui': ['interface', 'design', 'layout', 'navigation'],
        'performance': ['slow', 'lag', 'speed', 'loading'],
        'positive': ['great', 'awesome', 'love', 'excellent'],
        'negative': ['bad', 'terrible', 'hate', 'awful']
    }
}

# Determine the absolute path to reviews.db
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'reviews.db')
