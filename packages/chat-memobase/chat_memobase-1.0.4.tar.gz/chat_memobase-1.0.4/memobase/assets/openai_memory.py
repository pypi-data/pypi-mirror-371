"""Read the docs of how this patch works: https://docs.memobase.io/features/openai"""

from memobase_server.src.client.memobase import MemoBaseClient
from openai import AzureOpenAI, AsyncAzureOpenAI
from memobase_server.src.client.memobase.patch.openai import openai_memory
from time import sleep
import asyncio
import os

os.environ["OPENAI_API_KEY"]="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"
endpoint = "https://weiwei-openai-resource.cognitiveservices.azure.com/"
model_name = "gpt-4.1-mini"
deployment = "gpt-4.1-mini"

subscription_key = "7rKbsNBXvhlE7eicXjQ4f5oP2xKBiBhxedPtdUyvN2ZY1EDc3n2uJQQJ99BFACHYHv6XJ3w3AAAAACOGScjT"
api_version = "2024-12-01-preview"

stream = True
user_name = "test41"

# 1. Patch the OpenAI client to use MemoBase
# client = OpenAI()
client = AsyncAzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)
mb_client = MemoBaseClient(
    project_url="http://localhost:8019",
    api_key="secret",
)
client = openai_memory(client, mb_client)
# ------------------------------------------
# 2. 将 chat 函数改为 async def
async def chat(message, close_session=False, use_users=True):
    print("Q: ", message)
    # 3. 使用 await 调用 create 方法 🚀
    r = await client.chat.completions.create(
        messages=[
            {"role": "user", "content": message},
        ],
        model=deployment,
        stream=stream,
        # 4. user_id 的用法保持不变
        user_id=user_name if use_users else None,
    )
    # 下面是处理异步响应
    if stream:
        # 5. 使用 async for 遍历异步流
        async for i in r:
            if i.choices:
                print(i.choices[0].delta.content or "", end="", flush=True)
        print()
    else:
        # 非流式模式下，r 已经是完整的响应对象
        print(r.choices[0].message.content)

    # 6. flush 部分
    if close_session:
        # 在异步函数中，使用 asyncio.sleep
        await asyncio.sleep(0.1)  # 等待最后一条消息被后台任务处理
        client.flush(user_name)


# 7. 创建一个 main 异步函数来运行所有测试步骤
async def main():
    print("--------Use OpenAI without memory--------")
    await chat("I'm Gus, how are you?", use_users=False)
    await chat("What's my name?", use_users=False)

    print("\n--------Use OpenAI with memory--------")
    await chat("I'm Gus, how are you?", close_session=True)
    await chat("What's my name?")

    print("\n--------Memobase Memory--------")
    # get_memory_prompt 是一个同步函数，所以不需要 await
    print(client.get_memory_prompt(user_name))

    print("\n--------User Profile--------")
    # 修正：通过 client 获取 profile，而不是未定义的 user 对象
    print(client.get_profile(user_name))


# 8. 使用 asyncio.run() 来启动程序
if __name__ == "__main__":
    # 请确保替换上面的 endpoint, deployment, 和 subscription_key
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure your Azure OpenAI credentials (endpoint, deployment, api_key) are set correctly.")
