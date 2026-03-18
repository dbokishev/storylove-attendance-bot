import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

def setup_sheets():
    """Создание структуры таблиц в Google Sheets"""

    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_file(
            'credentials.json',
            scopes=scope
        )

        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(os.getenv('SPREADSHEET_ID'))

        print("✅ Подключение к Google Sheets успешно!")

        try:
            logs_sheet = spreadsheet.worksheet('Logs')
            print("ℹ️  Лист 'Logs' уже существует")
        except:
            logs_sheet = spreadsheet.add_worksheet(title='Logs', rows=1000, cols=7)
            logs_sheet.append_row([
                'date', 'user_id', 'name', 'check_in', 'check_out', 'raw_timestamp', 'action'
            ])
            logs_sheet.format('A1:G1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            print("✅ Создан лист 'Logs'")

        try:
            users_sheet = spreadsheet.worksheet('Users')
            print("ℹ️  Лист 'Users' уже существует")
        except:
            users_sheet = spreadsheet.add_worksheet(title='Users', rows=100, cols=3)
            users_sheet.append_row(['user_id', 'name', 'username'])
            users_sheet.format('A1:C1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            print("✅ Создан лист 'Users'")

        try:
            summary_sheet = spreadsheet.worksheet('Summary')
            print("ℹ️  Лист 'Summary' уже существует")
        except:
            summary_sheet = spreadsheet.add_worksheet(title='Summary', rows=1000, cols=6)
            summary_sheet.append_row([
                'name', 'date', 'check_in', 'check_out', 'late', 'worked_hours'
            ])
            summary_sheet.format('A1:F1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            print("✅ Создан лист 'Summary'")

            print("\nℹ️  Инструкция по настройке Summary:")
            print("1. В ячейку A2 введите имя сотрудника вручную или используйте формулу")
            print("2. В ячейку B2 введите дату (ГГГГ-ММ-ДД)")
            print("3. В ячейку C2: =QUERY(Logs!A:G, \"SELECT D WHERE B=''&A2&'' AND A=''&B2&'' AND G='check-in' LIMIT 1\")")
            print("4. В ячейку D2: =QUERY(Logs!A:G, \"SELECT E WHERE B=''&A2&'' AND A=''&B2&'' AND G='check-out' LIMIT 1\")")
            print("5. В ячейку E2: =IF(C2>TIME(10,0,0), \"Late\", \"OK\")")
            print("6. В ячейку F2: =IF(AND(C2<>\"\", D2<>\"\"), D2-C2, \"\")")

        print("\n✅ Все листы настроены успешно!")
        print(f"\n🔗 Ссылка на таблицу: https://docs.google.com/spreadsheets/d/{os.getenv('SPREADSHEET_ID')}/edit")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        print("\nПроверьте:")
        print("1. Файл credentials.json находится в папке с проектом")
        print("2. SPREADSHEET_ID указан правильно в .env")
        print("3. Сервисному аккаунту дан доступ к таблице (email из credentials.json)")

if __name__ == '__main__':
    setup_sheets()
