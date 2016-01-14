/**
 * Created by weather on 10/15/15.
 */
var _ERROR = {
    _LOGIN_ERROR: '登录失败，请登录',
    _AUTH_ERROR: '权限不足，请与管理员联系',
    _HEAD_PAGE: "退一步海阔天空，别往前翻了",
    _BACK_PAGE: "苦海无涯，回头是岸！别往后翻了",
    _DATA_FAITURE: "获取数据失败，请点击其他标签尝试，如果不行，请与技术联系"
};

var EXP_MIN = 25, SHANGHUACC_MIN = 3, DELIVERYACC_MIN = 5;
var EXP_MLS = EXP_MIN*60000, SHANGHUACC_MLS = SHANGHUACC_MIN*60000, DELIVERYACC_MLS = DELIVERYACC_MIN*60000;
var lookorderModule = angular.module("lookorderModule", ["ngSanitize"]);

lookorderModule.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol("{[{");
    $interpolateProvider.endSymbol("}]}");
});

//通用接口
lookorderModule.factory("Service", function ($http) {
    service = {};
    var ERROR_RETRUN = function (status, callback) {
        utils.progressbar.hide();
        if (status == 403) {
            callback({success: false, msg: _ERROR._AUTH_ERROR});
        } else {
            callback({success: false, msg: _ERROR._DATA_FAITURE});
        }
    };

    //获取信息（get)
    service.getQueryData = function (url, params, callback) {
        utils.progressbar.show();
        $http({
            method: "GET",
            url: url,
            params: params,
            timeout: 30000
        }).success(function (data, status, headers, config) {
            utils.progressbar.hide();
            if (data) {
                if (typeof(data) == 'object') {
                    if (data["respcd"] == "0000") {
                        callback({success: true, msg: data["respmsg"], data: data["data"]});
                    } else {
                        callback({success: false, msg: data["respmsg"]});
                    }
                } else {
                    callback({success: false, msg: _ERROR._LOGIN_ERROR});
                }
            } else {
                callback({success: false, msg: "数据为空"});
            }
        }).error(function (data, status, headers, config) {
             ERROR_RETRUN(status, callback);
        })
    };

        //发送信息接口
    service.postFormData = function (url, params, callback) {
        //utils.progressbar.show();
        $http.post(url,params).success(function (data) {
            if (data) {
                callback(data);
            } else {
                callback([]);
            }
        }).error(function (data, status) {
            ERROR_RETRUN(status, callback);
        });
    }

    return service;
});

// 全局
var DELIVERY = [1, 2, 3, 12, 5, 10];
lookorderModule.controller("lookorderCtrl", function ($scope, Service){
    $scope.time = "";
    $scope.day = "1"; //1=今天；2=昨天
    $scope.date = "某天"; //日期
    $scope.lastopid = 0; // 最新的ordersoperatingid， 判断是否有更新
    $scope.lastoid = 0; // 最新的orderid， 统计使用
    $scope.orders = [];
    $scope.page = 1;
    $scope.selorder = null;
    $scope.ns = 0;
    $scope.tag_delivery = [0, 1, 1, 1, 1, 1];
    $scope.allorders = [];
    $scope.count_shto = 0;
    $scope.count_psto = 0;
    $scope.count_neworderall = 0;
    $scope.count_neworderto = 0;
    $scope.count_acceptall = 0;
    $scope.count_acceptto = 0;
    $scope.count_delaccall = 0;
    $scope.count_delaccto = 0;
    $scope.count_deliveryall = 0;
    $scope.count_deliveryto = 0;
    $scope.count_arrivalall = 0;
    $scope.count_arrivalto = 0;
    $scope.tb_change = 0;
    $scope.shanghuot = 0; // 1商户确认超时
    $scope.peisongot = 0; // 1配送员接单超时
    $scope.init = function(){
        setInterval(function(){
            //更新当页统计
            $scope.updatelefttime();
        }, 1000);
        setInterval(function(){
            //更新总统计
            $scope.goto($scope.page, 0);
        }, 60000);

        var socket = io.connect('http://' + document.domain + ':' + location.port);
        socket.on('connect', function(ret) {
            console.log("socket connected!!");
            socket.send('socket connected');
            socket.emit('askfortime', "askfortime");
        });
        socket.on('disconnect', function(ret) {
            console.log("socket disconnected!!");
            socket.send('disconnected');
        });
        socket.on('error', function(ret) {
            console.log("socket error!!");
            socket.send('error');
        });
        socket.on('orderupdate', function(ret) {
            console.log(ret);
        });
        socket.on('time', function(ret) {
            console.log("t:"+ret.data+",last"+ret.lastid[0]);
            $scope.$apply(function(){
                $scope.updateorders(ret.lastid[0], ret.data);
            });
        });
        $scope.updateorders = function(lastid, time){
            $scope.time = time;
            if (lastid == 'undefined'){
                return ;
            }
            if (lastid != $scope.lastopid){
                //有更新则更新
                $scope.ns = 1;
                if ($scope.selorder != null){
                    $scope.setuporderdetail($scope.orders[$scope.selorder], $scope.selorder);
                }
                $scope.goto($scope.page, 0);
                $scope.lastopid = lastid;
            }
        };
    };

    $scope.updatelefttime = function(){
        var currtime = new Date($scope.time.replace(/-/g, "/"));

        for (var i = 0; i < $scope.orders.length; i++){
            var pydate = new Date($scope.orders[i].pay_time.replace(/-/g, "/"));
            // 更新选择order的index
            if ($scope.orders[i].id == $scope.detail_oid){
                $scope.selorder = i;
                $scope.setuporderdetail($scope.orders[$scope.selorder], $scope.selorder);
            }
            //更新配送剩余时间
            if ($scope.orders[i].status == 10){
                // 状态为已送达 显示用时
                var ardate = null;
                if ($scope.orders[i].delivery != undefined){
                    ardate = new Date($scope.orders[i].delivery.update_time.replace(/-/g, "/"));
                }else{
                    ardate = new Date($scope.orders[i].update_time.replace(/-/g, "/"));
                }
                $scope.orders[i].lefttime = Number(((ardate - pydate)/60000.0).toFixed(0));
            }else{
                // 其他状态 显示剩余时间
                var xp = new Date($scope.orders[i].expected_date.replace(/-/g, "/"));
                $scope.orders[i].lefttime = Number(((xp - currtime)/60000.0).toFixed(0));
            }
            //更新订单颜色
            // 默认蓝色
            $scope.orders[i].color = "blue";
            // 首要,付款后超过25分钟，红色
            var duration_m = parseInt((currtime - pydate)/60000.0);
            if (duration_m >= 25 && $scope.orders[i].status != 10){
                $scope.orders[i].color = "red";
            }else{
                // 已付款后3分钟商户未接单，显示深蓝色
                if($scope.orders[i].status == 2 ){
                    var costtime = parseInt((currtime-pydate)/60000.0);
                    if (costtime >= 3){
                        $scope.orders[i].color = "deepblue";
                    }
                }
                // 商户已经接单，但配送员超过5分钟未接单 显示黄色
                if($scope.orders[i].status == 3 ){
                    var update = new Date($scope.orders[i].update_time.replace(/-/g, "/"));
                    var costtime = parseInt((currtime-update)/60000.0);
                    if (costtime >= 5){
                        $scope.orders[i].color = "yellow";
                    }
                }
                // 已送达订单显示灰色
                if($scope.orders[i].status == 10 ){
                    $scope.orders[i].color = "gray";
                }
            }
        }
    };

    $scope.update_count = function(stats){
        //{'oo5': 0, 'oo4': 0, 'oo1': 3, 'oop': 0, 'oos': 3, 'oo2': 0, 't': '0:00:00.042615', 'o5': 204, 'o4': 0, 'o2': 0, 'o1': 3}
        $scope.count_shto = stats.oos;
        $scope.count_psto = stats.oop;
        $scope.count_neworderall = stats.o1;
        $scope.count_neworderto = stats.oo1;
        $scope.count_acceptall = stats.o2;
        $scope.count_acceptto = stats.oo2;
        $scope.count_delaccall = stats.o3;
        $scope.count_delaccto = stats.oo3;
        $scope.count_deliveryall = stats.o4;
        $scope.count_deliveryto = stats.oo4;
        $scope.count_arrivalall = stats.o5;
        $scope.count_arrivalto = stats.oo5;
    };

    $scope.alltag = function(i) {
        $scope.tag_delivery[1] = i;
        $scope.tag_delivery[2] = i;
        $scope.tag_delivery[3] = i;
        $scope.tag_delivery[4] = i;
        $scope.tag_delivery[5] = i;
        $scope.shanghuot = i;
        $scope.peisongot = i;
    };

    $scope.alldeliverytag = function(i) {
        $scope.tag_delivery[1] = i;
        $scope.tag_delivery[2] = i;
        $scope.tag_delivery[3] = i;
        $scope.tag_delivery[4] = i;
        $scope.tag_delivery[5] = i;
    };

    $scope.goto = function(page, showload){
        if (page <= 0){
            page = 1;
        }
        $scope.tb_change = 0;
        if(showload){
            $("#progress-bar").foundation('reveal', 'open', {
                animation: 'none', //fade, fadeAndPop, none
                animationspeed: 300, //how fast animtions are
                close_on_background_click: false //if you click background will modal close
            });
        }
        //订单状态选择
        var state = [];
        for (var i = 0; i < DELIVERY.length; i++){
            if($scope.tag_delivery[i]){
                state.push(DELIVERY[i]);
            }
        }
        //是否超时选择
        var exp_t = 0;
        if ($scope.shanghuot){
            exp_t = SHANGHUACC_MIN;
        } else if ($scope.peisongot){
            exp_t = DELIVERYACC_MIN;
        }
        //日期选择
        var d = $scope.day;
        if ($scope.date != "某天"){
            var darr = $scope.date.split("/");
            d = ""+darr[2]+"-"+darr[0]+"-"+darr[1];
        }
        Service.getQueryData("/orderget", {
            type: 6, //外卖订单
            state: String(state),
            page: page,
            pagesize: 20,
            lastoid: $scope.lastoid,
            day: d,
            exp_time: exp_t
        }, function(ret){
            if(showload) {
                $("#progress-bar").foundation('reveal', 'close');
            }
            if(ret.success){
                $scope.orders = ret.data.orders;
                if ($scope.orders.length <= 0){
                    $scope.page = 1;
                }else{
                    $scope.updatelefttime();
                }
                $scope.update_count(ret.data.stats);
            }else{
                $scope.orders = [];
            }
            $scope.ns = 0;
        });
        $scope.page = page;
    };

    $scope.setuporderdetail = function(order, i){
        $scope.selorder = i;
        //orders
        if (order == undefined){
            return ;
        }
        $scope.detail_oid = order.id;
        //shop
        $scope.detail_shopuid = order.qf_uid;
        if (order.shop != undefined){
            $scope.detail_shoptitle = order.shop.title;
            $scope.detail_shopaddr = order.shop.addr;
            $scope.detail_shoptel = order.shop.tel;
        }else{
            $scope.detail_shoptitle = "";
            $scope.detail_shopaddr = "";
            $scope.detail_shoptel = "";
        }
        //customer
        $scope.detail_cusuid = order.openid;
        $scope.detail_cusname = order.contact;
        $scope.detail_cusaddr = order.address;
        $scope.detail_custel = order.telephone;
        //goods
        $scope.detail_goodsname = order.good_name;
        $scope.detail_goodsremark = order.remark;
        $scope.detail_goodsamount = order.amount;
        $scope.detail_goodspayable = order.payable;
        //delivery
        if (order.delivery != undefined){
            $scope.detail_postman = order.delivery.courier_name;
            $scope.detail_posttel = order.delivery.courier_mobile;
            $scope.detail_poststatus = order.delivery.wstatus;
            $scope.detail_postut = order.delivery.update_time;
        }else{
            $scope.detail_postman = "";
            $scope.detail_posttel = "";
            $scope.detail_poststatus = "";
            $scope.detail_postut = "";
        }
        //orderoprating
        Service.getQueryData("/orderops", {
            order_id: order.id
        }, function(ret){
            if(ret.success){
                $scope.detail_oops = [];
                for (var i = 0; i < ret.data.ops.length; i++){
                    if (i < ret.data.ops.length-1){
                        if (ret.data.ops[i].operate_type == 0){
                            continue;
                        }
                        var op = ret.data.ops[i];
                        op.duration = $scope.timegap_s(
                            ret.data.ops[i].operate_time,
                            ret.data.ops[i+1].operate_time
                        );
                        op.duration_m = parseInt(op.duration/60);
                        $scope.detail_oops.push(op);
                    }else{
                        $scope.detail_oops.push(ret.data.ops[i]);
                    }
                }
            }else{
                $scope.detail_oops = [];
            }
        });
    };

    $scope.popdetail = function(order, i){
        $scope.setuporderdetail(order, i);
        $("#orderdetail_modal").foundation('reveal', 'open', {
            animation: 'fadeAndPop', //fade, fadeAndPop, none
            animationspeed: 300, //how fast animtions are
            close_on_background_click: true //if you click background will modal close
        });
    };

    $(document).on('close.fndtn.reveal', '[data-reveal]', function () {
        var modal = $(this);
        if (modal.attr("id") == "orderdetail_modal"){
            $scope.selorder = null;
        }
    });

    $scope.timegap_s = function(t1, t2){
        t1 = t1.toString().replace(/-/g, "/");
        t2 = t2.toString().replace(/-/g, "/");
        var d1 = new Date(t1);
        var d2 = new Date(t2);
        return ((d2-d1)/1000.0).toFixed(2);
    }

    $scope.intro = function(){
        $("#intro_modal").foundation('reveal', 'open', {
            animation: 'fadeAndPop', //fade, fadeAndPop, none
            animationspeed: 300, //how fast animtions are
            close_on_background_click: true //if you click background will modal close
        });
    }
});

var utils = {
    tips: function (msg, delay) {
        var html = '<div class="alert alert-warning alert-dismissable">'
            + '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button>'
            + '<strong>' + msg + '</strong>'
            + '</div>';
        $("#tips").html(html).show();

        //重新设置关闭按钮的事件
        $("#tips").find(".close").click(function () {
            $("#tips").hide("slow").empty();
        });

        var timeout = 3000;
        if (typeof(delay) == 'undefined') {
            setTimeout(function () {
                $("#tips").hide("slow").empty();
            }, timeout);
            return;
        }
        if (delay > 0) {
            setTimeout(function () {
                $("#tips").hide("slow").empty();
            }, delay);
        }
    },
    progressbar: {
        show: function (msg) {
            var info = "加载中";
            if (!(typeof(msg) == 'undefined') && msg != "") {
                info = msg;
            }
            var a = '<div class="modal fade in" role="dialog" aria-hidden="false" aria-labelledby="good_modalLabel" tabindex="1" style="background-color:#303030; display: block; opacity:0.6;">';
            var html = '<div class="progress progress-striped active"><div class="progress-bar progress-bar-success"  role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%;opacity:1;">' + info + '</div></div>';
            $("#tips").html(a+html+"</div>").show();
        },
        hide: function () {
            $("#tips").hide();
        }
    }
};