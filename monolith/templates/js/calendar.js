function populate_day_names(container) {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    var row = container.querySelector('#names-row');
    var monday = row.firstElementChild
    monday.querySelector(".day-name").textContent = days[0];
    for(let i = 1; i < 7; i++) {
        var new_day = monday.cloneNode(true);
        new_day.querySelector(".day-name").textContent = days[i];
        row.appendChild(new_day);
    }
}

function set_sent_received(day, sent, received, ind) {
    if(sent[ind] === 0) day.querySelector(".sent-badge").classList.add("invisible");
    else {
        day.querySelector(".sent-badge").classList.remove("invisible");
        day.querySelector(".sent-count").textContent = sent[ind];
    }

    if(received[ind] === 0) day.querySelector(".received-badge").classList.add("invisible");
    else {
        day.querySelector(".received-badge").classList.remove("invisible");
        day.querySelector(".received-count").textContent = received[ind]; 
    }
}

function populate_first_row(container, starts_with, sent, received){

    var row = container.querySelector('#first-row');
    var day_1= row.firstElementChild
    day_1.querySelector(".day-number").textContent = "1";
    set_sent_received(day_1, sent, received, 0);

    fst_row_days= 7 - starts_with;
    for(let i = 0; i < fst_row_days - 1; i++) {
        var new_day = day_1.cloneNode(true);
        new_day.querySelector(".day-number").textContent = (i + 2);
        set_sent_received(new_day, sent, received, i+1);
        row.appendChild(new_day);
    }

    return fst_row_days;
}

function populate_full_rows(container, days_in_month, day_num, sent, received){

    var full_rows = ~~((days_in_month - fst_row_days) / 7);
    var ref_row = container.querySelector('#full-row-0');
    ref_row.id = "full-row-" + (full_rows - 1);

    for(let i=0; i<full_rows; i++) {
        var row;
        if(i < full_rows - 1) {
            new_row = ref_row.cloneNode(true);
            new_row.id = "full-row-" + i;
            container.insertBefore(new_row, ref_row);
            row = new_row;
        } else row = ref_row;

        var day_1 = row.firstElementChild;
        set_sent_received(day_1, sent, received, day_num);
        day_1.querySelector(".day-number").textContent = ++day_num;
        for(let i = 1; i < 7; i++) {
            var new_day = day_1.cloneNode(true);
            set_sent_received(new_day, sent, received, day_num);
            new_day.querySelector(".day-number").textContent = ++day_num;
            row.appendChild(new_day);
        }
    }

    return full_rows * 7;

}

function populate_last_row(container, days_in_month, day_num, sent, received){

    var last_row_days = days_in_month - day_num;

    var row = container.querySelector('#last-row');
    var day_1 = row.firstElementChild
    set_sent_received(day_1, sent, received, day_num);
    day_1.querySelector(".day-number").textContent = ++day_num;

    for(let i = 0; i < last_row_days - 1; i++) {
        var new_day = day_1.cloneNode(true);
        set_sent_received(new_day, sent, received, day_num);
        new_day.querySelector(".day-number").textContent = ++day_num;
        row.appendChild(new_day);
    }
}

function populate_month_nav(container, calendar) {
    container.querySelector(".next-button").onclick = function() { 
        location.href=
            "/timeline/month/" + 
            (calendar.month == 12 ? calendar.year + 1 : calendar.year) + "/" + 
            (calendar.month == 12 ? 1 : calendar.month + 1); 
    };
    container.querySelector(".prev-button").onclick = function() { 
        location.href=
            "/timeline/month/" + 
            (calendar.month == 1 ? calendar.year - 1 : calendar.year) + "/" + 
            (calendar.month == 1 ? 12 : calendar.month - 1); 
    };
    container.querySelector(".month-year-desc").textContent = calendar.month_name + " " + calendar.year;
}

function populate_day_nav(container, calendar) {
    container.querySelector(".next-button").onclick = function() { 
        location.href="/timeline/" + 
        calendar.tomorrow[0] + "/" + 
        calendar.tomorrow[1] + "/" + 
        calendar.tomorrow[2];
    };
    container.querySelector(".prev-button").onclick = function() { 
        location.href="/timeline/" + 
        calendar.yesteray[0] + "/" + 
        calendar.yesteray[1] + "/" + 
        calendar.yesteray[2];
    };
    container.querySelector(".date-desc").textContent = calendar.today[2] + "/" + calendar.today[1] + "/" + calendar.today[0];

}

function populate_calendar(calendar){
    console.log(calendar.sent);
    console.log(calendar.received);

    var container = document.getElementsByClassName("container")[0];
    populate_day_names(container);
    var fst_row_days = populate_first_row(container, calendar.starts_with, calendar.sent, calendar.received);
    var full_rows_days = populate_full_rows(container, calendar.days_in_month, fst_row_days, calendar.sent, calendar.received);
    populate_last_row(container, calendar.days_in_month, fst_row_days + full_rows_days, calendar.sent, calendar.received);
    populate_month_nav(container, calendar);
}
