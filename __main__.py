import logging

from reaction_timer import ReactionTimer

logging.basicConfig()


def main():
    rt = ReactionTimer()
    rt.run()


if __name__ == "__main__":
    main()
