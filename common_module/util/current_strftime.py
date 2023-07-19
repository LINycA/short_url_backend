from datetime import datetime

def current_strftime():
    cur_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return cur_time


if __name__ == "__main__":
    current_strftime()