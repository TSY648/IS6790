def build_progress_steps(current_level, total_levels, complete_all=False):
    steps = []
    for order in range(1, total_levels + 1):
        if complete_all or order < current_level:
            state = 'done'
        elif order == current_level and not complete_all:
            state = 'current'
        else:
            state = 'locked'
        steps.append({'order': order, 'state': state})
    return steps
