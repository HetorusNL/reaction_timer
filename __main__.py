import logging

from reaction_timer import ReactionTimer

logging.basicConfig()


def main():
    _reaction_timer = ReactionTimer()
    _reaction_timer.run()


if __name__ == "__main__":
    main()
