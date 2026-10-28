#!/bin/bash
echo "Bắt đầu khởi động Ollama server..."
ollama serve &
OLLAMA_PID=$!
sleep 10 # Đợi Ollama khởi động

echo "Bắt đầu chạy inference..."
python predict.py

echo "Hoàn tất. Kết quả lưu tại /result/submission.jsonl"
kill $OLLAMA_PID