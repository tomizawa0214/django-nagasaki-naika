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
// Common
// ===================================================
// Smooth Scroll
$(document).on('click', 'a[href^="#"]', function (e) {
  e.preventDefault()
  let href = $(this).attr('href')
  let target = $(href)
  if (target.length) {
    let position = target.offset().top
    $('html, body').stop().animate({ scrollTop: position }, 500)
  }
})

// Pagetop
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

// Error Message Scroll
$(function () {
  if ($('.js-form-error').length) {
    const position = $('.js-form-error').prev().offset().top
    $('html, body').stop().animate({scrollTop: position}, 500)
  }
})

// Error Message Change Style
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
// My Page
// ===================================================

// Logout Alert
$(document).on('click', '.js-logout', function (event) {
  event.preventDefault()

  if (!window.confirm('ログアウトしますか？')) {
    return
  }

  fetch('/logout/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
      'X-CSRFToken': csrftoken,
    },
  })
    .then((res) => {
      window.location.href = '/logout.php'
    })
    .catch((err) => {
      console.error(err)
      window.alert('ログアウトに失敗しました。時間をおいて再度お試しください。')
    })
})

// Delete
$(document).on('click', '.js-appointment-delete', function (event) {
  event.preventDefault()

  const appointmentDt = $(this).attr('appointment-dt')
  const appointmentId = $(this).attr('appointment-id')

  if (!window.confirm(`本当に${appointmentDt}の予約を取り消しますか？`)) {
    return
  }

  const body = new URLSearchParams()
  body.append('appointmentId', appointmentId)

  fetch('/mypage/appointment/delete/', {
    method: 'POST',
    body: body,
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
      'X-CSRFToken': csrftoken,
    },
  })
    .then((res) => {
      window.location.href = '/mypage/'
    })
    .catch((err) => {
      console.error(err)
      window.alert('予約の取消に失敗しました。時間をおいて再度お試しください。')
    })
})

// ===================================================
// Datetime Calendar
// ===================================================
const calendarPostUrl = window.location.pathname + window.location.search

// Prev Week
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
    .then((res) => {
      window.location.reload()
    })
    .catch((err) => {
      console.error(err)
      window.alert('前の週の表示に失敗しました。時間をおいて再度お試しください。')
    })
})

// Next Week
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
    .then((res) => {
      window.location.reload()
    })
    .catch((err) => {
      console.error(err)
      window.alert('次の週の表示に失敗しました。時間をおいて再度お試しください。')
    })
})

// Month Change
let isManualMonthChange = false

$(document)
  .on('mousedown touchstart', '.js-display-month', function () {
    isManualMonthChange = true
  })
  .on('change', '.js-display-month', function (event) {
    if (!isManualMonthChange) return
    isManualMonthChange = false
  
    event.preventDefault()

    const startDate = $(this).find('option:selected').data('start-date')

    const body = new URLSearchParams()
    body.append('start_date', startDate)

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

// Selected Datetime
$(document).on('change', 'input[name="appointment_dt"]', function () {
  const value = $(this).val()
  
  const dt = new Date(value)
  const weekdays = ['日', '月', '火', '水', '木', '金', '土']
  const year = dt.getFullYear()
  const month = dt.getMonth() + 1
  const day = dt.getDate()
  const weekday = weekdays[dt.getDay()]
  const hours = String(dt.getHours()).padStart(2, '0')
  const minutes = String(dt.getMinutes()).padStart(2, '0')
  
  const selectedDtText = `${year}年${month}月${day}日（${weekday}） ${hours}：${minutes}〜`

  $('.js-appointment-dt').text(selectedDtText)
})

// ===================================================
// Questionnaire
// ===================================================

// Symptom Checkbox
function toggleSymptomCheckbox() {
  if ($('.js-symptom-other').prop('checked')) {
    $('.js-symptom-other-field').fadeIn(300).prop('disabled', false)
  } else {
    $('.js-symptom-other-field').fadeOut(300).prop('disabled', true)
  }
}
toggleSymptomCheckbox()
$('[name="symptom[]"]:checkbox').change(toggleSymptomCheckbox)

// Medical History Radio
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

// Under Treatment Radio
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

// Current Medication Radio
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

// Smoking Radio
function toggleSmokingRadio() {
  if ($('.js-smoking').prop('checked')) {
    $('.js-has-quit-smoking').fadeOut(0).prop('disabled', true)
    $('.js-has-smoking').fadeIn(300).prop('disabled', false)
  } else if ($('.js-quit-smoking').prop('checked')) {
    $('.js-has-smoking').fadeOut(0).prop('disabled', true)
    $('.js-has-quit-smoking').fadeIn(300).prop('disabled', false)
  } else {
    $('.js-has-smoking').fadeOut(300).prop('disabled', true)
    $('.js-has-quit-smoking').fadeOut(300).prop('disabled', true)
  }
}
$(function () {
  toggleSmokingRadio()
})
$('input[name="smoking"]').change(toggleSmokingRadio)

// Alcohol Radio
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

// Allergy Radio
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
