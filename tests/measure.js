var ROSLIB = require("roslib");
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
});