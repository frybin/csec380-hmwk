// What is document? ---> Literally the webpage
$(document).ready(function() {

    var e = (new Date).getTime();
    $.post("/getSecure", function(t) {
        // What is "t"? what is it searching for?
        key = t.substring(t.indexOf(":"));

        var o = !!(() => { // Function that takes no params and "o" --> return value
                const e = { // Dictionary?
                    firefox: !!window.InstallTrigger,
                    safari: !!window.ApplePaySession,
                    opera: window.opr && !!window.opr.addons,
                    chrome: !!window.chrome
                };

                return Object.keys(e).find(t => !0 === e[t])
            })() + 1, // WTF is this shit

            // X and Y are given in the html of the page
            i = math.complex(x + " + 3i"),
            // 4 + o should be 5 for no browser and 6 with browser 
            n = math.complex(4 + o, y);

        out2 = math.multiply(i, n), out1 = math.eval("e*(pi*i)"), x = math.add(out2, out1);
        var a = (new Date).getTime();

        // Figure out how AJAX requests are sent/queued
        $.post("/flag5redir", {
            a: x.im,
            b: x.re,
            c: a - e,
            d: key
        }, function(e) {
            document.write(e)
        })
    })
});