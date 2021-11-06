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

function populate_first_row(container, starts_with){

    var row = container.querySelector('#first-row');
    var day_1= row.firstElementChild
    day_1.querySelector(".day-number").textContent = "1";

    fst_row_days= 7 - starts_with;
    for(let i = 0; i < fst_row_days - 1; i++) {
        var new_day = day_1.cloneNode(true);
        new_day.querySelector(".day-number").textContent = (i + 2);
        row.appendChild(new_day);
    }

    return fst_row_days;
}

function populate_full_rows(container, days_in_month, day_num){

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
        day_1.querySelector(".day-number").textContent = ++day_num;
        for(let i = 1; i < 7; i++) {
            var new_day = day_1.cloneNode(true);
            new_day.querySelector(".day-number").textContent = ++day_num;
            row.appendChild(new_day);
        }
    }

    return full_rows * 7;

}

function populate_last_row(container, days_in_month, day_num){

    var last_row_days = days_in_month - day_num;

    var row = container.querySelector('#last-row');
    var day_1 = row.firstElementChild
    day_1.querySelector(".day-number").textContent = ++day_num;

    for(let i = 0; i < last_row_days - 1; i++) {
        var new_day = day_1.cloneNode(true);
        new_day.querySelector(".day-number").textContent = ++day_num;
        row.appendChild(new_day);
    }
}

function populate_calendar(calendar){

    var container = document.getElementsByClassName("container")[0]
    populate_day_names(container);
    var fst_row_days = populate_first_row(container, calendar.starts_with);
    var full_rows_days = populate_full_rows(container, calendar.days_in_month, fst_row_days);
    populate_last_row(container, calendar.days_in_month, fst_row_days + full_rows_days);

}
