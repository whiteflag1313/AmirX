package main

import "C"
import (
	"fmt"
	"net"
	"time"
)

//export StartCore
func StartCore(configJson *C.char, port C.int) C.int {
	cfgStr := C.GoString(configJson)
	fmt.Printf("[AmirX Go Core] Starting with config length: %d on port: %d\n", len(cfgStr), port)
	
	_, err := net.DialTimeout("tcp", "1.1.1.1:443", 3*time.Second)
	if err != nil {
		return -1
	}
	return 0
}

func main() {}

