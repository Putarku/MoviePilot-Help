# 基础镜像
FROM python:3.11-slim

# 设置环境变量，时区
ENV TZ=Asia/Shanghai
ENV DEBIAN_FRONTEND=noninteractive

# 安装 Nonebot 必要依赖
RUN pip install --no-cache-dir 'nonebot2[fastapi]' nonebot-adapter-onebot httpx

# 设置工作目录为 nb2
WORKDIR /nb2

# 设置容器启动时执行的命令
CMD ["python3", "bot.py", "--reload"]