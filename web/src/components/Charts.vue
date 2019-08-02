<template>
    <div>
        <div class="loading" v-show="showLoading"></div>
        <div class="search-input">
            <input
                    type="text"
                    class="text-edit"
                    v-model="keyword"
                    placeholder="--输入感兴趣的食物例如:牛肉--"
                    @focus="handleTextEditFocus"
            />
             <!--<button class="btn">OK</button>-->
        </div>
        <div class="search-content" ref="searchContent" v-show="showSearchList">
            <ul>
                <li
                        class="search-item border-bottom"
                        v-for="item in list"
                        :key="item"
                        @click="handleFoodClick(item)"
                >{{item}}
                </li>
            </ul>
        </div>
        <div v-show="!showSearchList" class="echart-container" ref="echartContainer1"></div>
        <div v-show="!showSearchList" class="echart-container" ref="echartContainer2"></div>
        <div v-show="!showSearchList" class="echart-container" ref="echartContainer3"></div>
        <div v-show="this.keyword.length === 0" class="echart-container" ref="echartContainer4"></div>
        <div v-show="this.keyword.length === 0" class="echart-container" ref="echartContainer5"></div>
        <div v-show="this.keyword.length === 0" class="echart-container" ref="echartContainer_d_1"></div>
        <div v-show="this.keyword.length === 0" class="echart-container" ref="echartContainer_d_2"></div>
        <div v-show="this.keyword.length === 0" class="echart-container" ref="echartContainer_d_3"></div>
        <div v-show="this.keyword.length === 0" class="echart-container" ref="echartContainer_d_4"></div>
        <div v-show="this.keyword.length === 0" class="echart-container" ref="echartContainer_d_5"></div>
    </div>
</template>

<script>
    import echarts from "echarts";
    import axios from "axios";
    import {foodNames, allLikeCount, allDislikeCount, allCount, dayLikeCount, dayDislikeCount, dayOfWeekHighRate} from "@/comm/data"

    export default {
        name: "Charts",
        data() {
            return {
                keyword: "",
                list: [],
                allNames: [],
                showList: false,
                host_addr: "http://10.13.145.72:8888",
                showLoading: false,
            };
        },
        methods: {
            handleTextEditFocus() {
                this.showList = true;
            },
            handleFoodClick(name) {
                this.showList = false;
                this.keyword = name;
                let self = this;
                axios
                    .get(this.host_addr + "/food/dayofweek/count?name=" + name)
                    .then(res => {
                        if (res.data) {
                            self.chart1.setOption({
                                title: {text: name + "周次分布"},
                                tooltip: {},
                                xAxis: {
                                    data: ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                                    axisLabel: {
                                        rotate: 0
                                    }
                                },
                                yAxis: {},
                                series: [
                                    {
                                        name: "次数",
                                        type: "bar",
                                        data: res.data
                                    }
                                ]
                            });
                        }
                    });

                axios.get(this.host_addr + "/food/date/count?name=" + name).then(res => {
                    if (res.data) {
                        self.chart2.setOption({
                            title: {text: name + "出现日期分布"},
                            tooltip: {},
                            xAxis: {
                                data: res.data.dates,
                                axisLabel: {
                                    rotate: 0
                                }
                            },
                            yAxis: {},
                            series: [
                                {
                                    name: "次数",
                                    type: "bar",
                                    data: res.data.counts
                                }
                            ]
                        });
                    }
                });

                axios
                    .get(this.host_addr + "/food/likedislike/count?name=" + name)
                    .then(res => {
                        if (res.data) {
                            self.chart3.setOption({
                                title: {text: name + "点赞数/踩数"},
                                tooltip: {},
                                xAxis: {
                                    data: ["赞", "踩"]
                                },
                                yAxis: {},
                                series: [
                                    {
                                        name: "数量",
                                        type: "bar",
                                        data: res.data
                                    }
                                ]
                            });
                        }
                    });
            },

            initFoodNames() {
                this.showLoading = true;
                let self = this;
                axios.get(this.host_addr + "/food/names").then(res => {
                  if (res.data) {
                    self.allNames = res.data;
                    this.showLoading = false;
                  }
                });
                // self.allNames = foodNames()
            },
            initFoodLikeDislike() {
                let self = this;
                axios
                  .all([
                    axios.get(this.host_addr + "/all/like/count"),
                    axios.get(this.host_addr + "/all/dislike/count"),
                    axios.get(this.host_addr + "/all/count")
                  ])
                  .then(
                    axios.spread((a, b, c) => {
                      if (a.data) self.allLikeCnt = a.data;
                      if (b.data) self.allDislikeCnt = b.data;
                      if (c.data) self.allCnt = c.data;
                      self.setAllCharts();
                    })
                  );
                this.dayLikeCnt = dayLikeCount();
                this.dayDislikeCnt = dayDislikeCount()
            },
            setAllCharts() {
                this.chart1.setOption({
                    title: {text: "点赞总榜前15名"},
                    tooltip: {},
                    xAxis: {
                        data: this.allLikeCnt.names,
                        axisLabel: {
                            rotate: 60
                        }
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "点赞数",
                            type: "bar",
                            data: this.allLikeCnt.counts
                        }
                    ]
                });
                this.chart2.setOption({
                    title: {text: "踩总榜前15名"},
                    tooltip: {},
                    xAxis: {
                        data: this.allDislikeCnt.names,
                        axisLabel: {
                            rotate: 60
                        }
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "踩数",
                            type: "bar",
                            data: this.allDislikeCnt.counts
                        }
                    ]
                });
                this.chart3.setOption({
                    title: {text: "菜式种类/总数"},
                    tooltip: {},
                    xAxis: {
                        data: ["菜式种类", "出现总数"]
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "数量",
                            type: "bar",
                            data: this.allCnt
                        }
                    ]
                });
                this.chart4.setOption({
                    title: {text: "单日点赞榜前15名"},
                    tooltip: {},
                    xAxis: {
                        data: this.dayLikeCnt.names,
                        axisLabel: {
                            rotate: 60
                        }
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "数量",
                            type: "bar",
                            data: this.dayLikeCnt.counts
                        }
                    ]
                });
                this.chart5.setOption({
                    title: {text: "单日踩榜前15名"},
                    tooltip: {},
                    xAxis: {
                        data: this.dayDislikeCnt.names,
                        axisLabel: {
                            rotate: 60
                        }
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "数量",
                            type: "bar",
                            data: this.dayDislikeCnt.counts
                        }
                    ]
                });
                this.chart_d_1.setOption({
                    title: {text: "周一高频菜品(仅午晚餐)"},
                    tooltip: {},
                    xAxis: {
                        data: dayOfWeekHighRate(1).names,
                        axisLabel: {
                            rotate: 30
                        }
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "出现次数",
                            type: "bar",
                            data: dayOfWeekHighRate(1).counts
                        }
                    ]
                });
                this.chart_d_2.setOption({
                    title: {text: "周二高频菜品(仅午晚餐)"},
                    tooltip: {},
                    xAxis: {
                        data: dayOfWeekHighRate(2).names,
                        axisLabel: {
                            rotate: 30
                        }
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "出现次数",
                            type: "bar",
                            data: dayOfWeekHighRate(2).counts
                        }
                    ]
                });
                this.chart_d_3.setOption({
                    title: {text: "周三高频菜品(仅午晚餐)"},
                    tooltip: {},
                    xAxis: {
                        data: dayOfWeekHighRate(3).names,
                        axisLabel: {
                            rotate: 30
                        }
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "出现次数",
                            type: "bar",
                            data: dayOfWeekHighRate(3).counts
                        }
                    ]
                });
                this.chart_d_4.setOption({
                    title: {text: "周四高频菜品(仅午晚餐)"},
                    tooltip: {},
                    xAxis: {
                        data: dayOfWeekHighRate(4).names,
                        axisLabel: {
                            rotate: 30
                        }
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "出现次数",
                            type: "bar",
                            data: dayOfWeekHighRate(4).counts
                        }
                    ]
                });
                this.chart_d_5.setOption({
                    title: {text: "周五高频菜品(仅午晚餐)"},
                    tooltip: {},
                    xAxis: {
                        data: dayOfWeekHighRate(5).names,
                        axisLabel: {
                            rotate: 30
                        }
                    },
                    yAxis: {},
                    series: [
                        {
                            name: "出现次数",
                            type: "bar",
                            data: dayOfWeekHighRate(5).counts
                        }
                    ]
                });
            }
        },
        computed: {
            showSearchList() {
                return this.showList && this.keyword !== "";
            }
        },
        mounted() {
            this.initFoodNames();
            this.initFoodLikeDislike();
            this.chart1 = echarts.init(this.$refs.echartContainer1);
            this.chart2 = echarts.init(this.$refs.echartContainer2);
            this.chart3 = echarts.init(this.$refs.echartContainer3);
            this.chart4 = echarts.init(this.$refs.echartContainer4);
            this.chart5 = echarts.init(this.$refs.echartContainer5);
            this.chart_d_1 = echarts.init(this.$refs.echartContainer_d_1);
            this.chart_d_2 = echarts.init(this.$refs.echartContainer_d_2);
            this.chart_d_3 = echarts.init(this.$refs.echartContainer_d_3);
            this.chart_d_4 = echarts.init(this.$refs.echartContainer_d_4);
            this.chart_d_5 = echarts.init(this.$refs.echartContainer_d_5);
            this.setAllCharts()
        },
        watch: {
            keyword(w) {
                if (w == "" && self.allLikeCnt !== null && self.allDislikeCnt !== null) {
                    this.setAllCharts();
                }
                if (this.allNames.length > 0) {
                    this.list = this.allNames.filter(name => {
                        return name.indexOf(w) !== -1;
                    });
                }
            }
        }
    };
</script>


<style scoped>
    .loading {
        height: 100px;
        width: 100px;
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        margin: auto;
        position: fixed;
        background: url("../assets/loading.gif") no-repeat center;
    }

    li {
        list-style-type: none;
    }

    ul {
        padding: 0;
    }

    .search-input {
        display: flex;
        height: 40px;
    }

    .text-edit {
        flex: 1;
        font-size: 1em;
        text-align: center;
    }

    .btn {
        width: 120px;
        background-color: cornflowerblue;
        color: white;
        margin-left: 5px;
    }

    .search-content {
        z-index: 1;
        position: absolute;
        top: 100px;
        left: 0;
        right: 0;
        bottom: 0;
        background: #eee;
    }

    .search-item {
        line-height: 40px;
        background: #fff;
        color: #666;
        text-align: center;
        /* text-indent: 10px; */
    }

    .echart-container {
        margin-top: 10px;
        height: 570px;
    }
</style>

