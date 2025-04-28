FROM golang:1.24.2-alpine
WORKDIR /
COPY . .
RUN go mod download
RUN go build -o ratingCronJob main.go
CMD ["./ratingCronJob"]