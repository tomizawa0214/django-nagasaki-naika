'use strict'

// ===================================================
// CSRF対策
// ===================================================
function getCookie(name) {
  if (document.cookie && document.cookie !== '') {
    for (const cookie of document.cookie.split(';')) {
      const [key, value] = cookie.trim().split('=')
      if (key === name) {
        return decodeURIComponent(value)
      }
    }
  }
}
const csrftoken = getCookie('csrftoken')

// ===================================================
// スムーススクロール
// ===================================================
$(document).on('click', 'a[href^="#"]', function (e) {
  e.preventDefault()
  const href = $(this).attr('href')
  const target = $(href)
  if (target.length) {
    const position = target.offset().top
    $('html, body').stop().animate({ scrollTop: position }, 500)
  }
})

// ===================================================
// ページの先頭へスムーススクロール
// ===================================================
const pagetop = $('.l-pagetop')
function togglePageTop() {
  if (!window.matchMedia('(min-width: 1024px)').matches) {
    pagetop.hide()
    return
  }
  if ($(window).scrollTop() > 300) {
    pagetop.fadeIn()
  } else {
    pagetop.fadeOut()
  }
}

$(window).on('scroll resize', togglePageTop)
togglePageTop()
pagetop.on('click', function () {
  $('html, body').animate({ scrollTop: 0 }, 500)
})

// ===================================================
// エラーメッセージの先頭へスムーススクロール
// ===================================================
$(function () {
  if ($('.js-form-error').length) {
    const position = $('.js-form-error').prev().offset().top
    $('html, body').stop().animate({scrollTop: position}, 500)
  }
})

// ===================================================
// エラーメッセージの削除
// ===================================================
$(function () {
  $('.js-form-error').each(function () {
    const ErrorMessage = $(this)
    ErrorMessage.prev().addClass('is-error')
    ErrorMessage.prev().one('input change', function () {
      $(this).removeClass('is-error')
      ErrorMessage.fadeOut(300)
    })
  })
})

// ===================================================
// ログアウト
// ===================================================
$(function () {
  $(document).on('submit', '.js-logout', function (event) {
    if (!window.confirm('ログアウトしますか？'))
    event.preventDefault()
  })
})

// ===================================================
// 本日はどうなさいましたか？
// 「その他」を選択で入力フィールドを表示
// ===================================================
function toggleSymptomCheckbox() {
  if ($('.js-symptom-other').prop('checked')) {
    $('.js-symptom-other-field').fadeIn(300).prop('disabled', false)
  } else {
    $('.js-symptom-other-field').fadeOut(300).prop('disabled', true)
  }
}
toggleSymptomCheckbox()
$('[name="symptom"]:checkbox').change(toggleSymptomCheckbox)

// ===================================================
// 大きな病気で治療や手術
// 「ある」を選択で入力フィールドを表示
// ===================================================
function toggleMedicalHistoryRadio() {
  if ($('.js-has-medical-history').prop('checked')) {
    $('.js-has-medical-history-field').fadeIn(300).prop('disabled', false)
  } else {
    $('.js-has-medical-history-field').fadeOut(300).prop('disabled', true)
  }
}
$(function () {
  toggleMedicalHistoryRadio()
})
$('input[name="medical_history"]').change(toggleMedicalHistoryRadio)

// ===================================================
// 治療中の病気
// 「ある」を選択で入力フィールドを表示
// ===================================================
function toggleUnderTreatmentRadio() {
  if ($('.js-has-under-treatment').prop('checked')) {
    $('.js-has-under-treatment-field').fadeIn(300).prop('disabled', false)
  } else {
    $('.js-has-under-treatment-field').fadeOut(300).prop('disabled', true)
  }
}
$(function () {
  toggleUnderTreatmentRadio()
})
$('input[name="under_treatment"]').change(toggleUnderTreatmentRadio)

// ===================================================
// 飲んでいるお薬
// 「ある」を選択で入力フィールドを表示
// ===================================================
function toggleCurrentMedicationRadio() {
  if ($('.js-has-current-medication').prop('checked')) {
    $('.js-has-current-medication-field').fadeIn(300).prop('disabled', false)
  } else {
    $('.js-has-current-medication-field').fadeOut(300).prop('disabled', true)
  }
}
$(function () {
  toggleCurrentMedicationRadio()
})
$('input[name="current_medication"]').change(toggleCurrentMedicationRadio)

// ===================================================
// 煙草について
// 「吸う」または「禁煙した」を選択で入力フィールドを表示
// ===================================================
function toggleSmokingRadio() {
  if ($('.js-smoking').prop('checked')) {
    $('.js-has-quit-smoking').fadeOut(0).find('select, input').prop('disabled', true)
    $('.js-has-smoking').fadeIn(300).find('select, input').prop('disabled', false)
  } else if ($('.js-quit-smoking').prop('checked')) {
    $('.js-has-smoking').fadeOut(0).find('select, input').prop('disabled', true)
    $('.js-has-quit-smoking').fadeIn(300).find('select, input').prop('disabled', false)
  } else {
    $('.js-has-smoking').fadeOut(300).find('select, input').prop('disabled', true)
    $('.js-has-quit-smoking').fadeOut(300).find('select, input').prop('disabled', true)
  }
}
$(function () {
  toggleSmokingRadio()
})
$('input[name="smoking"]').change(toggleSmokingRadio)

// ===================================================
// 飲酒について
// 「飲む」を選択で入力フィールドを表示
// ===================================================
function toggleAlcoholRadio() {
  if ($('.js-alcohol').prop('checked')) {
    $('.js-has-alcohol').fadeIn(300).prop('disabled', false)
  } else {
    $('.js-has-alcohol').fadeOut(300).prop('disabled', true)
  }
}
$(function () {
  toggleAlcoholRadio()
})
$('input[name="alcohol"]').change(toggleAlcoholRadio)

// ===================================================
// お薬・食べ物のアレルギー
// 「ある」を選択で入力フィールドを表示
// ===================================================
function toggleAllergyRadio() {
  if ($('.js-has-allergy').prop('checked')) {
    $('.js-has-allergy-field').fadeIn(300).prop('disabled', false)
  } else {
    $('.js-has-allergy-field').fadeOut(300).prop('disabled', true)
  }
}
$(function () {
  toggleAllergyRadio()
})
$('input[name="allergy"]').change(toggleAllergyRadio)

// ===================================================
// カレンダーの週移動・月変更
// ===================================================
const calendarPostUrl = window.location.pathname + window.location.search

// 前の週
$(document).on('click', '.js-prev-week', function (event) {
  event.preventDefault()

  const body = new URLSearchParams()
  body.append('prev_days', 7)

  fetch(calendarPostUrl, {
    method: 'POST',
    body: body,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
      'X-CSRFToken': csrftoken,
    },
  })
    .then(() => {
      window.location.reload()
    })
    .catch((err) => {
      console.error(err)
      window.alert('前の週の表示に失敗しました。時間をおいて再度お試しください。')
    })
})

// 次の週
$(document).on('click', '.js-next-week', function (event) {
  event.preventDefault()

  const body = new URLSearchParams()
  body.append('next_days', 7)

  fetch(calendarPostUrl, {
    method: 'POST',
    body: body,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
      'X-CSRFToken': csrftoken,
    },
  })
    .then(() => {
      window.location.reload()
    })
    .catch((err) => {
      console.error(err)
      window.alert('次の週の表示に失敗しました。時間をおいて再度お試しください。')
    })
})

// 表示月の切り替え
let isManualMonthChange = false

$(document)
  .on('mousedown touchstart', '.js-display-month', function () {
    isManualMonthChange = true
  })
  .on('change', '.js-display-month', function (event) {
    if (!isManualMonthChange) return
    isManualMonthChange = false
  
    event.preventDefault()

    const monthFirstDate = $(this).find('option:selected').data('month-first-date')

    const body = new URLSearchParams()
    body.append('month_first_date', monthFirstDate)

    fetch(calendarPostUrl, {
      method: 'POST',
      body: body,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
        'X-CSRFToken': csrftoken,
      },
    })
      .then((res) => {
        window.location.reload()
      })
      .catch((err) => {
        console.error(err)
        window.alert('表示月の切り替えに失敗しました。時間をおいて再度お試しください。')
      })
})

// ===================================================
// 選択中のご来院日時の表示
// ===================================================
function appointmentDt() {
  const $checked = $('input[name="appointment_dt"]:checked')
  if (!$checked.length) return

  const dt = new Date($checked.val())
  const weekdays = ['日', '月', '火', '水', '木', '金', '土']
  const year = dt.getFullYear()
  const month = dt.getMonth() + 1
  const day = dt.getDate()
  const weekday = weekdays[dt.getDay()]
  const hours = String(dt.getHours()).padStart(2, '0')
  const minutes = String(dt.getMinutes()).padStart(2, '0')

  const selectedDtText = `${year}年${month}月${day}日(${weekday}) ${hours}:${minutes}〜`

  $('.js-appointment-dt').text(selectedDtText)
}

$(document).on('change', 'input[name="appointment_dt"]', appointmentDt)
$(window).on('pageshow', appointmentDt)
$(appointmentDt)

// ===================================================
// 予約の取消
// ===================================================
$(function () {
  $(document).on('submit', '.js-appointment-delete', function (event) {

    const appointmentDt = $(event.target).find('button').attr('appointment-dt')
    const dt = new Date(appointmentDt)
    const today = new Date()

    const isToday =
      dt.getFullYear() === today.getFullYear() &&
      dt.getMonth() === today.getMonth() &&
      dt.getDate() === today.getDate()

    if (isToday) {
      alert('本日ご来院予定のキャンセルは、診療時間内にお電話にてご連絡ください。')
      event.preventDefault()
      return
    }

    const weekdays = ['日', '月', '火', '水', '木', '金', '土']
    const month = dt.getMonth() + 1
    const day = dt.getDate()
    const weekday = weekdays[dt.getDay()]
    const hours = String(dt.getHours()).padStart(2, '0')
    const minutes = String(dt.getMinutes()).padStart(2, '0')
    const appointmentDtText = `${month}月${day}日(${weekday}) ${hours}:${minutes}〜`
    if (!window.confirm(`本当に${appointmentDtText}の予約を取り消しますか？`))
      event.preventDefault()
  })
})

// ===================================================
// 当日の予約変更
// ===================================================
$(function () {
  $(document).on('click', '.js-appointment-change', function (event) {

    const appointmentDt = $(this).attr('appointment-dt')
    const dt = new Date(appointmentDt)
    const today = new Date()

    const isToday =
      dt.getFullYear() === today.getFullYear() &&
      dt.getMonth() === today.getMonth() &&
      dt.getDate() === today.getDate()

    if (isToday) {
      alert('本日ご来院予定の変更は、診療時間内にお電話にてご連絡ください。')
      event.preventDefault()
      return
    }
  })
})
