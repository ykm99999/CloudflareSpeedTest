package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"runtime"
	"time"

	"github.com/XIU2/CloudflareSpeedTest/task"
	"github.com/XIU2/CloudflareSpeedTest/utils"
)

var (
	version    = "v1.0.0"
	versionNew string
	ipCountry  = make(map[string]string)
)

func init() {
	var printVersion bool
	var minDelay, maxDelay, downloadTime int
	var maxLossRate float64

	flag.IntVar(&task.Routines, "n", 200, "延迟测速线程")
	flag.IntVar(&task.PingTimes, "t", 4, "延迟测速次数")
	flag.IntVar(&task.TestCount, "dn", 10, "下载测速数量")
	flag.IntVar(&downloadTime, "dt", 10, "下载测速时间")
	flag.IntVar(&task.TCPPort, "tp", 443, "指定测速端口")
	flag.StringVar(&task.URL, "url", "https://cf.xiu2.xyz/url", "指定测速地址")

	flag.IntVar(&maxDelay, "tl", 9999, "平均延迟上限")
	flag.IntVar(&minDelay, "tll", 0, "平均延迟下限")
	flag.Float64Var(&maxLossRate, "tlr", 1, "丢包几率上限")
	flag.Float64Var(&task.MinSpeed, "sl", 0, "下载速度下限")

	flag.IntVar(&utils.PrintNum, "p", 10, "显示结果数量")
	flag.StringVar(&task.IPFile, "f", "ip.txt", "IP段数据文件")
	flag.StringVar(&task.IPText, "ip", "", "指定IP段数据")
	flag.StringVar(&utils.Output, "o", "result.csv", "输出结果文件")

	flag.BoolVar(&task.Disable, "dd", false, "禁用下载测速")
	flag.BoolVar(&task.TestAll, "allip", false, "测速全部 IP")
	flag.BoolVar(&utils.Debug, "debug", false, "调试输出模式")
	flag.BoolVar(&printVersion, "v", false, "打印程序版本")
	flag.Usage = func() { fmt.Print("使用 -h 查看帮助说明\n") }
	flag.Parse()

	utils.InputMaxDelay = time.Duration(maxDelay) * time.Millisecond
	utils.InputMinDelay = time.Duration(minDelay) * time.Millisecond
	utils.InputMaxLossRate = float32(maxLossRate)
	task.Timeout = time.Duration(downloadTime) * time.Second
	task.HttpingCFColomap = task.MapColoMap()

	if printVersion {
		println(version)
		fmt.Println("检查版本更新中...")
		checkUpdate()
		if versionNew != "" {
			utils.Yellow.Printf("*** 发现新版本 [%s]！请前往 [https://github.com/XIU2/CloudflareSpeedTest] 更新！ ***", versionNew)
		} else {
			utils.Green.Println("当前为最新版本 [" + version + "]！")
		}
		os.Exit(0)
	}
}

func main() {
	task.InitRandSeed()
	fmt.Printf("# XIU2/CloudflareSpeedTest %s \n\n", version)

	pingData := task.NewPing().Run().FilterDelay().FilterLossRate()
	speedData := task.TestDownloadSpeed(pingData)
	utils.ExportCsv(speedData)
	speedData.Print()

	writeIPWithCountry(speedData)
	endPrint()
}

func writeIPWithCountry(data []*task.IPResult) {
	file, err := os.Create("ip.txt")
	if err != nil {
		fmt.Println("无法创建 ip.txt:", err)
		return
	}
	defer file.Close()

	for _, r := range data {
		ip := r.IP.String()
		country := getCountry(ip)
		if country != "" && country != "未知" {
			file.WriteString(fmt.Sprintf("%s#%s\n", ip, country))
		}
	}
	fmt.Println("✅ 已生成 ip.txt（格式：IP#国家）")
}

func getCountry(ip string) string {
	if val, ok := ipCountry[ip]; ok {
		return val
	}
	url := fmt.Sprintf("http://ip-api.com/json/%s?lang=zh-CN", ip)
	client := http.Client{Timeout: 5 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return "未知"
	}
	defer resp.Body.Close()
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return "未知"
	}
	var result struct {
		Status  string `json:"status"`
		Country string `json:"country"`
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return "未知"
	}
	if result.Status == "success" && result.Country != "" {
		ipCountry[ip] = result.Country
		return result.Country
	}
	return "未知"
}

func endPrint() {
	if utils.NoPrintResult() {
		return
	}
	if runtime.GOOS == "windows" {
		fmt.Printf("按下 回车键 或 Ctrl+C 退出。")
		fmt.Scanln()
	}
}

func checkUpdate() {
	timeout := 10 * time.Second
	client := http.Client{Timeout: timeout}
	res, err := client.Get("https://api.xiu2.xyz/ver/cloudflarespeedtest.txt")
	if err != nil {
		return
	}
	body, err := io.ReadAll(res.Body)
	if err != nil {
		return
	}
	defer res.Body.Close()
	if string(body) != version {
		versionNew = string(body)
	}
}