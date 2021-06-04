import os
import datetime
import threading
import logging
# import telebot

from odoo import models, fields, api

from pydoc import locate

# # import openerp.tools.config as config
# from odoo import models, fields, api
# from openerp.modules import module
# from openerp.service.server import ThreadedServer

# BOT = None

# start_bak = ThreadedServer.start

class TelegramBot(models.Model):
    _name = "sincro_data_base.telegram_bot"
    _description = "Sincro Data Telegram bot"

    active_bot = fields.Boolean("ACtive")

    @api.depends("active_bot")
    def run_bot(self):
        s =2
        # bot = telebot.TeleBot('1781624098:AAFa7LIEPqLiSq9MZPwchdzxrwl07olNP2M')

        #
        # @bot.message_handler(commands=['start', 'help'])
        # def send_welcome(message):
        #     bot.reply_to(message, "Howdy, how are you doing?")
        #
        # @bot.message_handler(func=lambda message: True)
        # def echo_all(message):
        #     bot.reply_to(message, message.text)

        # bot.polling()
    # def telegram_thread(bot, telegram_none_stop, telegram_interval,
    #                     telegram_timeout):
    #     _logger.debug(
    #         "telegram_thread:: "
    #         "bot = %r | "
    #         "telegram_none_stop = %r | "
    #         "telegram_interval = %r | "
    #         "telegram_timeout = %r" % (
    #             bot,
    #             telegram_none_stop,
    #             telegram_interval,
    #             telegram_timeout
    #         )
    #     )
    #
    #     def listener(messages):
    #         for m in messages:
    #             _logger.debug('listener = %r' % (m))
    #
    #     bot.set_update_listener(listener)
    #     bot.polling(
    #         none_stop=bool(telegram_none_stop),
    #         interval=int(telegram_interval),
    #         timeout=int(telegram_timeout))
    #
    #
    # def telegram_spawn(self):
    #     global BOT
    #     datetime.datetime.strptime('2012-01-01', '%Y-%m-%d')
    #     #
    #     # telegram_apikey = config.get('telegram_apikey')
    #     # telegram_none_stop = config.get('telegram_none_stop', False)
    #     # telegram_interval = config.get('telegram_interval', 0)
    #     # telegram_timeout = config.get('telegram_timeout', True)
    #     telegram_apikey = '1781624098:AAFa7LIEPqLiSq9MZPwchdzxrwl07olNP2M'
    #     telegram_none_stop = False
    #     telegram_interval = 0
    #     telegram_timeout = True
    #     if telegram_apikey:
    #         # _logger.debug("telebot.logger = %s" %
    #         # telebot.logger.setLevel(logging.ERROR)
    #         # _logger.debug("telebot.logger = %s" % (telebot.logger))
    #         BOT = telebot.TeleBot(telegram_apikey, threaded=False)
    #
    #         # Handlers discovery
    #         try:
    #             _logger.debug("handlers discovery...")
    #             for m in module.get_modules():
    #                 m_path = module.get_module_path(m)
    #                 if os.path.isdir(os.path.join(m_path, 'telegram')):
    #                     _logger.debug("telegram handlers on path %r" % (
    #                         os.path.join(m_path, 'telegram')))
    #                     TelegramBotHandlers = locate(
    #                         'openerp.addons.' + m + '.telegram.handlers.TelegramBotHandlers')
    #                     TelegramBotHandlers(BOT).handle()
    #                     _logger.debug('imported!')
    #         except Exception as e:
    #             _logger.error(e)
    #             raise e
    #
    #         def target():
    #             self.telegram_thread(
    #                 BOT, telegram_none_stop, telegram_interval, telegram_timeout)
    #
    #         t = threading.Thread(target=target, name="openerp.service.telegrambot")
    #         t.setDaemon(True)
    #         t.start()
    #         _logger.debug('ThreadedServer:: telegram-bot started!')
    #     else:
    #         _logger.warning(
    #             "Telegram server not started! Please specify an bot api key!")
    #
    #
    # def new_start(self, stop=False):
    #     telegram_apikey = '1781624098:AAFa7LIEPqLiSq9MZPwchdzxrwl07olNP2M'
    #     if telegram_apikey and not stop:
    #         self.telegram_spawn()
    #     start_bak(self, stop=stop)
    #
    #
    # ThreadedServer.start = new_start