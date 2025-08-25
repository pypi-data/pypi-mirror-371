"""
Main entry point for the trading bot package
"""
import sys
import argparse
from pathlib import Path

def main():
    """Main entry point for the trading bot CLI"""
    parser = argparse.ArgumentParser(description='Trading Bot ML Package')
    parser.add_argument('--version', action='version', version='1.0.0')
    parser.add_argument('--train', action='store_true', help='Start training pipeline')
    parser.add_argument('--inference', action='store_true', help='Start inference service')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    parser.add_argument('--config', type=str, help='Config file path')
    
    args = parser.parse_args()
    
    if args.train:
        try:
            from arbi.ai.training_v2 import main as train_main
            train_main()
        except ImportError:
            print("Training module not available. Run: pip install trading-bot-ml[ml-extra]")
            sys.exit(1)
    elif args.inference:
        try:
            from arbi.api.server import main as server_main
            server_main()
        except ImportError:
            print("API server not available.")
            sys.exit(1)
    elif args.demo:
        try:
            from demo import main as demo_main
            demo_main()
        except ImportError:
            print("Demo not available.")
            sys.exit(1)
    else:
        print("Trading Bot ML Package v1.0.0")
        print("Usage: trading-bot [--train|--inference|--demo] [--config CONFIG_FILE]")
        print("For help: trading-bot --help")

if __name__ == '__main__':
    main()
