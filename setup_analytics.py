import gspread
from google.oauth2.service_account import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

def setup_analytics():
    """Создание листов с аналитикой"""

    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    creds = Credentials.from_service_account_file('credentials.json', scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(os.getenv('SPREADSHEET_ID'))

    # Лист: Месячная статистика
    try:
        monthly_sheet = spreadsheet.worksheet('Monthly Stats')
        print("ℹ️  Лист 'Monthly Stats' уже существует")
    except:
        monthly_sheet = spreadsheet.add_worksheet(title='Monthly Stats', rows=100, cols=10)

        headers = [
            'Месяц', 'Сотрудник', 'Рабочих дней', 'Опозданий',
            'Опозданий %', 'Всего часов', 'Средние часы/день',
            'Мин часов', 'Макс часов', 'Статус'
        ]
        monthly_sheet.append_row(headers)

        monthly_sheet.format('A1:J1', {
            'textFormat': {'bold': True, 'fontSize': 11},
            'backgroundColor': {'red': 0.2, 'green': 0.4, 'blue': 0.7},
            'horizontalAlignment': 'CENTER'
        })

        print("✅ Создан лист 'Monthly Stats'")
        print("\nДобавь формулы в Monthly Stats (начиная со строки 2):")
        print('A2: =TEXT(TODAY(),"YYYY-MM") - текущий месяц')
        print("B2: Имя сотрудника")
        print('C2: =COUNTIFS(Summary!$A:$A,B2,Summary!$B:$B,">="&DATE(YEAR(A2&"-01"),MONTH(A2&"-01"),1),Summary!$B:$B,"<="&EOMONTH(A2&"-01",0),Summary!$C:$C,"<>")')
        print('D2: =COUNTIFS(Summary!$A:$A,B2,Summary!$B:$B,">="&DATE(YEAR(A2&"-01"),MONTH(A2&"-01"),1),Summary!$B:$B,"<="&EOMONTH(A2&"-01",0),Summary!$E:$E,"Late")')
        print('E2: =IF(C2>0,ROUND(D2/C2*100,1)&"%","0%")')
        print('F2: =SUMIFS(Summary!$F:$F,Summary!$A:$A,B2,Summary!$B:$B,">="&DATE(YEAR(A2&"-01"),MONTH(A2&"-01"),1),Summary!$B:$B,"<="&EOMONTH(A2&"-01",0))')
        print("G2: =IF(C2>0,F2/C2,0)")
        print('H2: =MINIFS(Summary!$F:$F,Summary!$A:$A,B2,Summary!$B:$B,">="&DATE(YEAR(A2&"-01"),MONTH(A2&"-01"),1),Summary!$B:$B,"<="&EOMONTH(A2&"-01",0),Summary!$F:$F,">0")')
        print('I2: =MAXIFS(Summary!$F:$F,Summary!$A:$A,B2,Summary!$B:$B,">="&DATE(YEAR(A2&"-01"),MONTH(A2&"-01"),1),Summary!$B:$B,"<="&EOMONTH(A2&"-01",0))')
        print('J2: =IF(E2>20,"⚠️ Много опозданий",IF(G2<7,"⚠️ Мало часов","✅ OK"))')

    # Лист: Недельная статистика
    try:
        weekly_sheet = spreadsheet.worksheet('Weekly Stats')
        print("ℹ️  Лист 'Weekly Stats' уже существует")
    except:
        weekly_sheet = spreadsheet.add_worksheet(title='Weekly Stats', rows=200, cols=8)

        headers = [
            'Неделя начало', 'Неделя конец', 'Сотрудник',
            'Рабочих дней', 'Опозданий', 'Всего часов',
            'Средние часы/день', 'Статус'
        ]
        weekly_sheet.append_row(headers)

        weekly_sheet.format('A1:H1', {
            'textFormat': {'bold': True, 'fontSize': 11},
            'backgroundColor': {'red': 0.3, 'green': 0.6, 'blue': 0.5},
            'horizontalAlignment': 'CENTER'
        })

        print("✅ Создан лист 'Weekly Stats'")
        print("\nДобавь формулы в Weekly Stats (начиная со строки 2):")
        print("A2: Дата начала недели (понедельник)")
        print("B2: =A2+6")
        print("C2: Имя сотрудника")
        print('D2: =COUNTIFS(Summary!$A:$A,C2,Summary!$B:$B,">="&A2,Summary!$B:$B,"<="&B2,Summary!$C:$C,"<>")')
        print('E2: =COUNTIFS(Summary!$A:$A,C2,Summary!$B:$B,">="&A2,Summary!$B:$B,"<="&B2,Summary!$E:$E,"Late")')
        print('F2: =SUMIFS(Summary!$F:$F,Summary!$A:$A,C2,Summary!$B:$B,">="&A2,Summary!$B:$B,"<="&B2)')
        print("G2: =IF(D2>0,F2/D2,0)")
        print('H2: =IF(D2<5,"⚠️ Мало дней",IF(F2<35,"⚠️ Мало часов","✅ OK"))')

    # Лист: Дашборд
    try:
        dashboard = spreadsheet.worksheet('Dashboard')
        print("ℹ️  Лист 'Dashboard' уже существует")
    except:
        dashboard = spreadsheet.add_worksheet(title='Dashboard', rows=50, cols=10)

        dashboard.update('A1', [['📊 DASHBOARD - СТАТИСТИКА ПОСЕЩАЕМОСТИ']])
        dashboard.merge_cells('A1:J1')
        dashboard.format('A1:J1', {
            'textFormat': {'bold': True, 'fontSize': 16},
            'backgroundColor': {'red': 0.1, 'green': 0.1, 'blue': 0.3},
            'horizontalAlignment': 'CENTER'
        })

        dashboard.update('A3', [['ТЕКУЩИЙ МЕСЯЦ']])
        dashboard.merge_cells('A3:E3')
        dashboard.format('A3:E3', {
            'textFormat': {'bold': True, 'fontSize': 12},
            'backgroundColor': {'red': 0.8, 'green': 0.8, 'blue': 0.8}
        })

        metrics = [
            ['Метрика', 'Значение', '', 'Метрика', 'Значение'],
            ['Всего сотрудников', '=COUNTA(UNIQUE(Users!B:B))-1', '', 'Отработано дней', '=COUNTA(Summary!B:B)-1'],
            ['Сегодня пришло', '=COUNTIF(Logs!A:A,TODAY())', '', 'Всего опозданий', '=COUNTIF(Summary!E:E,"Late")'],
            ['Опозданий сегодня', '=COUNTIFS(Logs!A:A,TODAY(),Logs!G:G,"check-in",Logs!D:D,">11:00")', '', '% опозданий', '=IF(COUNTA(Summary!B:B)>1,ROUND(COUNTIF(Summary!E:E,"Late")/(COUNTA(Summary!B:B)-1)*100,1)&"%","0%")']
        ]
        dashboard.update('A5', metrics)

        dashboard.format('A5:B5', {'textFormat': {'bold': True}})
        dashboard.format('D5:E5', {'textFormat': {'bold': True}})

        dashboard.update('A11', [['🏆 ТОП СОТРУДНИКИ (БЕЗ ОПОЗДАНИЙ)']])
        dashboard.merge_cells('A11:E11')
        dashboard.format('A11:E11', {
            'textFormat': {'bold': True, 'fontSize': 12},
            'backgroundColor': {'red': 0.6, 'green': 0.8, 'blue': 0.6}
        })

        dashboard.update('A12', [['Место', 'Сотрудник', 'Рабочих дней', 'Опозданий', 'Часов']])
        dashboard.format('A12:E12', {'textFormat': {'bold': True}})

        print("✅ Создан лист 'Dashboard'")
        print("\nДобавь формулы для рейтинга лучших сотрудников в Dashboard (A13-E15)")

    print("\n✅ Все листы аналитики созданы!")
    print(f"\n🔗 Открой таблицу: https://docs.google.com/spreadsheets/d/{os.getenv('SPREADSHEET_ID')}/edit")

if __name__ == '__main__':
    setup_analytics()
