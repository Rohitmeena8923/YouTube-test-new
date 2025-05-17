def is_admin(user_id, admin_ids):
    return user_id in admin_ids

def format_progress(current, total):
    percent = (current / total) * 100 if total else 0
    filled = int(percent // 5)
    bar = '█' * filled + '░' * (20 - filled)
    mb_done = round(current / 1024 / 1024, 2)
    mb_total = round(total / 1024 / 1024, 2)
    return f"[{bar}] {percent:.2f}%\n{mb_done}MB / {mb_total}MB"