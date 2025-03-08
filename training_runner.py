# training_runner.py
import sys
from husmorph.model import init_training  # Replace with your actual module name

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python training_runner.py <xml_file> <save_path> <threads> <n_trials>")
        sys.exit(1)
    xml_file = sys.argv[1]
    save_path = sys.argv[2]
    threads = int(sys.argv[3])
    n_trials = int(sys.argv[4])
    # Call your training function.
    init_training(xml_file, save_path, threads, n_trials)
