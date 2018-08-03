from decimal import Decimal
import config
import tariffs
from models import User


def reward_users(bot, job):
    levels_percentage = tariffs.get_referral_levels_percentage()
    deposit_reward = User.deposit * User.deposit_reward
    query = User.update(
        balance=(
                User.balance
                + User.deposit * User.deposit_reward
                + User.first_level_partners_deposit * User.deposit_reward * levels_percentage[0]
                + User.second_level_partners_deposit * User.deposit_reward * levels_percentage[1]
                + User.third_level_partners_deposit * User.deposit_reward * levels_percentage[2]
        ),
        sum_deposit_reward=User.sum_deposit_reward + deposit_reward
    ).where(User.deposit >= tariffs.eth_minimal_deposit())
    query.execute()

    users = User.select().where(User.deposit >= tariffs.eth_minimal_deposit())

    for user in users:
        reward = user.deposit * user.deposit_reward \
                 + user.first_level_partners_deposit * levels_percentage[0] \
                 + user.second_level_partners_deposit * levels_percentage[1] \
                 + user.third_level_partners_deposit * levels_percentage[2]
        bot.send_message(
            chat_id=user.chat_id,
            text=f'Вы получили начислений на сумму {reward:.7f} ETH'
        )
