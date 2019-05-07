var pagecount = 1;
var btn = document.getElementById("load-button");
var container = document.getElementById("object-holder");
var input = document.getElementById('buysearch');
var form = document.getElementById('search-form');

form.onsubmit = function search() {
    console.log("submitted");
    var request = new XMLHttpRequest();
    request.withCredentials = true;
    console.log(input.value);
    request.open("GET", "https://ide50-slarbi10.legacy.cs50.io:8080/search?q=" + input.value, true);
    console.log("req opened");
    request.onload = function() {
        console.log(request.responseText);
        var data = JSON.parse(request.responseText);
        while (container.firstChild) {
            container.removeChild(container.firstChild);
        }
        renderHTML(data);
    };
    request.send();
    return false;
};

btn.onclick = function() {
    console.log("clicked");
    var request = new XMLHttpRequest();
    request.withCredentials = true;
    request.open("GET", "https://ide50-slarbi10.legacy.cs50.io:8080/getdata?section=" + pagecount, true);
    console.log("req opened");
    console.log(pagecount);
    request.onload = function() {
        console.log("loaded");
        var data = JSON.parse(request.responseText);
        renderHTML(data);
        console.log("done");
    };
    request.send();
    pagecount++;
};
function renderHTML(data) {
    console.log("rnder");
    for (var i = 0; i < data.length; i++) {
        var html = "";
        var script = "";
        console.log(i);
        html += " <div class='stock-object center-row-flex'><div class='stock-logo-holder'><div class='center-row-flex'><div class='column-center-flex'>";
        html +=  "<img class='stock-logo' src='" + data[i].url + "'>";
        html += "</div></div></div><div class='buystock-names column-center-flex'><div class='buystock-symbol'>" + data[i].stock + "</div>";
        html += "<div class='buystock-name'>" + data[i].name + "</div></div>";
        html += "<div class='buystock-graph' id='" + data[i].stock + "'>" + "</div>";
        html += "<script class='renderer' type='text/javascript'>";
        script += "var chart" +data[i].stock + " = new CanvasJS.Chart('" + data[i].stock + "', {";
        script += " animationEnabled: true, backgroundColor: '#4ED48D', colorSet:'#001C5D', theme: 'blue', title: { text: '' }, axisY: { includeZero: false },";
        script += " data: [{ type: 'line', yValueFormatString: '$#.###', dataPoints: [";
        for (var n = 0; n < data[i].data.length; n++) {
            script += "{label: "+ "'"+ data[i].labels[n] +"'"+ ", y: " + data[i].data[n] + " },";
        }
        script += "] }], options: { responsive: true, } });";
        script += "chart" + data[i].stock + ".render()";
        //script += " console.log('chartren');";
        html += "</script>";
        html += "<div class='buystock-data center-column-flex'>";
        html += "<div class='stock-price center-row-flex'>Price:" + data[i].data[data[i].data.length-1] + "</div>";
        html += "<div class='data-month center-row-flex'> <span style='color: #001C5D; font-weight: 400;'>Month: </span>";
        var diff = data[i].data[data[i].data.length-1] - data[i].data[0];
        var percentchange = (diff / data[i].data[0]) * 100;
        if (diff > 0) {
            html += "<span style='color: white; border-radius: 50%; background-color: #001C5D; font-weight: 700;'>&thinsp;&uarr;&thinsp;</span>";
        }
        else if (diff < 0) {
            html += "<span style='color: white; border-radius: 50%; background-color: #d50000; font-weight: 700;'>&thinsp;&darr;&thinsp;</span>";
        }
        else {
            html += "<span style='color: white; border-radius: 50%; background-color: #001C5D; font-weight: 700;'>&thinsp;&rarr;&thinsp;</span>";
        }
        html += "<span";
        if (diff >= 0) {
            html += "style='color: #001C5D;'";
        }
        else {
            html += "style='color: #d50000;'";
        }
        html += ">";
        html += "$" + (Math.round((data[i].data[data[i].data.length-1])*100))/100 + "," + "<br>" + "(" + (Math.round(percentchange*100))/100 + ")";
        html += "</span> </div> </div> <div class='buy-button-holder column-start-flex'>";
        html += "<a href='/stock?stock=" + data[i].stock + "'>";
        html += "<div class='buy-button center-row-flex'>See More</div></a></div></div>";
        var elscript = document.createElement('script');
        elscript.innerHTML = script;
        container.insertAdjacentHTML('beforeend', html);
        container.appendChild(elscript);
    }
    var loader = document.getElementById('loader');
    loader.style.display = 'hidden';
    //container.insertAdjacentHTML('beforeend', html);
    container.appendChild(loader);
}