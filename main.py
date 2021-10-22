from omegaconf import OmegaConf, DictConfig
from src.Navigator import Navigator
from src.Page import GamePage
from src.Writer import Writer


def main() -> None:
    cfg = OmegaConf.load('config.yaml')

    nav = Navigator(cfg.url_games, cfg.user_agent)

    writer = Writer(type=GamePage)
    for i, game_link in enumerate(nav):
        game = GamePage(game_link, cfg.user_agent)
        info = game.scrap()
        writer.save(info)

        if i % 25 == 0:
            print(f'Pages scraped: {i}', end='\r')


if __name__ == "__main__":
    main()
