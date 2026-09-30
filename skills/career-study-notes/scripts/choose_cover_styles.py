"""Create a reproducible, balanced initial cover-style sequence."""
import argparse
import json
import random


def choose(count, seed=None):
    if count < 1:
        raise ValueError('count must be positive')
    rng = random.Random(seed)
    styles = ['S01', 'S02', 'S03', 'S04', 'S05']
    result = []
    while len(result) < count:
        bag = styles[:]
        rng.shuffle(bag)
        if result and bag[0] == result[-1]:
            j = rng.randrange(1, len(bag))
            bag[0], bag[j] = bag[j], bag[0]
        result.extend(bag[:count-len(result)])
    return [{'id': i+1, 'style': s} for i, s in enumerate(result)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, required=True)
    parser.add_argument('--seed')
    args = parser.parse_args()
    print(json.dumps(choose(args.count, args.seed), ensure_ascii=False, indent=2))
