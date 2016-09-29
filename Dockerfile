FROM python:3-onbuild
ENV COOL_STORAGE /data
RUN mkdir -p /etc/cool /data
CMD ["./server.py", "--host", "0.0.0.0", "--port", "26100"]
EXPOSE 26100
