# Настройка аналитики в Google Sheets

## Лист Summary - автоматическая сводка

После того как бот начнёт записывать данные в Logs, настрой Summary для анализа.

---

## Структура Summary

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| name | date | check_in | check_out | late | worked_hours |

---

## Как заполнять вручную (для начала)

### Строка 2 (первый сотрудник):
- **A2**: впиши имя сотрудника (например: Daniyar)
- **B2**: впиши дату (например: 2026-03-18)
- **C2-F2**: вставь формулы (см. ниже)

---

## Формулы для автоматического расчёта

### C2 - Время прихода (check_in)
```
=QUERY(Logs!A:G, "SELECT D WHERE B='"&A2&"' AND A='"&B2&"' AND G='check-in' LIMIT 1")
```

**Что делает:**
- Ищет в листе Logs запись с check-in для данного user_id и даты
- Возвращает время из колонки D (check_in)

---

### D2 - Время ухода (check_out)
```
=QUERY(Logs!A:G, "SELECT E WHERE B='"&A2&"' AND A='"&B2&"' AND G='check-out' LIMIT 1")
```

**Что делает:**
- Ищет в листе Logs запись с check-out для данного user_id и даты
- Возвращает время из колонки E (check_out)

---

### E2 - Опоздание (late)
```
=IF(C2>TIME(10,0,0), "Late", "OK")
```

**Что делает:**
- Если время прихода > 10:00 -> "Late"
- Иначе -> "OK"

**Для изменения времени начала:**
- Замени `TIME(10,0,0)` на `TIME(9,30,0)` для 9:30
- Формат: `TIME(часы, минуты, секунды)`

---

### F2 - Отработанные часы (worked_hours)
```
=IF(AND(C2<>"", D2<>""), D2-C2, "")
```

**Что делает:**
- Если есть и приход, и уход -> вычисляет разницу
- Иначе -> пустая ячейка

**Для формата времени:**
1. Выдели ячейку F2
2. Format -> Number -> Duration

---

## Автоматическое заполнение имён

### Вместо ручного ввода имён, используй формулу в A2:

```
=UNIQUE(Logs!C:C)
```

Это создаст список уникальных имён из Logs.

### Для дат можно использовать:

```
=UNIQUE(Logs!A:A)
```

---

## Продвинутая аналитика

### Подсчёт опозданий за месяц

В отдельной ячейке:
```
=COUNTIF(E:E, "Late")
```

### Средние часы работы

```
=AVERAGE(F:F)
```

### Количество рабочих дней

```
=COUNTA(B:B)-1
```
(минус 1 для исключения заголовка)

---

## Автоматический отчёт по неделям

### Создай новый лист "Weekly Report":

| Week | Name | Days Worked | Late Count | Avg Hours |

### Формулы:

**Days Worked:**
```
=COUNTIFS(Summary!B:B, ">="&A2, Summary!B:B, "<="&B2, Summary!A:A, C2)
```

**Late Count:**
```
=COUNTIFS(Summary!B:B, ">="&A2, Summary!B:B, "<="&B2, Summary!A:A, C2, Summary!E:E, "Late")
```

---

## Визуализация (графики)

### График посещаемости:

1. Выдели колонку B (даты) и E (late/OK)
2. Insert -> Chart
3. Chart type: Column chart
4. Настрой цвета: OK = зелёный, Late = красный

### График часов работы:

1. Выдели B (даты) и F (worked_hours)
2. Insert -> Chart
3. Chart type: Line chart

---

## Автоматизация для новых строк

### Проблема:
Каждый раз нужно копировать формулы вниз для новых дат.

### Решение 1: ARRAYFORMULA (продвинутое)

В C2 вместо обычной формулы:
```
=ARRAYFORMULA(IF(ROW(A:A)=1, "check_in", IF(A:A="", "",
  QUERY(Logs!A:G, "SELECT D WHERE B='"&A:A&"' AND A='"&B:B&"' AND G='check-in' LIMIT 1"))))
```

### Решение 2: Google Apps Script (автоматизация)

1. В таблице: Extensions -> Apps Script
2. Вставь код:

```javascript
function onEdit(e) {
  var sheet = e.source.getActiveSheet();

  if (sheet.getName() == "Summary") {
    var row = e.range.getRow();

    if (row > 2) {
      var formulas = sheet.getRange("C2:F2").getFormulas();
      sheet.getRange(row, 3, 1, 4).setFormulas(formulas);
    }
  }
}
```

3. Save -> закрой

Теперь при добавлении новой строки формулы скопируются автоматически!

---

## Пример готовой таблицы

### Summary должен выглядеть так:

| name | date | check_in | check_out | late | worked_hours |
|------|------|----------|-----------|------|--------------|
| Daniyar | 2026-03-18 | 09:05:00 | 18:30:00 | OK | 09:25:00 |
| Daniyar | 2026-03-19 | 10:15:00 | 18:00:00 | Late | 07:45:00 |
| Aliya | 2026-03-18 | 09:00:00 | 17:30:00 | OK | 08:30:00 |

---

## Условное форматирование

### Выделить опоздания красным:

1. Выдели колонку E (late)
2. Format -> Conditional formatting
3. Format cells if: Text is exactly -> "Late"
4. Formatting style: красный фон
5. Done

### Выделить короткие дни жёлтым:

1. Выдели колонку F (worked_hours)
2. Format -> Conditional formatting
3. Format cells if: Less than -> 0.33 (= 8 часов в формате времени)
4. Formatting style: жёлтый фон
5. Done

---

## Советы

1. **Копируй формулы вниз:** Выдели C2:F2 -> потяни за правый нижний угол вниз
2. **Фильтры:** Data -> Create a filter -> удобно искать опоздавших
3. **Защита:** Data -> Protect sheets -> защити листы Logs и Users от случайного изменения
4. **Резервное копирование:** File -> Make a copy -> создавай копии раз в месяц
