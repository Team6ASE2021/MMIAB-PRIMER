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
        if(nr_childs[i].htmlFor != undefined &&
                nr_childs[i].htmlFor.includes("recipients-") &&
                nr_childs[i].htmlFor.includes("-recipient")) 
        {
            nr_childs[i].htmlFor = "recipients-" + new_id + "-recipient";
        }
        if(nr_childs[i].id.includes("recipients-") &&
                nr_childs[i].id.includes("-recipient")) 
        {
            nr_childs[i].id = "recipients-" + new_id + "-recipient";
            nr_childs[i].name = "recipients-" + new_id + "-recipient";
        }
        if(nr_childs[i].classList.contains("recipient-field")) {
            var a_tags = nr_childs[i].getElementsByTagName("a");
            if (a_tags.length == 0) {
                if(new_id > 0) {
                    div = document.createElement("div");
                    div.classList.add("recipient-delete");
                    ref = document.createElement("a");
                    ref.href = "javascript: removeRecipient(" + new_id + ");";
                    ref.text = "x";
                    div.appendChild(ref);
                    nr_childs[i].appendChild(div);
                }
            } else {
                a_tags[0].href = "javascript: removeRecipient(" + new_id + ");";
            }

            if(new_id > 0) {
                var select_tags = nr_childs[i].getElementsByTagName("select");
                select_tags[0].disabled = false;
                var input_tags = nr_childs[i].getElementsByTagName("input");
                nr_childs[i].removeChild(input_tags[0]);
            }
            
        }
    }
}

function removeRecipient(id){
    var form_to_remove = document.getElementById("recipients-" + id + "-form");
    document.getElementById("recipient-list").removeChild(form_to_remove);

    var recipients = document.getElementById("recipient-list").getElementsByClassName("recipient-form");
    for(let i = 0; i < recipients.length; i++){
        console.log(recipients.length);
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
}

