#!/bin/bash

interval=30
pause=10

beep () {
	printf "%s\a\n" "$1"
}

workout () {
	i=0
	while [ $i -lt 3 ]; do
		beep '*'
		sleep 1
		i=$((i + 1))
	done

	for e in 'Jumping Jacks' 'Wall Sit' 'Push-up' 'Crunch' 'Chair Step' 'Squat' 'Dip' 'Plank' 'High Knees' 'Lunge' 'Push-up Rotation' 'Plank Right' 'Plank Left'; do
		echo $e
		sleep ${pause}
		beep 'START'
		sleep ${interval}
		beep 'STOP'
	done
}

workout
