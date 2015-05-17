from enum import Enum
from messaging.messagecontroller import *
from sensor import *
from ledcontroller import *


class GameState(Enum):
    idle = 1
    instant_game = 2
    live_game = 3


class GameController(Configurable):
    def __init__(self, logger):
        Configurable.__init__(self, 'game.ini')
        self.state = GameState.idle
        self.player1score = 0
        self.player2score = 0

        sensor_config = self.ConfigSectionMap('sensor')
        sensors = SensorController(logger)
        sensors.AddSensor(sensor_config['sensor1port'], self.player1scored, sensor_config['sensor1bounce'])
        sensors.AddSensor(sensor_config['sensor2port'], self.player2scored, sensor_config['sensor2bounce'])
        sensors.AddButton(sensor_config['greenbuttonport'], self.start_instant_game, sensor_config['greenbuttonbounce'])

        self.logger = logger
        self.game = Game()
        self.messages = MessageController(logger, self.start_live_game)
        self.led = LedController(logger)
        self.run_idle()
        logger.info("%s Initialzed", __name__)

    def start_instant_game(self, channel):
        self.game = Game()
        self.state = GameState.instant_game
        self.led.clear()
        self.logger.info("New Instant Game Started")

    def start_live_game(self, game):
        self.state = GameState.live_game
        self.game = game
        self.led.clear()
        self.logger.info("New Live Game Started between %s and %s", self.game.player1, self.game.player2)

    def player1scored(self, channel):
        if self.state != GameState.idle:
            self.game.player1Score += 1
            self.messages.send_goal_scored(self.game.id, self.game.player1)
            self.led.set_player_score(1, self.game.player1Score)
            self.logger.info("Player %s scored!", self.game.player1)
            self.has_game_ended()

    def player2scored(self, channel):
        if self.state != GameState.idle:
            self.game.player2Score += 1
            self.messages.send_goal_scored(self.game.id, self.game.player2)
            self.led.set_player_score(2, self.game.player2Score)
            self.logger.info("Player %s scored!", self.game.player2)
            self.has_game_ended()

    def has_game_ended(self):
        if self.game.player1Score == 10 or self.game.player2Score == 10:
            if self.state == GameState.live_game:
                self.messages.send_end_game(self.game)
            self.state = GameState.idle
            self.run_idle()
            self.logger.info("Game has ended!")

    def run_idle(self):
        self.led.rainbow_cycle()
