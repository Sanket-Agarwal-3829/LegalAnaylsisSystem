


$('#file_form').submit(function(event){
        event.preventDefault();
        var formData = new FormData(this); //get data of form elements for submission
        // formData.append('sg_id', '{{ sg_id }}'); //add additional data to form's data
        for (var pair of formData.entries()) {
            console.log(pair[0]+ ', ' + pair[1]);
            console.log("Helo")

        }
        console.log("Hel'o") 

        $.ajax({
            url: "http://127.0.0.1:8000/legal/new-judgement",
            type: "POST",
            enctype: 'multipart/form-data',
            data: formData,
            dataType: 'json',
            contentType: false,
            cache : false,
        processData: false,
            success: function (data) {
                console.log(data)
                if (data['summary']=="None"){
                   return alert("Already Present")
                }
                else
                {    
                    $('.textarea-summary').html(data['summary'])
                    for (const property in data['NER']) {
                        
                        const iidiv = document.createElement('div')
                        iidiv.className = "NER-keywords-inner"
                        const iiidiv = document.createElement('div')
                        iiidiv.className = "NER-keyword-inner1"
                        
                        iiidiv.style.display = "flex"
                        iiidiv.style.width = "97%"
                        iiidiv.style.flexWrap = "wrap"
                        iiidiv.style.gap = "0.3rem"
                        const label = document.createElement('label')
                        label.innerHTML = property + ':' 
                        console.log(`${property}:`);
                        for (const p in data['NER'][property]) {
                            console.log(data['NER'][property][p])
                            $(`<span>${ data['NER'][property][p]}</span>`).appendTo(iiidiv)
                        }
                        
                        iidiv.append(label)
                        iidiv.append(iiidiv)
                        document.querySelector('div.NER-keywords').append(iidiv)

                    
                
                        
                    }
                }
        //    return alert("Hey");
                
            }
        });
    });

    

    