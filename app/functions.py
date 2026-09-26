import datetime
from datetime import timedelta

import jpholiday
from django.conf import settings
from django.utils import timezone

from .models import *


# =====================================================================================================
# セッション判定
# =====================================================================================================
def session_check(request, session_key):

    # セッションを取得
    session_data = request.session.get(session_key)

    # セッションが無い
    if not session_data:
        return None

    # セッションの更新日時を取得
    updated_at = datetime.datetime.fromisoformat(session_data.get("updated_at"))

    # セッションの更新日時から60分以上経過している場合はセッションを削除
    if timezone.now() - updated_at > timedelta(minutes=settings.SESSION_AGE_TIME):
        request.session.pop(session_key, None)
        return None

    # セッションの更新日時を更新して保存
    session_data["updated_at"] = timezone.localtime(timezone.now()).isoformat()
    request.session[session_key] = session_data

    return session_data


# =====================================================================================================
# 予約枠を埋めるスタッフアカウントの判定
# =====================================================================================================
def is_staff_block(user):

    # 未ログインの場合は対象外
    if not user.is_authenticated:
        return False

    # 登録済みのスタッフアカウントのメールアドレスと一致するか判定
    staff_emails = [email.lower() for email in settings.STAFF_BLOCK_EMAILS]
    return (user.email or "").lower() in staff_emails


# =====================================================================================================
# 予約の変更・取消の不可判定（当日以前の予約は変更・取消不可）
# =====================================================================================================
def is_appointment_locked(appointment):
    return timezone.localtime(appointment.appointment_dt).date() <= timezone.localdate()


# =====================================================================================================
# 問診票の変更の不可判定（来院日時を過ぎた予約は変更不可）
# =====================================================================================================
def is_questionnaire_locked(appointment):
    return appointment.appointment_dt < timezone.now()


# =====================================================================================================
# 保存済みの「症状のはじまりの時期」を今日基準の選択肢の値に当てはめる
# （AppointmentQuestionnaireFormの選択肢、symptom_start_displayの表示区分と同じ区分）
# =====================================================================================================
def symptom_start_choice(symptom_start):

    # 今日
    today = datetime.date.today()

    # 今日との差分（日数）
    diff = (today - symptom_start).days

    # 差分を選択肢の区分に当てはめ（今日から / 昨日から / 2〜3日前から / 4〜6日前から / 1週間以上前から）
    if diff <= 0:
        days = 0
    elif diff == 1:
        days = 1
    elif diff <= 3:
        days = 3
    elif diff <= 6:
        days = 6
    else:
        days = 7

    return (today - timedelta(days=days)).isoformat()


# =====================================================================================================
# 休診設定の取得
# =====================================================================================================
def closing_map():
    return {
        "regular": list(RegularClosing.objects.values("weekday", "closed_hours")),
        "summer": list(SummerClosing.objects.values("start_date", "end_date")),
        "new_year": list(NewYearClosing.objects.values("start_date", "end_date")),
        "temp": list(TempClosing.objects.values("date", "closed_hours")),
    }

# =====================================================================================================
# 予約済み枠の取得
# =====================================================================================================
def reservation_map(start_date=None, end_date=None):

    # 来院日時のみをリストで取得
    reservation_appointment_dt = Appointment.objects.values_list("appointment_dt", flat=True)

    # 期間の指定がある場合は期間内の予約のみ取得（カレンダーの表示週など）
    if start_date and end_date:
        reservation_appointment_dt = reservation_appointment_dt.filter(
            appointment_dt__date__range=(start_date, end_date)
        )

    # 予約枠ごとの件数を格納する辞書を定義
    reservation_map = {}
    for appointment_dt in reservation_appointment_dt:

        # 現在のタイムゾーンに変換
        slot_dt = timezone.localtime(appointment_dt)

        # 30分単位に切り捨て
        slot_dt = slot_dt.replace(minute=(slot_dt.minute // 30) * 30, second=0, microsecond=0)

        # 枠を表すキーを作成
        key = (slot_dt.date(), slot_dt.time())

        # 同枠に対して件数を加算
        reservation_map[key] = reservation_map.get(key, 0) + 1

    return reservation_map

# =====================================================================================================
# 予約可否判定
# =====================================================================================================
def status_check(date_obj, time_str, closing_map, reservation_map):

    # 時間帯の午前判定
    is_morning = time_str < "12:00"

    # 初期値
    status = "open"

    # 今日以前は終日予約不可
    if date_obj < datetime.date.today() + timedelta(days=1):
        status = "closed"

    # 予約受付停止中の時間帯は常に予約不可
    if time_str in settings.UNAVAILABLE_TIME_LIST:
        status = "closed"

    # 休診日（時間帯設定を考慮）
    if status == "open":

        # 曜日キーを取得
        weekday_key = settings.MODEL_WEEKDAY_MAP.get(date_obj.weekday())

        # 休診日の設定を取得
        for closing in closing_map.get("regular"):

            # 休診日の曜日一致 または 休診日の祝日一致かつ祝日の場合
            if closing["weekday"] == weekday_key or (
                closing["weekday"] == "holiday" and jpholiday.is_holiday(date_obj)
            ):

                # 終日休診の場合は予約不可に設定
                if closing["closed_hours"] == "all_day":
                    status = "closed"

                # 午前休診の場合は12:00以前であれば予約不可に設定
                elif closing["closed_hours"] == "morning" and is_morning:
                    status = "closed"

                # 午後休診の場合は12:00以降であれば予約不可に設定
                elif closing["closed_hours"] == "afternoon" and not is_morning:
                    status = "closed"

    # 夏季休診は終日予約不可
    if status == "open":

        # 夏季休診の設定を取得
        for closing in closing_map.get("summer"):

            # 夏季休診期間内の場合は終日予約不可
            if closing["start_date"] <= date_obj <= closing["end_date"]:
                status = "closed"
                break

    # 年末年始休診は終日予約不可
    if status == "open":

        # 年末年始休診の設定を取得
        for closing in closing_map.get("new_year"):

            # 年末年始休診期間内の場合は終日予約不可
            if closing["start_date"] <= date_obj <= closing["end_date"]:
                status = "closed"
                break

    # 臨時休診日（時間帯設定を考慮）
    if status == "open":

        # 臨時休診日の設定を取得
        for closing in closing_map.get("temp"):

            # 臨時休診日に該当しない場合はスルー
            if closing["date"] != date_obj:
                continue

            # 終日休診の場合は予約不可に設定
            if closing["closed_hours"] == "all_day":
                status = "closed"

            # 午前休診の場合は12:00以前であれば予約不可に設定
            elif closing["closed_hours"] == "morning" and is_morning:
                status = "closed"

            # 午後休診の場合は12:00以降であれば予約不可に設定
            elif closing["closed_hours"] == "afternoon" and not is_morning:
                status = "closed"

    # 予約枠の残数を確認（30分枠に対して最大 APPOINTMENT_SLOT_CAPACITY 件）
    if status == "open":
        target_time = datetime.time.fromisoformat(time_str)

        # 既存予約の件数を取得
        reserved_count = reservation_map.get((date_obj, target_time), 0)

        # 予約不可
        if reserved_count >= settings.APPOINTMENT_SLOT_CAPACITY:
            status = "closed"

    return status


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

        # 選択された表示月が今月以外の場合はその月の初日を開始日に設定（日付として不正な値は無視）
        else:
            try:
                start_date = datetime.date.fromisoformat(month_first_date)
            except ValueError:
                pass

    # 開始日が表示可能な範囲（今日を含む週 〜 2ヶ月後）外の場合は今週の月曜日に戻す（POST値の改ざん・古いセッション対策）
    if not (today - timedelta(days=6) <= start_date <= two_months_later):
        start_date = this_monday

    # 開始日をセッションに保存
    session_data.update({"start_date": start_date.isoformat()})
    request.session[session_key] = session_data

    # 開始日の月の初日を取得
    current_month = start_date.replace(day=1)

    # 休診設定と表示週の予約済み枠を取得（ループ内で毎回DBを参照しないよう先に1回だけ取得）
    closing_data = closing_map()
    reservation_data = reservation_map(start_date, start_date + timedelta(days=6))

    # 開始日から1週間分を取得してリストに格納
    appointment_dt_list = []
    for i in range(7):

        # 日付を取得
        date_obj = start_date + timedelta(days=i)

        # 曜日のインデックスを取得
        weekday_index = date_obj.weekday()

        # 日付と曜日のクラス名を定義
        if jpholiday.is_holiday(date_obj):
            class_name = "c-calendar__text c-text--holiday"
        elif weekday_index == 5:
            class_name = "c-calendar__text c-text--saturday"
        elif weekday_index == 6:
            class_name = "c-calendar__text c-text--sunday"
        else:
            class_name = "c-calendar__text"

        # 1日分のデータを格納
        oneday = {
            "date_obj": date_obj,
            "weekday_display": settings.WEEKDAYS[weekday_index],
            "class_name": class_name,
        }

        # 各診察時間ごとの予約可否判定
        for time_str in settings.TIME_LIST:
            oneday[time_str] = status_check(
                date_obj=date_obj,
                time_str=time_str,
                closing_map=closing_data,
                reservation_map=reservation_data,
            )

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

    return {
        "start_date": start_date,
        "tomorrow": tomorrow,
        "month_list": month_list,
        "time_list": settings.TIME_LIST,
        "current_month": current_month,
        "last_month_start_date": last_month_start_date,
        "appointment_dt_list": appointment_dt_list,
    }
