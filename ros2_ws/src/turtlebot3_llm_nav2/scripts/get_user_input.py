
# === File: scripts/get_user_input.py ===
def get_start_goal():
    print("Start (x y): ", end='')
    start = list(map(float, input().split()))
    print("Goal (x y): ", end='')
    goal = list(map(float, input().split()))
    return start, goal