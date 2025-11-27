import datetime
from datetime import timedelta

import jpholiday
from django.conf import settings


# =====================================================================================================
# 日時選択のカレンダー表示
# =====================================================================================================
def build_calendar(request, session_key):

    # 今日
    today = datetime.date.today()

    # 明日
    tomorrow = today + timedelta(days=1)

    # 今月
    this_month = today.replace(day=1)

    # 今週の月曜日
    this_monday = today - timedelta(days=today.weekday())

    # 今日から60日間の祝日リスト
    HOLIDAYS = [date.isoformat() for date, _ in jpholiday.between(today, today + timedelta(days=60))]

    # 定期休診
    REGULAR_CLOSING = []

    # 夏季休診
    SUMMER_CLOSING = [
        "2026-08-10",
        "2026-08-11",
        "2026-08-12",
        "2026-08-13",
        "2026-08-14",
        "2026-08-15",
        "2026-08-16",
        "2026-08-17",
    ]

    # 年末年始休診
    NEWYEAR_CLOSING = [
        "2025-12-29",
        "2025-12-30",
        "2025-12-31",
        "2026-01-01",
        "2026-01-02",
        "2026-01-03",
        "2026-01-04",
        "2026-01-05",
    ]

    # 臨時休診
    TEMP_CLOSING = [
        "2025-11-28",
    ]

    # セッションからカレンダーの開始日を取得（セッションが無ければ今週の月曜日を開始日に設定）
    session_data = request.session.get(session_key, {})
    session_start_date = session_data.get("start_date")
    if session_start_date:
        start_date = datetime.date.fromisoformat(session_start_date)
    else:
        start_date = this_monday

    # 前の週がクリックされた場合はカレンダーの開始日を-7日する
    if request.method == "POST" and "prev_days" in request.POST:
        start_date -= timedelta(days=7)

    # 次の週がクリックされた場合はカレンダーの開始日を+7日する
    if request.method == "POST" and "next_days" in request.POST:
        start_date += timedelta(days=7)

    # 表示月のプルダウンを手動で切り替えた場合
    if request.method == "POST" and "month_first_date" in request.POST:

        # 選択された表示月を取得
        month_first_date = request.POST["month_first_date"]

        # 選択された表示月が今月の場合は今週の月曜日を開始日に設定
        if month_first_date == this_month.isoformat():
            start_date = this_monday

        # 選択された表示月が今月以外の場合はその月の初日を開始日に設定
        else:
            start_date = datetime.date.fromisoformat(month_first_date)

    # 開始日をセッションに保存
    session_data.update({"start_date": start_date.isoformat()})
    request.session[session_key] = session_data

    # 開始日の月の初日を取得
    current_month = start_date.replace(day=1)

    # 開始日から1週間分を取得してリストに格納
    appointment_dt_list = []
    for i in range(7):

        # 日付を取得
        date_data = start_date + timedelta(days=i)

        # 日付を文字列で取得
        date_display = date_data.isoformat()

        # 曜日のインデックスを取得
        weekday_index = date_data.weekday()

        # 日付と曜日のクラス名を定義
        if date_display in HOLIDAYS:
            class_name = "c-calendar__text c-text--holiday"
        elif weekday_index == 5:
            class_name = "c-calendar__text c-text--saturday"
        elif weekday_index == 6:
            class_name = "c-calendar__text c-text--sunday"
        else:
            class_name = "c-calendar__text"

        # 1日分のデータを格納
        oneday = {
            "date_data": date_data,
            "weekday_display": settings.WEEKDAYS[weekday_index],
            "class_name": class_name,
        }

        # 各診察時間ごとの予約可否判定
        for time_data in settings.TIME_LIST:

            # 予約ステータスの初期値を定義
            status = "open"

            # 予約不可条件の判定（過去日 / 休診 / 臨時休診 / 夏季休診 / 年末年始休診）
            if (
                date_display < tomorrow.isoformat()
                or date_display in HOLIDAYS
                or date_display in NEWYEAR_CLOSING
                or date_display in SUMMER_CLOSING
                or date_display in TEMP_CLOSING
            ):
                status = "closed"

            # 各時間帯の予約可否を格納
            oneday[time_data] = status

        # 予約状況のリストに追加
        appointment_dt_list.append(oneday)

    # 翌々月まで定義
    month_list = []
    for i in range(3):

        # 該当年を取得
        year = this_month.year + (this_month.month - 1 + i) // 12

        # 該当月を取得
        month = (this_month.month - 1 + i) % 12 + 1

        # 該当月の初日を取得
        month_first = datetime.date(year, month, 1)

        # 月リストに追加
        month_list.append(
            {
                "month_first": month_first,
                "month_display": month_first.strftime("%Y年%-m月"),
            }
        )

    # 2ヶ月後の年月を取得
    year = today.year + (today.month - 1 + 2) // 12
    month = (today.month - 1 + 2) % 12 + 1

    # 2ヶ月後の月の最終日を取得（28日 → +4日 → 翌月に進んだ日付から日数を引く）
    tmp = datetime.date(year, month, 28) + datetime.timedelta(days=4)
    last_day = tmp - datetime.timedelta(days=tmp.day)

    # 存在しない日付は月末に丸めて2ヶ月後の日付を取得
    day = min(today.day, last_day.day)
    two_months_later = datetime.date(year, month, day)

    # 2ヶ月後の6日前
    last_month_start_date = two_months_later - datetime.timedelta(days=6)

    return {
        "start_date": start_date,
        "tomorrow": tomorrow,
        "month_list": month_list,
        "time_list": settings.TIME_LIST,
        "current_month": current_month,
        "last_month_start_date": last_month_start_date,
        "appointment_dt_list": appointment_dt_list,
    }
