document.addEventListener("DOMContentLoaded", function () {
    if (typeof flatpickr === "undefined") {
        return;
    }

    const ROW_HEIGHT = 46;
    const WHEEL_DELTA_THRESHOLD = 70;
    const WHEEL_STEP_COOLDOWN = 120;
    const hoursData = Array.from({ length: 12 }, (_, i) => String(i + 1).padStart(2, "0"));
    const minutesData = Array.from({ length: 60 }, (_, i) => String(i).padStart(2, "0"));
    const periodsData = ["AM", "PM"];

    const style = document.createElement("style");
    style.innerHTML = `
    .flatpickr-calendar.notice-datetime-picker {
        width: min(calc(100vw - 24px), 500px) !important;
        min-width: 500px !important;
        max-width: 500px !important;
        display: grid !important;
        grid-template-columns: 260px 64px 78px 58px !important;
        grid-template-rows: 44px auto !important;
        align-items: stretch !important;
        column-gap: 6px !important;
        row-gap: 0 !important;
        padding: 10px !important;
        border: 1px solid #e3e6ea !important;
        border-radius: 14px !important;
        background: #fafafa !important;
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.14) !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
    }

    .flatpickr-calendar.notice-datetime-picker::before,
    .flatpickr-calendar.notice-datetime-picker::after {
        display: none !important;
    }

    .notice-datetime-picker .flatpickr-months,
    .notice-datetime-picker .flatpickr-weekdays,
    .notice-datetime-picker .flatpickr-days {
        background: #fff !important;
    }

    .notice-datetime-picker .flatpickr-months {
        grid-column: 1 !important;
        grid-row: 1 !important;
        position: relative !important;
        width: 260px !important;
        height: 44px !important;
        border: 1px solid #eceff3 !important;
        border-bottom: 0 !important;
        border-radius: 12px 12px 0 0 !important;
        box-sizing: border-box !important;
        overflow: visible !important;
    }

    .notice-datetime-picker .flatpickr-innerContainer {
        grid-column: 1 !important;
        grid-row: 2 !important;
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
        display: block !important;
        border: 1px solid #eceff3 !important;
        border-radius: 0 0 12px 12px !important;
        overflow: hidden !important;
        background: #fff !important;
    }

    .notice-datetime-picker .flatpickr-rContainer,
    .notice-datetime-picker .flatpickr-days,
    .notice-datetime-picker .dayContainer {
        width: 260px !important;
        min-width: 260px !important;
        max-width: 260px !important;
    }

    .notice-datetime-picker .flatpickr-month {
        height: 43px !important;
        overflow: visible !important;
    }

    .notice-datetime-picker .flatpickr-current-month {
        left: 38px !important;
        width: 184px !important;
        height: 43px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        font-size: 14px !important;
        pointer-events: auto !important;
    }

    .notice-datetime-picker .flatpickr-current-month .flatpickr-monthDropdown-months,
    .notice-datetime-picker .flatpickr-current-month input.cur-year {
        height: 30px !important;
        border: 1px solid #dfe4ea !important;
        border-radius: 8px !important;
        background: #fff !important;
        color: #111827 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        box-sizing: border-box !important;
        cursor: pointer !important;
    }

    .notice-datetime-picker .flatpickr-current-month .flatpickr-monthDropdown-months {
        width: 104px !important;
        padding: 0 6px !important;
        appearance: auto !important;
    }

    .notice-datetime-picker .flatpickr-current-month .numInputWrapper {
        width: 66px !important;
    }

    .notice-datetime-picker .flatpickr-current-month input.cur-year {
        width: 66px !important;
        padding: 0 6px !important;
        text-align: center !important;
    }

    .notice-datetime-picker .flatpickr-current-month .numInputWrapper span {
        display: none !important;
    }

    .notice-datetime-picker .flatpickr-prev-month,
    .notice-datetime-picker .flatpickr-next-month {
        position: absolute !important;
        top: 5px !important;
        width: 34px !important;
        height: 34px !important;
        padding: 9px !important;
        border-radius: 9px !important;
        color: #64748b !important;
        fill: #64748b !important;
        z-index: 5 !important;
        box-sizing: border-box !important;
    }

    .notice-datetime-picker .flatpickr-prev-month:hover,
    .notice-datetime-picker .flatpickr-next-month:hover {
        background: #f1f5f9 !important;
        color: #2563eb !important;
        fill: #2563eb !important;
    }

    .notice-datetime-picker .flatpickr-prev-month {
        left: 5px !important;
        right: auto !important;
    }

    .notice-datetime-picker .flatpickr-next-month {
        left: auto !important;
        right: 5px !important;
    }

    .notice-datetime-picker .flatpickr-day {
        border-radius: 9px !important;
    }

    .notice-datetime-picker .flatpickr-day.flatpickr-disabled,
    .notice-datetime-picker .flatpickr-day.prevMonthDay.flatpickr-disabled,
    .notice-datetime-picker .flatpickr-day.nextMonthDay.flatpickr-disabled {
        color: #cbd5e1 !important;
        background: #f8fafc !important;
        border-color: transparent !important;
        filter: blur(0.7px) grayscale(1) !important;
        opacity: 0.45 !important;
        cursor: not-allowed !important;
        pointer-events: none !important;
    }

    .notice-datetime-picker .flatpickr-day.selected,
    .notice-datetime-picker .flatpickr-day.startRange,
    .notice-datetime-picker .flatpickr-day.endRange {
        background: #2563eb !important;
        border-color: #2563eb !important;
    }

    .notice-datetime-picker .flatpickr-time {
        position: relative !important;
        grid-column: 2 / 5 !important;
        grid-row: 1 / 3 !important;
        width: 212px !important;
        min-width: 212px !important;
        max-width: 212px !important;
        height: 100% !important;
        max-height: none !important;
        display: grid !important;
        grid-template-columns: 64px 78px 58px !important;
        align-items: start !important;
        justify-content: end !important;
        column-gap: 6px !important;
        margin-left: 0 !important;
        padding: var(--notice-time-top-offset, 44px) 0 0 !important;
        border: 0 !important;
        background: #fafafa !important;
        overflow: visible !important;
        box-sizing: border-box !important;
    }

    .notice-time-actions {
        position: absolute !important;
        top: 5px !important;
        left: 0 !important;
        width: 100% !important;
        height: 34px !important;
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
        z-index: 4 !important;
    }

    .notice-time-action {
        min-width: 0 !important;
        height: 34px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: 1px solid #d9e1ec !important;
        border-radius: 10px !important;
        background: #fff !important;
        color: #0f172a !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        letter-spacing: 0 !important;
        line-height: 1 !important;
        cursor: pointer !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
        transition: background 140ms ease, border-color 140ms ease, color 140ms ease, box-shadow 140ms ease, transform 140ms ease !important;
    }

    .notice-time-action:hover {
        border-color: #2563eb !important;
        background: #eff6ff !important;
        color: #1d4ed8 !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.12) !important;
    }

    .notice-time-action:active {
        transform: translateY(1px) !important;
        background: #dbeafe !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08) !important;
    }

    .notice-time-action:focus-visible {
        border-color: #2563eb !important;
        outline: none !important;
        background: #eff6ff !important;
        color: #1d4ed8 !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.16) !important;
    }

    .notice-time-action.is-done,
    .notice-time-action.is-done:hover,
    .notice-time-action.is-done:active,
    .notice-time-action.is-done:focus-visible {
        color: #0f172a !important;
    }

    .notice-datetime-picker .flatpickr-time .numInputWrapper,
    .notice-datetime-picker .flatpickr-time .flatpickr-am-pm,
    .notice-datetime-picker .flatpickr-time .flatpickr-time-separator {
        display: none !important;
    }

    .notice-time-wheel {
        position: relative !important;
        height: var(--notice-wheel-height, 230px) !important;
        min-height: var(--notice-wheel-height, 230px) !important;
        max-height: var(--notice-wheel-height, 230px) !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        scroll-snap-type: y mandatory !important;
        scrollbar-width: none !important;
        overscroll-behavior: contain !important;
        border: 1px solid #e3e6ea !important;
        border-radius: 12px !important;
        background: #fff !important;
        box-sizing: border-box !important;
    }

    .notice-time-wheel::-webkit-scrollbar {
        display: none !important;
    }

    .notice-time-wheel::before {
        content: "";
        position: sticky;
        top: var(--notice-wheel-center-offset, 92px);
        display: block;
        width: 100%;
        height: ${ROW_HEIGHT}px;
        margin-bottom: -${ROW_HEIGHT}px;
        border-top: 1px solid #dbeafe;
        border-bottom: 1px solid #dbeafe;
        background: #eff6ff;
        pointer-events: none;
        z-index: 0;
    }

    .notice-time-wheel-inner {
        padding: var(--notice-wheel-center-offset, 92px) 0 !important;
        position: relative !important;
        z-index: 1 !important;
    }

    .notice-time-option {
        height: ${ROW_HEIGHT}px !important;
        line-height: ${ROW_HEIGHT}px !important;
        text-align: center !important;
        color: #9ca3af !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        scroll-snap-align: center !important;
        user-select: none !important;
        transition: color 120ms ease, font-size 120ms ease, font-weight 120ms ease !important;
    }

    .notice-time-option.is-active {
        color: #1d4ed8 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
    }

    .notice-time-option.is-disabled {
        color: #cbd5e1 !important;
        filter: blur(0.7px) grayscale(1) !important;
        opacity: 0.45 !important;
        cursor: not-allowed !important;
        pointer-events: none !important;
    }

    @media (max-width: 540px) {
        .flatpickr-calendar.notice-datetime-picker {
            transform: scale(0.92);
            transform-origin: top left;
        }
    }
    `;
    document.head.appendChild(style);

    function clampIndex(index, data) {
        return Math.max(0, Math.min(data.length - 1, index));
    }

    function toTwelveHour(date) {
        const hour24 = date.getHours();
        const hour12 = hour24 % 12 || 12;

        return {
            hour: String(hour12).padStart(2, "0"),
            minute: String(date.getMinutes()).padStart(2, "0"),
            period: hour24 >= 12 ? "PM" : "AM"
        };
    }

    function toTwentyFourHour(hour, period) {
        const normalized = parseInt(hour, 10) % 12;
        return period === "PM" ? normalized + 12 : normalized;
    }

    function startOfDay(date) {
        const day = new Date(date);
        day.setHours(0, 0, 0, 0);
        return day;
    }

    function isToday(date) {
        return startOfDay(date).getTime() === startOfDay(new Date()).getTime();
    }

    function getMinimumSelectableDate() {
        const now = new Date();
        if (now.getSeconds() > 0 || now.getMilliseconds() > 0) {
            now.setMinutes(now.getMinutes() + 1);
        }
        now.setSeconds(0, 0);
        return now;
    }

    function clampToAvailableDate(date) {
        const candidate = date ? new Date(date) : new Date();
        const minimum = getMinimumSelectableDate();

        if (candidate < minimum) {
            return minimum;
        }

        return candidate;
    }

    function ensureSelectedDateIsAvailable(instance) {
        const selectedDate = instance.selectedDates[0];
        const inputDate = instance.input.value ? instance.parseDate(instance.input.value, instance.config.dateFormat) : null;
        const currentDate = selectedDate || inputDate;

        if (!currentDate) {
            return;
        }

        const availableDate = clampToAvailableDate(currentDate);
        if (availableDate.getTime() === currentDate.getTime()) {
            return;
        }

        const calendar = instance.calendarContainer;
        if (calendar) {
            calendar.noticeWheelSyncing = true;
        }

        instance.setDate(availableDate, true, instance.config.dateFormat);

        if (calendar) {
            calendar.noticeWheelSyncing = false;
        }
    }

    function refreshPickerForCurrentTime(instance) {
        instance.set("minDate", "today");
        ensureSelectedDateIsAvailable(instance);
        syncWheelsFromDate(instance, false);
        refreshDisabledTimeOptions(instance);
    }

    function bindSubmitTimeRefresh(instance) {
        const form = instance.input.form;
        if (!form || form.noticeTimeRefreshBound) {
            return;
        }

        form.noticeTimeRefreshBound = true;
        form.addEventListener("submit", function () {
            document.querySelectorAll(".flatpickr").forEach(function (input) {
                if (input._flatpickr) {
                    refreshPickerForCurrentTime(input._flatpickr);
                }
            });
        });
    }

    function positionCalendarBelowInput(instance) {
        const calendar = instance.calendarContainer;
        const input = instance.input;
        if (!calendar || !input) {
            return;
        }

        const rect = input.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

        calendar.style.position = "absolute";
        calendar.style.left = `${Math.round(rect.left + scrollLeft)}px`;
        calendar.style.top = `${Math.round(rect.bottom + scrollTop)}px`;
        calendar.style.right = "auto";
        calendar.style.bottom = "auto";
        calendar.style.transform = "none";
        calendar.style.zIndex = "9999";
    }

    function buildWheel(data, name, instance) {
        const wheel = document.createElement("div");
        wheel.className = `notice-time-wheel ${name}-wheel`;
        wheel.dataset.value = data[0];

        const inner = document.createElement("div");
        inner.className = "notice-time-wheel-inner";

        data.forEach((value, index) => {
            const item = document.createElement("div");
            item.className = "notice-time-option";
            item.textContent = value;
            item.dataset.value = value;
            item.dataset.index = String(index);
            item.addEventListener("click", function () {
                if (item.classList.contains("is-disabled")) {
                    return;
                }

                setWheelValue(wheel, data, value, true);
                syncTimeFromWheels(instance);
            });
            inner.appendChild(item);
        });

        wheel.appendChild(inner);

        wheel.addEventListener("wheel", function (event) {
            event.preventDefault();

            const delta = normalizeWheelDelta(event);
            wheel.wheelDelta = (wheel.wheelDelta || 0) + delta;

            if (Math.abs(wheel.wheelDelta) < WHEEL_DELTA_THRESHOLD) {
                return;
            }

            const now = Date.now();
            if (now - (wheel.lastWheelStep || 0) < WHEEL_STEP_COOLDOWN) {
                return;
            }

            const direction = wheel.wheelDelta > 0 ? 1 : -1;
            wheel.wheelDelta = 0;
            wheel.lastWheelStep = now;

            stepWheel(wheel, data, direction);
            syncTimeFromWheels(instance);
        }, { passive: false });

        wheel.addEventListener("scroll", function () {
            clearTimeout(wheel.scrollTimer);
            wheel.scrollTimer = setTimeout(function () {
                snapWheel(wheel, data, true);
                syncTimeFromWheels(instance);
            }, 90);
        }, { passive: true });

        return wheel;
    }

    function buildActionButton(label, className, onClick) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = `notice-time-action ${className}`;
        button.textContent = label;
        button.addEventListener("click", function (event) {
            event.preventDefault();
            event.stopPropagation();
            onClick();
        });

        return button;
    }

    function buildActionBar(instance) {
        const actions = document.createElement("div");
        actions.className = "notice-time-actions";
        actions.append(
            buildActionButton("Cancel", "is-cancel", function () {
                restoreOpenValue(instance);
                instance.close();
            }),
            buildActionButton("Done", "is-done", function () {
                syncTimeFromWheels(instance);
                instance.close();
            })
        );

        return actions;
    }

    function normalizeWheelDelta(event) {
        if (event.deltaMode === WheelEvent.DOM_DELTA_LINE) {
            return event.deltaY * 16;
        }

        if (event.deltaMode === WheelEvent.DOM_DELTA_PAGE) {
            return event.deltaY * ROW_HEIGHT;
        }

        return event.deltaY;
    }

    function stepWheel(wheel, data, direction) {
        const currentIndex = clampIndex(Math.round(wheel.scrollTop / ROW_HEIGHT), data);
        let nextIndex = clampIndex(currentIndex + direction, data);

        while (nextIndex >= 0 && nextIndex < data.length) {
            const option = wheel.querySelector(`.notice-time-option[data-index="${nextIndex}"]`);
            if (!option || !option.classList.contains("is-disabled")) {
                break;
            }
            nextIndex += direction;
        }

        nextIndex = findAvailableIndex(wheel, data, clampIndex(nextIndex, data));
        setWheelValue(wheel, data, data[nextIndex], true);
    }

    function setWheelValue(wheel, data, value, smooth) {
        const index = clampIndex(data.indexOf(value), data);
        wheel.dataset.value = data[index];
        wheel.scrollTo({
            top: index * ROW_HEIGHT,
            behavior: smooth ? "smooth" : "auto"
        });
        markActiveOption(wheel, index);
    }

    function snapWheel(wheel, data, smooth) {
        const index = clampIndex(Math.round(wheel.scrollTop / ROW_HEIGHT), data);
        const nextIndex = findAvailableIndex(wheel, data, index);
        setWheelValue(wheel, data, data[nextIndex], smooth);
    }

    function findAvailableIndex(wheel, data, preferredIndex) {
        const preferredOption = wheel.querySelector(`.notice-time-option[data-index="${preferredIndex}"]`);
        if (!preferredOption || !preferredOption.classList.contains("is-disabled")) {
            return preferredIndex;
        }

        for (let offset = 1; offset < data.length; offset += 1) {
            const nextIndex = preferredIndex + offset;
            const nextOption = wheel.querySelector(`.notice-time-option[data-index="${nextIndex}"]`);
            if (nextOption && !nextOption.classList.contains("is-disabled")) {
                return nextIndex;
            }

            const previousIndex = preferredIndex - offset;
            const previousOption = wheel.querySelector(`.notice-time-option[data-index="${previousIndex}"]`);
            if (previousOption && !previousOption.classList.contains("is-disabled")) {
                return previousIndex;
            }
        }

        return preferredIndex;
    }

    function markActiveOption(wheel, activeIndex) {
        wheel.querySelectorAll(".notice-time-option").forEach(function (item, index) {
            item.classList.toggle("is-active", index === activeIndex);
        });
    }

    function getWheelValue(calendar, selector, fallback) {
        const wheel = calendar.querySelector(selector);
        return wheel ? wheel.dataset.value || fallback : fallback;
    }

    function getCandidateTime(instance, overrideName, overrideValue) {
        const calendar = instance.calendarContainer;
        const selectedDate = instance.selectedDates[0] ? new Date(instance.selectedDates[0]) : new Date();
        const hour = overrideName === "hour" ? overrideValue : getWheelValue(calendar, ".hour-wheel", "12");
        const minute = overrideName === "minute" ? overrideValue : getWheelValue(calendar, ".minute-wheel", "00");
        const period = overrideName === "period" ? overrideValue : getWheelValue(calendar, ".period-wheel", "AM");

        selectedDate.setHours(toTwentyFourHour(hour, period), parseInt(minute, 10), 0, 0);
        return selectedDate;
    }

    function isPastTimeOption(instance, wheelName, value) {
        const date = instance.selectedDates[0] ? new Date(instance.selectedDates[0]) : new Date();
        if (!isToday(date)) {
            return false;
        }

        return getCandidateTime(instance, wheelName, value) < getMinimumSelectableDate();
    }

    function refreshDisabledTimeOptions(instance) {
        const calendar = instance.calendarContainer;
        if (!calendar) {
            return;
        }

        [
            { selector: ".hour-wheel", name: "hour" },
            { selector: ".minute-wheel", name: "minute" },
            { selector: ".period-wheel", name: "period" }
        ].forEach(function (config) {
            const wheel = calendar.querySelector(config.selector);
            if (!wheel) {
                return;
            }

            wheel.querySelectorAll(".notice-time-option").forEach(function (item) {
                item.classList.toggle("is-disabled", isPastTimeOption(instance, config.name, item.dataset.value));
            });
        });
    }

    function syncWheelLayout(instance) {
        const calendar = instance.calendarContainer;
        if (!calendar) {
            return;
        }

        const monthHeader = calendar.querySelector(".flatpickr-months");
        const calendarBody = calendar.querySelector(".flatpickr-innerContainer");
        const timeContainer = calendar.querySelector(".flatpickr-time");

        if (!monthHeader || !calendarBody || !timeContainer) {
            return;
        }

        const headerHeight = Math.round(monthHeader.getBoundingClientRect().height || 44);
        const bodyHeight = Math.round(calendarBody.getBoundingClientRect().height || 230);
        const centerOffset = Math.max(0, (bodyHeight - ROW_HEIGHT) / 2);

        timeContainer.style.setProperty("--notice-time-top-offset", `${headerHeight}px`);
        timeContainer.querySelectorAll(".notice-time-wheel").forEach(function (wheel) {
            wheel.style.setProperty("--notice-wheel-height", `${bodyHeight}px`);
            wheel.style.setProperty("--notice-wheel-center-offset", `${centerOffset}px`);
        });
    }

    function syncTimeFromWheels(instance) {
        const calendar = instance.calendarContainer;
        if (!calendar || calendar.noticeWheelSyncing) {
            return;
        }

        const hour = getWheelValue(calendar, ".hour-wheel", "12");
        const minute = getWheelValue(calendar, ".minute-wheel", "00");
        const period = getWheelValue(calendar, ".period-wheel", "AM");
        const baseDate = instance.selectedDates[0] ? new Date(instance.selectedDates[0]) : new Date();

        baseDate.setHours(toTwentyFourHour(hour, period), parseInt(minute, 10), 0, 0);
        const availableDate = clampToAvailableDate(baseDate);
        calendar.noticeWheelSyncing = true;
        instance.setDate(availableDate, true, instance.config.dateFormat);
        calendar.noticeWheelSyncing = false;
        syncWheelsFromDate(instance, false);
        refreshDisabledTimeOptions(instance);
    }

    function rememberOpenValue(instance) {
        instance.noticeOpenDate = instance.selectedDates[0] ? new Date(instance.selectedDates[0]) : null;
        instance.noticeOpenInputValue = instance.input.value;
    }

    function restoreOpenValue(instance) {
        const calendar = instance.calendarContainer;
        if (calendar) {
            calendar.noticeWheelSyncing = true;
        }

        if (instance.noticeOpenDate) {
            instance.setDate(new Date(instance.noticeOpenDate), true, instance.config.dateFormat);
        } else {
            instance.clear();
            instance.input.value = instance.noticeOpenInputValue || "";
        }

        if (calendar) {
            calendar.noticeWheelSyncing = false;
        }

        syncWheelsFromDate(instance, false);
    }

    function syncWheelsFromDate(instance, smooth) {
        const calendar = instance.calendarContainer;
        if (!calendar || calendar.noticeWheelSyncing) {
            return;
        }

        const date = instance.selectedDates[0];
        if (!date) {
            return;
        }

        const availableDate = clampToAvailableDate(date);
        if (availableDate.getTime() !== date.getTime()) {
            calendar.noticeWheelSyncing = true;
            instance.setDate(availableDate, true, instance.config.dateFormat);
            calendar.noticeWheelSyncing = false;
        }

        const time = toTwelveHour(availableDate);
        setWheelValue(calendar.querySelector(".hour-wheel"), hoursData, time.hour, smooth);
        setWheelValue(calendar.querySelector(".minute-wheel"), minutesData, time.minute, smooth);
        setWheelValue(calendar.querySelector(".period-wheel"), periodsData, time.period, smooth);
        refreshDisabledTimeOptions(instance);
    }

    function injectCustomTimeWheels(instance) {
        const calendar = instance.calendarContainer;
        if (!calendar) {
            return;
        }

        calendar.classList.add("notice-datetime-picker");

        let timeContainer = calendar.querySelector(".flatpickr-time");
        if (!timeContainer) {
            timeContainer = document.createElement("div");
            timeContainer.className = "flatpickr-time";
            calendar.appendChild(timeContainer);
        }

        if (!timeContainer.querySelector(".notice-time-wheel")) {
            timeContainer.innerHTML = "";
            timeContainer.append(
                buildActionBar(instance),
                buildWheel(hoursData, "hour", instance),
                buildWheel(minutesData, "minute", instance),
                buildWheel(periodsData, "period", instance)
            );
        } else if (!timeContainer.querySelector(".notice-time-actions")) {
            timeContainer.prepend(buildActionBar(instance));
        }

        syncWheelLayout(instance);
        syncWheelsFromDate(instance, false);

        requestAnimationFrame(function () {
            syncWheelLayout(instance);
        });
    }

    flatpickr(".flatpickr", {
        enableTime: true,
        noCalendar: false,
        time_24hr: false,
        allowInput: false,
        minDate: "today",
        dateFormat: "Y-m-d h:i K",
        monthSelectorType: "dropdown",
        minuteIncrement: 1,
        appendTo: document.body,
        position: "below left",

        onReady: function (selectedDates, dateStr, instance) {
            refreshPickerForCurrentTime(instance);
            bindSubmitTimeRefresh(instance);
            injectCustomTimeWheels(instance);

            const observer = new MutationObserver(function () {
                injectCustomTimeWheels(instance);
            });

            observer.observe(instance.calendarContainer, { childList: true });
            instance.noticeWheelObserver = observer;
        },

        onOpen: function (selectedDates, dateStr, instance) {
            refreshPickerForCurrentTime(instance);
            rememberOpenValue(instance);
            injectCustomTimeWheels(instance);
        },

        onMonthChange: function (selectedDates, dateStr, instance) {
            injectCustomTimeWheels(instance);
        },

        onYearChange: function (selectedDates, dateStr, instance) {
            injectCustomTimeWheels(instance);
        },

        onChange: function (selectedDates, dateStr, instance) {
            refreshPickerForCurrentTime(instance);
            injectCustomTimeWheels(instance);
            syncWheelsFromDate(instance, true);
        }
    });
});
