import sqlite3
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Personal OS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def init_db():
    conn = sqlite3.connect("tracker.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            exercise TEXT,
            sets INTEGER,
            reps INTEGER,
            notes TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS speech_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            week TEXT,
            day TEXT,
            slot TEXT,
            exercise TEXT,
            metric_val TEXT,
            notes TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            ticker TEXT,
            direction TEXT,
            setup_type TEXT,
            entry_price REAL,
            stop_loss REAL,
            take_profit REAL,
            risk_usd REAL,
            pnl_usd REAL,
            rr_realized REAL,
            compliance_rules TEXT,
            mistake_tag TEXT,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_workout(workout_date, exercise, sets, reps, notes):
    conn = sqlite3.connect("tracker.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO workouts (date, exercise, sets, reps, notes) VALUES (?, ?, ?, ?, ?)",
                (str(workout_date), exercise, sets, reps, notes))
    conn.commit()
    conn.close()

def save_speech_log(log_date, week, day, slot, exercise, metric_val, notes):
    conn = sqlite3.connect("tracker.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO speech_logs (date, week, day, slot, exercise, metric_val, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (str(log_date), week, day, slot, exercise, str(metric_val), notes))
    conn.commit()
    conn.close()

def save_trade(log_date, ticker, direction, setup, entry, sl, tp, risk, pnl, rr, compliance, mistake, notes):
    conn = sqlite3.connect("tracker.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO trades (date, ticker, direction, setup_type, entry_price, stop_loss, take_profit, risk_usd, pnl_usd, rr_realized, compliance_rules, mistake_tag, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (str(log_date), ticker, direction, setup, entry, sl, tp, risk, pnl, rr, compliance, mistake, notes))
    conn.commit()
    conn.close()

def get_workouts():
    conn = sqlite3.connect("tracker.db")
    df = pd.read_sql_query("SELECT * FROM workouts ORDER BY date ASC", conn)
    conn.close()
    return df

def get_speech_logs():
    conn = sqlite3.connect("tracker.db")
    df = pd.read_sql_query("SELECT * FROM speech_logs ORDER BY date ASC", conn)
    conn.close()
    return df

def get_trades():
    conn = sqlite3.connect("tracker.db")
    df = pd.read_sql_query("SELECT * FROM trades ORDER BY date ASC", conn)
    conn.close()
    return df

init_db()

SPEECH_PLAN = {
    "Понедельник": [
        {"slot": "00:00–00:07", "block": "Дикция и ТОиР", "title": "ТОиР-кластеры и артикуляция", "script": "1) Разминка губ и челюсти (2 мин).\n2) Кластеры: «ПТКА–БДГА–ВЗБРЯ», «КСТР–ГЗДР–ТРПР» (по 3 раза).\n3) Скороговорка: «Протокол превентивной проверки перепроверил прецизионный преобразователь».", "metric_name": "Четкость кластеров (1–5)"},
        {"slot": "00:07–00:22", "block": "Вербальная беглость", "title": "10 слов на «А» и «Б» (ТОиР + общая)", "script": "1) 5 ТОиР + 5 общих на «А» (Агрегат, Анализ, Амортизация | Аргумент, Акцент...)\n2) 5 ТОиР + 5 на «Б» (Байпас, Балансировка | Безупречный, Быстрый...)\n3) Связный экспромт за 2 минуты из 5 слов.", "metric_name": "Время на 10 слов (сек)"},
        {"slot": "00:22–00:30", "block": "Пересказ", "title": "Эффект Пигмалиона (1.5 мин)", "script": "Суть феномена: ожидания руководителя определяют результат окружающих (эксперимент Розенталя 1968 г.).", "metric_name": "Полнота пересказа (1–5)"}
    ],
    "Вторник": [
        {"slot": "00:00–00:07", "block": "Голос и дыхание", "title": "Дыхание и грудной резонатор", "script": "1) Животом вдох на 4, пауза 2, выдох «С-с-с» на 8.\n2) Губы сомкнуты, звук «Мммм» в грудь.\n3) Гласные в грудь: «И-Э-А-О-У-Ы».", "metric_name": "Длина выдоха (сек)"},
        {"slot": "00:07–00:22", "block": "Деловая речь", "title": "Открытие встречи и статус ТОиР", "script": "Отработайте открытие совещания:\n«Коллеги, цель за 30 минут — утвердить регламент ТОиР. Позиция классифицирована как Bad Actor, MTBF критический. Регламент: вибромониторинг, меры, ответственные».", "metric_name": "Уверенность подачи (1–5)"},
        {"slot": "00:22–00:30", "block": "Пересказ кейса", "title": "Кавитационный износ насоса", "script": "Суть кейса: Повышенная нагрузка -> треск и вибрация -> эрозия кромок рабочего колеса. Причина: падение подпора NPSHa ниже NPSHr из-за температуры. Решение: охлаждение на всасе.", "metric_name": "Точность причин отказа (1–5)"}
    ]
}

TERMS_DB = {
    "Понедельник": [
        ("Отказ (Failure) [ГОСТ 27.002]", "Утрата объектом работоспособности в пределах допусков."),
        ("Вид отказа (Failure Mode) [ISO 14224]", "Внешнее наблюдаемое проявление дефекта."),
        ("Механизм отказа [ISO 14224]", "Физико-химический процесс деградации (усталость, эрозия)."),
        ("Коренная причина [API 585]", "Исходный фактор, исключающий рецидив при устранении."),
        ("FMEA / FMECA [IEC 60812]", "Анализ видов и критичности отказов (RPN)."),
        ("Bad Actor", "Хронически дефектное оборудование с потерями надежности.")
    ],
    "Вторник": [
        ("Коэффициент готовности [ГОСТ 27.002]", "Вероятность готовности машины в любой момент."),
        ("Предупредительное ТО (PM)", "Обслуживание по фиксированным интервалам."),
        ("ТО по состоянию (CBM) [ISO 17359]", "Обслуживание по диагностическим замерам.")
    ]
}

EXERCISES_DB = {
    "День А (Грудь / Ноги / Пресс)": [
        {"name": "Отжимания от пола", "target": "Грудь, трицепс", "scheme": "3 подхода по 10-12 раз", "url": "https://www.youtube.com/results?search_query=proper+pushup+form"},
        {"name": "Приседания", "target": "Квадрицепс, ягодицы", "scheme": "3 подхода по 15-20 раз", "url": "https://www.youtube.com/results?search_query=bodyweight+squat+technique"},
        {"name": "Планка на локтях", "target": "Мышцы кора", "scheme": "3 подхода по 30-45 сек", "url": "https://www.youtube.com/results?search_query=proper+plank+form"}
    ],
    "День Б (Спина / Бедра / Плечи)": [
        {"name": "Австралийские тяги", "target": "Спина, бицепс", "scheme": "3 подхода по 8-10 раз", "url": "https://www.youtube.com/results?search_query=australian+pull+ups+form"},
        {"name": "Ягодичный мост", "target": "Задняя поверхность", "scheme": "3 подхода по 15 раз", "url": "https://www.youtube.com/results?search_query=glute+bridge+form"},
        {"name": "Отжимания уголком (Pike)", "target": "Плечи", "scheme": "3 подхода по 6-8 раз", "url": "https://www.youtube.com/results?search_query=pike+push+ups+technique"}
    ]
}

menu = st.segmented_control("Раздел:", ["📈 Трейдинг & Проп", "🏋️ Спорт", "🗣 Речь & ТОиР", "📊 Сводная Аналитика"], default="📈 Трейдинг & Проп")

if menu == "📈 Трейдинг & Проп":
    st.title("📈 Торговая система: Слом тренда и Проп-менеджмент")
    t_tab1, t_tab2, t_tab3, t_tab4 = st.tabs(["🧮 Риск-калькулятор", "📝 Чек-лист и Журнал", "🎯 Матрица 9×9", "📊 Аналитика"])
    
    with t_tab1:
        st.subheader("Калькулятор фиксированного риска")
        c1, c2, c3 = st.columns(3)
        with c1:
            account_size = st.selectbox("Депозит пропа ($)", [10000, 25000, 50000, 100000], index=0)
            risk_pct = st.selectbox("Риск (%)", [0.5, 0.75, 1.0], index=0)
            target_risk_usd = account_size * (risk_pct / 100.0)
            st.metric("Допустимый риск", f"${target_risk_usd:.2f}")
        with c2:
            entry_p = st.number_input("Цена входа", min_value=0.000001, value=65.0, format="%.4f")
            sl_p = st.number_input("Стоп-лосс (SL)", min_value=0.000001, value=63.5, format="%.4f")
            tp_p = st.number_input("Тейк-профит (TP)", min_value=0.000001, value=69.5, format="%.4f")
        with c3:
            dist_sl = abs(entry_p - sl_p)
            dist_tp = abs(tp_p - entry_p)
            if dist_sl > 0:
                pos_size_coins = target_risk_usd / dist_sl
                pos_size_usd = pos_size_coins * entry_p
                rr_ratio = dist_tp / dist_sl
                st.metric("Объем (Монет)", f"{pos_size_coins:.2f}")
                st.metric("Номинал позиции ($)", f"${pos_size_usd:.2f}")
                if rr_ratio >= 2.0:
                    st.success(f"R:R = 1:{rr_ratio:.2f} (Валидно)")
                else:
                    st.error(f"R:R = 1:{rr_ratio:.2f} (Меньше 1:2.0!)")

    with t_tab2:
        st.subheader("Фиксация сделки")
        with st.form("trade_form"):
            ct1, ct2 = st.columns(2)
            with ct1:
                t_date = st.date_input("Дата", value=date.today())
                t_ticker = st.text_input("Тикер", value="SOLUSDT").upper()
                t_dir = st.selectbox("Направление", ["LONG", "SHORT"])
                t_setup = st.selectbox("Сетап", ["Major BOS + Ретест", "iBOS + Ретест", "Re-claim уровня", "Зона OTE 0.618-0.786"])
            with ct2:
                t_risk = st.number_input("Риск ($)", min_value=1.0, value=50.0)
                t_pnl = st.number_input("PnL ($)", value=0.0, step=5.0)
                t_rr = st.number_input("Фактический R:R", value=0.0, step=0.1)
                t_mistake = st.selectbox("Ошибки дисциплины", [
                    "Без ошибок", "Микротейк (Ранний выход)", "Вход без ретеста", "Против старшего BOS", "Завышенный риск"
                ])
            st.markdown("**Чек-лист перед входом:**")
            ch1 = st.checkbox("1. Пробой подтвержден телом часовой свечи.")
            ch2 = st.checkbox("2. Ретест на затухающих объемах.")
            ch3 = st.checkbox("3. На младшем ТФ (5m-15m) есть отбойный паттерн.")
            ch4 = st.checkbox("4. R:R минимум 1:2.0.")
            compliance_status = "ДА" if (ch1 and ch2 and ch3 and ch4) else "НЕТ"
            t_notes = st.text_area("Заметки", placeholder="Контекст сессии...")
            if st.form_submit_button("Сохранить сделку", use_container_width=True):
                save_trade(t_date, t_ticker, t_dir, t_setup, entry_p, sl_p, tp_p, t_risk, t_pnl, t_rr, compliance_status, t_mistake, t_notes)
                st.success("Сделка сохранена!")

    with t_tab3:
        st.subheader("Матрица Харада 9×9: План $3 000/мес")
        matrix_blocks = {
            "1. Стратегия": ["Только импульсный BOS телом свечи 1H", "Ретест на затухающих объемах", "Зона OTE 0.618–0.786 Fib", "Подтверждение на 5m–15m", "Отмена при Re-claim", "Стоп за структурный свинг", "R:R от 1:2.0", "1-2 инструмента"],
            "2. Риск-менеджмент": ["Фиксированный риск 0.5% ($50 на $10k)", "Лимит: 2 стопа = терминал закрыт", "Расчет лота через калькулятор", "БУ только по структуре", "Запрет усреднений", "Не торговать за 15 мин до новостей", "Частичный фикс 50% на 1:2"],
            "3. Проп-капитал": ["Сдача первого $10k без спешки", "Первый Payout", "100% реинвест выплат в новые счета", "Диверсификация в 2-3 фирмы", "Пул $100 000 funded", "Соблюдение consistency", "Резервный фонд 10%"],
            "4. Режим вахты": ["Окно 1-2 часа в день", "Торговля по алертам TradingView", "Старшие ТФ (4H/1D контекст)", "Без сигнальных каналов", "Сон от 7 часов", "На смене — 100% фокус на работе"]
        }
        mc = st.columns(2)
        for i, (b_name, b_items) in enumerate(matrix_blocks.items()):
            with mc[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{b_name}**")
                    for itm in b_items:
                        st.markdown(f"- {itm}")

    with t_tab4:
        st.subheader("Статистика торговли")
        tdf = get_trades()
        if tdf.empty:
            st.info("Нет данных по сделкам.")
        else:
            w = tdf[tdf["pnl_usd"] > 0]
            wr = (len(w) / len(tdf)) * 100 if len(tdf) > 0 else 0
            net = tdf["pnl_usd"].sum()
            c1, c2, c3 = st.columns(3)
            c1.metric("Сделок", len(tdf))
            c2.metric("Винрейт", f"{wr:.1f}%")
            c3.metric("Чистый PnL", f"${net:.2f}")
            fig_p = px.bar(tdf, x="date", y="pnl_usd", color="pnl_usd", title="Динамика PnL ($)", color_continuous_scale=["red", "gray", "green"])
            st.plotly_chart(fig_p, use_container_width=True)
            st.dataframe(tdf.sort_values(by="id", ascending=False), use_container_width=True)

elif menu == "🏋️ Спорт":
    st.title("🏋️ Калистеника (20–30 минут)")
    tab_p, tab_l, tab_s = st.tabs(["Программа", "Записать подход", "История"])
    with tab_p:
        s_choice = st.selectbox("Сессия:", list(EXERCISES_DB.keys()))
        for ex in EXERCISES_DB[s_choice]:
            with st.container(border=True):
                st.markdown(f"**{ex['name']}**")
                st.caption(f"{ex['target']} • {ex['scheme']}")
                st.markdown(f"[▶️ Видеотехника]({ex['url']})")
    with tab_l:
        with st.form("w_form"):
            e_name = st.selectbox("Упражнение", [e["name"] for cat in EXERCISES_DB.values() for e in cat])
            c1, c2 = st.columns(2)
            sv = c1.number_input("Подходы", 1, 10, 3)
            rv = c2.number_input("Повторы/сек", 1, 200, 10)
            nv = st.text_input("Заметка", placeholder="Легко/тяжело")
            if st.form_submit_button("Сохранить", use_container_width=True):
                save_workout(date.today(), e_name, sv, rv, nv)
                st.success("Сохранено!")
    with tab_s:
        wdf = get_workouts()
        if not wdf.empty:
            wdf["total"] = wdf["sets"] * wdf["reps"]
            st.plotly_chart(px.bar(wdf, x="date", y="total", color="exercise", title="Объем повторений"), use_container_width=True)
            st.dataframe(wdf.sort_values(by="id", ascending=False), use_container_width=True)
        else:
            st.info("Нет записей.")

elif menu == "🗣 Речь & ТОиР":
    st.title("🗣 Ораторский пульт и фасилитация ТОиР")
    d_choice = st.selectbox("День недели:", list(SPEECH_PLAN.keys()))
    t1, t2, t3 = st.tabs(["Задания дня", "Словарь стандартов", "Прогресс"])
    with t1:
        for idx, task in enumerate(SPEECH_PLAN.get(d_choice, [])):
            with st.container(border=True):
                st.markdown(f"**⏱ {task['slot']} | {task['title']}**")
                st.caption(task['block'])
                st.info(task['script'])
                with st.expander("Оценить результат"):
                    mv = st.text_input(f"Метрика ({task['metric_name']})", key=f"sm_{idx}")
                    nv = st.text_input("Заметки", key=f"sn_{idx}")
                    if st.button("Сохранить блок", key=f"sbtn_{idx}", use_container_width=True):
                        save_speech_log(date.today(), "Неделя 1", d_choice, task['slot'], task['title'], mv, nv)
                        st.success("Записано!")
    with t2:
        for num, (tn, td) in enumerate(TERMS_DB.get(d_choice, []), 1):
            st.markdown(f"**{num}. {tn}**")
            st.caption(td)
            st.divider()
    with t3:
        sdf = get_speech_logs()
        if not sdf.empty:
            st.dataframe(sdf.sort_values(by="id", ascending=False), use_container_width=True)
        else:
            st.info("Нет записей.")

elif menu == "📊 Сводная Аналитика":
    st.title("📊 Единый дашборд привычек и результатов")
    ca1, ca2, ca3 = st.columns(3)
    wdf = get_workouts()
    sdf = get_speech_logs()
    tdf = get_trades()
    with ca1:
        st.subheader("🏋️ Спорт")
        st.metric("Дней тренировок", wdf["date"].nunique() if not wdf.empty else 0)
        st.metric("Объем повторений", int((wdf["sets"] * wdf["reps"]).sum()) if not wdf.empty else 0)
    with ca2:
        st.subheader("🗣 Речь")
        st.metric("Сессий речи", len(sdf))
        st.metric("Активных дней", sdf["date"].nunique() if not sdf.empty else 0)
    with ca3:
        st.subheader("📈 Трейдинг")
        st.metric("Сделок", len(tdf))
        st.metric("Итоговый PnL", f"${tdf['pnl_usd'].sum():.2f}" if not tdf.empty else "$0.00")
