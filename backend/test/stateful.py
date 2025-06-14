import sys

def main():
    while True:
        try:
            line = input().strip()
            if not line:  # Empty line means end of input
                break
            print(line, flush=True)  # Ensure output is flushed immediately
        except EOFError:
            break

if __name__ == "__main__":
    main()