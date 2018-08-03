import xlsxwriter
from telegram.ext import run_async
import tariffs

_EXCEL_DOCS_FOLDER = 'docs'


@run_async
def transactions_excel(bot, user):
    cols = {
        'Сумма': 'amount',
        'Дата': 'created_at',
    }

    withdrawals = user.withdrawals
    top_ups = user.top_ups
    deposit_transfers = user.deposit_transfers
    transfers_from = user.transfers_from
    transfers_to = user.transfers_to

    filename = f'{_EXCEL_DOCS_FOLDER}/transactions/{user.username}.xlsx'

    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    header = workbook.add_format()
    header.set_font_size(15)

    def rows_callback(prop_name, row, col, model):
        if prop_name == 'created_at':
            worksheet.write(row, col, model.created_at.strftime("%d/%m/%y"))
        else:
            worksheet.write(row, col, getattr(model, prop_name))

    row = 0
    worksheet.write(row, 0, 'Выводы', header)
    row += 1

    row = _write_models_to_excel(withdrawals, cols, worksheet, bold, row, rows_callback)
    row += 1
    worksheet.write(row, 0, 'Пополнения', header)
    row += 1
    row = _write_models_to_excel(top_ups, cols, worksheet, bold, row, rows_callback)
    row += 1
    worksheet.write(row, 0, 'Переводы в депозит', header)
    row += 1
    row = _write_models_to_excel(deposit_transfers, cols, worksheet, bold, row, rows_callback)
    row += 1
    worksheet.write(row, 0, 'Переводы другим пользователям', header)
    row += 1
    row = _write_models_to_excel(transfers_from, cols, worksheet, bold, row, rows_callback)
    row += 1
    worksheet.write(row, 0, 'Переводы вам от других пользователей', header)
    row += 1
    row = _write_models_to_excel(transfers_to, cols, worksheet, bold, row, rows_callback)

    workbook.close()
    bot.send_document(chat_id=user.chat_id, document=open(filename, 'rb'))


@run_async
def partners_excel(bot, user):
    cols = {
        'Телеграм username': 'username',
        'Имя': 'first_name',
        'Фамилия': 'last_name',
        'Депозит': 'deposit',
        'Дата регистрации': 'created_at'
    }

    partners_list = user.partners_per_levels
    filename = f'{_EXCEL_DOCS_FOLDER}/partners/{user.username}.xlsx'

    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    row = 0
    level_number = 0
    total_partners_reward = 0
    for level in partners_list:
        if not row == 0:
            row += 2
        worksheet.write(row, 0, f'{level_number + 1} реферальный уровень', bold)
        row += 1
        col = 0
        for field in cols.keys():
            worksheet.write(row, col, field, bold)
            col += 1
        row += 1
        col = 0
        levels_percentage = tariffs.get_referral_levels_percentage()
        for partner in level:
            for prop_name in cols.values():
                if prop_name == 'created_at':
                    worksheet.write(row, col, partner.created_at.strftime("%d/%m/%y"))
                else:
                    worksheet.write(row, col, getattr(partner, prop_name))
                col += 1
            row += 1
            col = 0
        level_number += 1
    row += 1
    col = 0
    worksheet.write(row, col, 'Суммарный заработок с партнёров', bold)
    col += 1
    worksheet.write(row, col, total_partners_reward)
    workbook.close()

    bot.send_document(chat_id=user.chat_id, document=open(filename, 'rb'))


def _write_models_to_excel(models, cols, worksheet, bold, row_start_with, callback):
    row = row_start_with
    col = 0

    for field in cols.keys():
        worksheet.write(row, col, field, bold)
        col += 1
    row += 1
    col = 0
    for model in models:
        for prop_name in cols.values():
            callback(prop_name, row, col, model)
            col += 1
        row += 1
        col = 0
    return row
