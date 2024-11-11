#!/bin/bash

ports=(443 1443 2443 3443 4443 5443 6443 7443 8443 9443 8080 8081 8082 8083)
hosts=('xxx.com' 'xxx2.com')

declare -i blocked_cnt
declare -i non_blocked_cnt

blocked_cnt=0
non_blocked_cnt=0

for host in ${hosts[*]}
do
	for port in ${ports[*]}
	do
		nc -z -vv -w 2 $host $port > /dev/null 2> err.txt
		if [ $? -ne 0 ]; then
			grep -q "refused" err.txt
			if [ $? -ne 0 ]
			then
				echo "$host:$port blocked!"
				let blocked_cnt++
			else
				echo "$host:$port not blocked"
				let non_blocked_cnt++
			fi	
		else
			echo "$host:$port not blocked"
			let non_blocked_cnt++
		fi
	done
done

rm -f err.txt

echo "blocked count: ${blocked_cnt}"
echo "non-blocked count: ${non_blocked_cnt}"
