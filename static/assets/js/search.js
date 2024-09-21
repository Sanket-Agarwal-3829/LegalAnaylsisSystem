const modal = document.querySelector(".custom-modal");
const trigger = document.querySelector(".trigger");
const closeButton = document.querySelector(".close-button");

document.querySelector(".dashboard-wrapper-1").addEventListener("mouseenter",()=>{
    window.scrollTo({ left: 0, top: document.body.scrollHeight, behavior: "smooth" });
})

function toggleModal() {
    // console.log(property)
    modal.classList.toggle("custom-show-modal");
}

function windowOnClick(event) {
    if (event.target === modal) {
        toggleModal();
    }
}

// TESTER = document.getElementById('tester');
// console.log( Plotly.BUILD );
// var config = {responsive: true}
// Plotly.newPlot( TESTER, [{
//     x: [1, 2, 3, 4, 5],
//     y: [1, 2, 4, 8, 16] }], { 
//     margin: { t: 0 } } ,config);
    
//     TESTER.on('plotly_click', function(data){
//     	alert('did you just click on me?!')
//     })

/* Current Plotly.js version */

// trigger.addEventListener("click", toggleModal);
closeButton.addEventListener("click", toggleModal);
window.addEventListener("click", windowOnClick);

document.querySelector("#folder_title").addEventListener("focus",(e)=>{
    document.getElementById('folder_title').classList.remove('is-invalid')                

})

function createFolder(){
    var title = document.getElementById('folder_title').value;
    $.ajax({
        headers: { "X-CSRFToken": $.cookie("csrftoken") },
        url: 'http://127.0.0.1:8000/legal/create-folder',
        type: 'POST',
        data: {"title":title,"judegments":Array.from(document.querySelectorAll(".title-name-custom")).map(x => x.innerHTML),'csrfmiddlewaretoken':$.cookie("csrftoken")},
        dataType: 'json',
        success: function (data) {
            console.log(data)
            if (data['is_valid']){
                document.getElementById('folder_title').classList.toggle('is-invalid')                
                document.querySelector('.folder_ERROR').innerHTML = data['msg']
            }
            
        }}
        )
}

function summarySearch() {
    
    const summry =$(".summary").val();
    
    document.querySelectorAll('.dashboard-wrapper-2 .row div.col-12').forEach(
        div=>
        div.remove()
    )

    // NER['csrfmiddlewaretoken'] = $.cookie("csrftoken")
    $.ajax({
        headers: { "X-CSRFToken": $.cookie("csrftoken") },
        url: 'http://127.0.0.1:8000/legal/summary',
        type: 'POST',
        data: {"summary":summry,'csrfmiddlewaretoken':$.cookie("csrftoken")},
        dataType: 'json',
        success: function (data) {
            console.log("data")
            
            for (const property in data['data']){
                const div1 = document.createElement('div')
                div1.className = "col-12 col-sm-6 col-xl-4 mb-4"
                const div2 = document.createElement('div')
                div2.className = "card border-0 shadow"
                const div3 = document.createElement('div')
                div3.className = "card-body"
                const div4 = document.createElement('div')
                div4.className = "judgement-title"
                const div5 = document.createElement('div')
                const div6 = document.createElement('div')
                div5.innerHTML = property
                div5.className = "title-name-custom"
                div6.className = "judgement-info"
                const div7 = document.createElement('div')
                div7.className = "icon-wrapper"
                const button1 = document.createElement('button')
                button1.className = "btn"
                
                const div8 = document.createElement('div')
                div8.className = "icon-wrapper"
                const button2 = document.createElement('button')
                button2.className = "btn trigger"
    
                const div9 = document.createElement('div')
                const button3 = document.createElement('button')
                button3.className = "btn"
                button3.innerHTML = Math.round( data['data'][property]) +"%"
                div1.append(div2)
                div2.append(div3)
                div3.append(div4)
                div4.append(div5)
                div4.append(div6)
                div6.append(div7)
                div7.append(button1)
                
                var img1 = document.createElement('img')
                img1.src = "../../static/assets/img/download-solid.svg"
                img1.className = "icon-custom"
                var url = document.createElement('a')
                // {% url 'download' document.id %}
                url.href = "http://127.0.0.1:8000/legal/download/"+property

                var img2 = document.createElement('img')
                img2.src = "../../static/assets/img/book-bookmark-solid.svg"
                img2.className = "icon-custom"
    
                div6.append(div8)
                div8.append(button2)
                button2.append(img2); 
                button2.addEventListener("click", ()=>{
                    console.log("Heelo j")
                    $("body").addClass("loading");
                    var xhr = new XMLHttpRequest();
                    // xhr.setRequestHeader("X-CSRFToken",$.cookie("csrftoken"))
                    xhr.open('GET','http://127.0.0.1:8000/legal/view-pdf/'+property+".PDF",true);
                    xhr.responseType = 'blob';

                            xhr.onload = function(e){
                                console.log("Hello")
                                    if (this.status == 200) {
                                        var url = window.URL.createObjectURL(new Blob([this.response], {type: 'application/pdf'}));
                                        document.querySelector("iframe").src = url
                                        
                                        // a.href = url;
                                        // a.download = 'report.pdf';
                                        // a.click();
                                        window.URL.revokeObjectURL(url);
                                        $('body').removeClass("loading"); //removing the loading spinner class
                                    }else{
                                        $('body').removeClass("loading") //removing the loading spinner class
                                        console.log(this.status);
                                        alert('Download failed...!  Please Try again!!!');
                                    }
                                };
                                xhr.send();
                                document.querySelector(".model-judgement-title").innerHTML = property

                    // $.ajax({
                    //     headers: { "X-CSRFToken": $.cookie("csrftoken") },
                    //     url: "http://127.0.0.1:8000/legal/view-pdf",
                        
                    //     responseType: 'arraybuffer',
            
                    //     success: function (data) {
                    //         var arrBuffer = base64ToArrayBuffer(data);
                    //         console.log(arrBuffer)
                    //         var blob = new Blob([data], { type: 'application/pdf' });
                    //         console.log(blob)
                    //         var fileURL = window.URL.createObjectURL(blob);
                    //         window.open(fileURL,'_blank');
                    //         // var file = window.URL.createObjectURL(this.response);
                    //         // var link = document.createElement('a');
                    //         // link.href = window.URL.createObjectURL(blob);
                    //         // link.download = "Filename.pdf";
                    //         // link.click();
                            
                    //         document.querySelector("iframe").src = fileURL
                    //         console.log(typeof(data))
                    //         console.log(( new Uint8Array(data)))

                    //     }
                    // })
                    modal.classList.toggle("custom-show-modal");
                    console.log(property)
                })

                // <a href="{% url 'download' document.id %}">Download</a>
                div6.append(div9)
                div9.append(button3)
    
                button1.append(url);
                url.append(img1) 
                
                document.querySelector('.dashboard-wrapper-2 .row').append(div1)
                
            }
        }
    });
}
function base64ToArrayBuffer(data) {
    var binaryString =  window.btoa(unescape(encodeURIComponent(data)))
    var binaryLen = binaryString.length;
    var bytes = new Uint8Array(binaryLen);
    for (var i = 0; i < binaryLen; i++) {
        var ascii = binaryString.charCodeAt(i);
        bytes[i] = ascii;
    }
    return bytes;
};

function downloadZip(){
// var xmlHttp = new XMLHttpRequest();
// xmlHttp.open("POST", "http://127.0.0.1:8000/legal/download_zip", true);
// xmlHttp.setRequestHeader("Content-type","application/json");
// xmlHttp.setRequestHeader("Access-Control-Allow-Origin", "*");
// xmlHttp.responseType= 'blob';
// xmlHttp.setRequestHeader("X-CSRFToken",$.cookie("csrftoken"))
// var fm = new FormData()
// fm.append('judegments',Array.from(document.querySelectorAll(".title-name-custom")).map(x => x.innerHTML))
// fm.append('user', 'person');
// xmlHttp.onreadystatechange = function() {
    
        // const downloadUrl = window.URL.createObjectURL(xmlHttp.response);
        // const link = document.createElement('a');
        // link.setAttribute('href', downloadUrl);
        // link.setAttribute('download', `filename.zip`);
        // link.style.display = 'none';
        // document.body.appendChild(link);
        // link.click();
        // window.URL.revokeObjectURL(link.href);
        // document.body.removeChild(link);
    
// }
// xmlHttp.responseType = "arraybuffer";
// xmlHttp.send(fm);

    $.ajax({
        headers: { "X-CSRFToken": $.cookie("csrftoken") },
        url: 'http://127.0.0.1:8000/legal/download_zip',
        type: 'POST',
        // responseType:'arraybuffer',
        data: {"judegments":Array.from(document.querySelectorAll(".title-name-custom")).map(x => x.innerHTML),'csrfmiddlewaretoken':$.cookie("csrftoken")},
        // dataType: 'json',
        xhrFields:{
            responseType: 'blob'
        },
        success: function (data) {
            console.log(data)
            const downloadUrl = window.URL.createObjectURL(data);
            const link = document.createElement('a');
            link.setAttribute('href', downloadUrl);
            link.setAttribute('download', `filename.zip`);
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            window.URL.revokeObjectURL(link.href);
            document.body.removeChild(link);
            // if (data['is_valid']){
            //     document.getElementById('folder_title').classList.toggle('is-invalid')                
            //     document.querySelector('.folder_ERROR').innerHTML = data['msg']
            // }
            
        }}
        )
}
function get_search() {
    var NER = {}
    // console.log(e)
    document.querySelectorAll('.dashboard-wrapper-2 .row div.col-12').forEach(
        div=>
        div.remove()
    )
    document.querySelector(".dashboard-wrapper-1").querySelectorAll('.row').forEach(
        row=>{
            if(row.querySelectorAll('.records .item').length){
            
                NER[row.querySelector('h4').innerHTML] = []

                row.querySelectorAll('.records .item').forEach(
                    item=>{
                        NER[row.querySelector('h4').innerHTML].push(item.innerHTML)
                    }
                )
        }
        }
    )
    // NER['csrfmiddlewaretoken'] = $.cookie("csrftoken")

    
    console.log(NER)
    $.ajax({
        headers: { "X-CSRFToken": $.cookie("csrftoken") },
        url: 'http://127.0.0.1:8000/legal/',
        type: 'POST',
        data: NER,
        dataType: 'json',
        success: function (data) {
            console.log(data)
            
            for (const property in data['data']){
                const div1 = document.createElement('div')
                div1.className = "col-12 col-sm-6 col-xl-4 mb-4"
                const div2 = document.createElement('div')
                div2.className = "card border-0 shadow"
                const div3 = document.createElement('div')
                div3.className = "card-body"
                const div4 = document.createElement('div')
                div4.className = "judgement-title"
                const div5 = document.createElement('div')
                const div6 = document.createElement('div')
                div5.innerHTML = property
                div5.className = "title-name-custom"
                div6.className = "judgement-info"
                const div7 = document.createElement('div')
                div7.className = "icon-wrapper"
                const button1 = document.createElement('button')
                button1.className = "btn"
                
                const div8 = document.createElement('div')
                div8.className = "icon-wrapper"
                const button2 = document.createElement('button')
                button2.className = "btn trigger"
    
                const div9 = document.createElement('div')
                const button3 = document.createElement('button')
                button3.className = "btn"
                button3.innerHTML = Math.round( data['data'][property]) +"%"
                div1.append(div2)
                div2.append(div3)
                div3.append(div4)
                div4.append(div5)
                div4.append(div6)
                div6.append(div7)
                div7.append(button1)
                
                var img1 = document.createElement('img')
                img1.src = "../../static/assets/img/download-solid.svg"
                img1.className = "icon-custom"
                var url = document.createElement('a')
                // {% url 'download' document.id %}
                console.log(data)
                url.href = "http://127.0.0.1:8000/legal/download/"+property

                var img2 = document.createElement('img')
                img2.src = "../../static/assets/img/book-bookmark-solid.svg"
                img2.className = "icon-custom"
    
                div6.append(div8)
                div8.append(button2)
                button2.append(img2); 
                button2.addEventListener("click", ()=>{
                    console.log("Heelo j")
                    $("body").addClass("loading");
                    var xhr = new XMLHttpRequest();
                    // xhr.setRequestHeader("X-CSRFToken",$.cookie("csrftoken"))
                    xhr.open('GET','http://127.0.0.1:8000/legal/view-pdf/'+property,true);
                    xhr.responseType = 'blob';

                            xhr.onload = function(e){
                                console.log("Hello")
                                    if (this.status == 200) {
                                        var url = window.URL.createObjectURL(new Blob([this.response], {type: 'application/pdf'}));
                                        document.querySelector("iframe").src = url
                                        
                                        // a.href = url;
                                        // a.download = 'report.pdf';
                                        // a.click();
                                        window.URL.revokeObjectURL(url);
                                        $('body').removeClass("loading"); //removing the loading spinner class
                                    }else{
                                        $('body').removeClass("loading") //removing the loading spinner class
                                        console.log(this.status);
                                        alert('Download failed...!  Please Try again!!!');
                                    }
                                };
                                xhr.send();
                                document.querySelector(".model-judgement-title").innerHTML = property

                    // $.ajax({
                    //     headers: { "X-CSRFToken": $.cookie("csrftoken") },
                    //     url: "http://127.0.0.1:8000/legal/view-pdf",
                        
                    //     responseType: 'arraybuffer',
            
                    //     success: function (data) {
                    //         var arrBuffer = base64ToArrayBuffer(data);
                    //         console.log(arrBuffer)
                    //         var blob = new Blob([data], { type: 'application/pdf' });
                    //         console.log(blob)
                    //         var fileURL = window.URL.createObjectURL(blob);
                    //         window.open(fileURL,'_blank');
                    //         // var file = window.URL.createObjectURL(this.response);
                    //         // var link = document.createElement('a');
                    //         // link.href = window.URL.createObjectURL(blob);
                    //         // link.download = "Filename.pdf";
                    //         // link.click();
                            
                    //         document.querySelector("iframe").src = fileURL
                    //         console.log(typeof(data))
                    //         console.log(( new Uint8Array(data)))

                    //     }
                    // })
                    modal.classList.toggle("custom-show-modal");
                    console.log(property)
                })

                // <a href="{% url 'download' document.id %}">Download</a>
                div6.append(div9)
                div9.append(button3)
    
                button1.append(url);
                url.append(img1) 
                
                document.querySelector('.dashboard-wrapper-2 .row').append(div1)
                
            }
        }
    });
}

// var modal = document.querySelector(".modal");
// var triggers = document.querySelectorAll(".trigger");
// var closeButton = document.querySelector(".close-button");

// function toggleModal() {
//   modal.classList.toggle("show-modal");
// }

// function windowOnClick(event) {
//   if (event.target === modal) {
//     toggleModal();
//   }
// }

// for (var i = 0, len = triggers.length; i < len; i++) {
//   triggers[i].addEventListener("click", toggleModal);
// }
// closeButton.addEventListener("click", toggleModal);
// window.addEventListener("click", windowOnClick);

