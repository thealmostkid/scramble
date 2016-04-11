function poll(fn, errBack, timeout, interval) {
    console.log('poll called')
    var endTime = Number(new Date()) + (timeout || 2000);
    interval = interval || 100;

    (function p() {
            // If the condition is met, we're done! 
            if (fn()) {
                return;
            }
            // If the condition isn't met but the timeout hasn't elapsed, go again
            if (Number(new Date()) < endTime) {
                setTimeout(p, interval);
            }
            // Didn't match and too much time, reject!
            else {
                errBack(new Error('timed out for ' + fn + ': ' + arguments));
            }
    })();
}

/*
function verify(result) {
    if(result === 1){
        window.location = "/game";
    } else {
        document.getElementById('target').innerHTML = '<p>NAT ERROR</p>';
    }
}

poll(
    function() {
        result = null;
        $.getJSON('/poll', function(data) {
            //data is the JSON string
            result = data[0];
            verify(result)
        });
        return false
    },
    function() {
        document.getElementById('target').innerHTML = '<p>TIMEOUT</p>';
    },
    1000,
    100
);
*/
