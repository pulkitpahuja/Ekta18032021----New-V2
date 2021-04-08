alert("Before Starting Please ensure Serial device is connected");
var overall_device = 1;
var count = 0;
var delay_count = 0;
var task_interval;
var timer;
var start_counter = 0;
var status;
var hasReturned = "false";
var secondMicro = "false";

for (var i = 1; i <= 13; i++) {
    if (i == 3) {

    } else {
        document.getElementById("max_" + i).value = 0;
        document.getElementById("min_" + i).value = 0;
    }

    if (document.getElementById("time_" + i).disabled) {
        document.getElementById("time_" + i).value = "";
    } else {
        document.getElementById("time_" + i).value = 0;

    }

}

document.getElementById("max_13").value = 0;
document.getElementById("min_13").value = 0;

document.getElementById("name_1").value = "20V";
document.getElementById("name_2").value = "30A";
document.getElementById("name_3").value = "kV";
document.getElementById("name_4").value = "mA";
document.getElementById("name_5").value = "Insulation";
document.getElementById("name_6").value = "Voltmeter";
document.getElementById("name_7").value = "VAW";
document.getElementById("name_10").value = "MicroAmpere";
document.getElementById("name_11").value = "PF";
document.getElementById("name_12").value = "Frequency";

document.getElementById("param_1").value = "V";
document.getElementById("param_2").value = "A";
document.getElementById("param_3").value = "kV";
document.getElementById("param_4").value = "mA";
document.getElementById("param_5").value = "MΩ";
document.getElementById("param_6").value = "V";
document.getElementById("param_7").value = "V";
document.getElementById("param_8").value = "A";
document.getElementById("param_9").value = "W";
document.getElementById("param_10").value = "μA-1";
document.getElementById("param_13").value = "μA-2";
document.getElementById("param_11").value = "";
document.getElementById("param_12").value = "Hz";

document.getElementById("datetime").innerHTML = Date.today().toString("MMMM dS, yyyy") + " " + new Date().toString("HH:mm:ss");

function reset() {
    for (var i = 1; i <= 12; i++) {
        document.getElementById("result_" + i).value = "";
    }
    document.getElementById("result_13").value = "";
    document.getElementById("strt_butt").innerHTML = "Start";
    document.getElementById("device_id").value = "";
    clearInterval(timer);
    clearInterval(task_interval);
    overall_device = 1;
    count = 0;
    delay_count = 0
    start_counter = 0;
    check_ext_trigg();

}

function turn_off_device_relay(device) {
    //turn off individual device relay
    $.ajax({
        type: "POST",
        url: "/turn_off_relay",
        data: { "device": device, "com_port": document.getElementById("com_port").value },  // serializes the form's elements.
        success: function (data) {
            console.log("Relay Status : " + data);
        }
    });
}

function main_task(device) {
    if (device == 3 || device == 4) {

        if (delay_count <= parseInt(document.getElementById("delay").value)) {

            run_task("false", device);
            if (overall_device == 4) {
                overall_device = 3;
            } else if (overall_device == 3) {
                overall_device = 4;
            }
            delay_count++;
        } else {

            if (count <= parseInt(document.getElementById("time_3").value)) {
                run_task("true", device);
                if (overall_device == 4) {
                    overall_device = 3;
                } else if (overall_device == 3) {
                    overall_device = 4;
                }
            } else {
                overall_device = 5;
                turn_off_device_relay(4);

                delay_count = 0;
                count = 0;

            }
        }
    } else if (device == 1 || device == 2) {

        if (delay_count <= parseInt(document.getElementById("delay").value)) {
            run_task("false", device);
            if (overall_device == 1) {
                overall_device = 2;
            } else if (overall_device == 2) {
                overall_device = 1;
            }
            delay_count++;
        } else {

            if (count <= parseInt(document.getElementById("time_1").value)) {
                run_task("true", device);
                if (overall_device == 1) {
                    overall_device = 2;
                } else if (overall_device == 2) {
                    overall_device = 1;
                }
            } else {
                setTimeout(function () {
                    turn_off_device_relay(1);
                    setTimeout(function () {
                        turn_off_device_relay(2);
                    }, 500);
                }, 500);
                overall_device = 3;
                delay_count = 0;
                count = 0;

            }
        }
    }
    else {

        if (delay_count <= parseInt(document.getElementById("delay").value)) {
            run_task("false", device);
            delay_count++;
        } else {
            var time = device;
            if (device == 8) {
                time = 10;
            } else if (device == 9) {
                time = 11;
            } else if (device == 10) {
                time = 12;
            }
            if (count <= parseInt(document.getElementById("time_" + time).value)) {
                run_task("true", device);
            } else {
                if (device == 10) {

                    setTimeout(function () {
                        turn_off_device_relay(10);
                    }, 500);


                    overall_device = 1;
                    delay_count = 0;
                    count = 0;
                    setTimeout(function () {
                        stop();
                        secondMicro = "false";
                        save_result_data();
                        start_counter = 0;

                    }, 500);

                } else {

                    turn_off_device_relay(overall_device);
                    if (overall_device != 8) {
                        overall_device++;
                    } else if (overall_device == 8 && secondMicro == "true") {
                        overall_device++;
                        secondMicro = "false";
                    } else {
                        secondMicro = "true";
                    }
                    delay_count = 0;
                    count = 0;
                }

            }

        }
    }


}

function stop() {
    start_counter = 0;
    stop_sequence();
    turn_off_device_relay(overall_device);
    check_ext_trigg();

    if (overall_device != 1) {
        document.getElementById("strt_butt").innerHTML = "Resume";
    }

    clearInterval(timer);
    clearInterval(task_interval);

}

function start() {
    if (document.getElementById("device_id").value == "") {
        alert("Enter Device ID");
        start_counter = 0;

        check_ext_trigg();

        return;
    }
    if (document.getElementById("ser_status").innerHTML == "Disconnected") {
        alert("Serial Connection Not Found");
        start_counter = 0;
        if (hasReturned == "true") {
            hasReturned = "false";
        }
        load_config();
        return;
    }
    console.log("STarting TASK");
    //check_stop_trigg();
    start_counter = 1;
    start_sequence();
    if (document.getElementById("strt_butt").innerHTML == "Resume") {
        var val = document.getElementById("device_id").value;
        reset();
        start_counter = 1;
        start_sequence();
        document.getElementById("device_id").value = val;
        document.getElementById("strt_butt").innerHTML = "Start";
    }
    clearInterval(status);
    timer = setInterval(function () {
        count++;
    }, 1000);
    task_interval = setInterval(function () {
        main_task(overall_device);
    }, 1600);
}

function start_sequence() {
    //##turning relay on or off
    $.ajax({
        type: "POST",
        url: "/sequence_init",
        data: { "type": "start", "com_port": document.getElementById("com_port").value },  // serializes the form's elements.
        success: function (data) {
            console.log("Result Status : " + data);
        }
    });
}

function stop_sequence() {
    //##turning relay on or off

    $.ajax({
        type: "POST",
        url: "/sequence_init",
        data: { "type": "stop", "com_port": document.getElementById("com_port").value },  // serializes the form's elements.
        success: function (data) {
            console.log("Result Status : " + data);
        }
    });

}


function check_ext_trigg() {
    //##checking external trigger

    $.ajax({
        type: "POST",
        url: "/check_ext_trigg",
        data: { "com_port": document.getElementById("com_port").value },
        success: function (data) {
            hasReturned = "true";
            if (data == "1") {
                console.log(data);
                if (start_counter == 1) {

                } else {
                    start_counter = 1;
                    start();
                }
            }

        }
    });

}

function check_stop_trigg() {
    //##checking external trigger

    $.ajax({
        type: "POST",
        url: "/check_stop_trigg",
        data: { "com_port": document.getElementById("com_port").value },
        success: function (data) {
            hasReturned = "true";
            if (data == "1") {
                console.log(data);
                if (start_counter == 1) {

                } else {
                    start_counter = 1;
                    stop();
                }
            }

        }
    });

}


function stop_task() {
    clearInterval(task_interval);
}

function save_result_data() {
    var curr_config = {};
    curr_config["device_id"] = document.getElementById("device_id").value;
    for (var i = 1; i <= 13; i++) {
        var temp_config = {};
        if (i > 7 && i < 10) {
            temp_config["name"] = document.getElementById("name_7").value;
            temp_config["param"] = document.getElementById("param_" + i).value;
            temp_config["result"] = document.getElementById("result_" + i).value;
            if (document.getElementById("result_" + i).style.color == "red") {
                temp_config["status"] = "Failed";
            } else {
                temp_config["status"] = "Passed";
            }
            curr_config[i.toString()] = temp_config;
        } else if (i == 13) {
            temp_config["name"] = document.getElementById("name_10").value;
            if (document.getElementById("result_" + i).style.color == "red") {
                temp_config["status"] = "Failed";
            } else {
                temp_config["status"] = "Passed";
            }
            temp_config["param"] = document.getElementById("param_" + i).value;
            temp_config["result"] = document.getElementById("result_" + i).value;
            curr_config[i.toString()] = temp_config;
        } else {
            temp_config["name"] = document.getElementById("name_" + i).value;
            if (document.getElementById("result_" + i).style.color == "red") {
                temp_config["status"] = "Failed";
            } else {
                temp_config["status"] = "Passed";
            }
            temp_config["param"] = document.getElementById("param_" + i).value;
            temp_config["result"] = document.getElementById("result_" + i).value;
            curr_config[i.toString()] = temp_config;
        }

    }

    curr_config["datetime"] = Date.today().toString("dd-MM-yyyy") + " " + new Date().toString("HH-mm-ss");

    $.ajax({
        type: "POST",
        url: "/save_result",
        data: JSON.stringify(curr_config),  // serializes the form's elements.
        success: function (data) {
            alert("Result Status : " + data);
        }
    });
}


function save_curr_config() {
    var curr_config = {};
    $(document).ready(function () {
        curr_config["device_id"] = document.getElementById("config_id").value;
        curr_config["delay"] = document.getElementById("delay").value;
        curr_config["com_port"] = document.getElementById("com_port").value;
        for (var i = 1; i <= 13; i++) {
            var temp_config = {};
            if (i > 7 && i < 10) {
                temp_config["name"] = document.getElementById("name_7").value;
                temp_config["max"] = document.getElementById("max_" + i).value;
                temp_config["min"] = document.getElementById("min_" + i).value;
                temp_config["param"] = document.getElementById("param_" + i).value;
                curr_config[i.toString()] = temp_config;
            } else if (i == 13) {
                temp_config["name"] = document.getElementById("name_10").value;
                temp_config["time"] = document.getElementById("time_10").value;
                temp_config["max"] = document.getElementById("max_13").value;
                temp_config["min"] = document.getElementById("min_13").value;
                temp_config["param"] = document.getElementById("param_13").value;
                curr_config[i.toString()] = temp_config;
            } else {
                temp_config["name"] = document.getElementById("name_" + i).value;
                temp_config["time"] = document.getElementById("time_" + i).value;
                temp_config["max"] = document.getElementById("max_" + i).value;
                temp_config["min"] = document.getElementById("min_" + i).value;
                temp_config["param"] = document.getElementById("param_" + i).value;
                curr_config[i.toString()] = temp_config;
            }
        }

        $.ajax({
            type: "POST",
            url: "/save_curr_config",
            data: JSON.stringify(curr_config),  // serializes the form's elements.
            success: function (data) {
                alert("Save Status : " + data);
            }
        });

    });
}

function run_task(truth, device) {

    if (device == 7) {
        var to_send = {
            "secondMicro": "false", "truth": truth, "com": document.getElementById("com_port").value, "device": device, "maximum": [document.getElementById("max_5").value, document.getElementById("max_6").value, document.getElementById("max_7").value].toString(),
            "minimum": [document.getElementById("min_5").value, document.getElementById("min_6").value, document.getElementById("min_7").value].toString()
        };
    } else if (device == 8 && secondMicro == "true") {
        var to_send = {
            "secondMicro": secondMicro, "truth": truth, "com": document.getElementById("com_port").value, "device": device, "maximum": document.getElementById("max_13").value,
            "minimum": document.getElementById("min_13").value
        };
    } else {
        var val = device;
        if (device > 7) {
            val = device + 2;
        }
        var to_send = {
            "secondMicro": "false", "truth": truth, "com": document.getElementById("com_port").value, "device": device, "maximum": document.getElementById("max_" + val).value,
            "minimum": document.getElementById("min_" + val).value
        };
    }


    $.ajax({
        type: "POST",
        url: "/run_task",
        cache: false,
        data: to_send,  // serializes the form's elements.

        success: function (response) {
            if (device == 7) {
                list = Object.values(JSON.parse(response))[0];
                for (var i = 0; i < list.length; i++) {
                    var val = device + i;
                    var max = document.getElementById("max_" + val).value;
                    var min = document.getElementById("min_" + val).value;
                    document.getElementById("result_" + val).value = list[i];
                    if (list[i] <= parseFloat(max) && list[i] >= parseFloat(min)) {

                        $("#result_" + val).css({ "color": "green" });
                    } else {
                        $("#result_" + val).css({ "color": "red" });
                        //stop();
                    }
                }
            } else if (device == 3) {
                list = Object.values(JSON.parse(response))[0];
                document.getElementById("result_3").value = list[1] == 2 ? list[0] + "-Failed" : list[0] + "-Passed";
                if (list[1] == 2) {
                    stop();
                    $("#result_3").css({ "color": "red" });
                } else {
                    $("#result_3").css({ "color": "green" });
                }
            } else if (device == 8 && secondMicro == "true") {
                document.getElementById("result_13").value = response;
                if (parseFloat(response) <= parseFloat(to_send["maximum"]) && parseFloat(response) >= parseFloat(to_send["minimum"])) {
                    $("#result_13").css({ "color": "green" });
                } else {
                    $("#result_13").css({ "color": "red" });
                }
            } else {
                var val = device;
                if (device > 7) {
                    val = device + 2;
                }
                document.getElementById("result_" + val).value = response;
                if (parseFloat(response) <= parseFloat(to_send["maximum"]) && parseFloat(response) >= parseFloat(to_send["minimum"])) {
                    $("#result_" + val).css({ "color": "green" });
                } else {
                    if (device == 5) {
                        var temp = parseInt(document.getElementById("delay").value);
                        if (delay_count <= temp) {

                        } else {
                            setTimeout(function () {
                                stop();
                            }, 2500);
                        }


                    }
                    $("#result_" + val).css({ "color": "red" });
                }
            }

        }
    });
}

function get_connect_status() {
    $.ajax({
        type: "POST",
        url: "/connected",
        data: { "com_port": document.getElementById("com_port").value },  // serializes the form's elements.
        success: function (data) {
            if (data == "true") {
                document.getElementById("ser_status").innerHTML = "Connected";
                $("#ser_status").css({ "color": "green" });
                check_ext_trigg();
            } else {
                document.getElementById("ser_status").innerHTML = "Disconnected";
                $("#ser_status").css({ "color": "red" });

            }
        }
    });
}



function load_config() {

    $.ajax({
        type: "POST",
        url: "/load_config",
        data: { "device_id": document.getElementById("config_id").value },  // serializes the form's elements.
        success: function (data) {
            if (typeof data == "string") {
                alert("Load Status: " + data);
            } else {
                for (var i = 1; i <= 13; i++) {
                    if (i > 7 && i < 10) {
                        document.getElementById("max_" + i).value = data[i]["max"];
                        document.getElementById("min_" + i).value = data[i]["min"];
                        document.getElementById("param_" + i).value = data[i]["param"];
                    } else if (i == 13) {
  
                        document.getElementById("max_13").value = data[i]["max"];
                        document.getElementById("min_13").value = data[i]["min"];
                        document.getElementById("param_13").value = data[i]["param"];
                        document.getElementById("name_10").value = data[i]["name"];
                    } else {
                        if (i != 3) {
                            document.getElementById("time_" + i).value = data[i]["time"];
                            document.getElementById("max_" + i).value = data[i]["max"];
                            document.getElementById("min_" + i).value = data[i]["min"];
                            document.getElementById("param_" + i).value = data[i]["param"];
                            document.getElementById("name_" + i).value = data[i]["name"];
                        } else {
                            if (document.getElementById("time_" + i).disabled) {
                                document.getElementById("time_" + i).value = "";
                            }else{
                                document.getElementById("time_" + i).value = data[i]["time"];
                            }
                            document.getElementById("param_" + i).value = data[i]["param"];
                            document.getElementById("name_" + i).value = data[i]["name"];
                        }
                    }

                }
                document.getElementById("delay").value = data["delay"];
                document.getElementById("com_port").value = data["com_port"];
                alert("Load Successful");
                get_connect_status();
                var i = 60;
                var thisinter = setInterval(() => {
                    if (i <= 0) {
                        clearInterval(thisinter);
                        reset();
                        i = 60;
                    }
                    if (start_counter == 0) {
                        i--;
                    } else {
                        clearInterval(thisinter);
                        i = 60;
                    }
                }, 1000);
            }
        }
    });
}