
from board import *
import random
import os

MAX_SIGMA = 0.0000001

PROB = [[0.8, 0.1, 0, 0.1],
        [0.1, 0.8, 0.1, 0],
        [0, 0.1, 0.8, 0.1],
        [0.1, 0, 0.1, 0.8]]

MOVE = [[-1, 0], [0, 1], [1, 0], [0, -1]]

DIR = [Ops.UP, Ops.RIGHT, Ops.DOWN, Ops.LEFT]

VALID_TILE = ['P', 'N', 'B', 'R']

TERMINATE_TILE = ['P', 'N']

NOTATION = {Ops.UP: '^', Ops.DOWN: 'V', Ops.LEFT: '<', Ops.RIGHT: '>', Ops.BLOCK: 'X'}


def value_iterate(board, gamma):

    """ Implement value iterate algorithm, param board is a Board
    instance which represents the environment, gamma is float as Gamma """
    height = board.height
    width = board.width
    util = Utility(height, width)
    util_star = Utility(height, width)

    sigma = 1
    while sigma > MAX_SIGMA:
        sigma = 0

        for x in range(height):
            for y in range(width):

                util_star.value[x][y] = board.reward[x][y]
                if board.board[x][y] != 'B' and board.board[x][y] != 'R':
                    continue

                max_reward = -float('Inf')
                for prob in PROB:
                    expected_reward = get_expected_reward(prob, x, y, util, board)
                    if expected_reward > max_reward + 0.00001:
                        max_reward = expected_reward

                util_star.value[x][y] += max_reward * gamma
                sigma = max(sigma, abs(util_star.value[x][y] - util.value[x][y]))

        tmp = util
        util = util_star
        util_star = tmp

    # Generate optimal policy
    p = Policy(height, width)

    for x in range(height):
        for y in range(width):

            if board.board[x][y] in TERMINATE_TILE:
                p.policy[x][y] = Ops.TERMINATE
            elif board.board[x][y] not in VALID_TILE:
                p.policy[x][y] = Ops.BLOCK
            else:
                max_reward = -float('Inf')
                for k in range(len(PROB)):
                    expected_reward = get_expected_reward(PROB[k], x, y, util, board)
                    if expected_reward > max_reward:
                        max_reward = expected_reward
                        p.policy[x][y] = DIR[k]

    return p, util


def get_expected_reward(probs, x, y, util, board):

    expected_reward = 0
    for k in range(len(probs)):
        prob = probs[k]
        next_x = x + MOVE[k][0]
        next_y = y + MOVE[k][1]
        if valid_move(board, next_x, next_y):
            expected_reward += prob * util.value[next_x][next_y]
        else:
            expected_reward += prob * util.value[x][y]

    return expected_reward


def valid_move(board, x, y):

    if x < 0 or x >= board.height:
        return False
    if y < 0 or y >= board.width:
        return False
    if board.board[x][y] not in VALID_TILE:
        return False
    return True


def print_policy(p, prev_p, b, notation, file):

    for x in range(b.height):
        for y in range(b.width):
            if p.policy[x][y] == Ops.TERMINATE:
                file.write(str(b.reward[x][y]))
            else:
                file.write(notation[p.policy[x][y]])

            if prev_p is not None and p.policy[x][y] != prev_p.policy[x][y]:
                file.write('*')

            file.write('\t')

        file.write('\n')
    file.write('\n')


def print_utility(util, file):

    for row in util.value:
        for element in row:
            #f = lambda x, n: round(x, n - len(str(int(x))));
            file.write('{:>7}'.format(round(element, 3)))
        file.write('\n')
    file.write('\n')


def monte_carlo(board, policy, x, y):
    reward = 0
    while board.board[x][y] not in TERMINATE_TILE:
        reward += board.reward[x][y]
        i = DIR.index(policy.policy[x][y])

        x, y = move(board, PROB[i], x, y)

    return reward + board.reward[x][y]


def move(board, prob, x, y):
    r = random.uniform(0, 1)
    for i in range(len(prob)):
        r -= prob[i]
        if r < 0.00001:
            if valid_move(board, x + MOVE[i][0], y + MOVE[i][1]):
                return x + MOVE[i][0], y + MOVE[i][1]
            else:
                return x, y
    return 0, 0


def problem_1(board, output):
    accuracy = 10000
    upper = 0
    lower = -20000

    reward = {'P': 1, 'N': -1, 'X': 0, 'B': 1.0 * upper / accuracy}
    board.set_reward(reward)
    p, _ = value_iterate(board, 1)
    start = upper

    while start > lower:
        right = start-1
        left = lower
        mid = (right + left) / 2

        while left <= right:
            reward['B'] = 1.0 * mid / accuracy
            board.set_reward(reward)
            q, _ = value_iterate(board, 1)
            if q.equals(p):
                right = mid - 1
            else:
                left = mid + 1

            mid = (right + left) / 2

        reward['B'] = 1.0 * right / accuracy
        board.set_reward(reward)
        next_p, _ = value_iterate(board, 1)
        if not next_p.equals(p):
            output.write(str(1.0 * left / accuracy))
            output.write('\n')
            print_policy(next_p, p, board, NOTATION, output)

        p = next_p

        start = right


def problem_2(board, output, n, x, y):
    rewards = []
    opt_policy, _ = value_iterate(board, 1)
    for _ in range(n):
        rewards.append(monte_carlo(board, opt_policy, x, y))

    for item in rewards:
        output.write(str(item) + '\n')



def problem_3(board, output):
    accuracy = 100000
    upper = 99000
    lower = 0
    start = upper

    p, _ = value_iterate(board, 1.0 * start / accuracy)

    print_policy(p, None, board, NOTATION, output)

    while start > lower:
        left = lower
        right = start - 1
        mid = (left + right) / 2
        while left <= right:
            q, _ = value_iterate(board, 1.0 * mid / accuracy)
            if q.equals(p):
                right = mid - 1
            else:
                left = mid + 1
            mid = (left + right) / 2

        p_next, util = value_iterate(board, 1.0 * right / accuracy)

        if p_next != p and left != 0:

            print_utility(util, output)
            output.write(str(1.0 * left / accuracy) + '\n\n')
            print_policy(p_next, p, board, NOTATION, output)

        p = p_next

        start = right


if not os.path.exists("generated"):
    os.makedirs("generated")

# Problem 1

board_1 = Board("board_1")

f = open('generated/P1-output.txt', 'w')
problem_1(board_1, f)
f.close()

# Problem 2
f = open('generated/P2-output.txt', 'w')
board_2 = Board("board_1")
board_2.set_reward({'P': 1, 'N': -1, 'X': 0, 'B': -0.04})
_, util = value_iterate(board_2, 1)
print_utility(util, f)
f.close()

f = open('generated/P2-data-10.txt', 'w')
problem_2(board_2, f, 10, 2, 3)
f.close()

f = open('generated/P2-data-100.txt', 'w')
problem_2(board_2, f, 100, 2, 3)
f.close()

f = open('generated/P2-data-1000.txt', 'w')
problem_2(board_2, f, 1000, 2, 3)
f.close()


# Problem 3
board_3 = Board("board_3")
board_3.set_reward({'P': 10, 'R': 3, 'B': -1})

f = open('generated/P3-output.txt', 'w')
problem_3(board_3, f)
f.close()