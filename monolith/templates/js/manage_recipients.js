function renameRecipientContent(recipient, new_id){
    recipient.id = "recipients-" + new_id + "-form";
    var nr_childs = recipient.getElementsByTagName("*");
    for(let i = 0; i<nr_childs.length; i++){
        if(nr_childs[i].id.includes("recipients-") &&
                nr_childs[i].id.includes("-csrf_token")) 
        {
            nr_childs[i].id = "recipients-" + new_id + "-csrf_token";
            nr_childs[i].name = "recipients-" + new_id + "-csrf_token";
        }
        /*
        if(nr_childs[i].htmlFor != undefined &&
                nr_childs[i].htmlFor.includes("recipients-") &&
                nr_childs[i].htmlFor.includes("-recipient")) 
        {
            nr_childs[i].htmlFor = "recipients-" + new_id + "-recipient";
        }
        */
        if(nr_childs[i].id.includes("recipients-") &&
                nr_childs[i].id.includes("-recipient")) 
        {
            nr_childs[i].id = "recipients-" + new_id + "-recipient";
            nr_childs[i].name = "recipients-" + new_id + "-recipient";
        }
        if(nr_childs[i].id.includes("recipients-") &&
                nr_childs[i].id.includes("-search")) 
        {
            nr_childs[i].id = "recipients-" + new_id + "-search";
            nr_childs[i].name = "recipients-" + new_id + "-search";
        }
        if(nr_childs[i].classList.contains("search-button")) {
            nr_childs[i].onclick = function() { trigger_update(new_id); }
        }
        if(nr_childs[i].classList.contains("recipient-field")) {
        }
        if(nr_childs[i].classList.contains("fields-container")) {
            if(new_id > 0) {
                var select_tags = nr_childs[i].getElementsByTagName("select");
                select_tags[0].disabled = false;
                var input_tags = nr_childs[i].getElementsByTagName("input");
                for(let i = 0; i < input_tags.length; i++) {
                    if(input_tags[i].type == 'hidden')
                        nr_childs[i].removeChild(input_tags[i]);
                }
            }

            var close = nr_childs[i].getElementsByClassName("close-button");
            if (close.length == 0) {
                    btn = document.createElement("button");
                    btn.classList.add("btn");
                    btn.classList.add("btn-danger");
                    btn.classList.add("close-button");
                    btn.type="button";
                    btn.onclick = function() { removeRecipient(new_id);};
                    nr_childs[i].appendChild(btn);
            } else {
                close[0].onclick = function() { removeRecipient(new_id);};
                if(new_id > 0) {
                    close[0].disabled = false;
                }
            }
        }
    }
}

function removeRecipient(id){
    var form_to_remove = document.getElementById("recipients-" + id + "-form");
    document.getElementById("recipient-list").removeChild(form_to_remove);

    var recipients = document.getElementById("recipient-list").getElementsByClassName("recipient-form");
    for(let i = 0; i < recipients.length; i++){
        renameRecipientContent(recipients[i], i);
    }
}

function addRecipient(){
    var recipients = document.getElementById("recipient-list");
    var childs = recipients.getElementsByClassName("recipient-form")
    var new_id = childs.length
    var new_recipient = childs[0].cloneNode(true);
    renameRecipientContent(new_recipient, new_id);
    recipients.appendChild(new_recipient);

    document.getElementById("recipients-" + new_id + "-search").value = ""
    trigger_update(new_id)
}

