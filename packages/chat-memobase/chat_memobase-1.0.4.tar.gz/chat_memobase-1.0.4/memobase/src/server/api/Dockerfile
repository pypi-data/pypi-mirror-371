FROM python:3.12-slim-bookworm

# 设置 pip 镜像
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/
ENV PIP_TRUSTED_HOST=mirrors.aliyun.com

# 替换 apt 源为阿里云
RUN echo "deb https://mirrors.aliyun.com/debian bookworm main contrib non-free non-free-firmware\n\
deb https://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free non-free-firmware\n\
deb https://mirrors.aliyun.com/debian bookworm-updates main contrib non-free non-free-firmware\n\
deb https://mirrors.aliyun.com/debian bookworm-backports main contrib non-free non-free-firmware" > /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libpq-dev \
    curl \
    git
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# 安装 Poetry（显式添加路径并确认版本）
RUN pip uninstall -y poetry || true

# 安装最新 poetry，确保用最新版本
RUN curl -sSL https://install.python-poetry.org | python3 -

# 设置 PATH
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

# 这里用一个 RUN 把导出和安装依赖放一起，确保 PATH 生效
RUN poetry config virtualenvs.in-project true  # 在项目内创建虚拟环境
ENV VIRTUAL_ENV=/app/.venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# 安装依赖（在激活的环境中进行）
RUN poetry install --no-interaction --no-root --only main

# 拷贝代码等后续操作...
COPY ./memobase_server /app/memobase_server
COPY ./api.py /app

EXPOSE 8000
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]