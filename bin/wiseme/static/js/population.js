/**
 * Created by cww on 15/8/1.
 */


var popModule = angular.module("popModule", ["ngSanitize"]);
//chart
var dailytrade = null;

var dailytm = null;
var dailyzx = null;

popModule.config(function ($interpolateProvider) {
    $interpolateProvider.startSymbol("{[{");
    $interpolateProvider.endSymbol("}]}");
});

//通用接口
popModule.factory("Service", function ($http) {
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
popModule.controller("popCtrl", function ($scope, Service){
    $scope.population = [];
    $scope.date = [];
    $scope.month = [];
    $scope.dailypvuv = null;
    $scope.dailyrihuo = null;
    $scope.dailyzz = null;
    $scope.dailytradeamt = null;
    $scope.init = function(population){
        $scope.population = population;
        var ydataset = $scope.dayscale(0, 1, true,
            ["user_day_cnt", "pv", "uv", "zx_amt", "tm_amt", "dh_amt", "qiye_amt", "wx_amt",
                "zx_num", "tm_num", "dh_num", "qiye_num", "wx_num", "others_amt", "others_num"],
            $scope.population);
        // 路径配置
        require.config({
            paths: {
                echarts: '../static/js/echart/dist/'
            }
        });
        require(
            [
                'echarts',
                'echarts/chart/line'
            ],
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
                dailytrade = ec.init(document.getElementById('dailytrade'), 'macarons');
                $scope.dailypvuv = ec.init(document.getElementById('dailypvuv'), 'macarons');
                $scope.dailyrihuo = ec.init(document.getElementById('dailyrihuo'), 'macarons');
                $scope.dailyzz = ec.init(document.getElementById('dailyzz'), 'macarons');
                $scope.dailytradeamt = ec.init(document.getElementById('dailytradeamt'), 'macarons');
                $scope.dailytradenum = ec.init(document.getElementById('dailytradenum'), 'macarons');
                dailytm = ec.init(document.getElementById('dailytm'), 'macarons');
                dailyzx = ec.init(document.getElementById('dailyzx'), 'macarons');
                // 为echarts对象加载数据
                var dailytrade_op = $scope.getOp();
                var dailytradeamt_op = $scope.getOp();
                var dailytradenum_op = $scope.getOp();
                var dailyzz_op = $scope.getOp();
                var dailyrihuo_op = $scope.getOp();
                var dailypvuv_op = $scope.getOp();
                var dailytm_op = $scope.getOp();
                var dailyzx_op = $scope.getOp();
                dailytradenum_op.title.text = "交易笔数";
                dailytradenum_op.legend.data = ["特卖笔数", "专享卡笔数", "微信交易笔数"];
                dailytradenum_op.xAxis = [
                    {
                        type : 'category',
                        data : ydataset.date.slice(40),
                        boundaryGap: false
                    }
                ]
                dailytradenum_op.yAxis = [
                    {
                        type : 'value',
                        name : '交易笔数'
                    }
                ];
                dailytradenum_op.series = [
                    {
                        name:'特卖笔数',
                        type:'line',
                        stack:"amt1",
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["tm_num"].slice(40)
                    },
                    {
                        name:'专享卡笔数',
                        type:'line',
                        stack:"amt1",
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["zx_num"].slice(40)
                    },
                    {
                        name:'微信交易笔数',
                        type:'line',
                        stack:"amt1",
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["others_num"].slice(40)
                    }
                ];
                dailytradeamt_op.title.text = "交易金额";
                dailytradeamt_op.legend.data = ["特卖金额", "专享卡金额", "微信交易金额"];
                dailytradeamt_op.xAxis = [
                    {
                        type : 'category',
                        data : ydataset.date.slice(40),
                        min : '2015-08-16 周日',
                        boundaryGap: false
                    }
                ]
                dailytradeamt_op.yAxis = [
                    {
                        type : 'value',
                        name : '交易金额'
                    }
                ];
                dailytradeamt_op.series = [
                    {
                        name:'特卖金额',
                        type:'line',
                        stack:"amt1",
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["tm_amt"].slice(40)
                    },
                    {
                        name:'专享卡金额',
                        type:'line',
                        stack:"amt1",
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["zx_amt"].slice(40)
                    },
                    {
                        name:'微信交易金额',
                        type:'line',
                        stack:"amt1",
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["others_amt"].slice(40)
                    }
                ];
                dailytrade_op.title.text = "微信总交易";
                dailytrade_op.legend.data = ["交易金额", "交易笔数"];
                dailytrade_op.xAxis = [
                    {
                        type : 'category',
                        data : ydataset.date.slice(40),
                        boundaryGap: false
                    }
                ]
                dailytrade_op.yAxis = [
                    {
                        type : 'value',
                        name : '交易金额'
                    },{
                        type : 'value',
                        name : '交易笔数'
                    }
                ];
                dailytrade_op.series = [
                    {
                        name:'交易金额',
                        type:'line',
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["wx_amt"].slice(40)
                    },{
                        name:'交易笔数',
                        type:'line',
                        yAxisIndex: 1,
                        z: 5,
                        data: ydataset["wx_num"].slice(40)
                    }
                ];
                dailyzz_op.title.text = "增长用户数";
                dailyzz_op.legend.data = ["增长用户数"];
                dailyzz_op.xAxis = [
                    {
                        type : 'category',
                        boundaryGap: false,
                        data : ydataset.date
                    }
                ]
                dailyzz_op.yAxis = [
                    {
                        type : 'value',
                        name : ''
                    }
                ];
                dailyzz_op.series = [
                    {
                        name:'增长用户数',
                        type:'line',
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["user_day_cnt"]
                    }
                ];
                var rihuodataset = $scope.dayscale(0, 7, true,["uv"], $scope.population, 1);
                dailyrihuo_op.title.text = "平均日活";
                dailyrihuo_op.legend.data = ["平均日活"];
                dailyrihuo_op.xAxis = [
                    {
                        type : 'category',
                        boundaryGap: false,
                        data : rihuodataset.date
                    }
                ]
                dailyrihuo_op.yAxis = [
                    {
                        type : 'value',
                        name : '平均日活'
                    }
                ];
                dailyrihuo_op.series = [
                    {
                        name:'平均日活',
                        type:'line',
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: rihuodataset["uv"]
                    }
                ];
                dailypvuv_op.title.text = "浏览量";
                dailypvuv_op.legend.data = ["总浏览量", "总浏览用户量"];
                dailypvuv_op.xAxis = [
                    {
                        type : 'category',
                        boundaryGap: false,
                        data : ydataset.date
                    }
                ]
                dailypvuv_op.yAxis = [
                    {
                        type : 'value',
                        name : '总浏览量'
                    },{
                        type : 'value',
                        name : '总浏览用户量'
                    }
                ];
                dailypvuv_op.series = [
                    {
                        name:'总浏览量',
                        type:'line',
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["pv"]
                    },{
                        name:'总浏览用户量',
                        type:'line',
                        yAxisIndex: 1,
                        z: 5,
                        data: ydataset["uv"]
                    }
                ];
                dailytm_op.title.text = "特卖";
                dailytm_op.legend.data = ["特卖金额", "特卖单数"];
                dailytm_op.xAxis = [
                    {
                        type : 'category',
                        boundaryGap: false,
                        data : ydataset.date.slice(40)
                    }
                ]
                dailytm_op.yAxis = [
                    {
                        type : 'value',
                        name : '特卖金额'
                    },{
                        type : 'value',
                        name : '特卖单数'
                    }
                ];
                dailytm_op.series = [
                    {
                        name:'特卖金额',
                        type:'line',
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["tm_amt"].slice(40)
                    },{
                        name:'特卖单数',
                        type:'line',
                        yAxisIndex: 1,
                        z: 5,
                        data: ydataset["tm_num"].slice(40)
                    }
                ];
                dailyzx_op.title.text = "专享交易";
                dailyzx_op.legend.data = ["专享金额", "专享笔数"];
                dailyzx_op.xAxis = [
                    {
                        type : 'category',
                        boundaryGap: false,
                        data : ydataset.date.slice(40)
                    }
                ]
                dailyzx_op.yAxis = [
                    {
                        type : 'value',
                        name : '专享金额'
                    },{
                        type : 'value',
                        name : '专享笔数'
                    }
                ];
                dailyzx_op.series = [
                    {
                        name:'专享金额',
                        type:'line',
                        itemStyle: {
                            normal: {
                                areaStyle: {type: 'default'}
                            }
                        },
                        data: ydataset["zx_amt"].slice(40)
                    },{
                        name:'专享笔数',
                        type:'line',
                        yAxisIndex: 1,
                        z: 5,
                        data: ydataset["zx_num"].slice(40)
                    }
                ];
                dailytrade.setOption(dailytrade_op);
                $scope.dailypvuv.setOption(dailypvuv_op);
                $scope.dailyrihuo.setOption(dailyrihuo_op);
                $scope.dailyzz.setOption(dailyzz_op);
                $scope.dailytradeamt.setOption(dailytradeamt_op);
                $scope.dailytradenum.setOption(dailytradenum_op);
                dailytm.setOption(dailytm_op);
                dailyzx.setOption(dailyzx_op);
            }
        );
    };

    $scope.getOp = function(){
        return {
            animation: false,
            title : {
                text: ''
            },
            tooltip : {
                trigger: 'axis'
            },
            legend: {
                data:[]
            },
            calculable : true,
            xAxis : [
                {
                    type : 'category',
                    boundaryGap: false
                }
            ],
            yAxis : [
                {
                    type : 'value'
                }
            ],
            series : []
        };
    };

    $scope.dayscale = function(weekday, gap, ifacc, pop_data, population, avrg, startfrom){
        //gap = 1;//gep=1 -> everyday
        //ifacc = true;
        //pop_data = ["pv", "uv"];
        var ret_data = {date:[]};
        var gg = population[0].weekday % gap;
        avrg = arguments[5] || 0;
        startfrom = arguments[6] || 0;
        population = population.slice(startfrom);
        for (var i = 0, g = gg; i < population.length; i++, g++){
            if ( g == weekday ){
                //第一天进入ret_data
                var wd = population[i].weekday+1;
                if (wd == 7){
                    wd = "日";
                }
                var strDate = population[i].c_yearmonthday + " 周" + wd;
                if (gap != 1){
                    strDate = strDate + "(+"+gap+")";
                }
                ret_data.date.push(strDate);
                for (var j = 0; j < pop_data.length; j++){
                    if(ret_data[pop_data[j]] == undefined){
                        ret_data[pop_data[j]] = [];
                    }
                    if (population[i][pop_data[j]] != undefined){
                        if (avrg){
                            ret_data[pop_data[j]].push(Number(population[i][pop_data[j]])/gap);
                        }else{
                            ret_data[pop_data[j]].push(Number(population[i][pop_data[j]]));
                        }
                    }else{
                        ret_data[pop_data[j]] = [0];
                    }
                }
            }else if (ifacc){
                //如果ifacc则累加数据
                if (!ret_data.date.length){
                    var strDate = population[i].c_yearmonthday;
                    if (gap != 1){
                        strDate = strDate + "(+"+gap+")";
                    }
                    ret_data.date.push(strDate);
                }
                for (var j = 0; j < pop_data.length; j++){
                    if (ret_data[pop_data[j]] == undefined){
                        ret_data[pop_data[j]] = [0];
                    }
                    if (population[i][pop_data[j]] != undefined){
                        var popup = ret_data[pop_data[j]].pop();
                        if (avrg){
                            popup += Number(population[i][pop_data[j]])/gap;
                        }else{
                            popup += Number(population[i][pop_data[j]]);
                        }
                        ret_data[pop_data[j]].push(popup);
                    }
                }
            }
            if (g >= gap-1){
                //g++，下个循环变回0
                g = -1;
            }
        }
        return ret_data;
    };

    $scope.monthscale = function(pop_data, population, avrg, startfrom){
        var ret_data = {date:[], days:[]};
        avrg = arguments[2] || 0;
        startfrom = arguments[3] || 0;
        population = population.slice(startfrom);
        for (var i = 0; i < population.length; i++){
            var topx = ret_data.date.pop();
            if(topx == population[i].c_yearmonth){
                ret_data.date.push(population[i].c_yearmonth);
                ret_data.days.push(ret_data.days.pop()+1);
                for (var j = 0; j < pop_data.length; j++){
                    if(ret_data[pop_data[j]] == undefined){
                        ret_data[pop_data[j]] = [];
                    }
                    if (population[i][pop_data[j]] != undefined){
                        var popup = ret_data[pop_data[j]].pop();
                        popup += Number(population[i][pop_data[j]]);
                        ret_data[pop_data[j]].push(popup);
                    }else{
                        ret_data[pop_data[j]] = [0];
                    }
                }
            }else{
                if(topx){
                    ret_data.date.push(topx);
                }
                ret_data.days.push(1);
                ret_data.date.push(population[i].c_yearmonth);
                for (var j = 0, d = 1; j < pop_data.length; j++, d++){
                    if(ret_data[pop_data[j]] == undefined){
                        ret_data[pop_data[j]] = [];
                    }
                    if (population[i][pop_data[j]] != undefined){
                        ret_data[pop_data[j]].push(Number(population[i][pop_data[j]]));
                    }else{
                        ret_data[pop_data[j]] = [0];
                    }
                }
            }
        }
        if (avrg){
            for(var i = 0; i < pop_data.length; i++){
                for(var j = 0; j < ret_data[pop_data[i]].length; j++){
                    ret_data[pop_data[i]][j] = Number((ret_data[pop_data[i]][j]/ret_data.days[j]).toFixed(2));
                }
            }
        }

        return ret_data;
    };

    $scope.rechart = function(weekday, gap, ifacc, pop_data, thechart, averg, startfrom){
        var ret_data = {};
        averg = arguments[5] || 0;
        startfrom = arguments[6] || 0;
        if(gap == 30){
            ret_data = $scope.monthscale(pop_data, $scope.population, averg, startfrom);
        }else{
            ret_data = $scope.dayscale(weekday, gap, ifacc, pop_data, $scope.population, averg, startfrom);
        }
        var chop = thechart.getOption();
        chop.xAxis[0].data = ret_data.date;
        for (var i = 0; i < chop.series.length; i++){
            if (ret_data[pop_data[i]]){
                chop.series[i].data = ret_data[pop_data[i]];
            }else{
                chop.series[i].data = [];
            }
        }
        thechart.setOption(chop, true);
    }
});

/*
  `c_yearmonthday` varchar(64) NOT NULL DEFAULT '' COMMENT '年月日',
  `c_yearmonth` varchar(64) DEFAULT NULL COMMENT '年月',
  `c_year` varchar(64) DEFAULT NULL COMMENT '年',
  `topic_day_cnt` int(10) DEFAULT NULL COMMENT '增长话题数',
  `topic_cnt` int(10) DEFAULT NULL COMMENT '截止到当天累计话题数',
  `post_day_cnt` int(10) DEFAULT NULL COMMENT '增长帖子量',
  `post_cnt` int(10) DEFAULT NULL COMMENT '截止到当天累计帖子数',
  周／月平均日活
  !`user_day_cnt` int(10) DEFAULT NULL COMMENT '增长用户数',
  `user_cnt` int(10) DEFAULT NULL COMMENT '累计到当天总体用户数',
  `commnets_day_cnt` int(10) DEFAULT NULL COMMENT '增长评论数',
  `comments_cnt` int(10) DEFAULT NULL COMMENT '累计到当天评论数',
  `pv` int(10) DEFAULT NULL COMMENT '当天总浏览量',
  !`uv` int(10) DEFAULT NULL COMMENT '当天总浏览用户量',
  !`active_user_cnt` int(10) DEFAULT NULL COMMENT '核心活跃用户数',
  `sale_day_cnt` int(10) DEFAULT NULL COMMENT '特卖单数',
  `sale_cnt` int(10) DEFAULT NULL COMMENT '累计特卖单数',
  `sale_day_amt` int(10) DEFAULT NULL COMMENT '特卖金额',
  `sale_amt` int(10) DEFAULT NULL COMMENT '累计金额',
  `average_post_cnt` int(10) DEFAULT NULL COMMENT '每个话题平均贴子数',
  `average_post_likes` int(10) DEFAULT NULL COMMENT '平均帖子点赞数',

  `qiye_num` int(10) DEFAULT NULL COMMENT '企业活动特卖单数',
  `qiye_amt` double(16,2) DEFAULT NULL COMMENT '企业活动特卖金额',
  `zx_num` int(10) DEFAULT NULL COMMENT '企业专享卡消费笔数',
  `zx_amt` double(16,2) DEFAULT NULL COMMENT '企业专享卡消费金额',
  `soho_num` int(10) DEFAULT NULL COMMENT 'SOHO商户微信交易笔数',
  `soho_amt` double(16,2) DEFAULT NULL COMMENT 'SOHO商户微信交易金额',
  `tm_num` int(10) DEFAULT NULL COMMENT '特卖交易笔数',
  `tm_amt` double(16,2) DEFAULT NULL COMMENT '特卖交易金额',
  `dh_num` int(10) DEFAULT NULL COMMENT '特卖兑换单数',
  `dh_amt` double(16,2) DEFAULT NULL COMMENT '特卖兑换金额',
  `wx_num` int(10) DEFAULT NULL COMMENT '总微信交易笔数',
  `wx_amt` double(16,2) DEFAULT NULL COMMENT '总微信交易金额',
*
* */