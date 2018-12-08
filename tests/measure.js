var ROSLIB = require("roslib");
function measure() {
    ctr = 0
    measureTotal = 0
    websocket_url_str = 'ws://172.28.0.5:9090';
    ros = new ROSLIB.Ros({
        url: websocket_url_str
    });
    listenerMeasure = new ROSLIB.Topic({
        ros: ros,
        name: '/measure',
        messageType: 'std_msgs/Float64'
    });
    listenerMeasure.subscribe(function(message) {
            measureTotal = measureTotal + parseFloat(message.data)
            ctr = ctr + 1;
            measureMean = measureTotal / ctr;
            console.log(measureMean);
            if (ctr == 250){
                return 0;
            }

    });
    ros.on('error', function(error) {
        console.log('Error connecting to websocket server: ', error.code);
        setTimeout(measure, 5000);
    });
}
measure();