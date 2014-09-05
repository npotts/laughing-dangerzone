#!/bin/bash

atftp --trace --option "timeout 1" --option "mode octet" --put --local-file $1 192.168.1.20
