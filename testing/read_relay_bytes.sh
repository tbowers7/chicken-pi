#!/bin/bash

for i in {1..4}
do
    #echo "i2cget -y 1 0x10 ${i}"
    i2cget -y 1 0x10 $i
done
