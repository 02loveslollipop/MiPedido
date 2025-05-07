FROM golang:1.24.2-alpine
WORKDIR /
COPY . .
RUN go mod download
RUN go build -o redisIndexerCronJon cmd/main/main.go
CMD ["./redisIndexerCronJon"]