import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

def setup_advanced_system():
    """Создание продвинутой системы учёта"""

    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(os.getenv('SPREADSHEET_ID'))

    # 1. Обновляем лист Users - добавляем колонку с полным именем
    print("📝 Настройка листа Users...")
    users_sheet = spreadsheet.worksheet('Users')

    headers = users_sheet.row_values(1)
    if 'full_name' not in headers:
        users_sheet.add_cols(2)
        users_sheet.update('D1', 'full_name')
        print("✅ Добавлена колонка 'full_name' в Users")

    print("\n📋 ИНСТРУКЦИЯ:")
    print("Заполни колонку D (full_name) в листе Users для каждого сотрудника:")
    print("Пример: D2: Данияр Бокишев")
    print("        D3: Алихан Тохтаров")

    # 2. Создаём лист Employees
    try:
        mapping_sheet = spreadsheet.worksheet('Employees')
        print("\nℹ️  Лист 'Employees' уже существует")
    except:
        mapping_sheet = spreadsheet.add_worksheet(title='Employees', rows=100, cols=5)

        headers = ['telegram_id', 'username', 'full_name', 'position', 'active']
        mapping_sheet.append_row(headers)

        mapping_sheet.format('A1:E1', {
            'textFormat': {'bold': True, 'fontSize': 11},
            'backgroundColor': {'red': 0.2, 'green': 0.5, 'blue': 0.8},
            'horizontalAlignment': 'CENTER'
        })

        print("\n✅ Создан лист 'Employees'")
        print("\nЗаполни этот лист:")
        print("A2: telegram_id (из Users)")
        print("B2: username (из Users)")
        print("C2: Данияр Бокишев")
        print("D2: Разработчик (должность)")
        print("E2: TRUE (работает ли сейчас)")

    # 3. Создаём лист Schedule (график выходных)
    try:
        schedule_sheet = spreadsheet.worksheet('Schedule')
        print("\nℹ️  Лист 'Schedule' уже существует")
    except:
        schedule_sheet = spreadsheet.add_worksheet(title='Schedule', rows=500, cols=4)

        headers = ['date', 'full_name', 'type', 'note']
        schedule_sheet.append_row(headers)

        schedule_sheet.format('A1:D1', {
            'textFormat': {'bold': True, 'fontSize': 11},
            'backgroundColor': {'red': 0.9, 'green': 0.7, 'blue': 0.3},
            'horizontalAlignment': 'CENTER'
        })

        examples = [
            ['2026-03-19', 'Данияр Бокишев', 'Выходной', 'Запланированный выходной'],
            ['2026-03-20', 'Алихан Тохтаров', 'Отпуск', 'Отпуск 2 недели'],
            ['2026-03-21', 'Аброр Саиткаримов', 'Больничный', '']
        ]

        for example in examples:
            schedule_sheet.append_row(example)

        print("\n✅ Создан лист 'Schedule'")
        print("\nДобавляй сюда выходные/отпуска:")
        print("Типы: Выходной, Отпуск, Больничный, Командировка")

    # 4. ГЛАВНЫЙ ЛИСТ - Daily Report
    try:
        daily_sheet = spreadsheet.worksheet('Daily Report')
        print("\nℹ️  Лист 'Daily Report' уже существует")
    except:
        daily_sheet = spreadsheet.add_worksheet(title='Daily Report', rows=1000, cols=10)

        headers = [
            'Дата', 'ФИО', 'Должность', 'Пришёл', 'Ушёл',
            'Отработано', 'Опоздал', 'Статус', 'Примечание', 'ID'
        ]
        daily_sheet.append_row(headers)

        daily_sheet.format('A1:J1', {
            'textFormat': {'bold': True, 'fontSize': 12, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}},
            'backgroundColor': {'red': 0.1, 'green': 0.3, 'blue': 0.7},
            'horizontalAlignment': 'CENTER'
        })

        print("\n✅ Создан лист 'Daily Report'")
        print("\n📝 Добавь формулы в Daily Report (начиная со строки 2):")
        print("\nA2: дата (например: 2026-03-18)")
        print('B2: =VLOOKUP(J2,Employees!A:C,3,FALSE)')
        print('C2: =VLOOKUP(J2,Employees!A:D,4,FALSE)')
        print('D2: =IFERROR(QUERY(Logs!A:G,"SELECT D WHERE A=\'"&A2&"\' AND B="&J2&" AND G=\'check-in\' LIMIT 1"),"")')
        print('E2: =IFERROR(QUERY(Logs!A:G,"SELECT E WHERE A=\'"&A2&"\' AND B="&J2&" AND G=\'check-out\' LIMIT 1"),"")')
        print('F2: =IF(AND(D2<>"",E2<>""),TEXT(E2-D2,"[h]:mm"),"")')
        print('G2: =IF(D2="","",IF(D2>TIME(11,0,0),"Опоздал","Вовремя"))')
        print('H2: =IF(COUNTIFS(Schedule!A:A,A2,Schedule!B:B,B2)>0,INDEX(Schedule!C:C,MATCH(1,(Schedule!A:A=A2)*(Schedule!B:B=B2),0)),IF(D2="","Прогул","Работал"))')
        print('I2: =IF(COUNTIFS(Schedule!A:A,A2,Schedule!B:B,B2)>0,INDEX(Schedule!D:D,MATCH(1,(Schedule!A:A=A2)*(Schedule!B:B=B2),0)),"")')
        print("J2: telegram_id из Users")

    # 5. Условное форматирование
    print("\n\n🎨 НАСТРОЙ УСЛОВНОЕ ФОРМАТИРОВАНИЕ:")
    print("\nВ Daily Report, колонка G (Опоздал):")
    print("1. Выдели G2:G1000")
    print("2. Format → Conditional formatting")
    print("3. Если текст = 'Опоздал' → красный фон")
    print("4. Если текст = 'Вовремя' → зелёный фон")

    print("\nВ Daily Report, колонка H (Статус):")
    print("1. Выдели H2:H1000")
    print("2. Format → Conditional formatting")
    print("3. Если текст = 'Прогул' → тёмно-красный фон")
    print("4. Если текст содержит 'Выходной/Отпуск/Больничный' → голубой фон")
    print("5. Если текст = 'Работал' → светло-зелёный фон")

    print("\n\n✅ Система готова!")
    print(f"\n🔗 Открой таблицу: https://docs.google.com/spreadsheets/d/{os.getenv('SPREADSHEET_ID')}/edit")

if __name__ == '__main__':
    setup_advanced_system()
