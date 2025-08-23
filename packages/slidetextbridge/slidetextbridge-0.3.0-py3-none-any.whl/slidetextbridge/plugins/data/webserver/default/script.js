function get_appropriate_ws_url(extra_url) {
    var pcol;
    var u = document.URL;
    if (u.substring(0, 5) === "https") {
        pcol = "wss://";
        u = u.substr(8).split("/")[0];
    } else {
        pcol = "ws://";
        if (u.substring(0, 4) === "http")
            u = u.substr(7).split("/")[0];
    }
    return pcol + u + "/" + extra_url;
}

function text_to_html(text) {
    return text.replace(/[&<>"']/g, function (c) {
        return ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "\"": "&quot;",
            "'": "&#39;",
        })[c];
    }).replace(/\\n/g, "<br/>");
}

let ws_failed = 0;
function connect_ws() {
    let url = get_appropriate_ws_url("ws/text");
    console.log("Connecting to", url);
    let ws = new WebSocket(url);
    ws.onmessage = function(msg) {
        ws_failed = 0;
        console.log("Received:", msg.data);
        let e = document.getElementById("placeholder");
        let h = text_to_html(msg.data);
        console.log("HTML:", h);
        e.innerHTML = h;
    };
    ws.onclose = function() {
        ws_failed += 1;
        setTimeout(connect_ws, ws_failed < 6 ? ws_failed * 500 : 3000);
    };
}

document.addEventListener("DOMContentLoaded", function() {
    connect_ws();
});
