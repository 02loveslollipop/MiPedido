package utils

import (
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

//A singleton instance of Upgrader to manage WebSocket connections
// This is a thread-safe singleton pattern implementation in Go

var lock = &sync.Mutex{}

type UpgraderInstance struct {
	*websocket.Upgrader
}

var upgraderInstance *UpgraderInstance

func GetInstance() *UpgraderInstance {
	if upgraderInstance == nil {
		lock.Lock() // Lock to ensure that only one goroutine can create the instance at a time
		defer lock.Unlock() // Ensure that only one goroutine can create the instance at a time and release the lock when done by defer statement
		if upgraderInstance == nil {
			upgraderInstance = &UpgraderInstance{
				&websocket.Upgrader{
					CheckOrigin: func(r *http.Request) bool {
						return true
					},
					ReadBufferSize:  1024,
					WriteBufferSize: 1024,
				},
			}
		}
	}
	return upgraderInstance
}

// WebSocket connection parameters

