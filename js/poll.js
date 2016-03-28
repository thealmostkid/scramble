function poll(fn, callback, errback, timeout, interval) {
    console.log('poll called')
    var endTime = Number(new Date()) + (timeout || 2000);
    interval = interval || 100;

    (function p() {
            // If the condition is met, we're done! 
            if(fn()) {
                callback();
            }
            // If the condition isn't met but the timeout hasn't elapsed, go again
            else if (Number(new Date()) < endTime) {
                setTimeout(p, interval);
            }
            // Didn't match and too much time, reject!
            else {
                errback(new Error('timed out for ' + fn + ': ' + arguments));
            }
    })();
}

poll(
    function() {
        console.log('periodic');
        ready = false;
        result = null;
        $.getJSON('/poll', function(data) {
            //data is the JSON string
            console.log(data);
            result = data[0];
            console.log(result);
        });
        console.log(result);
        console.log('returning');
        console.log(result === 1);
        return result === 1;
    },
    function() {
        // Done, success callback
        document.getElementById('target').innerHTML = '<p>NAT SUCCESS</p>';
    },
    function() {
        // Error, failure callback
        document.getElementById('target').innerHTML = '<p>NAT ERROR</p>';
    },
    1000,
    100
);
